import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api.anomaly_routes import router as anomaly_router
from api.assign_routes import router as assign_router
from api.auth_routes import router as auth_router
from api.blocked_routes import router as blocked_router
from api.protected_routes import router as protected_router
from config.database import SessionLocal
from config.settings import settings

logger = logging.getLogger("insider_threat_api")
MAX_REQUEST_BYTES = 1_048_576

app = FastAPI(title="Insider Threat System API", docs_url="/docs" if not settings.is_production else None, redoc_url=None, openapi_url="/openapi.json" if not settings.is_production else None)


app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"], max_age=600)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            body_size = int(content_length)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header"})
        if body_size > MAX_REQUEST_BYTES:
            return JSONResponse(status_code=413, content={"detail": "Request body is too large"})
    request_id = str(uuid4())
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request error request_id=%s path=%s", request_id, request.url.path)
        response = JSONResponse(status_code=500, content={"detail": "Internal server error"})
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith(("/auth", "/api", "/dashboard")) else "public, max-age=60"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%d", request_id, request.method, request.url.path, response.status_code, (time.perf_counter() - started_at) * 1000)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Invalid request data"})


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Insider Threat System API is running"}


@app.get("/healthz", include_in_schema=False)
def health_check():
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(protected_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(anomaly_router, prefix="/api", tags=["Anomalies"])
app.include_router(assign_router, prefix="/api", tags=["Assign"])
app.include_router(blocked_router, prefix="/api", tags=["Blocked"])
