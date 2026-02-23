"""Bookshelf API — a production-relevant FastAPI application for Kubernetes."""

import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.routing import Route

from .database import Base, engine
from .metrics import REQUEST_COUNT, REQUEST_DURATION, metrics_endpoint
from .routes import router as books_router

# ---------------------------------------------------------------------------
# Structured JSON Logging
# ---------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _configure_logging() -> None:
    """Set up structured JSON-style logging."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(LOG_LEVEL)


_configure_logging()
logger = logging.getLogger("bookshelf")


# ---------------------------------------------------------------------------
# Application Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting Bookshelf API — creating database tables")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down Bookshelf API")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Bookshelf API",
    description="A production-relevant REST API for learning Kubernetes deployments.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include CRUD routes
app.include_router(books_router)

# Prometheus metrics endpoint (served outside FastAPI for clean separation)
app.routes.append(Route("/metrics", endpoint=metrics_endpoint, methods=["GET"]))


# ---------------------------------------------------------------------------
# Health Checks
# ---------------------------------------------------------------------------


@app.get("/healthz", tags=["health"])
def liveness():
    """Liveness probe — is the process alive?"""
    return {"status": "alive"}


@app.get("/readyz", tags=["health"])
def readiness():
    """Readiness probe — is the app ready to serve traffic?"""
    try:
        # Quick DB check
        from sqlalchemy import text
        from .database import SessionLocal

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready"}
    except Exception as exc:
        logger.error("Readiness check failed: %s", exc)
        return {"status": "not ready", "error": str(exc)}


# ---------------------------------------------------------------------------
# Request Metrics Middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request count and duration for Prometheus."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    # Normalize path to avoid cardinality explosion
    path = request.url.path
    for route in app.routes:
        if hasattr(route, "path") and route.path != "/metrics":
            # Match parameterized routes like /books/{book_id}
            if hasattr(route, "param_convertors") or path.startswith(route.path.split("{")[0]):
                path = route.path
                break

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=path,
        status=response.status_code,
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=path,
    ).observe(duration)

    return response


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@app.get("/", tags=["root"])
def root():
    """Root endpoint with API information."""
    return {
        "app": "Bookshelf API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz",
        "metrics": "/metrics",
    }
