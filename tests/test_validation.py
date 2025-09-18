import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db
from app.models import Base, Rule, RuleType
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_validation.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_rules(client):
    """Create sample rules for testing validation"""
    db = TestingSessionLocal()

    rules = [
        Rule(
            rule_id="TEST-DATE-001",
            source="TEST",
            article="001",
            title="Expiry Date Check",
            text="Presentation must be before expiry date",
            type=RuleType.CODABLE,
            logic="presentation_date <= expiry_date",
            version="1.0"
        ),
        Rule(
            rule_id="TEST-AMOUNT-001",
            source="TEST",
            article="002",
            title="Amount Validation",
            text="Amount must be positive",
            type=RuleType.CODABLE,
            logic="amount > 0",
            version="1.0"
        ),
        Rule(
            rule_id="TEST-AI-001",
            source="TEST",
            article="003",
            title="Document Quality Check",
            text="Documents must appear authentic and properly formatted",
            type=RuleType.AI_ASSISTED,
            logic=None,
            version="1.0"
        )
    ]

    for rule in rules:
        db.add(rule)

    db.commit()
    db.close()

    return rules

@pytest.fixture
def sample_lc_document():
    """Sample Letter of Credit document for testing"""
    return {
        "document_id": "LC-TEST-001",
        "applicant": "Test Applicant Ltd",
        "beneficiary": "Test Beneficiary Ltd",
        "amount": "50000.00",
        "currency": "USD",
        "expiry_date": "2024-12-31",
        "shipment_date": "2024-12-15",
        "presentation_date": "2024-12-20",
        "latest_shipment_date": "2024-12-30",
        "documents": [
            "Commercial Invoice",
            "Bill of Lading",
            "Insurance Certificate"
        ],
        "description_of_goods": "Test goods for validation",
        "port_of_loading": "Test Port A",
        "port_of_discharge": "Test Port B"
    }

@pytest.fixture
def invalid_lc_document():
    """Invalid Letter of Credit document for testing failures"""
    return {
        "document_id": "LC-INVALID-001",
        "applicant": "Test Applicant Ltd",
        "beneficiary": "Test Beneficiary Ltd",
        "amount": "-1000.00",  # Invalid negative amount
        "currency": "USD",
        "expiry_date": "2024-12-31",
        "shipment_date": "2024-12-15",
        "presentation_date": "2025-01-05",  # After expiry date
        "latest_shipment_date": "2024-12-30",
        "documents": [],
        "description_of_goods": "Invalid test goods",
        "port_of_loading": "Test Port A",
        "port_of_discharge": "Test Port B"
    }

class TestValidationEngine:
    """Test the validation engine functionality"""

    def test_validate_compliant_document(self, client, sample_rules, sample_lc_document):
        """Test validation of a compliant document"""
        validation_request = {
            "document_id": sample_lc_document["document_id"],
            "document_data": sample_lc_document,
            "rule_filters": {"source": "TEST"}
        }

        response = client.post("/validate/", json=validation_request)
        assert response.status_code == 200

        result = response.json()
        assert result["document_id"] == sample_lc_document["document_id"]
        assert result["total_rules_checked"] > 0
        assert "results" in result
        assert "timestamp" in result

    def test_validate_non_compliant_document(self, client, sample_rules, invalid_lc_document):
        """Test validation of a non-compliant document"""
        validation_request = {
            "document_id": invalid_lc_document["document_id"],
            "document_data": invalid_lc_document,
            "rule_filters": {"source": "TEST"}
        }

        response = client.post("/validate/", json=validation_request)
        assert response.status_code == 200

        result = response.json()
        assert result["document_id"] == invalid_lc_document["document_id"]
        assert result["failed"] > 0 or result["warnings"] > 0  # Should have failures/warnings

    def test_quick_validation(self, client, sample_rules, sample_lc_document):
        """Test quick validation endpoint"""
        validation_request = {
            "document_id": sample_lc_document["document_id"],
            "document_data": sample_lc_document,
            "rule_filters": {"source": "TEST"}
        }

        response = client.post("/validate/quick", json=validation_request)
        assert response.status_code == 200

        result = response.json()
        assert "summary" in result
        assert "overall_status" in result
        assert "timestamp" in result

    def test_validation_with_domain_filter(self, client, sample_rules, sample_lc_document):
        """Test validation with domain filtering"""
        # Add UCP600 rule for LC domain testing
        db = TestingSessionLocal()
        ucp_rule = Rule(
            rule_id="UCP600-TEST-001",
            source="UCP600",
            article="TEST",
            title="UCP Test Rule",
            text="Test UCP rule for LC validation",
            type=RuleType.CODABLE,
            logic="amount > 0",
            version="1.0"
        )
        db.add(ucp_rule)
        db.commit()
        db.close()

        validation_request = {
            "document_id": sample_lc_document["document_id"],
            "document_data": sample_lc_document,
            "rule_filters": {"domain": "LC"}
        }

        response = client.post("/validate/", json=validation_request)
        assert response.status_code == 200

        result = response.json()
        # Should include UCP600 rules
        rule_sources = [r["rule_id"] for r in result["results"]]
        assert any("UCP600" in rule_id for rule_id in rule_sources)

    def test_validation_history(self, client, sample_rules, sample_lc_document):
        """Test getting validation history for a document"""
        # First, perform a validation to create history
        validation_request = {
            "document_id": sample_lc_document["document_id"],
            "document_data": sample_lc_document,
            "rule_filters": {"source": "TEST"}
        }

        client.post("/validate/", json=validation_request)

        # Now get the history
        response = client.get(f"/validate/history/{sample_lc_document['document_id']}")
        assert response.status_code == 200

        history = response.json()
        assert history["document_id"] == sample_lc_document["document_id"]
        assert "sessions" in history
        assert len(history["sessions"]) > 0

    def test_validation_history_nonexistent_document(self, client):
        """Test getting validation history for non-existent document"""
        response = client.get("/validate/history/NONEXISTENT")
        assert response.status_code == 404

