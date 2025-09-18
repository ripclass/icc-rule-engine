from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.routers import rules, validate, health
from app.db import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown
    """
    # Startup
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

    yield

    # Shutdown
    print("🔄 Shutting down ICC Rule Engine...")

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
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please check the logs.",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )