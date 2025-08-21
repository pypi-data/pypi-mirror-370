from dataclasses import dataclass
import inspect
import sys
from pathlib import Path
import datetime
import importlib
import logging
import pickle
import time
from inspect import getmembers, isfunction
from typing import List, Dict, Set
import pandas as pd
from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_decorators import KawaScriptParameter
from kywy.client.kawa_types import Types

# script runner is executed as the separate process,
# so we need to import all the modules from kawapythonserver package,
# which should be in the PYTHONPATH of the script runner process,
# for PEX, the equivalent would be the PEX_EXTRA_SYS_PATH variable
current_file = Path(__file__)
sys.path.append(str(current_file.parent.parent))

from kawapythonserver.scripts.meta_data_checker import MetaDataChecker
from kawapythonserver.server.interpreter_error import InterpreterError
from kawapythonserver.server.kawa_log_manager import KawaLogManager
from kawapythonserver.server.kawa_script_runner_inputs import ScriptRunnerInputs

current_step = ''

sub_process_log_config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}


@dataclass(frozen=True)
class FileIdAndPath:
    file_id: str
    file_path: str


def _get_executable_from_repo(repo_path_: str,
                              module_: str):
    global current_step
    try:
        sys.path.append(f'{repo_path_}')
        python_module = importlib.import_module(module_)
        importlib.reload(python_module)
    finally:
        sys.path.remove(f'{repo_path_}')

    potential_functions_with_decorator = [t[1] for t in getmembers(python_module, isfunction) if
                                          hasattr(t[1], 'inputs')]

    if len(potential_functions_with_decorator) == 0:
        raise Exception('The python script provided contains no kawa tool (method decorated with @kawa_tool).')

    if len(potential_functions_with_decorator) > 1:
        raise Exception('The script provided contains more than one kawa tool (method decorated with @kawa_tool).')
    final_function = potential_functions_with_decorator[0]

    inputs_provided_by_kawa = ['df', 'kawa', 'data_preview', 'append']

    params_and_secrets_mapping = _extract_secrets_and_parameters(final_function)
    inputs_provided_by_kawa.extend(params_and_secrets_mapping)

    _validate_function_arguments(final_function, inputs_provided_by_kawa)

    return final_function


def _validate_function_arguments(function, inputs_provided):
    function_signature = inspect.signature(function)
    necessaries_inputs = [param_name for param_name, param in function_signature.parameters.items()
                          if param.default is param.empty]

    missing_inputs = list(set(necessaries_inputs).difference(inputs_provided))

    if len(missing_inputs) != 0:
        raise InterpreterError(f'Some arguments defined in the main function: {function.__name__} '
                               f'are not defined. The list : {",".join(missing_inputs)}')


def _extract_secrets_and_parameters(final_function):
    params_and_secrets_mapping = []

    secret_names = set()
    if hasattr(final_function, 'secrets'):
        secret_names = set(dict(final_function.secrets).keys())
        if 'kawa' in secret_names:
            raise InterpreterError('kawa is a reserved name for the KawaClient and cannot be used in secrets')
        if 'df' in secret_names:
            raise InterpreterError('df is a reserved name for the DataFrame input and cannot be used in secrets')

    param_names = set()
    if hasattr(final_function, 'parameters'):
        param_names = {d.name for d in final_function.parameters}
        params_and_secrets_mapping.extend(param_names)
        if 'kawa' in param_names:
            raise InterpreterError('kawa is a reserved name for the KawaClient and cannot be used in parameters')
        if 'df' in param_names:
            raise InterpreterError('df is a reserved name for the DataFrame input and cannot be used in parameters')

    if hasattr(final_function, 'secrets') and hasattr(final_function, 'parameters'):
        intersection_of_keys = set.intersection(secret_names, param_names)
        if intersection_of_keys:
            raise InterpreterError(f'Some secrets and parameters have the same name, this is not possible:'
                                   f' {intersection_of_keys}')
    params_and_secrets_mapping.extend(secret_names)
    params_and_secrets_mapping.extend(param_names)
    return params_and_secrets_mapping


