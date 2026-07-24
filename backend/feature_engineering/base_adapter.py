import pandas as pd
from typing import Callable
from core.interfaces import DataReader, DataWriter


class TemporalReader(DataReader):
    def __init__(self, read_func: Callable[[], pd.DataFrame]):
        self.read_func = read_func

    def read(self) -> pd.DataFrame:
        return self.read_func()


class PeerReader(DataReader):
    def __init__(self, read_func: Callable[[], pd.DataFrame]):
        self.read_func = read_func

    def read(self) -> pd.DataFrame:
        return self.read_func()


class FinalFeaturesWriter(DataWriter):
    def __init__(self, write_func: Callable[[pd.DataFrame], None]):
        self.write_func = write_func

    def write(self, df: pd.DataFrame) -> None:
        self.write_func(df)