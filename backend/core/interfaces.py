from abc import ABC, abstractmethod
import pandas as pd


# ===============================
# GENERIC DATA READER
# ===============================
class DataReader(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame:
        pass


# ===============================
# GENERIC DATA WRITER
# ===============================
class DataWriter(ABC):
    @abstractmethod
    def write(self, df: pd.DataFrame) -> None:
        pass


# ===============================
# MODEL ARTIFACT WRITER
# ===============================
class ModelArtifactWriter(ABC):
    @abstractmethod
    def save(self, obj, path: str) -> None:
        pass

