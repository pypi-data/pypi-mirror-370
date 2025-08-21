from dataclasses import dataclass
from typing import cast

from kywy.client.kawa_client import KawaClient

from ..scripts.processors.kawa_action_processor import ActionProcessor
from ..scripts.processors.kawa_python_column_processor import PythonColumnProcessor
from ..scripts.processors.kawa_python_datasource_processor import PythonDatasourceProcessor
from ..scripts.processors.kawa_python_datasource_preview_processor import PythonDatasourcePreviewProcessor
from ..scripts.processors.kawa_python_metadata_processor import PythonMetaDataProcessor
from ..scripts.kawa_secrets import KawaSecrets


@dataclass
class ScriptRunnerInputs:
    python_action_type: str
    script_runner_path: str
    pex_file_path: str
    job_id: str
    module: str
    job_log_file: str
    secrets: KawaSecrets
    repo_path: str
    kawa_client: KawaClient
    action_processor: ActionProcessor
    kawa_meta_data: dict
    script_parameters_values_dict: dict

    def needs_defined_outputs(self) -> bool:
        return self.action_processor.need_defined_outputs()

    def is_preview(self) -> bool:
        return isinstance(self.action_processor, PythonDatasourcePreviewProcessor)

    def is_datasource_script(self) -> bool:
        return isinstance(self.action_processor, PythonDatasourceProcessor)

    def is_incremental(self) -> bool:
        return self.is_datasource_script() and not cast(PythonDatasourceProcessor,
                                                        self.action_processor).reset_before_insert

    def is_metadata(self) -> bool:
        return isinstance(self.action_processor, PythonMetaDataProcessor)

    def _is_python_column_script(self):
        return isinstance(self.action_processor, PythonColumnProcessor)

    def should_delete_files_at_end_of_run(self) -> bool:
        return self._is_python_column_script()
