"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.config import get_settings
from app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Starting {} v{}", settings.APP_NAME, settings.API_VERSION)
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        description="AI-powered Interview Preparation Coach with RAG",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()


@app.get("/")
async def root():
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "api": settings.API_PREFIX,
    }
