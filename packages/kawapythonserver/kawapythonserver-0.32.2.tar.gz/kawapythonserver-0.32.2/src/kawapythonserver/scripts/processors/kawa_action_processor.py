import typing
from abc import ABC, abstractmethod
from functools import reduce

import pandas as pd


class ActionProcessor(ABC):

    @abstractmethod
    def load(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def retrieve_data(self) -> pd.DataFrame:
        pass

    def need_defined_outputs(self) -> bool:
        return True

    def dump_metadata(self, to_dump):
        pass

    def data_source_id(self) -> typing.Optional[str]:
        return None
