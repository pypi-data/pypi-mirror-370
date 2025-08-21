import concurrent.futures
import json
import logging
import threading
import traceback
import os
import time
import sys
from dataclasses import dataclass
from pathlib import Path

import tempfile
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.flight
import pyarrow.parquet
from importlib.metadata import version

from .git_repository import GitRepository, build_and_sync_git_repository
from .interpreter_error import InterpreterError
from .jobs.job_executor_2 import KawaJobExecutorBatched
from .jobs.job_manager_client import JobManagerClient
from .kawa_directory_manager import KawaDirectoryManager
from ..server.jobs.job_executor import KawaJobExecutor
from ..server.jobs.job_runner import JobRunner
from .kawa_log_manager import KawaLogManager, get_kawa_logger
from .. import __version__


class KawaFlightServer(pa.flight.FlightServerBase):
    MAX_OLD_JOB = 12 * 3600
    CHECK_OLD_JOB_INTERVAL = 3600

    def __init__(self,
                 dict_logging_config,
                 job_logging_level,
                 job_logging_formatter,
                 pex_executable_path: str,
                 script_runner_path: str,
                 location=None,
                 working_directory: Path = None,
                 tls_certificates=None,
                 aes_key=None,
                 kawa_url=None,
                 **kwargs):
        super(KawaFlightServer, self).__init__(location=location, tls_certificates=tls_certificates, **kwargs)
        self._location = location
        self._aes_key = aes_key
        self.kawa_url = kawa_url
        self.executor: concurrent.futures.ProcessPoolExecutor = concurrent.futures.ProcessPoolExecutor()

        self.directory_manager: KawaDirectoryManager = KawaDirectoryManager(working_directory)
        self.log_manager: KawaLogManager = KawaLogManager(
            dict_logging_config,
            job_logging_level,
            logging.Formatter(job_logging_formatter)
        )
        self.kawa_job_runner: JobRunner = JobRunner(self.directory_manager,
                                                    pex_executable_path,
                                                    script_runner_path,
                                                    self._aes_key,
                                                    self.kawa_url)
        self.python_job_manager_client = JobManagerClient(self.kawa_url, self._aes_key)

        self.kawa_job_executor: KawaJobExecutorBatched = KawaJobExecutorBatched(self.python_job_manager_client,
                                                                                self.kawa_job_runner,
                                                                                self.directory_manager)
        self.remove_old_jobs()

        server_version = __version__
        kywy_version = version("kywy")
        connected_to_kawa = os.getenv('KAWA_URL', 'http://localhost:8080')
        python_version = sys.version

        get_kawa_logger().info('KAWA Python automation server started at location: %s', self._location)
        get_kawa_logger().info(f'''
        
WWWNKOkddoolllcc:::::::::::::::::cccllooddkOKNWWWW
MWKxl::;:;;;;;;;;;;;;;;;;;;;:;;;;;;;;;;;;;::lxKWMM
WOl:;;;;;:::;;;;;;;;;::;;;;;;;;;;;;;;;;;:;;::;ckNM
0l:;;;;:;;;;;;;;;;;;;::;;:;;;;;;;;:;;;;;:;;:;;;cOW
x:;;;;;;;;;;;;;;;;;;;::ccc::;:;;;;;;;;;;;;;;;;::dX
o;;;;;;;;;;;;;;;::;:cx0XXK0xl:;;;;;;;;;;;;;;;;;;oK
l;;;;;;;;;;;;;;;::cxKWWNNWWWXkl:;;;;;;;;;;;;;;;;l0
c;;;;;;;;:;;;;;:lxKWWXOoldkXWWXkl:;;:;;;;;;;;;;;cO
:;;;;:;;:;;:::cxKWWXOl:;;;:lkXWWXkl::;;:;;;;;;;;ck
:;;;;;::;;;;:oKWWXOlcll::cloclkXWWKd:::;;;;;;;;;:k
:;:;;;;:;;:;:kWMWOc;:dkkkkkdc;ckNMWOc;;;:;;;;;;;:x
:;;;;:;;;;;;:lONMW0dc::cccc::o0NWN0o:;;;;;;;;;;;:x
:;;;;;::;:;;:;:o0NMW0dc::::o0NWN0dc;;::;;;;;;;;;:x
:;::;;;;;;;;;::::o0NWN0xdk0NWN0d::::;:;;;;;;;;;;:x
:;;:;;;:;;;:lk0xc::o0NMWWMWN0dc:cx0Oo:;;;;;;;;;;:k
:;;;;;;;;;cxXWWKo:::dXMMNX0dl:::l0WWNkc;;;;;;;;;:k
c;;;;;;;;;lKMMXd::d0NMN0dlokK0dc:oKMMXo;;;;;::;;cO
l;;;;;;;;;:dKWWXO0NWN0d:::lONWWKOXWWXxc;;;;;:;;;c0
o;;;;;;;:;;:lxKWWWN0dc;;;;;:oONWWWXkl:;;;;;;:;;;lK
d:;;;:;;::;;;:coddlc:;;;::;;;:lddoc:;;;;;;;;::;;oX
kc;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;::;:xN
Xd:;:;;::::;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::oKM
MNkl:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:;:cxXMM
MMWXOxolccc::::::::;;;;;;;;;;;;:::::::cccloxOXWMMM
MMMMMWNXK0OOkxxdddooooooooooooodddxxkOO0KXNWMMMMMM

Python {python_version}
KAWA Python Server Version: {server_version}
KAWA Python SDK version (KYWY): {kywy_version}
KAWA Server @ {connected_to_kawa}

Visit us at: https://www.kawa.ai''')

    def _make_flight_info(self, job_id):
        schema = pq.read_schema(self.directory_manager.dataset_path(job_id))
        metadata = pq.read_metadata(self.directory_manager.dataset_path(job_id))
        descriptor = pa.flight.FlightDescriptor.for_path(
            job_id.encode('utf-8')
        )
        endpoints = [pa.flight.FlightEndpoint(job_id, [self._location])]
        return pyarrow.flight.FlightInfo(schema,
                                         descriptor,
                                         endpoints,
                                         metadata.num_rows,
                                         metadata.serialized_size)

    def list_flights(self, context, criteria):
        raise InterpreterError('Not supported')

    def get_flight_info(self, context, descriptor):
        return self._make_flight_info(descriptor.path[0].decode('utf-8'))

    def do_put(self, context, descriptor, reader, writer):
        job_id = descriptor.path[0].decode('utf-8')
        data_table = reader.read_all()
        get_kawa_logger().info('Upload dataset for job: %s', job_id)
        self.directory_manager.write_table(job_id, data_table)

    def do_get(self, context, ticket):
        job_id = ticket.ticket.decode('utf-8')
        get_kawa_logger().info('Download dataset for job: %s', job_id)
        return pa.flight.RecordBatchStream(self.directory_manager.read_table(job_id))

    def list_actions(self, context):
        return [
            ('run_script', 'Queue an automation script for execution.'),
            ('restart_script', 'Restart an already uploaded script.'),
            ('script_metadata', 'Get automation script metadata (parameters, outputs).'),
            ('health', 'Check server health.'),
            ('etl_preview', 'Load a preview of the output of the script'),

            # git related actions
            ('git_healthcheck', 'Checks the validity of the git repo'),
            ('git_load_toolkits', 'Load the content of a toolkit library for a git repo'),
            ('git_load_tool', 'Load one file from its path on the server')
        ]

    def do_action(self, context, action):
        try:
            get_kawa_logger().debug('action.type: %s', action.type)
            if action.type == 'script_metadata':
                return self.json_to_array_of_one_flight_result(self.action_metadata(action))
            elif action.type == 'health':
                j = f'"status":"OK", "version": "{__version__}"'
                return self.json_to_array_of_one_flight_result('{' + j + '}')
            elif action.type == 'etl_preview':
                return self.json_to_array_of_one_flight_result(self.action_etl_preview(action))
            elif action.type == 'git_load_toolkits':
                return self.json_to_array_of_one_flight_result(self.action_git_load_toolkits(action))
            elif action.type == 'git_load_tool':
                return self.json_to_array_of_one_flight_result(self.action_git_load_tool(action))
            elif action.type == 'git_healthcheck':
                return self.json_to_array_of_one_flight_result(self.action_git_healthcheck(action))
            else:
                raise NotImplementedError
        except Exception as err:
            traceback.print_exception(err)
            raise err

    def action_etl_preview(self, action):
        job_id = None
        try:
            json_action_payload = self.parse_action_payload(action)
            job_id = json_action_payload['job']
            self.kawa_job_runner.run_job(job_id, json_action_payload)
            etl_preview_json = self.directory_manager.read_json_etl_preview(job_id)
            return EtlPreviewResult(etl_preview_json, '').to_json()
        except Exception as err:
            get_kawa_logger().error(f'Error when getting etl preview: {err}')
            res = EtlPreviewResult('', str(err)).to_json()
            return res
        finally:
            if job_id:
                self.directory_manager.remove_etl_preview(job_id)

    def action_metadata(self, action):
        job_id = None
        try:
            json_action_payload = self.parse_action_payload(action)
            job_id = json_action_payload['job']
            self.kawa_job_runner.run_job(job_id, json_action_payload)
            metadata = self.directory_manager.read_json_metadata(job_id)
            return MetadataResult(metadata, '').to_json()
        except Exception as err:
            get_kawa_logger().error(f'Error when getting metadata: {err}')
            res = MetadataResult('', str(err)).to_json()
            return res
        finally:
            if job_id:
                self.directory_manager.remove_metadata(job_id)

    def action_git_load_toolkits(self, action):
        try:
            git = self.load_git_from_action(action)
            files = git.load_toolkits()
            return json.dumps(files)

        except Exception as err:
            get_kawa_logger().error(f'🔴 Error when loading file structure from a git repo: {err}')
            res = MetadataResult('', str(err)).to_json()
            return res

    def action_git_load_tool(self, action):
        try:
            git = self.load_git_from_action(action)
            json_action_payload = self.parse_action_payload(action)
            file_content = git.load_one_file(json_action_payload['fileName'])
            return json.dumps({'fileContent': file_content})

        except Exception as err:
            get_kawa_logger().error(f'🔴 Error when loading a file from a git repo: {err}')
            res = MetadataResult('', str(err)).to_json()
            return res

    def action_git_healthcheck(self, action):
        try:
            git = self.load_git_from_action(action)
            check = git.check_repository_structure()
            return json.dumps(check)

        except Exception as err:
            get_kawa_logger().error(f'🔴 Error when performing the healthcheck: {err}')
            return json.dumps({
                'sourceControlApiConfiguration': False,
                'requirements': False,
                'kawaToolKits': False,
            })

    def remove_old_jobs(self):
        get_kawa_logger().info(f'Start removing the old jobs, with max old job: {self.MAX_OLD_JOB}')
        self.directory_manager.remove_files_older_than(self.MAX_OLD_JOB)
        threading.Timer(self.CHECK_OLD_JOB_INTERVAL, self.remove_old_jobs).start()
        get_kawa_logger().info(f'End removing the old jobs')

    @staticmethod
    def json_to_array_of_one_flight_result(json_result: str):
        flight_result = pyarrow.flight.Result(pyarrow.py_buffer(json_result.encode('utf-8')))
        return [flight_result]

    @staticmethod
    def parse_action_payload(action: pyarrow.flight.Action):
        return json.loads(action.body.to_pybytes().decode('utf-8'))

    def load_git_from_action(self, action: pyarrow.flight.Action) -> GitRepository:
        json_action_payload = self.parse_action_payload(action)
        private_key_content = json_action_payload['privateKey']
        repo_directory = self.directory_manager.repository_root_path()
        return build_and_sync_git_repository(
            repo_directory=repo_directory,
            ssh_remote_url=json_action_payload['remoteUrl'],
            branch=json_action_payload['branchName'],
            private_key=private_key_content,
        )


@dataclass
class EtlPreviewResult:
    result: str
    error: str

    def to_json(self):
        return json.dumps(self.__dict__)


@dataclass
class MetadataResult:
    result: str
    error: str

    def to_json(self):
        return json.dumps(self.__dict__)
