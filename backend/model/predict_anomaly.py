import logging
import pandas as pd
import numpy as np
from typing import Tuple
from model.db_writer import AnomalyWriter
from core.interfaces import DataReader, ModelArtifactWriter
from config.settings import ANOMALY_FEATURES, ANOMALY_MODEL_PATH, SCALER_PATH

import joblib

logger = logging.getLogger(__name__)


# ===============================
# MODEL LOADER (PURE FUNCTION ✅)
# ===============================
def load_artifacts(model_path: str, scaler_path: str):
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        raise RuntimeError(f"Failed to load model artifacts: {e}")


# ===============================
# PREDICTION LOGIC (PURE ✅)
# ===============================
def predict(df: pd.DataFrame, model, scaler) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input dataframe is empty")

    missing = set(ANOMALY_FEATURES) - set(df.columns)
    if missing:
        raise ValueError(f"Missing features: {missing}")

    df = df.copy()

    X = df[ANOMALY_FEATURES]

    # ===============================
    # SCALE (CONSISTENT WITH TRAINING ✅)
    # ===============================
    X_scaled = scaler.transform(X)

    # ===============================
    # MODEL PREDICTIONS
    # ===============================
    scores = model.decision_function(X_scaled)
    labels = model.predict(X_scaled)  # -1 = anomaly, 1 = normal

    df["anomaly_score"] = scores
    df["is_anomaly"] = (labels == -1).astype(int)

    logger.info("Prediction completed successfully")

    return df


# ===============================
# SAFE NORMALIZATION FUNCTION ✅
# ===============================
def safe_minmax(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series(np.zeros(len(series)), index=series.index)

    return (series - min_val) / (max_val - min_val)


# ===============================
# RISK LEVEL LOGIC (FIXED 🔥)
# ===============================
def compute_risk(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Cannot compute risk on empty dataframe")

    df = df.copy()

    # ===============================
    # VALIDATION (SAFE ACCESS)
    # ===============================
    required_cols = [
        "anomaly_score",
        "behavior_deviation_score",
        "total_activity"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column for risk: {col}")

    # Optional columns fallback
    df["peer_deviation_score"] = df.get("peer_deviation_score", 0)
    df["temporal_deviation_score"] = df.get("temporal_deviation_score", 0)

    # ===============================
    # NORMALIZATION (STABLE ✅)
    # ===============================
    df["behavior_norm"] = safe_minmax(df["behavior_deviation_score"])
    df["peer_norm"] = safe_minmax(df["peer_deviation_score"])
    df["temporal_norm"] = safe_minmax(df["temporal_deviation_score"])
    df["activity_norm"] = safe_minmax(df["total_activity"])

    # ===============================
    # ANOMALY SCORE NORMALIZATION
    # ===============================
    # Isolation Forest: higher = normal, lower = anomaly
    df["anomaly_norm"] = safe_minmax(-df["anomaly_score"])

    # ===============================
    # FINAL HYBRID RISK SCORE
    # ===============================
    df["risk_score"] = (
        df["anomaly_norm"] * 0.5
        + df["behavior_norm"] * 0.2
        + df["peer_norm"] * 0.1
        + df["temporal_norm"] * 0.1
        + df["activity_norm"] * 0.1
    ) * 100

    # ===============================
    # RISK LEVELS
    # ===============================
    def get_risk(row):
        score = row["risk_score"]
        is_anomaly = row["is_anomaly"]
        anomaly_score = row["anomaly_score"]

    # 🔴 HIGH: must be truly anomalous + high score
        if is_anomaly == 1 and score >= 70 and anomaly_score < 0:
            return "HIGH"

    # 🟠 MEDIUM: either moderate anomaly OR high behavior deviation
        elif score >= 50:
            return "MEDIUM"

    # 🟢 LOW: everything else
        return "LOW"


    df["risk_level"] = df.apply(get_risk, axis=1)

    return df


# ===============================
# PIPELINE (LOOSELY COUPLED ✅)
# ===============================
def run_prediction_pipeline(
    reader: DataReader,
    writer: ModelArtifactWriter
) -> pd.DataFrame:

    logger.info("🚀 Prediction Pipeline Started")

    # ===============================
    # READ DATA
    # ===============================
    df = reader.read()

    if df is None or df.empty:
        raise ValueError("No input data for prediction")

    # ===============================
    # LOAD MODEL
    # ===============================
    model, scaler = load_artifacts(
        ANOMALY_MODEL_PATH,
        SCALER_PATH
    )

    # ===============================
    # PREDICT
    # ===============================
    result_df = predict(df, model, scaler)

    # ===============================
    # COMPUTE RISK
    # ===============================
    result_df = compute_risk(result_df)

    # ===============================
    # FINAL SAFETY CHECK
    # ===============================
    if result_df.isnull().any().any():
        logger.warning("Null values detected in prediction output, filling safely")
        result_df = result_df.fillna(0)

    # ===============================
    # SAVE RESULTS
    # ===============================
    writer.save(result_df, "anomaly_results")

    logger.info("✅ Prediction Results Saved Successfully")

    return result_df


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    import logging
    from core.db_repository import DBRepository
    from model.db_adapter import FinalFeaturesReader

    logging.basicConfig(level=logging.INFO)

    repo = DBRepository()

    # Reader
    reader = FinalFeaturesReader(repo.get_final_features)

    # Writer
    writer = AnomalyWriter(repo.save_anomaly_results)

    try:
        df = run_prediction_pipeline(reader, writer)

        print("\n✅ Prediction Pipeline Completed (STABLE RISK ENGINE)\n")
        print(df[[
            "employee",
            "date",
            "anomaly_score",
            "is_anomaly",
            "risk_score",
            "risk_level"
        ]].head())

    except Exception as e:
        print(f"❌ Error: {e}")