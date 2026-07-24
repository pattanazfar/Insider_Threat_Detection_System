import pandas as pd
import logging
from typing import List

from core.interfaces import DataReader, DataWriter

logger = logging.getLogger(__name__)


# ===============================
# VALIDATION
# ===============================
def validate_dataframe(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty")

    required_cols = {"employee", "date"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


# ===============================
# PURE CLEANING LOGIC
# ===============================
def clean_dataframe(df: pd.DataFrame, count_columns: List[str]) -> pd.DataFrame:
    df = df.copy()

    logger.info("Cleaning started")

    for col in count_columns:
        if col in df.columns:
            df = df[df[col] >= 0]

    df = df.dropna(subset=["employee"])

    existing_cols = [c for c in count_columns if c in df.columns]
    df[existing_cols] = df[existing_cols].fillna(0)

    df = df.reset_index(drop=True)

    logger.info("Cleaning completed")

    return df


# ===============================
# PIPELINE (ONLY ORCHESTRATION ✅)
# ===============================
def run_clean_pipeline(
    reader: DataReader,
    writer: DataWriter,
    count_columns: List[str]
) -> pd.DataFrame:

    logger.info("Pipeline started")

    df = reader.read()

    validate_dataframe(df)

    cleaned_df = clean_dataframe(df, count_columns)

    writer.write(cleaned_df)

    logger.info("Pipeline completed")

    return cleaned_df


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from core.db_repository import DBRepository
    from cleaning.db_adapter import RawLogsReader, CleanLogsWriter

    repo = DBRepository()

    reader = RawLogsReader(repo)
    writer = CleanLogsWriter(repo)

    count_columns = [
        "logon_count",
        "file_count",
        "device_count",
        "email_count",
        "http_count"
    ]

    try:
        df = run_clean_pipeline(reader, writer, count_columns)

        print("\n✅ Clean Logs Stored Successfully\n")
        print(df.head())

    except Exception as e:
        print(f"❌ Error: {e}")