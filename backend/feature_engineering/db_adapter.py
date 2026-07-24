import pandas as pd
from typing import Callable
from core.interfaces import DataReader, DataWriter


class CleanLogsReader(DataReader):
    def __init__(self, read_func: Callable[[], pd.DataFrame]):
        if not callable(read_func):
            raise ValueError("read_func must be callable")
        self.read_func = read_func

    def read(self) -> pd.DataFrame:
        df = self.read_func()

        if df is None:
            raise ValueError("Reader returned None")

        return df


class TemporalFeaturesWriter(DataWriter):
    def __init__(self, write_func: Callable[[pd.DataFrame], None]):
        if not callable(write_func):
            raise ValueError("write_func must be callable")
        self.write_func = write_func

    def write(self, df: pd.DataFrame) -> None:
        if df is None:
            raise ValueError("Cannot write None DataFrame")
        self.write_func(df)


class PeerFeaturesWriter(DataWriter):
    def __init__(self, write_func: Callable[[pd.DataFrame], None]):
        if not callable(write_func):
            raise ValueError("write_func must be callable")
        self.write_func = write_func

    def write(self, df: pd.DataFrame) -> None:
        if df is None:
            raise ValueError("Cannot write None DataFrame")
        self.write_func(df)