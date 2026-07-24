import pandas as pd
import logging
from core.interfaces import DataReader, DataWriter

logger = logging.getLogger(__name__)


# ===============================
# PURE FEATURE LOGIC
# ===============================
def build_peer_features(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input dataframe is empty")

    df = df.copy()

    # ===============================
    # VALIDATION
    # ===============================
    required_cols = ["employee", "date"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop invalid dates early
    df = df.dropna(subset=["date"])

    # Sort (important for consistency)
    df = df.sort_values(["employee", "date"]).reset_index(drop=True)

    activity_cols = [
        "logon_count",
        "file_count",
        "device_count",
        "email_count",
        "http_count"
    ]

    for col in activity_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # ===============================
    # LEAVE-ONE-OUT PEER LOGIC (FIXED ✅)
    # ===============================
    for col in activity_cols:
        # Group stats
        group_sum = df.groupby("date")[col].transform("sum")
        group_count = df.groupby("date")[col].transform("count")

        # Leave-one-out mean
        loo_mean = (group_sum - df[col]) / (group_count - 1)

        # Handle edge cases (only 1 employee that day)
        loo_mean = loo_mean.where(group_count > 1, 0)

        # Standard deviation (safe)
        std = df.groupby("date")[col].transform("std")

        # Handle std issues
        std = std.replace(0, 1).fillna(1)

        # Features
        df[f"{col}_peer_diff"] = df[col] - loo_mean
        df[f"{col}_peer_zscore"] = df[f"{col}_peer_diff"] / std

    # ===============================
    # SCORE
    # ===============================
    diff_cols = [f"{c}_peer_diff" for c in activity_cols]
    z_cols = [f"{c}_peer_zscore" for c in activity_cols]

    df["peer_deviation_score"] = (
        df[diff_cols].abs().sum(axis=1) +
        df[z_cols].abs().sum(axis=1)
    )

    # ===============================
    # FINAL CLEANUP
    # ===============================
    keep_cols = (
        ["employee", "date"]
        + diff_cols
        + z_cols
        + ["peer_deviation_score"]
    )

    result = df[keep_cols].copy()

    # Final safety check
    if result.isnull().any().any():
        logger.warning("Null values detected in peer features, filling safely")
        result = result.fillna(0)

    return result


# ===============================
# PIPELINE (LOOSELY COUPLED ✅)
# ===============================
def run_peer_pipeline(reader: DataReader, writer: DataWriter):
    logger.info("Peer Pipeline Started")

    df = reader.read()

    if df is None or df.empty:
        raise ValueError("No input data")

    features = build_peer_features(df)

    writer.write(features)

    logger.info("Peer Pipeline Completed")

    return features


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    import logging
    from core.db_repository import DBRepository
    from feature_engineering.db_adapter import (
        CleanLogsReader,
        PeerFeaturesWriter
    )

    logging.basicConfig(level=logging.INFO)

    repo = DBRepository()

    reader = CleanLogsReader(repo.get_clean_logs)
    writer = PeerFeaturesWriter(repo.save_peer_features)

    try:
        df = run_peer_pipeline(reader, writer)

        print("\n✅ Peer Features Generated (NO LEAKAGE - FIXED)\n")
        print(df.head())

    except Exception as e:
        print(f"❌ Error: {e}")