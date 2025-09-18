from .rule import Rule, RuleType, Base as RuleBase
from .validation import Validation, ValidationStatus, Base as ValidationBase

# Ensure both models use the same Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Re-create models with shared Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False)
    source = Column(String(100), nullable=False)
    article = Column(String(50), nullable=False)
    title = Column(String(200), nullable=True)
    text = Column(Text, nullable=False)
    type = Column(Enum(RuleType), nullable=False)
    logic = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Validation(Base):
    __tablename__ = "validations"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    document_id = Column(String(100), nullable=False)
    status = Column(Enum(ValidationStatus), nullable=False)
    details = Column(Text, nullable=True)
    confidence_score = Column(String(10), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    rule = relationship("Rule", back_populates="validations")

Rule.validations = relationship("Validation", back_populates="rule")

__all__ = ["Base", "Rule", "Validation", "RuleType", "ValidationStatus"]