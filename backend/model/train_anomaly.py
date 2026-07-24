import logging
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from config.settings import ANOMALY_FEATURES

logger = logging.getLogger(__name__)


def train_isolation_forest(df: pd.DataFrame):
    if df is None or df.empty:
        raise ValueError("Training data is empty")

    missing = set(ANOMALY_FEATURES) - set(df.columns)
    if missing:
        raise ValueError(f"Missing features: {missing}")

    logger.info("📊 Preparing training data")

    X = df[ANOMALY_FEATURES]

    # ✅ Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    logger.info("⚙️ Training Isolation Forest model")

    # ✅ Model
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_scaled)

    logger.info("✅ Model training completed")

    return model, scaler