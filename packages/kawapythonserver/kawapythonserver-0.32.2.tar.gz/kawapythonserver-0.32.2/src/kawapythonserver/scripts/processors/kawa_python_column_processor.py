import time
import typing

import pandas as pd
import pyarrow as pa
from typing import List, Optional
from kywy.client.data_loader import KawaDataLoader
from kywy.client.kawa_client import KawaClient
from kywy.client.dsl import KawaColumn
from kywy.client.kawa_client import KawaEntities

from .kawa_action_processor import ActionProcessor
from ...server.kawa_log_manager import get_kawa_logger


class PythonColumnProcessor(ActionProcessor):
    def __init__(self, python_private_join_id: str,
                 job_id: str,
                 kawa_client: KawaClient,
                 dashboard_id: Optional[str],
                 application_id: Optional[str]):
        self.K: KawaClient = kawa_client
        self.python_private_join_id: str = python_private_join_id
        self.dashboard_id = dashboard_id
        self.application_id = application_id
        self.job_id: str = job_id
        self.entities: KawaEntities = self.K.entities
        self.python_private_join: dict = self.entities.python_private_joins().get_entity_by_id(
            self.python_private_join_id)
        sheet_id = self.python_private_join['sheetId']
        self.joined_data_source_id: str = self.python_private_join['joinDatasourceId']
        self.sheet: dict = self.entities.sheets().get_entity_by_id(sheet_id)
        self.script: dict = self.entities.entities_of_kind('scripts').get_entity_by_id(
            self.python_private_join['scriptId'])
        self.pk_columns: dict = self.pk_columns()  # columnId to kawa column (java column)
        self.column_ids_to_parameter_name: dict = self.parameters_column_ids_to_parameter_name()
        self.pk_parameter_name_to_indicator_id: dict = self.pk_parameter_name_to_indicator_id()
        self.missing_pks_to_add: List[KawaColumn] = self.missing_pks_to_add()

    def data_source_id(self) -> typing.Optional[str]:
        return self.joined_data_source_id

    def retrieve_data(self) -> pd.DataFrame:
        get_kawa_logger().info(f'Start retrieving data from Kawa, jobId: {self.job_id}')
        columns_to_load = self.columns_to_load_from_params()
        # we add the missing pks to be able to feed the data properly in clickhouse
        columns_to_load.extend(self.missing_pks_to_add)
        sheet_name = self.sheet['displayInformation']['displayName']

        df = (self.K.sheet(sheet_name)
              .dashboard_id(self.dashboard_id)
              .application_id(self.application_id)
              .select(*columns_to_load)
              .limit(-1)
              .compute())

        get_kawa_logger().info(f'End retrieving data from Kawa, jobId: {self.job_id}')
        return df

    def load(self, df: pd.DataFrame):
        start_time = time.time()
        get_kawa_logger().info(f'Start loading the computed data into kawa for jobId: {self.job_id}')
        datasource = self.__before_load_python_private_join_data_source(self.python_private_join_id)
        self.__load_python_private_join_data_source(datasource, df)
        self.__after_load_python_private_join_data_source(self.python_private_join_id, self.job_id)
        t = round(time.time() - start_time, 1)
        get_kawa_logger().info(f'End loading the computed data into kawa in {t} for jobId: {self.job_id}')

    def __before_load_python_private_join_data_source(self, python_private_join_id: str):
        return self.K.commands._run_command(command_name='BeforeLoadPythonPrivateJoinDataSource',
                                            command_parameters={
                                                "pythonPrivateJoinId": python_private_join_id
                                            })

    def __load_python_private_join_data_source(self, datasource, df):
        df.rename(columns=self.pk_parameter_name_to_indicator_id, inplace=True)
        data_loader = KawaDataLoader(
            self.K,
            df=None,
            arrow_table=pa.Table.from_pandas(df),
            datasource_name=None,
            datasource_id=datasource['id'],
        )
        data_loader.load_data(
            reset_before_insert=True,
            job_id=self.job_id
        )

    def __after_load_python_private_join_data_source(self, python_private_join_id: str, job_id: str):
        self.K.commands._run_command(command_name='AfterLoadPythonPrivateJoinDataSource',
                                     command_parameters={
                                         "pythonPrivateJoinId": python_private_join_id,
                                         'jobId': job_id
                                     })

    def pk_columns(self) -> dict:

        def is_pk(c):
            # Check if it is a KEY and in the Primary DS
            # (keys in other datasources should be ignored)
            link = c.get('dataSourceLink', {})
            return (c['isKey']
                    and not (link.get('keyPairings'))
                    and not (link.get('foreignKeyNames'))
                    and not (link.get('defaultValueForAttributes')))

        return {
            c['columnId']: c
            for c
            in self.sheet['indicatorColumns']
            if is_pk(c)
        }

    def pk_parameter_name_to_indicator_id(self) -> dict:
        return {param_name: self.pk_columns[col_id]['indicatorId']
                for col_id, param_name in self.column_ids_to_parameter_name.items()
                if col_id in self.pk_columns}

    def missing_pks_to_add(self) -> List[KawaColumn]:
        return [self.K.col(col['displayInformation']['displayName']).alias(col['indicatorId'])
                for col_id, col in self.pk_columns.items()
                if col_id not in self.column_ids_to_parameter_name]

    def parameters_column_ids_to_parameter_name(self) -> dict:
        return {mapping['columnId']: mapping['paramName'] for mapping in self.python_private_join['paramMapping']}

    def columns_to_load_from_params(self) -> List[KawaColumn]:
        column_id_to_name = self._column_id_to_name(self.sheet)
        column_id_to_alias = self.column_ids_to_parameter_name

        return [self.K.col(column_id_to_name[col_id]).alias(param_name)
                for col_id, param_name in column_id_to_alias.items()]

    @staticmethod
    def _column_id_to_name(sheet):
        res = {}
        for c in sheet['computedColumns']:
            res[c['columnId']] = c['displayInformation']['displayName']
        for c in sheet['indicatorColumns']:
            res[c['columnId']] = c['displayInformation']['displayName']
        return res