def update_datasource_indicators_with_new_outputs(datasource_id: str,
                                                  outputs: List[dict],
                                                  kawa_client: KawaClient,
                                                  kawa_logger: logging.Logger):
    kawa_logger.info('Start updating the datasource indicators with potential new outputs')
    try:
        kawa_client.commands.run_command('UpdateDataSourceWithScriptOutputIfNecessary', {
            'dataSourceId': datasource_id,
            'outputs': outputs
        })
        kawa_logger.info('End updating the datasource indicators with potential new outputs')
    except Exception as e:
        kawa_logger.error(f'Issue when updating potential new indicators in datasource with error: {e}')


def _execute_function(script_runner_inputs: ScriptRunnerInputs,
                      df: pd.DataFrame,
                      kawa_logger: logging.Logger) -> pd.DataFrame:
    global current_step
    file_paths_to_clean: Set[FileIdAndPath] = set()

    try:
        current_step = 'extracting executable'
        function = _get_executable_from_repo(script_runner_inputs.repo_path, script_runner_inputs.module)

        available_parameters = {'df': df, 'kawa': script_runner_inputs.kawa_client}
        kawa_meta_data = script_runner_inputs.kawa_meta_data
        kawa_inputs = kawa_meta_data['parameters']
        kawa_outputs = kawa_meta_data.get('outputs', [])
        kawa_parameters = kawa_meta_data.get('scriptParameters', [])

        if script_runner_inputs.needs_defined_outputs():
            if not hasattr(function, 'outputs') or not function.outputs:
                raise Exception('No output was defined on the tool. It is necessary for python columns and Python ETL')

        meta_data_checker = MetaDataChecker.from_dicts(kawa_inputs,
                                                       kawa_outputs,
                                                       kawa_parameters,
                                                       function.inputs,
                                                       function.outputs,
                                                       function.parameters,
                                                       kawa_logger)
        meta_data_checker.check()

        datasource_id = script_runner_inputs.action_processor.data_source_id() if script_runner_inputs.action_processor else None
        if datasource_id:
            update_datasource_indicators_with_new_outputs(datasource_id,
                                                          function.outputs,
                                                          script_runner_inputs.kawa_client,
                                                          kawa_logger)

        if hasattr(function, 'secrets'):
            available_parameters.update({param: script_runner_inputs.secrets.get(key_secret)
                                         for param, key_secret in function.secrets.items()})

        if hasattr(function, 'parameters'):
            parameters = _extract_parameters_and_convert_if_date_or_datetime(
                script_runner_inputs.script_parameters_values_dict,
                function.parameters)

            available_parameters.update(parameters)

            file_param_to_path = _download_files_and_return_local_path(script_runner_inputs.kawa_client,
                                                                       function.parameters,
                                                                       script_runner_inputs.script_parameters_values_dict,
                                                                       kawa_logger)
            file_paths_to_clean.update(file_param_to_path.values())
            file_param_to_path = {k: v.file_path for k, v in file_param_to_path.items()}
            kawa_logger.info(f'File param to path: {file_param_to_path}')
            available_parameters.update(file_param_to_path)

        # get the function parameters
        necessary_parameters = function.__code__.co_varnames[:function.__code__.co_argcount]

        # In preview mode we set the data_preview to True (this is not mandatory anymore)
        if 'data_preview' in necessary_parameters:
            if script_runner_inputs.is_preview():
                available_parameters['data_preview'] = True
            else:
                available_parameters['data_preview'] = False

        # In datasource mode, use might want to have different way of working when we do incremental
        # or reset_before_insert
        if 'append' in necessary_parameters:
            if script_runner_inputs.is_incremental():
                available_parameters['append'] = True
            else:
                available_parameters['append'] = False

        # now keep only the necessaries parameters
        final_parameters = {k: v for k, v in available_parameters.items() if k in necessary_parameters}
        current_step = 'executing the script'
        # now apply the parameters to the function
        return function(**final_parameters)
    except Exception as e:
        raise e
    finally:
        for file_id_and_path in file_paths_to_clean:
            try:
                Path(file_id_and_path.file_path).unlink()
            except Exception as e:
                kawa_logger.error(f'Could not remove local file with path: {file_id_and_path.file_path}, error: {e}')
            try:
                if script_runner_inputs.should_delete_files_at_end_of_run():
                    res = script_runner_inputs.kawa_client.delete_file(file_id_and_path.file_id)
                    if res.get('error'):
                        raise Exception(res.get('error'))
            except Exception as e:
                kawa_logger.error(f'Could not delete file on file store with id: '
                                  f'{file_id_and_path.file_id}, error: {e}')


