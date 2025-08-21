import pandas as pd

from .kawa_action_processor import ActionProcessor


class PythonRunnableProcessor(ActionProcessor):

    def retrieve_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load(self, df: pd.DataFrame):
        pass  # we do not load any data for automation

    def need_defined_outputs(self) -> bool:
        return False
