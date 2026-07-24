import pandas as pd
from typing import Callable
from core.interfaces import DataReader


class FinalFeaturesReader(DataReader):

    def __init__(self, read_func: Callable[[], pd.DataFrame]):
        if not callable(read_func):
            raise ValueError("read_func must be callable")
        self.read_func = read_func

    def read(self) -> pd.DataFrame:
        df = self.read_func()

        if df is None or df.empty:
            raise ValueError("No data received from DB")

        return df