from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.validation import ValidationRequest, ValidationResponse
from app.services.validator import ValidationEngine

router = APIRouter(prefix="/validate", tags=["validation"])

@router.post("/", response_model=ValidationResponse)
async def validate_document(
    validation_request: ValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a document (LC) against stored ICC rules
    """
    try:
        # Initialize validation engine
        validator = ValidationEngine(db)

        # Perform validation
        result = validator.validate_document(
            document_id=validation_request.document_id,
            document_data=validation_request.document_data,
            rule_filters=validation_request.rule_filters
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during validation: {str(e)}"
        )

@router.post("/quick")
async def quick_validate(
    validation_request: ValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Quick validation that returns only summary status without storing results
    """
    try:
        # Initialize validation engine
        validator = ValidationEngine(db)

        # Perform validation
        result = validator.validate_document(
            document_id=validation_request.document_id,
            document_data=validation_request.document_data,
            rule_filters=validation_request.rule_filters
        )

        # Return simplified response
        return {
            "document_id": result.document_id,
            "overall_status": result.overall_status,
            "summary": {
                "total_rules": result.total_rules_checked,
                "passed": result.passed,
                "failed": result.failed,
                "warnings": result.warnings
            },
            "timestamp": result.timestamp
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during validation: {str(e)}"
        )

@router.get("/history/{document_id}")
async def get_validation_history(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get validation history for a specific document
    """
    from app.models import Validation, Rule

    try:
        # Get all validations for this document
        validations = db.query(Validation).join(Rule).filter(
            Validation.document_id == document_id
        ).order_by(Validation.timestamp.desc()).all()

        if not validations:
            raise HTTPException(status_code=404, detail="No validation history found for this document")

        # Group by timestamp to get validation sessions
        validation_sessions = {}
        for validation in validations:
            timestamp_key = validation.timestamp.isoformat()[:19]  # Group by minute
            if timestamp_key not in validation_sessions:
                validation_sessions[timestamp_key] = {
                    "timestamp": validation.timestamp,
                    "results": []
                }

            validation_sessions[timestamp_key]["results"].append({
                "rule_id": validation.rule.rule_id,
                "rule_text": validation.rule.text[:100] + "..." if len(validation.rule.text) > 100 else validation.rule.text,
                "status": validation.status.value,
                "details": validation.details,
                "confidence_score": validation.confidence_score
            })

        return {
            "document_id": document_id,
            "total_sessions": len(validation_sessions),
            "sessions": list(validation_sessions.values())
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving validation history: {str(e)}"
        )