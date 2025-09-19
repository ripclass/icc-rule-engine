# Import models and enums from their respective files
from .rule import Rule, RuleType
from .validation import Validation, ValidationStatus

# Import the shared Base from db module
from app.db import Base

# Set up relationships between models after import
# This needs to be done after both models are defined
from sqlalchemy.orm import relationship

# Add relationships to Rule model
Rule.validations = relationship("Validation", back_populates="rule")

# Export all models and related classes
__all__ = ["Base", "Rule", "Validation", "RuleType", "ValidationStatus"]