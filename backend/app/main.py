"""NexusAI FastAPI application entrypoint.

Initializes the FastAPI app, configures logging, registers global
exception handlers, sets up CORS, and exposes a health check endpoint.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import NexusAIException
from app.core.logging import configure_logging, get_logger
from app.db.session import check_db_connection

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events.

    Configures logging when the app starts, and logs a clean shutdown
    message when the app stops. Runs exactly once per process lifetime.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to FastAPI to run the application.
    """
    configure_logging()
    logger.info("app_starting", app_name=settings.APP_NAME, env=settings.APP_ENV)
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-Grade AI Research & Coding Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NexusAIException)
async def nexusai_exception_handler(request: Request, exc: NexusAIException) -> JSONResponse:
    """Convert any NexusAIException into a consistent JSON error response.

    Args:
        request: The incoming HTTP request that triggered the exception.
        exc: The raised NexusAIException instance.

    Returns:
        A JSONResponse with the appropriate status code and error body.
    """
    logger.error(
        "request_failed",
        path=str(request.url),
        error=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Check the health of the application and its dependencies.

    Returns:
        A dictionary indicating overall status and database connectivity.
    """
    db_healthy = await check_db_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "connected" if db_healthy else "disconnected",
    }


@app.get("/", tags=["System"])
async def root() -> dict:
    """Return basic API information at the root endpoint.

    Returns:
        A welcome message and link to interactive API docs.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
    }