from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db, test_connection
from app.services.llm_classifier import LLMClassifier
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health", include_in_schema=False)
@router.get("/health/", include_in_schema=False)
async def health_check():
    """
    Basic health check endpoint - always returns OK for load balancer
    Handles both /health and /health/ to avoid redirects
    """
    return {
        "status": "ok",
        "service": "ICC Rule Engine",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check including database and external services
    Does not use DB dependency to avoid failures
    """
    health_status = {
        "status": "healthy",
        "service": "ICC Rule Engine",
        "version": "1.0.0",
        "components": {}
    }

    # Check database connection
    try:
        if test_connection():
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        else:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": "Database connection failed"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"

    # Check OpenAI API connection
    try:
        llm_classifier = LLMClassifier()
        if llm_classifier.test_connection():
            health_status["components"]["openai"] = {
                "status": "healthy",
                "message": "OpenAI API connection successful"
            }
        else:
            health_status["components"]["openai"] = {
                "status": "unhealthy",
                "message": "OpenAI API connection failed"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"OpenAI health check error: {e}")
        health_status["components"]["openai"] = {
            "status": "unhealthy",
            "message": f"OpenAI API error: {str(e)}"
        }
        health_status["status"] = "degraded"

    # Check environment variables
    required_env_vars = ["DATABASE_URL"]
    optional_env_vars = ["OPENAI_API_KEY"]

    missing_required = [var for var in required_env_vars if not os.getenv(var)]
    missing_optional = [var for var in optional_env_vars if not os.getenv(var)]

    if missing_required:
        health_status["components"]["environment"] = {
            "status": "unhealthy",
            "message": f"Missing required environment variables: {', '.join(missing_required)}"
        }
        health_status["status"] = "unhealthy"
    else:
        env_message = "All required environment variables are set"
        if missing_optional:
            env_message += f" (Optional missing: {', '.join(missing_optional)})"

        health_status["components"]["environment"] = {
            "status": "healthy",
            "message": env_message
        }

    return health_status