from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
import enum

class RuleType(enum.Enum):
    CODABLE = "codable"
    AI_ASSISTED = "ai_assisted"

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "UCP600-14a"
    source = Column(String(100), nullable=False)  # e.g., "UCP600"
    article = Column(String(50), nullable=False)  # e.g., "14a"
    title = Column(String(200), nullable=True)
    text = Column(Text, nullable=False)
    type = Column(Enum(RuleType), nullable=False)
    logic = Column(Text, nullable=True)  # pseudo-code for codable rules
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to Validation model
    validations = relationship("Validation", back_populates="rule")