from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RuleType(str, Enum):
    CODABLE = "codable"
    AI_ASSISTED = "ai_assisted"

class RuleBase(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier (e.g., UCP600-14a)")
    source: str = Field(..., description="Rule source document (e.g., UCP600)")
    article: str = Field(..., description="Article or section number")
    title: Optional[str] = Field(None, description="Rule title")
    text: str = Field(..., description="Full rule text")
    type: RuleType = Field(..., description="Rule classification type")
    logic: Optional[str] = Field(None, description="Pseudo-code logic for codable rules")
    version: str = Field(default="1.0", description="Rule version")

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    type: Optional[RuleType] = None
    logic: Optional[str] = None
    version: Optional[str] = None

class Rule(RuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RuleUploadResponse(BaseModel):
    message: str
    rules_created: int
    rules: list[Rule]