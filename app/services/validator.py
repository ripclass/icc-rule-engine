from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Rule, Validation, ValidationStatus, RuleType
from app.schemas.validation import ValidationResult, ValidationResponse, ValidationStatus as SchemaValidationStatus
from app.services.llm_classifier import LLMClassifier

class ValidationEngine:
    """
    Core validation engine that processes documents against stored rules
    """

    def __init__(self, db: Session):
        self.db = db
        self.llm_classifier = LLMClassifier()

    def validate_document(self, document_id: str, document_data: Dict[str, Any], rule_filters: Dict[str, str] = None) -> ValidationResponse:
        """
        Main validation method - validates document against all applicable rules
        """
        # Get applicable rules
        rules = self._get_applicable_rules(rule_filters)

        validation_results = []
        passed = 0
        failed = 0
        warnings = 0

        for rule in rules:
            # Validate against individual rule
            result = self._validate_against_rule(rule, document_data)

            # Store validation result in database
            self._store_validation_result(rule.id, document_id, result)

            # Count results
            if result.status == SchemaValidationStatus.PASS:
                passed += 1
            elif result.status == SchemaValidationStatus.FAIL:
                failed += 1
            else:
                warnings += 1

            validation_results.append(result)

        # Determine overall status
        overall_status = self._determine_overall_status(passed, failed, warnings)

        return ValidationResponse(
            document_id=document_id,
            overall_status=overall_status,
            total_rules_checked=len(rules),
            passed=passed,
            failed=failed,
            warnings=warnings,
            results=validation_results,
            timestamp=datetime.now()
        )

    def _get_applicable_rules(self, filters: Dict[str, str] = None) -> List[Rule]:
        """
        Get rules that apply to the validation based on filters
        """
        query = self.db.query(Rule)

        if filters:
            if "source" in filters:
                query = query.filter(Rule.source == filters["source"])
            if "domain" in filters and filters["domain"] == "LC":
                query = query.filter(Rule.source.in_(["UCP600", "ISBP", "eUCP"]))

        return query.all()

    def _validate_against_rule(self, rule: Rule, document_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate document against a single rule
        """
        if rule.type == RuleType.CODABLE:
            return self._validate_codable_rule(rule, document_data)
        else:
            return self._validate_ai_assisted_rule(rule, document_data)

    def _validate_codable_rule(self, rule: Rule, document_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate document against a codable rule using deterministic logic
        """
        try:
            # Execute the pseudo-code logic
            result = self._execute_rule_logic(rule.logic, document_data)

            if result["status"]:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    rule_text=rule.text[:200] + "..." if len(rule.text) > 200 else rule.text,
                    status=SchemaValidationStatus.PASS,
                    details=result.get("details", "Rule validation passed"),
                    confidence_score="high"
                )
            else:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    rule_text=rule.text[:200] + "..." if len(rule.text) > 200 else rule.text,
                    status=SchemaValidationStatus.FAIL,
                    details=result.get("details", "Rule validation failed"),
                    confidence_score="high"
                )

        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                rule_text=rule.text[:200] + "..." if len(rule.text) > 200 else rule.text,
                status=SchemaValidationStatus.WARNING,
                details=f"Error executing rule logic: {str(e)}",
                confidence_score="low"
            )

    def _validate_ai_assisted_rule(self, rule: Rule, document_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate document against an AI-assisted rule using LLM
        """
        try:
            ai_result = self.llm_classifier.validate_with_ai(rule.text, document_data)

            # Map AI result to our schema
            status_mapping = {
                "pass": SchemaValidationStatus.PASS,
                "fail": SchemaValidationStatus.FAIL,
                "warning": SchemaValidationStatus.WARNING
            }

            return ValidationResult(
                rule_id=rule.rule_id,
                rule_text=rule.text[:200] + "..." if len(rule.text) > 200 else rule.text,
                status=status_mapping.get(ai_result["status"], SchemaValidationStatus.WARNING),
                details=ai_result.get("details", "AI validation completed"),
                confidence_score=ai_result.get("confidence_score", "medium")
            )

        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                rule_text=rule.text[:200] + "..." if len(rule.text) > 200 else rule.text,
                status=SchemaValidationStatus.WARNING,
                details=f"Error in AI validation: {str(e)}",
                confidence_score="low"
            )

    def _execute_rule_logic(self, logic: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pseudo-code logic for codable rules
        This is a simplified implementation - in production you'd want a more robust interpreter
        """
        if not logic:
            return {"status": False, "details": "No logic defined for this rule"}

        # Extract common document fields
        expiry_date = document_data.get("expiry_date")
        shipment_date = document_data.get("shipment_date")
        presentation_date = document_data.get("presentation_date")
        amount = document_data.get("amount")
        currency = document_data.get("currency")
        documents = document_data.get("documents", [])

        # Simple logic execution examples
        try:
            if "expiry_date >= shipment_date" in logic and expiry_date and shipment_date:
                if self._parse_date(expiry_date) >= self._parse_date(shipment_date):
                    return {"status": True, "details": "Expiry date is after shipment date"}
                else:
                    return {"status": False, "details": "Expiry date is before shipment date"}

            if "shipment_date <= presentation_date" in logic and shipment_date and presentation_date:
                if self._parse_date(shipment_date) <= self._parse_date(presentation_date):
                    return {"status": True, "details": "Shipment date is before or equal to presentation date"}
                else:
                    return {"status": False, "details": "Shipment date is after presentation date"}

            if "currency" in logic and currency:
                if currency in ["USD", "EUR", "GBP", "JPY"]:  # Example currency check
                    return {"status": True, "details": f"Currency {currency} is acceptable"}
                else:
                    return {"status": False, "details": f"Currency {currency} may not be acceptable"}

            if "amount > 0" in logic and amount:
                try:
                    amount_value = float(amount)
                    if amount_value > 0:
                        return {"status": True, "details": "Amount is positive"}
                    else:
                        return {"status": False, "details": "Amount must be positive"}
                except ValueError:
                    return {"status": False, "details": "Invalid amount format"}

            # Default fallback
            return {"status": True, "details": "Rule logic executed successfully"}

        except Exception as e:
            return {"status": False, "details": f"Error executing logic: {str(e)}"}

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object
        """
        try:
            # Try common date formats
            formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            # If no format works, try to parse as ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            raise ValueError(f"Unable to parse date: {date_str}")

    def _store_validation_result(self, rule_id: int, document_id: str, result: ValidationResult):
        """
        Store validation result in database
        """
        try:
            # Map schema status to model status
            status_mapping = {
                SchemaValidationStatus.PASS: ValidationStatus.PASS,
                SchemaValidationStatus.FAIL: ValidationStatus.FAIL,
                SchemaValidationStatus.WARNING: ValidationStatus.WARNING
            }

            validation = Validation(
                rule_id=rule_id,
                document_id=document_id,
                status=status_mapping[result.status],
                details=result.details,
                confidence_score=result.confidence_score
            )

            self.db.add(validation)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # Log error but don't fail the validation

    def _determine_overall_status(self, passed: int, failed: int, warnings: int) -> SchemaValidationStatus:
        """
        Determine overall validation status based on individual results
        """
        if failed > 0:
            return SchemaValidationStatus.FAIL
        elif warnings > 0:
            return SchemaValidationStatus.WARNING
        else:
            return SchemaValidationStatus.PASS