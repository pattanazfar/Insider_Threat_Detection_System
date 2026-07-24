import pandas as pd
import logging
from typing import Optional, Dict

from scripts.load_data import load_raw_data
from core.db_repository import DBRepository

logger = logging.getLogger(__name__)


# ===============================
# Normalize Function (NO SIDE EFFECT ✅)
# ===============================
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()  # ✅ avoid modifying original

    for col in ["timestamp", "date", "time"]:
        if col in df.columns:
            df["date"] = pd.to_datetime(df[col], errors="coerce").dt.date
            return df

    raise ValueError("No timestamp column found")


# ===============================
# Aggregate Function
# ===============================
def aggregate(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    return (
        df.groupby(["employee", "date"])   # 🔥 UPDATED
        .size()
        .reset_index(name=col_name)
    )


# ===============================
# Merge Logic (FULLY GENERIC + SAFE ✅)
# ===============================
def merge_data(
    base_path: Optional[str],
    nrows: int = 10000,
    repo: Optional[DBRepository] = None,
    mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:

    if base_path is None:
        raise ValueError("base_path must be provided")

    if repo is None:
        raise ValueError("DBRepository instance must be provided")

    if mapping is None:
        mapping = {
            "logon": "logon_count",
            "file": "file_count",
            "device": "device_count",
            "email": "email_count",
            "http": "http_count"
        }

    if not mapping:
        raise ValueError("Mapping cannot be empty")

    logger.info("Starting merge pipeline")

    # ✅ Load data
    data: Dict[str, pd.DataFrame] = load_raw_data(base_path=base_path, nrows=nrows)

    # ✅ Validate loaded data
    if not data:
        raise ValueError("No data loaded")

    # ✅ Normalize + 🔥 RENAME HERE
    for key in data:
        logger.info("Normalizing %s", key)

        df = normalize(data[key])

        # 🔥 CRITICAL FIX (user → employee)
        if "user" in df.columns:
            df.rename(columns={"user": "employee"}, inplace=True)

        data[key] = df

    # ✅ Aggregate dynamically
    summaries: Dict[str, pd.DataFrame] = {}

    for key, col_name in mapping.items():
        if key not in data:
            raise KeyError(f"{key} not found in loaded data")

        summaries[key] = aggregate(data[key], col_name)

    # ✅ Dynamic merge
    keys = list(summaries.keys())

    logger.info("Merging %d datasets", len(keys))

    merged = summaries[keys[0]]

    for key in keys[1:]:
        merged = merged.merge(summaries[key], on=["employee", "date"], how="left")  # 🔥 UPDATED

    merged = merged.fillna(0)

    # ✅ Save to DB
    logger.info("Saving merged data to database")
    repo.save_raw_logs(merged)

    logger.info("Merge pipeline completed successfully")

    return merged


# ===============================
# Entry Point
# ===============================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    BASE_PATH = "data/raw/r4.1"

    try:
        repo = DBRepository()

        df = merge_data(
            base_path=BASE_PATH,
            repo=repo
        )

        print("\n✅ Data Merged & Stored Successfully\n")
        print(df.head())

    except Exception as e:
        print(f"❌ Error: {e}")