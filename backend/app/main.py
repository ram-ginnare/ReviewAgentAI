from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import time
import uuid
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.production import SlidingWindowRateLimiter, enforce_rate_limit
from backend.app.db.database import SessionLocal
from backend.app.models.audit_log import AuditLog
from backend.app.db.init_db import initialize_database

logger = logging.getLogger("reviewagentai")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="reviewagentai API",
    version="0.1.0",
    description="Backend API for the reviewagentai MVP.",
    lifespan=lifespan,
)

app.state.rate_limiter = SlidingWindowRateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials="*" not in settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    return await enforce_rate_limit(request, call_next, app.state.rate_limiter)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.url.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        status_code = response.status_code if response is not None else 500
        logger.info(
            "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%s",
            request_id, request.method, request.url.path, status_code, elapsed_ms,
        )
        if settings.audit_log_enabled and request.url.path.startswith("/api/v1/") and request.url.path not in {"/api/v1/health"}:
            try:
                user = getattr(request.state, "current_user", None)
                with SessionLocal() as audit_db:
                    audit_db.add(AuditLog(
                        user_id=getattr(user, "id", None), business_id=getattr(user, "business_id", None),
                        action=f"{request.method} {request.url.path}", method=request.method, path=request.url.path,
                        status_code=status_code, request_id=request_id,
                        ip_address=request.client.host if request.client else None,
                    ))
                    audit_db.commit()
            except Exception:
                logger.exception("audit_log_write_failed request_id=%s", request_id)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = (exc.headers or {}).get("X-Error-Code") or f"HTTP_{exc.status_code}"
    headers = {k: v for k, v in (exc.headers or {}).items() if k.lower() != "x-error-code"}
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": code},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors()), "code": "VALIDATION_ERROR"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_request_error method=%s path=%s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred.", "code": "INTERNAL_SERVER_ERROR"},
    )

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["system"])
def root():
    return {
        "application": "reviewagentai",
        "version": "0.1.0",
        "status": "running",
    }
