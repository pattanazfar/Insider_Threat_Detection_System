import pandas as pd
from core.db_repository import DBRepository
from core.interfaces import DataReader, DataWriter


class RawLogsReader(DataReader):

    def __init__(self, repo: DBRepository):
        self.repo = repo

    def read(self) -> pd.DataFrame:
        return self.repo.get_raw_logs()


class CleanLogsWriter(DataWriter):

    def __init__(self, repo: DBRepository):
        self.repo = repo

    def write(self, df: pd.DataFrame) -> None:
        self.repo.save_clean_logs(df)