class TestValidationLogic:
    """Test specific validation logic"""

    def test_date_validation_logic(self):
        """Test date comparison logic"""
        from app.services.validator import ValidationEngine
        from datetime import datetime

        # Mock database session
        class MockDB:
            def query(self, model):
                return self
            def filter(self, condition):
                return self
            def all(self):
                return []
            def add(self, obj):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass

        validator = ValidationEngine(MockDB())

        # Test date parsing
        date1 = validator._parse_date("2024-12-31")
        date2 = validator._parse_date("2024-12-01")

        assert date1 > date2

    def test_rule_logic_execution(self):
        """Test execution of rule logic"""
        from app.services.validator import ValidationEngine

        class MockDB:
            def query(self, model):
                return self
            def filter(self, condition):
                return self
            def all(self):
                return []
            def add(self, obj):
                pass
            def commit(self):
                pass
            def rollback(self):
                pass

        validator = ValidationEngine(MockDB())

        # Test amount validation
        document_data = {"amount": "1000.00"}
        result = validator._execute_rule_logic("amount > 0", document_data)
        assert result["status"] == True

        # Test invalid amount
        document_data = {"amount": "-100.00"}
        result = validator._execute_rule_logic("amount > 0", document_data)
        assert result["status"] == False

    def test_overall_status_determination(self):
        """Test overall status determination logic"""
        from app.services.validator import ValidationEngine
        from app.schemas.validation import ValidationStatus

        class MockDB:
            pass

        validator = ValidationEngine(MockDB())

        # All passed
        status = validator._determine_overall_status(5, 0, 0)
        assert status == ValidationStatus.PASS

        # Some failed
        status = validator._determine_overall_status(3, 2, 0)
        assert status == ValidationStatus.FAIL

        # Some warnings but no failures
        status = validator._determine_overall_status(3, 0, 2)
        assert status == ValidationStatus.WARNING

class TestMockAIValidation:
    """Test AI validation with mocked responses"""

    @pytest.fixture
    def mock_ai_validation(self, monkeypatch):
        """Mock AI validation responses"""
        def mock_validate_with_ai(self, rule_text, document_data):
            # Mock different responses based on rule content
            if "authentic" in rule_text.lower():
                return {
                    "status": "pass",
                    "details": "Documents appear authentic and properly formatted",
                    "confidence_score": "high"
                }
            else:
                return {
                    "status": "warning",
                    "details": "Unable to fully assess document quality",
                    "confidence_score": "medium"
                }

        from app.services import llm_classifier
        monkeypatch.setattr(llm_classifier.LLMClassifier, "validate_with_ai", mock_validate_with_ai)

    def test_ai_assisted_validation(self, client, sample_rules, sample_lc_document, mock_ai_validation):
        """Test AI-assisted rule validation"""
        validation_request = {
            "document_id": sample_lc_document["document_id"],
            "document_data": sample_lc_document,
            "rule_filters": {"source": "TEST"}
        }

        response = client.post("/validate/", json=validation_request)
        assert response.status_code == 200

        result = response.json()

        # Find AI-assisted rule results
        ai_results = [r for r in result["results"] if "TEST-AI-001" in r["rule_id"]]
        assert len(ai_results) > 0

        ai_result = ai_results[0]
        assert ai_result["confidence_score"] in ["high", "medium", "low"]

def test_validation_error_handling(client):
    """Test validation error handling"""
    # Test with invalid request data
    invalid_request = {
        "document_id": "",  # Empty document ID
        "document_data": {},  # Empty document data
    }

    response = client.post("/validate/", json=invalid_request)
    # Should handle gracefully, not crash
    assert response.status_code in [400, 422, 500]  # Various possible error codes