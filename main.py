"""
Crop Disease Treatment Recommendation API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from config.settings import settings
from config.logging import setup_logging, get_logger
from routes import recommend, disease, suppliers, prices
from services.cache import init_cache, close_cache



setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Crop Disease Treatment Recommendation API", extra={
        "version": settings.app_version,
        "debug": settings.debug
    })

    await init_cache()
    logger.info("Cache initialized")

    yield

    logger.info("Shutting down Crop Disease Treatment Recommendation API")
    await close_cache()
    logger.info("Cache closed")



app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive API for crop disease treatment recommendations in Ghana",
    debug=settings.debug,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)


    logger.info("Request processed", extra={
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "process_time": process_time
    })

    return response



app.include_router(disease.router, prefix="/api", tags=["diseases"])
app.include_router(recommend.router, prefix="/api", tags=["recommendations"])
app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])
app.include_router(prices.router, prefix="/api", tags=["prices"])


@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Crop Disease Treatment Recommendation API",
        "version": settings.app_version,
        "status": "healthy",
        "supported_crops": settings.supported_crops,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error("Unhandled exception", extra={
        "method": request.method,
        "url": str(request.url),
        "error": str(exc),
        "type": type(exc).__name__
    }, exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )
