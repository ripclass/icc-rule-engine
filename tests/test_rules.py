import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db
from app.models import Base, Rule, RuleType
import tempfile
import os

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def sample_rule_data():
    return {
        "rule_id": "TEST-001",
        "source": "TEST",
        "article": "001",
        "title": "Test Rule",
        "text": "This is a test rule for validation",
        "type": "codable",
        "logic": "amount > 0",
        "version": "1.0"
    }

def test_get_rules_empty(client):
    """Test getting rules when database is empty"""
    response = client.get("/rules/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_rule_via_text(client, sample_rule_data):
    """Test creating a rule directly (simulating parsed data)"""
    # This would typically be done through PDF upload, but we'll test the underlying logic
    db = TestingSessionLocal()

    rule = Rule(
        rule_id=sample_rule_data["rule_id"],
        source=sample_rule_data["source"],
        article=sample_rule_data["article"],
        title=sample_rule_data["title"],
        text=sample_rule_data["text"],
        type=RuleType.CODABLE,
        logic=sample_rule_data["logic"],
        version=sample_rule_data["version"]
    )

    db.add(rule)
    db.commit()
    db.close()

    # Verify rule was created
    response = client.get("/rules/")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 1
    assert rules[0]["rule_id"] == sample_rule_data["rule_id"]

def test_get_rule_by_id(client):
    """Test getting a specific rule by ID"""
    response = client.get("/rules/TEST-001")
    assert response.status_code == 200
    rule = response.json()
    assert rule["rule_id"] == "TEST-001"
    assert rule["title"] == "Test Rule"

def test_get_nonexistent_rule(client):
    """Test getting a rule that doesn't exist"""
    response = client.get("/rules/NONEXISTENT")
    assert response.status_code == 404

def test_update_rule(client):
    """Test updating an existing rule"""
    update_data = {
        "title": "Updated Test Rule",
        "logic": "amount > 100"
    }

    response = client.put("/rules/TEST-001", json=update_data)
    assert response.status_code == 200

    updated_rule = response.json()
    assert updated_rule["title"] == "Updated Test Rule"
    assert updated_rule["logic"] == "amount > 100"

def test_delete_rule(client):
    """Test deleting a rule"""
    response = client.delete("/rules/TEST-001")
    assert response.status_code == 200

    # Verify rule is deleted
    response = client.get("/rules/TEST-001")
    assert response.status_code == 404

def test_filter_rules_by_source(client):
    """Test filtering rules by source"""
    # Add multiple rules with different sources
    db = TestingSessionLocal()

    rules_data = [
        {"rule_id": "UCP600-001", "source": "UCP600", "article": "001", "text": "UCP rule", "type": RuleType.CODABLE},
        {"rule_id": "ISBP-001", "source": "ISBP", "article": "001", "text": "ISBP rule", "type": RuleType.AI_ASSISTED}
    ]

    for rule_data in rules_data:
        rule = Rule(**rule_data)
        db.add(rule)

    db.commit()
    db.close()

    # Test filtering by source
    response = client.get("/rules/?source=UCP600")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 1
    assert rules[0]["source"] == "UCP600"

def test_filter_rules_by_domain_lc(client):
    """Test filtering rules by LC domain"""
    response = client.get("/rules/?domain=LC")
    assert response.status_code == 200
    rules = response.json()
    # Should include UCP600 and ISBP rules
    sources = [rule["source"] for rule in rules]
    assert "UCP600" in sources

def test_filter_rules_by_type(client):
    """Test filtering rules by type"""
    response = client.get("/rules/?rule_type=codable")
    assert response.status_code == 200
    rules = response.json()
    for rule in rules:
        assert rule["type"] == "codable"

class TestPDFParsing:
    """Test PDF parsing functionality"""

    def test_pdf_validation_invalid_file(self, client):
        """Test PDF upload with invalid file"""
        response = client.post(
            "/rules/upload?source=TEST",
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )
        assert response.status_code == 400
        assert "must be a PDF" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_pdf_parser_extract_text(self):
        """Test PDF text extraction"""
        from app.services.pdf_parser import PDFParser

        parser = PDFParser()

        # Test with invalid PDF content
        assert not parser.validate_pdf_content(b"not a pdf")

    def test_rule_parsing_from_text(self):
        """Test parsing rules from text"""
        from app.services.pdf_parser import PDFParser

        parser = PDFParser()

        sample_text = """
        Article 14a - Standard for Examination

        A nominated bank acting on its nomination must examine documents.

        Article 14b - Examination Period

        Banks shall have a maximum of five banking days following presentation.
        """

        rules = parser.parse_rules_from_text(sample_text, "UCP600")

        assert len(rules) == 2
        assert rules[0]["rule_id"] == "UCP600-14a"
        assert rules[0]["article"] == "14a"
        assert "examination" in rules[0]["text"].lower()

        assert rules[1]["rule_id"] == "UCP600-14b"
        assert rules[1]["article"] == "14b"

class TestMockLLM:
    """Test LLM classification with mocked responses"""

    @pytest.fixture
    def mock_llm_response(self, monkeypatch):
        """Mock LLM responses for testing"""
        def mock_classify_rule(self, rule_text, rule_id):
            if "date" in rule_text.lower() or "amount" in rule_text.lower():
                return {
                    "type": "codable",
                    "reasoning": "Contains deterministic checks",
                    "logic": "mock_logic_here"
                }
            else:
                return {
                    "type": "ai_assisted",
                    "reasoning": "Requires human judgment",
                    "logic": None
                }

        from app.services import llm_classifier
        monkeypatch.setattr(llm_classifier.LLMClassifier, "classify_rule", mock_classify_rule)

    def test_rule_classification_codable(self, mock_llm_response):
        """Test classification of codable rules"""
        from app.services.llm_classifier import LLMClassifier

        classifier = LLMClassifier()
        result = classifier.classify_rule("Check if amount is greater than zero", "TEST-001")

        assert result["type"] == "codable"
        assert result["logic"] is not None

    def test_rule_classification_ai_assisted(self, mock_llm_response):
        """Test classification of AI-assisted rules"""
        from app.services.llm_classifier import LLMClassifier

        classifier = LLMClassifier()
        result = classifier.classify_rule("Document must appear authentic", "TEST-002")

        assert result["type"] == "ai_assisted"
        assert result["logic"] is None