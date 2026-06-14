"""
IKCO Store - Main Application
فروشگاه آنلاین ایران خودرو
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
from database import Base, engine
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for IKCO Online Store",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from routes import (
    auth_router,
    products_router,
    orders_router,
    users_router,
    reviews_router,
    wishlist_router
)

# Include routes
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(wishlist_router)

# Health check endpoint
@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    سلامت‌سنجی سرور
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    return JSONResponse({
        "message": "Welcome to IKCO Store API",
        "docs": "/api/docs",
        "version": settings.APP_VERSION
    })

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
