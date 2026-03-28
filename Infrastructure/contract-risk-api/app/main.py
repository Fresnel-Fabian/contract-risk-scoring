"""
Contract Risk Scoring Engine — FastAPI Application
====================================================
Run:
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

Docs:
    http://localhost:8080/docs
    http://localhost:8080/redoc
"""
from __future__ import annotations
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.routers.analyze import router as analyze_router
from app.routers.health import health_router, clauses_router
from app.services.scorer import init_scoring_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
    logger.info("=== %s v%s starting ===", settings.app_name, settings.version)
    svc = init_scoring_service()
    logger.info("Model: %s", svc.model_name)
    logger.info("CORS origins: %s", settings.origins_list)
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "AI-powered contract clause extraction and risk scoring. "
            "Fine-tuned RoBERTa on CUAD — 510 contracts, 41 clause types. "
            "Falls back to LR+TF-IDF automatically when no GPU/model is present."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing header ─────────────────────────────────────────────────
    @app.middleware("http")
    async def add_timing(request: Request, call_next) -> Response:
        t0 = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-Ms"] = str(
            round((time.perf_counter() - t0) * 1000)
        )
        return response

    # ── Global error handler ──────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def on_error(request: Request, exc: Exception):
        logger.exception("Unhandled: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(analyze_router)
    app.include_router(health_router)
    app.include_router(clauses_router)

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name":    settings.app_name,
            "version": settings.version,
            "docs":    "/docs",
            "health":  "/health",
            "clauses": "/clauses",
        }

    return app


app = create_app()
