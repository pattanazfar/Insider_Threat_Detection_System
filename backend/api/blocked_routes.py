from fastapi import APIRouter, Depends

from api.deps import require_admin
from api.schemas import EmployeeRequest
from core.db_repository import DBRepository
from security.audit import log_security_event

router = APIRouter()
repo = DBRepository()


@router.post("/block")
def block_employee(req: EmployeeRequest, user=Depends(require_admin)):
    repo.block_employee(req.employee)
    log_security_event("employee_blocked", user["sub"], req.employee)
    return {"message": f"{req.employee} blocked successfully"}


@router.get("/blocked")
def get_blocked(user=Depends(require_admin)):
    return repo.get_blocked_employees()


@router.delete("/unblock/{employee}")
def unblock(employee: str, user=Depends(require_admin)):
    employee = EmployeeRequest(employee=employee).employee
    repo.unblock_employee(employee)
    log_security_event("employee_unblocked", user["sub"], employee)
    return {"message": f"{employee} unblocked successfully"}
