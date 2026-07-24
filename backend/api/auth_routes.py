from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.schemas import LoginRequest
from security.auth import authenticate
from security.rate_limit import login_limiter

router = APIRouter()


def enforce_login_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    retry_after = login_limiter.check(f"login:{client_ip}", limit=5, window_seconds=60)
    if retry_after:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts. Try again shortly.", headers={"Retry-After": str(retry_after)})


@router.post("/login")
def login(request: LoginRequest, _: None = Depends(enforce_login_rate_limit)):
    result = authenticate(request.username, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result
