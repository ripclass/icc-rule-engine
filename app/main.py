from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import logging

from app.routers import rules, validate, health
from app.db import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown
    """
    # Startup
    logger.info("Starting ICC Rule Engine...")
    try:
        create_tables()
        logger.info("✅ Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Error with database tables: {e}")
        # Don't fail startup - allow app to run even if DB is temporarily unavailable

    yield

    # Shutdown
    logger.info("🔄 Shutting down ICC Rule Engine...")

# Create FastAPI application
app = FastAPI(
    title="ICC Rule Engine",
    description="""
    ICC Rule Engine MVP - A microservice for ingesting, parsing, and validating
    documents against ICC trade finance rules.

    ## Features
    * **PDF Ingestion**: Upload ICC rulebooks and automatically parse rules
    * **LLM Classification**: Automatically classify rules as codable or AI-assisted
    * **Document Validation**: Validate Letter of Credit documents against stored rules
    * **Rule Management**: CRUD operations for managing rules
    * **Health Monitoring**: Service health checks and diagnostics

    ## Supported Rule Sources
    * UCP600 - Uniform Customs and Practice for Documentary Credits
    * ISBP - International Standard Banking Practice
    * eUCP - Electronic Uniform Customs and Practice

    ## API Documentation
    * **Swagger UI**: Available at `/docs`
    * **ReDoc**: Available at `/redoc`
    """,
    version="1.0.0",
    contact={
        "name": "ICC Rule Engine Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(rules.router)
app.include_router(validate.router)

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "service": "ICC Rule Engine",
        "version": "1.0.0",
        "description": "Microservice for ICC trade finance rule validation",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "rules": "/rules",
            "validate": "/validate"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please check the logs.",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    # For local development - SQLAlchemy 2.0 compatible
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )