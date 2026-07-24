from fastapi import APIRouter, Depends
from api.deps import require_admin
from core.db_repository import DBRepository

router = APIRouter()
repo = DBRepository()


# ✅ GET ALL ANOMALY RESULTS
@router.get("/anomalies")
def get_anomalies(user=Depends(require_admin)):
    df = repo.get_anomaly_results()

    if df.empty:
        return []

    risk_priority = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    dashboard_df = (
        df.assign(
            _risk_priority=df["risk_level"]
            .str.strip()
            .str.upper()
            .map(risk_priority)
            .fillna(0)
        )
        .sort_values(
            ["employee", "_risk_priority", "risk_score"],
            ascending=[True, False, False],
        )
        .drop_duplicates(subset="employee", keep="first")
        .drop(columns="_risk_priority")
    )

    return dashboard_df.to_dict(orient="records")