def _download_files_and_return_local_path(kawa: KawaClient,
                                          function_parameters: List[KawaScriptParameter],
                                          param_values: dict,
                                          kawa_logger: logging.Logger) -> Dict[str, FileIdAndPath]:
    kawa_logger.info(f'Now loading the files')
    res = {p.name: FileIdAndPath(param_values.get(p.name), kawa.download_file_as_id(param_values.get(p.name)))
           for p in function_parameters
           if p.extensions and param_values.get(p.name)}
    kawa_logger.info(f'Loading files finished')
    return res


def _extract_parameters_and_convert_if_date_or_datetime(script_parameters_values_dict: dict,
                                                        function_parameters: List[KawaScriptParameter]) -> dict:
    new_values = {}
    for function_parameter in function_parameters:
        param_name = function_parameter.name
        param_type = function_parameter.type
        param_value = script_parameters_values_dict.get(param_name, function_parameter.default)
        if param_type == Types.DATE:
            new_values[param_name] = datetime.date(1970, 1, 1) + datetime.timedelta(days=param_value)
        elif param_type == Types.DATE_TIME:
            new_values[param_name] = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=param_value)
        elif param_type == Types.BOOLEAN:
            if isinstance(param_value, bool):
                new_values[param_name] = param_value
            elif isinstance(param_value, str):
                new_values[param_name] = True if param_value.upper() == 'TRUE' else False
            else:
                raise Exception(f'The parameter {param_name} is noted as boolean and we received the value :'
                                f' {param_value}')
        else:
            new_values[param_name] = param_value

    return new_values


def _run_script_with_callback(script_runner_inputs: ScriptRunnerInputs, kawa_logger: logging.Logger, job_id):
    global current_step
    current_step = 'retrieve data from kawa'
    df = script_runner_inputs.action_processor.retrieve_data()
    kawa_logger.info(f'Start executing the tool, jobId: {job_id}')
    start_time = time.time()
    output_if_available = _execute_function(script_runner_inputs, df, kawa_logger)
    t = round(time.time() - start_time, 1)
    kawa_logger.info(f'End  executing the tool in {t} for jobId: {job_id}')
    if script_runner_inputs.action_processor.need_defined_outputs():
        current_step = 'loading the resulting dataframe into Kawa'
        if isinstance(output_if_available, pd.DataFrame):
            script_runner_inputs.action_processor.load(output_if_available)
        else:
            raise InterpreterError(f'Script must return a pandas.DataFrame, jobId: {job_id}')


def _run_script(script_runner_inputs: ScriptRunnerInputs):
    global current_step
    job_id = script_runner_inputs.job_id

    kawa_log_manager = KawaLogManager(sub_process_log_config, 0, None, False)
    kawa_log_manager.configure_root_logger_of_job_process(script_runner_inputs.job_log_file)
    kawa_logger = logging.getLogger('kawa')
    start_time = time.time()
    kawa_logger.info(f'Start for jobId: {job_id}')
    try:
        function = _get_executable_from_repo(script_runner_inputs.repo_path, script_runner_inputs.module)
        if script_runner_inputs.is_metadata():
            kawa_logger.info(f'Extracting metadata for jobId: {job_id}')
            metadata = {
                'parameters': function.inputs,
                'outputs': function.outputs,
                'scriptParameters': function.parameters,
                'toolDescription': function.description
            }
            script_runner_inputs.action_processor.dump_metadata(metadata)
        else:
            _run_script_with_callback(script_runner_inputs, kawa_logger, job_id)
        execution_time = round(time.time() - start_time, 1)
        kawa_logger.info(f'End of task in subprocess in {execution_time} seconds for jobId: {job_id}')
    except Exception as e:
        kawa_logger.error(f'Error while {current_step}: for jobId: {job_id}')
        kawa_logger.error(e)
        raise e

    finally:
        root_logger = logging.getLogger()
        kawa_log_manager.remove_all_handlers(root_logger)


if __name__ == '__main__':
    runner_inputs: ScriptRunnerInputs = pickle.loads(sys.stdin.buffer.read())
    _run_script(runner_inputs)
