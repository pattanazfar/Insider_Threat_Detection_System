import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[1]
ANOMALY_MODEL_PATH = str(BACKEND_DIR / "models" / "anomaly" / "isolation_forest.pkl")
SCALER_PATH = str(BACKEND_DIR / "models" / "anomaly" / "scaler.pkl")
ANOMALY_FEATURES = [
    "logon_count",
    "file_count",
    "device_count",
    "email_count",
    "http_count",
    "total_activity",
    "logon_ratio",
    "file_ratio",
    "device_ratio",
    "email_ratio",
    "http_ratio",
    "logon_log",
    "file_log",
    "device_log",
    "email_log",
    "http_log",
    "high_file_activity",
    "high_http_activity",
    "behavior_deviation_score",
    "resource_access_score",
]


def _origins(value: str | None) -> tuple[str, ...]:
    return tuple(origin.strip().rstrip("/") for origin in (value or "").split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: str
    secret_key: str
    cors_origins: tuple[str, ...]
    token_exp_minutes: int

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def load_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development").lower()
    database_url = os.getenv("DB_URL", "")
    secret_key = os.getenv("SECRET_KEY", "")
    cors_origins = _origins(os.getenv("CORS_ORIGINS"))
    if environment not in {"development", "test", "production"}:
        raise RuntimeError("ENVIRONMENT must be development, test, or production")
    if not database_url:
        raise RuntimeError("DB_URL must be set")
    if len(secret_key) < 32:
        raise RuntimeError("SECRET_KEY must be a random value of at least 32 characters")
    if environment == "production" and not cors_origins:
        raise RuntimeError("CORS_ORIGINS must list the deployed frontend origin in production")
    return Settings(environment, database_url, secret_key, cors_origins or ("http://localhost:5173",), int(os.getenv("TOKEN_EXP_MINUTES", "30")))


settings = load_settings()
