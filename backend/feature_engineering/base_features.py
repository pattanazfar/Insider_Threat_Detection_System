import pandas as pd
import numpy as np
import logging
from core.interfaces import DataReader, DataWriter

logger = logging.getLogger(__name__)


# ===============================
# PURE LOGIC
# ===============================
def build_base_features(
    clean: pd.DataFrame,
    temporal: pd.DataFrame,
    peers: pd.DataFrame
) -> pd.DataFrame:

    # ===============================
    # VALIDATION
    # ===============================
    if clean is None or clean.empty:
        raise ValueError("Clean dataframe is empty")

    if temporal is None or temporal.empty:
        raise ValueError("Temporal dataframe is empty")

    if peers is None or peers.empty:
        raise ValueError("Peer dataframe is empty")

    clean = clean.copy()
    temporal = temporal.copy()
    peers = peers.copy()

    raw_cols = [
        "logon_count",
        "file_count",
        "device_count",
        "email_count",
        "http_count"
    ]

    # ===============================
    # CHECK REQUIRED COLUMNS
    # ===============================
    missing_cols = set(raw_cols) - set(clean.columns)
    if missing_cols:
        raise ValueError(f"Missing raw columns in clean data: {missing_cols}")

    # ===============================
    # CLEAN AUX TABLES
    # ===============================
    temporal = temporal.drop(
        columns=[c for c in raw_cols if c in temporal.columns],
        errors="ignore"
    )

    peers = peers.drop(
        columns=[c for c in raw_cols if c in peers.columns],
        errors="ignore"
    )

    # ===============================
    # MERGE (SAFE)
    # ===============================
    df = clean.merge(
        temporal,
        on=["employee", "date"],
        how="left",
        suffixes=("", "_temp")
    )

    df = df.merge(
        peers,
        on=["employee", "date"],
        how="left",
        suffixes=("", "_peer")
    )

    # ===============================
    # REMOVE SUFFIX DUPLICATES
    # ===============================
    for col in list(df.columns):
        if col.endswith("_temp") or col.endswith("_peer"):
            base = col.replace("_temp", "").replace("_peer", "")
            if base not in df.columns:
                df.rename(columns={col: base}, inplace=True)
            else:
                df.drop(columns=[col], inplace=True)

    # ===============================
    # BASIC CLEANING
    # ===============================
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df = df.sort_values(["employee", "date"]).reset_index(drop=True)

    # ===============================
    # HANDLE MISSING FEATURES (FIXED 🔥)
    # ===============================
    # Preserve meaning of missing vs zero
    df["missing_temporal"] = df["temporal_deviation_score"].isna().astype(int)
    df["missing_peer"] = df["peer_deviation_score"].isna().astype(int)

    df["temporal_deviation_score"] = df["temporal_deviation_score"].fillna(0)
    df["peer_deviation_score"] = df["peer_deviation_score"].fillna(0)

    # Fill raw counts safely (these can be zero legitimately)
    for col in raw_cols:
        df[col] = df[col].fillna(0)

    # ===============================
    # DERIVED FEATURES
    # ===============================
    df["total_activity"] = df[raw_cols].sum(axis=1)

    for col in raw_cols:
        name = col.replace("_count", "")

        df[f"{name}_ratio"] = df[col] / (df["total_activity"] + 1)
        df[f"{name}_log"] = np.log1p(df[col])

    # ===============================
    # HIGH-RISK FLAGS (FIXED EDGE CASES 🔥)
    # ===============================
    WINDOW = 30
    MIN_PERIODS = 7

    df["high_file_activity"] = 0
    df["high_http_activity"] = 0

    for employee, employee_df in df.groupby("employee"):
        idx = employee_df.index

        file_thr = (
            employee_df["file_count"]
            .rolling(WINDOW, min_periods=MIN_PERIODS)
            .quantile(0.95)
            .shift(1)
        )

        http_thr = (
            employee_df["http_count"]
            .rolling(WINDOW, min_periods=MIN_PERIODS)
            .quantile(0.95)
            .shift(1)
        )

        # Handle early NaNs properly
        file_thr = file_thr.fillna(method="bfill").fillna(0)
        http_thr = http_thr.fillna(method="bfill").fillna(0)

        df.loc[idx, "high_file_activity"] = (
            (employee_df["file_count"] > file_thr).astype(int)
        )

        df.loc[idx, "high_http_activity"] = (
            (employee_df["http_count"] > http_thr).astype(int)
        )

    # ===============================
    # SCORES
    # ===============================
    df["behavior_deviation_score"] = (
        df["temporal_deviation_score"]
        + df["peer_deviation_score"]
    )

    df["resource_access_score"] = (
        df["file_count"] + df["http_count"]
    )

    # ===============================
    # FINAL SAFETY CHECK
    # ===============================
    if any(c.endswith("_x") or c.endswith("_y") for c in df.columns):
        raise ValueError("Column duplication issue detected")

    if df.isnull().any().any():
        logger.warning("Final dataframe still has nulls, filling safely")
        df = df.fillna(0)

    logger.info("Base features generated successfully")

    return df


# ===============================
# PIPELINE (LOOSELY COUPLED ✅)
# ===============================
def run_base_pipeline(
    clean_reader: DataReader,
    temporal_reader: DataReader,
    peer_reader: DataReader,
    writer: DataWriter
):
    logger.info("Base Feature Pipeline Started")

    clean_df = clean_reader.read()
    temporal_df = temporal_reader.read()
    peer_df = peer_reader.read()

    features = build_base_features(clean_df, temporal_df, peer_df)

    writer.write(features)

    logger.info("Base Features Stored Successfully")

    return features


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    import logging
    from core.db_repository import DBRepository
    from feature_engineering.db_adapter import CleanLogsReader
    from feature_engineering.base_adapter import (
        FinalFeaturesWriter,
        TemporalReader,
        PeerReader
    )

    logging.basicConfig(level=logging.INFO)

    repo = DBRepository()

    clean_reader = CleanLogsReader(repo.get_clean_logs)
    temporal_reader = TemporalReader(repo.get_temporal_features)
    peer_reader = PeerReader(repo.get_peer_features)

    writer = FinalFeaturesWriter(repo.save_final_features)

    try:
        df = run_base_pipeline(
            clean_reader,
            temporal_reader,
            peer_reader,
            writer
        )

        print("\n✅ Final Features Generated (PRODUCTION READY)\n")
        print(df.head())

    except Exception as e:
        print(f"❌ Error: {e}")