"""FastAPI application entrypoint for the guardrail auditor platform."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.api.routes.explanations import router as explanation_router
from app.api.routes.health import router as health_router
from app.api.routes.scans import router as scan_router
from app.api.routes.uploads import router as upload_router
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, ParsingError, UploadError
from app.core.logging import configure_logging, get_logger
from app.infrastructure.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the application on startup and clean up on shutdown."""
    logger = get_logger("app.lifespan")
    logger.info("Application startup", extra={"lifecycle_event": "startup"})
    init_db()
    logger.info(
        "Database initialized", extra={"lifecycle_event": "database_initialized"}
    )
    yield
    logger.info("Application shutdown", extra={"lifecycle_event": "shutdown"})


def create_app(settings_obj: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = settings_obj or get_settings()
    logger = configure_logging(settings)

    app = FastAPI(
        title=settings.openapi_title,
        version=settings.app_version,
        description=settings.openapi_description,
        contact={"name": settings.contact_name, "email": settings.contact_email},
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next: Any) -> Any:
        """Log incoming requests with latency and response status."""
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Request completed",
            extra={
                "request_method": request.method,
                "request_path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.exception_handler(UploadError)
    async def upload_error_handler(_: Request, exc: UploadError) -> JSONResponse:
        """Handle invalid or unsupported uploads with a client-safe 400 response."""
        logger.warning(
            "Upload error",
            extra={"error_type": exc.__class__.__name__, "details": str(exc)},
        )
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ParsingError)
    async def parsing_error_handler(_: Request, exc: ParsingError) -> JSONResponse:
        """Handle malformed or unparseable templates with a client-safe 400 response."""
        logger.warning(
            "Parsing error",
            extra={"error_type": exc.__class__.__name__, "details": str(exc)},
        )
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        """Handle application-level exceptions with a consistent payload."""
        logger.error(
            "Application error",
            extra={"error_type": exc.__class__.__name__, "details": str(exc)},
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions using a consistent error response schema."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation failures with detailed error payloads."""
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        """Capture unexpected failures and return a generic 500 response."""
        logger.exception(
            "Unhandled exception",
            extra={"error_type": exc.__class__.__name__, "details": str(exc)},
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    app.include_router(health_router)
    app.include_router(upload_router)
    app.include_router(scan_router)
    app.include_router(explanation_router)
    return app


app = create_app()
