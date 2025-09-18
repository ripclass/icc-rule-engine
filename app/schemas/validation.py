from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

class ValidationRequest(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    document_data: Dict[str, Any] = Field(..., description="LC document data in JSON format")
    rule_filters: Optional[Dict[str, str]] = Field(None, description="Optional filters (e.g., {'source': 'UCP600'})")

class ValidationResult(BaseModel):
    rule_id: str
    rule_text: str
    status: ValidationStatus
    details: Optional[str] = None
    confidence_score: Optional[str] = None

class ValidationResponse(BaseModel):
    document_id: str
    overall_status: ValidationStatus
    total_rules_checked: int
    passed: int
    failed: int
    warnings: int
    results: list[ValidationResult]
    timestamp: datetime

class ValidationCreate(BaseModel):
    rule_id: int
    document_id: str
    status: ValidationStatus
    details: Optional[str] = None
    confidence_score: Optional[str] = None

class Validation(BaseModel):
    id: int
    rule_id: int
    document_id: str
    status: ValidationStatus
    details: Optional[str] = None
    confidence_score: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True