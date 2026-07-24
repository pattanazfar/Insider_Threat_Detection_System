import pandas as pd
import logging
from core.interfaces import DataReader, DataWriter

logger = logging.getLogger(__name__)


# ===============================
# PURE FEATURE LOGIC
# ===============================
def build_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
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

    # Drop invalid dates
    df = df.dropna(subset=["date"])

    # Sort properly
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
    # ROLLING FEATURES (NO LEAKAGE ✅)
    # ===============================
    for col in activity_cols:
        # 7-day rolling mean
        df[f"{col}_mean_7d"] = (
            df.groupby("employee")[col]
            .transform(lambda x: x.rolling(7, min_periods=1).mean().shift(1))
        )

        # 30-day rolling mean
        df[f"{col}_mean_30d"] = (
            df.groupby("employee")[col]
            .transform(lambda x: x.rolling(30, min_periods=1).mean().shift(1))
        )

        # Delta (current vs past)
        df[f"{col}_delta"] = df[col] - df[f"{col}_mean_7d"]

    # ===============================
    # ROLLING Z-SCORE (FIXED 🔥)
    # ===============================
    for col in activity_cols:
        rolling_mean = (
            df.groupby("employee")[col]
            .transform(lambda x: x.rolling(30, min_periods=7).mean().shift(1))
        )

        rolling_std = (
            df.groupby("employee")[col]
            .transform(lambda x: x.rolling(30, min_periods=7).std().shift(1))
        )

        # Handle std issues safely
        rolling_std = rolling_std.replace(0, 1).fillna(1)

        df[f"{col}_zscore"] = (df[col] - rolling_mean) / rolling_std

    # ===============================
    # SCORE
    # ===============================
    delta_cols = [f"{c}_delta" for c in activity_cols]
    z_cols = [f"{c}_zscore" for c in activity_cols]

    df["temporal_deviation_score"] = (
        df[delta_cols].abs().sum(axis=1)
        + df[z_cols].abs().sum(axis=1)
    )

    # ===============================
    # FINAL CLEANUP
    # ===============================
    keep_cols = (
        ["employee", "date"]
        + [c for c in df.columns if c.endswith("_mean_7d")]
        + [c for c in df.columns if c.endswith("_mean_30d")]
        + [c for c in df.columns if c.endswith("_delta")]
        + [c for c in df.columns if c.endswith("_zscore")]
        + ["temporal_deviation_score"]
    )

    result = df[keep_cols].copy()

    # Final safety check
    if result.isnull().any().any():
        logger.warning("Null values detected in temporal features, filling safely")
        result = result.fillna(0)

    return result


# ===============================
# PIPELINE (FULLY DECOUPLED ✅)
# ===============================
def run_temporal_pipeline(reader: DataReader, writer: DataWriter):
    logger.info("Temporal Pipeline Started")

    df = reader.read()

    if df is None or df.empty:
        raise ValueError("No input data")

    features = build_temporal_features(df)

    writer.write(features)

    logger.info("Temporal Pipeline Completed")

    return features


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    import logging
    from core.db_repository import DBRepository
    from feature_engineering.db_adapter import (
        CleanLogsReader,
        TemporalFeaturesWriter
    )

    logging.basicConfig(level=logging.INFO)

    repo = DBRepository()

    reader = CleanLogsReader(repo.get_clean_logs)
    writer = TemporalFeaturesWriter(repo.save_temporal_features)

    try:
        df = run_temporal_pipeline(reader, writer)

        print("\n✅ Temporal Features Generated (NO LEAKAGE - FIXED)\n")
        print(df.head())

    except Exception as e:
        print(f"❌ Error: {e}")