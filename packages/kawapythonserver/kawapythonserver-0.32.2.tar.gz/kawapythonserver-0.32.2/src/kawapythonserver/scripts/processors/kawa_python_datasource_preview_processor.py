import datetime
from typing import List

import pandas as pd

from .kawa_action_processor import ActionProcessor
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_log_manager import get_kawa_logger


class PythonDatasourcePreviewProcessor(ActionProcessor):
    def __init__(self,
                 job_id: str,
                 meta_data: dict,
                 kawa_directory_manager: KawaDirectoryManager):
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager
        self.job_id: str = job_id
        self.meta_data = meta_data

    def retrieve_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load(self, df: pd.DataFrame):
        get_kawa_logger().info(f'Start to dump preview json, metadata: {self.meta_data}, jobId: {self.job_id}')
        new_df = df.head(100)
        for date_column in self.date_columns():
            if len(new_df) != 0:
                new_df[date_column] = new_df.apply(
                    lambda row: PythonDatasourcePreviewProcessor.map_date_to_epoch(row[date_column]), axis=1)
        json = new_df.to_json(orient='records', date_unit='ms')
        self.kawa_directory_manager.write_json_etl_preview(self.job_id, json)
        get_kawa_logger().info(f'End to dump preview json, metadata: {self.meta_data}, jobId: {self.job_id}')

    def date_columns(self) -> List[str]:
        return self.type_columns('date')

    def type_columns(self, t: str) -> List[str]:
        return [output.get('name') for output in self.meta_data.get('outputs', {}) if output.get('type') == t]

    @staticmethod
    def map_date_to_epoch(value):
        if isinstance(value, datetime.date):
            return (value - datetime.date(1970, 1, 1)).days
        return None
