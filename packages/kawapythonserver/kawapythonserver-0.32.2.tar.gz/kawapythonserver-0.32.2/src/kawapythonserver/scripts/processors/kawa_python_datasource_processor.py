import time
import typing

import pandas as pd
import pyarrow as pa
from kywy.client.data_loader import KawaDataLoader
from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_client import KawaEntities

from .kawa_action_processor import ActionProcessor
from ...server.kawa_log_manager import get_kawa_logger


class PythonDatasourceProcessor(ActionProcessor):
    def __init__(self,
                 datasource_id: str,
                 reset_before_insert: bool,
                 optimize_after_insert: bool,
                 job_id: str,
                 kawa_client: KawaClient):
        self.K: KawaClient = kawa_client
        self.datasource_id: str = datasource_id
        self.reset_before_insert = reset_before_insert
        self.optimize_after_insert = optimize_after_insert
        self.job_id: str = job_id
        self.entities: KawaEntities = self.K.entities

    def retrieve_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load(self, df: pd.DataFrame):
        try:
            start_time = time.time()
            get_kawa_logger().info(f'Start data loading (arrow streaming) for jobId: {self.job_id}')
            self._load_with_arrow_streaming(df)
            t = round(time.time() - start_time, 1)
            get_kawa_logger().info(f'End of data loading in {t} for jobId: {self.job_id}')
            return

        except Exception as e:
            get_kawa_logger().info(f'Error while data loading with arrow streaming: {e}')
            get_kawa_logger().info(f'Start data loading (with parquet), jobId: {self.job_id}')
            self._load_with_parquet(df)
            get_kawa_logger().info(f'End of data loading, jobId: {self.job_id}')


    def _load_with_arrow_streaming(self, df: pd.DataFrame):
        table = pa.Table.from_pandas(df)
        data_loader = KawaDataLoader(
            self.K,
            df=None,
            arrow_table=table,
            datasource_name=None,
            datasource_id=self.datasource_id
        )
        data_loader.load_data(reset_before_insert=self.reset_before_insert,
                              job_id=self.job_id,
                              optimize_after_insert=self.optimize_after_insert)

    def _load_with_parquet(self, df: pd.DataFrame):
        data_loader = KawaDataLoader(
            self.K,
            df=df,
            datasource_name=None,
            datasource_id=self.datasource_id
        )
        data_loader.load_data(reset_before_insert=self.reset_before_insert,
                              job_id=self.job_id,
                              optimize_after_insert=self.optimize_after_insert)

    def data_source_id(self) -> typing.Optional[str]:
        return self.datasource_id

