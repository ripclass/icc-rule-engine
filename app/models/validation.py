from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class ValidationStatus(enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

class Validation(Base):
    __tablename__ = "validations"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    document_id = Column(String(100), nullable=False)  # external document identifier
    status = Column(Enum(ValidationStatus), nullable=False)
    details = Column(Text, nullable=True)  # discrepancy notes or validation details
    confidence_score = Column(String(10), nullable=True)  # for AI-assisted validations
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to Rule model
    rule = relationship("Rule", backref="validations")