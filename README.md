# ICC Rule Engine MVP

A full-featured microservice for ingesting ICC rulebooks, parsing them into machine-readable rules, and providing validation APIs for trade finance documents.

## 🚀 Features

- **PDF Ingestion**: Upload ICC rulebooks (PDF) and automatically extract rules
- **LLM Classification**: Automatically classify rules as codable or AI-assisted using GPT-4o-mini
- **Document Validation**: Validate Letter of Credit documents against stored rules
- **REST API**: Comprehensive API with auto-generated Swagger/OpenAPI documentation
- **Database Storage**: PostgreSQL with SQLAlchemy and Alembic migrations
- **Health Monitoring**: Service health checks and diagnostics

## 🏗️ Architecture

```
icc-rule-engine/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # SQLAlchemy database models
│   │   ├── rule.py          # Rule model
│   │   └── validation.py    # Validation model
│   ├── schemas/             # Pydantic schemas for API validation
│   │   ├── rule.py          # Rule schemas
│   │   └── validation.py    # Validation schemas
│   ├── services/            # Business logic services
│   │   ├── pdf_parser.py    # PDF text extraction and rule parsing
│   │   ├── llm_classifier.py # OpenAI integration for rule classification
│   │   └── validator.py     # Document validation engine
│   ├── routers/             # API endpoint routers
│   │   ├── rules.py         # Rule management endpoints
│   │   ├── validate.py      # Document validation endpoints
│   │   └── health.py        # Health check endpoints
│   └── db.py                # Database connection and configuration
├── scripts/
│   └── seed_rules.py        # Database seeding with sample UCP600 rules
├── tests/                   # Comprehensive test suite
├── alembic/                 # Database migration scripts
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd icc-rule-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and OpenAI API key
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb icc_rules

   # Run migrations
   alembic upgrade head
   ```

5. **Seed with sample data**
   ```bash
   python scripts/seed_rules.py --create-sample
   ```

### Running the Application

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Usage

### Core Endpoints

#### Upload PDF Rules
```bash
POST /rules/upload
```
Upload ICC rulebook PDF and automatically parse and classify rules.

#### Get Rules
```bash
GET /rules/
GET /rules/?source=UCP600
GET /rules/?domain=LC
GET /rules/?rule_type=codable
```

#### Validate Document
```bash
POST /validate/
```
Validate a Letter of Credit document against stored rules.

#### Health Check
```bash
GET /health/
GET /health/detailed
```

### Example: Document Validation

```bash
curl -X POST "http://localhost:8000/validate/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "LC-001",
    "document_data": {
      "amount": "100000.00",
      "currency": "USD",
      "expiry_date": "2024-12-31",
      "presentation_date": "2024-12-20",
      "documents": ["Commercial Invoice", "Bill of Lading"]
    },
    "rule_filters": {"source": "UCP600"}
  }'
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_validation.py
```

## 🏭 Production Deployment

### Environment Variables

Required environment variables for production:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
DEBUG=false
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🔍 Rule Types

The system classifies rules into two types:

### Codable Rules
Deterministic rules that can be validated programmatically:
- Date comparisons (expiry vs presentation)
- Amount validations
- Currency checks
- Document presence verification

Example: "Presentation must be before expiry date"
Logic: `presentation_date <= expiry_date`

### AI-Assisted Rules
Rules requiring human judgment or AI interpretation:
- Document authenticity
- Content quality assessment
- Compliance nuances

Example: "Documents must appear authentic and properly formatted"

## 📊 Sample Data

The seed script includes 8 sample UCP600 rules covering:
- Document examination standards (Article 14a)
- Examination periods (Article 14b)
- Commercial invoice requirements (Article 18)
- Insurance documentation (Article 28a)
- Shipment dates (Article 31)
- Expiry dates (Article 29)
- Credit independence (Article 3)
- Issuing bank undertakings (Article 7a)

## 🤝 Integration

### TRDR Hub Integration
```python
# Example integration with TRDR Hub
import requests

response = requests.post("http://rule-engine:8000/validate/", json={
    "document_id": lc_id,
    "document_data": extracted_lc_data,
    "rule_filters": {"domain": "LC"}
})

validation_result = response.json()
```

### ICC Rule GPT Integration
The engine can serve as a backend for conversational AI systems, providing structured rule data and validation results.

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running
   - Verify database exists

2. **OpenAI API Errors**
   - Check OPENAI_API_KEY in .env
   - Verify API key has sufficient credits
   - Check rate limits

3. **PDF Processing Errors**
   - Ensure uploaded files are valid PDFs
   - Check file size limits
   - Verify PDF is not password-protected

### Logs and Monitoring

Check application logs for detailed error information:
```bash
# View logs in development
uvicorn app.main:app --log-level debug

# Health check endpoints
curl http://localhost:8000/health/detailed
```

## 📈 Performance Considerations

- **Database Indexing**: Rules are indexed by rule_id and source
- **Connection Pooling**: SQLAlchemy handles database connection pooling
- **Async Processing**: FastAPI provides async request handling
- **Caching**: Consider Redis for frequently accessed rules (not implemented in MVP)

## 🔮 Future Enhancements

- Redis caching for improved performance
- Batch validation endpoints
- Webhook notifications for validation results
- Advanced rule logic interpreter
- Multi-language rule support
- Audit trail for validation history

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section above
- Review API documentation at `/docs`
- Check logs for detailed error messages