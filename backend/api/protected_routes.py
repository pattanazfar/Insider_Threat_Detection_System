from fastapi import APIRouter, Depends
from api.deps import require_admin

router = APIRouter()


# ✅ Only ADMIN can access
@router.get("/admin-dashboard")
def admin_dashboard(user=Depends(require_admin)):
    return {
        "message": "Welcome Admin 🚀",
        "user": user
    }