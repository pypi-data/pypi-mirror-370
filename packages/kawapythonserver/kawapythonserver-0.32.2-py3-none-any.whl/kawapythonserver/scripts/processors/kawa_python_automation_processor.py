
import pandas as pd

from .kawa_action_processor import ActionProcessor
from ...server.kawa_directory_manager import KawaDirectoryManager


class PythonAutomationProcessor(ActionProcessor):
    def __init__(self,
                 job_id: str,
                 kawa_directory_manager: KawaDirectoryManager):
        self.job_id = job_id
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager

    def retrieve_data(self) -> pd.DataFrame:
        arrow_table = self.kawa_directory_manager.read_table(self.job_id)
        return arrow_table.to_pandas()

    def load(self, df: pd.DataFrame):
        pass  # we do not load any data for automation

    def need_defined_outputs(self) -> bool:
        return False
