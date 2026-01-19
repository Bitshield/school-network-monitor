"""
Main FastAPI application entry point.
UPDATED: Added warning suppression and improved error handling
"""

# Suppress warnings FIRST before other imports
import suppress_warnings

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime

from config import settings, validate_settings
from database import async_init_db, async_session
from api.v1.router import api_router
from core.logger import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


# Background monitoring task
monitoring_task = None


async def start_background_monitoring():
    """
    Start background monitoring tasks.
    This will run continuously in the background.
    Uses separate database sessions to avoid concurrent connection issues.
    """
    from services.monitoring import MonitoringService
    
    logger.info("Starting background monitoring service...")
    
    try:
        # Create a dedicated session for monitoring
        async with async_session() as db:
            monitor = MonitoringService(db)
            
            # Start continuous monitoring with configured interval
            # This will create NEW sessions for each monitoring cycle
            asyncio.create_task(
                monitor.start_continuous_monitoring(
                    interval=settings.MONITORING_INTERVAL
                )
            )
            
        logger.info(
            f"Background monitoring started (interval: {settings.MONITORING_INTERVAL}s)"
        )
    except Exception as e:
        logger.error(f"Failed to start background monitoring: {e}", exc_info=True)


async def stop_background_monitoring():
    """Stop background monitoring tasks."""
    global monitoring_task
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task # pyright: ignore[reportGeneralTypeIssues]
        except asyncio.CancelledError:
            logger.info("Background monitoring stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    try:
        # Validate settings
        validate_settings()
        logger.info("✓ Configuration validated")
        
        # Initialize database
        await async_init_db()
        logger.info("✓ Database initialized")
        
        # Start background tasks (only in production/non-debug mode)
        if not settings.DEBUG:
            await start_background_monitoring()
            logger.info("✓ Background monitoring started")
        else:
            logger.info("⚠ Background monitoring disabled in debug mode")
            logger.info("  (This prevents conflicts with auto-reload)")
        
        logger.info("=" * 60)
        logger.info(f"🚀 {settings.APP_NAME} is ready!")
        logger.info(f"📚 API Docs: http://localhost:8000{settings.API_DOCS_URL}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info(f"Shutting down {settings.APP_NAME}...")
    logger.info("=" * 60)
    
    try:
        await stop_background_monitoring()
        logger.info("✓ Background tasks stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL,
    openapi_url=settings.API_OPENAPI_URL,
    lifespan=lifespan,
)


# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Request validation failed",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoints
@app.get("/health", tags=["System"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/detailed", tags=["System"])
async def detailed_health_check():
    """Detailed health check with database connectivity."""
    from database import async_engine
    
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "api": "healthy",
        }
    }
    
    # Check database connectivity
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1") # type: ignore
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    return health_status


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": settings.API_DOCS_URL,
        "redoc": settings.API_REDOC_URL,
        "openapi": settings.API_OPENAPI_URL,
    }


# Run application
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME}...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True,
    )