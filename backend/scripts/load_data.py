import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Iterator, Tuple, Optional

# ===============================
# Logger (NO global config here)
# ===============================
logger = logging.getLogger(__name__)

REQUIRED_FILES = ["logon.csv", "file.csv", "device.csv", "email.csv", "http.csv"]


# ===============================
# Validation
# ===============================
def validate_path(base_path: Path) -> None:
    if not base_path.exists():
        raise FileNotFoundError(f"Base path not found: {base_path}")

    missing = [f for f in REQUIRED_FILES if not (base_path / f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files: {missing}")


# ===============================
# Safe CSV Reader
# ===============================
def read_csv_file(file_path: Path, nrows: int) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, nrows=nrows)

        if df.empty:
            raise ValueError(f"File is empty: {file_path.name}")

        return df

    except Exception as e:
        raise RuntimeError(f"Failed reading {file_path.name}") from e


# ===============================
# Main Loader
# ===============================
def load_raw_data(
    base_path: Optional[str],
    nrows: int = 10000
) -> Dict[str, pd.DataFrame]:

    if base_path is None:
        raise ValueError("base_path must be provided (no default allowed)")

    base_path = Path(base_path)

    logger.info("Loading raw CSV files from %s", base_path)

    validate_path(base_path)

    data: Dict[str, pd.DataFrame] = {}

    for file_name in REQUIRED_FILES:
        key = file_name.replace(".csv", "")
        file_path = base_path / file_name

        logger.info("Loading %s", file_name)

        df = read_csv_file(file_path, nrows)
        data[key] = df

    logger.info("All CSV files loaded successfully")

    return data


# ===============================
# Lazy Loader (for large data)
# ===============================
def load_raw_data_lazy(
    base_path: Optional[str],
    chunksize: int = 5000
) -> Iterator[Tuple[str, pd.io.parsers.TextFileReader]]:

    if base_path is None:
        raise ValueError("base_path must be provided (no default allowed)")

    base_path = Path(base_path)

    logger.info("Lazy loading enabled from %s", base_path)

    validate_path(base_path)

    for file_name in REQUIRED_FILES:
        key = file_name.replace(".csv", "")
        file_path = base_path / file_name

        logger.info("Streaming %s", file_name)

        try:
            chunk_iterator = pd.read_csv(file_path, chunksize=chunksize)
            yield key, chunk_iterator

        except Exception as e:
            raise RuntimeError(f"Failed streaming {file_name}") from e


# ===============================
# Entry Point (SAFE, OPTIONAL)
# ===============================
if __name__ == "__main__":
    import logging

    # Only configure logging here (not in library code)
    logging.basicConfig(level=logging.INFO)

    BASE_PATH = r"data/raw/r4.1"

    try:
        data = load_raw_data(base_path=BASE_PATH, nrows=10000)

        print("\n✅ Data Loaded Successfully:\n")

        for name, df in data.items():
            print(f"{name}: {df.shape}")

    except Exception as e:
        print(f"❌ Error: {e}")