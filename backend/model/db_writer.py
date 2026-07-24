from core.interfaces import ModelArtifactWriter
import pandas as pd
from typing import Callable

class AnomalyWriter(ModelArtifactWriter):
    def __init__(self, write_func: Callable[[pd.DataFrame], None]):
        if not callable(write_func):
            raise ValueError("write_func must be callable")
        self.write_func = write_func

    def save(self, df: pd.DataFrame, path: str) -> None:
        if df is None or df.empty:
            raise ValueError("Cannot save empty dataframe")

        self.write_func(df)