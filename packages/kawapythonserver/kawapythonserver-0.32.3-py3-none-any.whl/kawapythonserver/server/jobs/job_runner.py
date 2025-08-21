import glob
import os
import pickle
import subprocess
import time

from kywy.client.kawa_client import KawaClient

from ..git_repository import GitRepository, build_and_sync_git_repository
from ...scripts.processors.kawa_python_automation_processor import PythonAutomationProcessor
from ...scripts.processors.kawa_python_column_processor import PythonColumnProcessor
from ...scripts.processors.kawa_python_datasource_processor import PythonDatasourceProcessor
from ...scripts.processors.kawa_python_datasource_preview_processor import PythonDatasourcePreviewProcessor
from ...scripts.processors.kawa_python_metadata_processor import PythonMetaDataProcessor
from ...scripts.processors.kawa_python_runnable_processor import PythonRunnableProcessor
from ...scripts.kawa_tool_kit import build_kawa_toolkit_from_yaml_file
from ...server.clear_script_with_secrets import ClearScriptWithSecrets
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_log_manager import get_kawa_logger
from ...server.kawa_pex_builder import KawaPexBuilder
from ...server.kawa_script_runner_inputs import ScriptRunnerInputs


class JobRunner:

    def __init__(self,
                 directory_manager: KawaDirectoryManager,
                 pex_executable_path: str,
                 script_runner_path: str,
                 aes_key: str,
                 kawa_url: str):
        self.directory_manager: KawaDirectoryManager = directory_manager
        self.logger = get_kawa_logger()
        self.pex_executable_path = pex_executable_path
        self.script_runner_path = script_runner_path
        self._aes_key = aes_key
        self.kawa_url = kawa_url

    def run_job(self,
                job_id: str,
                json_action_payload: dict):
        try:
            self.logger.info(f'▶️ Starting to run the job: {job_id}')
            encrypted_script_with_secrets = json_action_payload['script']

            clear_script_with_secrets = ClearScriptWithSecrets.decrypt(encrypted_script_with_secrets, self._aes_key)
            self._load_package_from_source_control(clear_script_with_secrets, job_id)

            module = self._extract_module_from_package_and_task(clear_script_with_secrets, job_id)

            if clear_script_with_secrets.ssh_git:
                git = build_and_sync_git_repository(
                    repo_directory=self.directory_manager.repository_root_path(),
                    ssh_remote_url=clear_script_with_secrets.repo_url,
                    branch=clear_script_with_secrets.branch,
                    private_key=clear_script_with_secrets.repo_key,
                )
                repository_dir = git.local_repo_directory
            else:
                repository_dir = self.directory_manager.repo_path(job_id)

            pex_builder = KawaPexBuilder(
                pex_executable_path=self.pex_executable_path,
                reqs_file_path=f'{repository_dir}/requirements.txt',
                pex_path=self.directory_manager.pex_path(),
            )

            pex_file_path = pex_builder.build_pex_if_necessary(job_id)

            kawa_client = self._create_kawa_client(json_action_payload, job_id, clear_script_with_secrets.api_key)
            callback = self._create_processor(json_action_payload, kawa_client, clear_script_with_secrets)

            script_parameters_values = json_action_payload.get('scriptParametersValues', [])
            script_parameters_dict = {p['scriptParameterName']: p['value']
                                      for p in script_parameters_values
                                      if p.get('value') is not None}

            inputs = ScriptRunnerInputs(
                python_action_type=json_action_payload['pythonActionType'],
                script_runner_path=self.script_runner_path,
                pex_file_path=pex_file_path,
                job_id=job_id,
                module=module,
                job_log_file=self.directory_manager.log_path(job_id),
                secrets=clear_script_with_secrets.kawa_secrets,
                repo_path=repository_dir,
                kawa_client=kawa_client,
                action_processor=callback,
                kawa_meta_data=clear_script_with_secrets.meta_data,
                script_parameters_values_dict=script_parameters_dict,
            )

            self._execute_script_in_sub_process(inputs)
        except Exception as e:
            raise e
        finally:
            self._clean_files(job_id)

    def _execute_script_in_sub_process(self, inputs: ScriptRunnerInputs):
        self.logger.info(f'Starting the sub process to run the script for jobId: {inputs.job_id}')
        start_time = time.time()
        error = ''
        try:
            my_env = os.environ.copy()
            my_env['PEX_EXTRA_SYS_PATH'] = os.pathsep.join([str(inputs.repo_path)])
            self.logger.info(f'PEX_EXTRA_SYS_PATH is {my_env["PEX_EXTRA_SYS_PATH"]}')
            sub = subprocess.run([
                inputs.pex_file_path, self.script_runner_path
            ],
                input=pickle.dumps(inputs),
                timeout=10 * 60,
                check=True,
                capture_output=True,
                env=my_env
            )
            execution_time = round(time.time() - start_time, 1)
            self.logger.info(f'''Logs from subprocess: 
                                 ###### SUB PROCESS LOGS START ######
                                 {sub.stdout.decode("unicode_escape")}
                                 ###### SUB PROCESS LOGS FINISH ######''')
            self.logger.info(f'Sub process ended in {execution_time}s')

        except FileNotFoundError as exc:
            error = f'Process failed because the executable could not be found.{exc}'
        except subprocess.CalledProcessError as exc:
            self.logger.info(exc.stdout.decode("unicode_escape"))
            error = f'Error when execution script: \n {exc.stderr.decode("unicode_escape")}'
        except subprocess.TimeoutExpired as exc:
            if exc.stdout:
                self.logger.info(exc.stdout.decode("unicode_escape"))
            error = f'Process timed out.\n{exc}'
        except Exception as exc:
            self.logger.info('Some unknown exception occurred')
            error = f'Process failed.\n{exc}'
        finally:
            if error:
                self.logger.error(error)
                raise Exception(error)

    def _clean_files(self, job_id):
        self.directory_manager.remove_job_working_files(job_id)
        self.directory_manager.remove_repo_files(job_id)

    def _create_kawa_client(self, action_payload, job_id, api_key) -> KawaClient:
        start = time.time()
        workspace_id = action_payload.get('workspaceId')
        if not api_key:
            return KawaClient(kawa_api_url=self.kawa_url)  # if key is not there we don't need the client
        kawa_client = KawaClient(kawa_api_url=self.kawa_url)
        kawa_client.set_api_key(api_key=api_key)
        kawa_client.set_active_workspace_id(workspace_id=workspace_id)
        exec_time = round(time.time() - start, 1)
        self.logger.info(f'KawaClient created in {exec_time}s for jobId: {job_id}')
        return kawa_client

    def _create_processor(self, action_payload,
                          kawa_client: KawaClient,
                          clear_script_with_secrets: ClearScriptWithSecrets):
        job_id = action_payload['job']

        python_action_type = action_payload['pythonActionType']

        self.logger.info(f'Building a processor for {python_action_type}')
        match python_action_type:
            case 'METADATA':
                return PythonMetaDataProcessor(job_id, self.directory_manager)
            case 'PYTHON_COLUMN':
                python_private_join_id = action_payload.get('pythonPrivateJoinId')
                dashboard_id = action_payload.get('dashboardId')
                application_id = action_payload.get('applicationId')
                return PythonColumnProcessor(python_private_join_id,
                                             job_id,
                                             kawa_client,
                                             dashboard_id,
                                             application_id)
            case 'ETL':
                datasource_id = action_payload.get('dataSourceId')
                reset_before_insert = action_payload.get('isFullRefresh')
                optimize_after_insert = action_payload.get('optimizeTableAfterInsert')
                return PythonDatasourceProcessor(datasource_id=datasource_id,
                                                 reset_before_insert=reset_before_insert,
                                                 optimize_after_insert=optimize_after_insert,
                                                 job_id=job_id,
                                                 kawa_client=kawa_client)
            case 'ETL_PREVIEW':
                return PythonDatasourcePreviewProcessor(job_id,
                                                        clear_script_with_secrets.meta_data,
                                                        self.directory_manager)
            case 'RUNNABLE':
                return PythonRunnableProcessor()
            case 'AUTOMATION':
                return PythonAutomationProcessor(job_id, self.directory_manager)
            case _:
                raise Exception(f'Unknown python action type: {python_action_type}')

    def _load_package_from_source_control(self,
                                          clear_script_with_secrets: ClearScriptWithSecrets,
                                          job_id: str):
        start_time = time.time()
        repo_path = self.directory_manager.repo_path(job_id)
        self.logger.info(f'💾 Start loading repo from source control in {repo_path} for jobId: {job_id}')
        if clear_script_with_secrets.is_from_kawa_source_control():
            # in case of tool coming from kawa source control, we just load the content from ClearScriptWithSecrets
            # and copy it to the repo path
            os.mkdir(repo_path)
            with open(f'{repo_path}/kawa_managed_tool.py', 'w') as file:
                file.write(clear_script_with_secrets.content)
            with open(f'{repo_path}/requirements.txt', 'w') as file:
                file.write(clear_script_with_secrets.requirements)

        elif not clear_script_with_secrets.ssh_git:
            command = 'git clone -b {branch} --single-branch https://oauth2:{token}@{repo_url} {repo_path}'.format(
                branch=clear_script_with_secrets.branch,
                token=clear_script_with_secrets.repo_key,
                repo_url=clear_script_with_secrets.repo_url.replace('https://', ''),
                repo_path=repo_path
            )
            self.logger.info(f'💾 Running {command}')
            os.system(command)
        t = round(time.time() - start_time, 1)
        self.logger.info(f'End loading repo in {t}s from source control for jobId: {job_id}')

    def _extract_module_from_package_and_task(self,
                                              clear_script_with_secrets: ClearScriptWithSecrets,
                                              job_id: str) -> str:
        if clear_script_with_secrets.is_from_kawa_source_control():
            return 'kawa_managed_tool'

        elif clear_script_with_secrets.ssh_git:
            git = GitRepository(
                repo_directory=self.directory_manager.repository_root_path(),
                ssh_remote_url=clear_script_with_secrets.repo_url,
                branch=clear_script_with_secrets.branch,
                private_key=clear_script_with_secrets.repo_key,
            )
            return git.find_one_tool(
                toolkit_name=clear_script_with_secrets.toolkit,
                tool_name=clear_script_with_secrets.tool,
            )
        else:
            toolkit_name = clear_script_with_secrets.toolkit
            tool_name = clear_script_with_secrets.tool
            repo_path = self.directory_manager.repo_path(job_id)
            files = glob.glob(f'{repo_path}/**/kawa-toolkit.yaml', recursive=True)
            kawa_toolkits = [build_kawa_toolkit_from_yaml_file(repo_path, file) for file in files]
            for kawa_toolkit in kawa_toolkits:
                if kawa_toolkit.name != toolkit_name:
                    continue
                for tool in kawa_toolkit.tools:
                    if tool.name != tool_name:
                        continue
                    self.logger.debug(f'MODULE TO USE: {tool.module} for jobId: {job_id}')
                    return tool.module

            raise Exception(f'No module found in the repo for toolkit: {toolkit_name} and tool: {tool_name}')
