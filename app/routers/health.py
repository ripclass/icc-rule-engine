from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.llm_classifier import LLMClassifier
import os

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "ICC Rule Engine",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including database and external services
    """
    health_status = {
        "status": "healthy",
        "service": "ICC Rule Engine",
        "version": "1.0.0",
        "components": {}
    }

    # Check database connection
    try:
        db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"

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
        health_status["components"]["openai"] = {
            "status": "unhealthy",
            "message": f"OpenAI API error: {str(e)}"
        }
        health_status["status"] = "degraded"

    # Check environment variables
    required_env_vars = ["DATABASE_URL", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        health_status["components"]["environment"] = {
            "status": "unhealthy",
            "message": f"Missing environment variables: {', '.join(missing_vars)}"
        }
        health_status["status"] = "unhealthy"
    else:
        health_status["components"]["environment"] = {
            "status": "healthy",
            "message": "All required environment variables are set"
        }

    return health_status