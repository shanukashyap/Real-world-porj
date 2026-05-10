"""FastAPI application with security middleware and routers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes_auth import router as auth_router
from app.api.routes_health import router as health_router
from app.api.routes_rag import router as rag_router
from app.api.routes_threat import router as threat_router
from app.core.config import get_settings
from app.core.middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter
from app.db.init_db import init_extensions_and_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_extensions_and_tables()
    yield


app = FastAPI(
    title="SOC AI Copilot",
    description=(
        "Real-world security operations assistant: RAG over OWASP, MITRE, and SOC runbooks, "
        "with JWT auth, audit logging, and threat-intel queries."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.expose_docs else None,
    redoc_url="/api/redoc" if settings.expose_docs else None,
    openapi_url="/api/openapi.json" if settings.expose_docs else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(threat_router, prefix="/api/v1")
