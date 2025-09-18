from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Rule, RuleType
from app.schemas import rule as rule_schemas
from app.services.pdf_parser import PDFParser
from app.services.llm_classifier import LLMClassifier

router = APIRouter(prefix="/rules", tags=["rules"])

@router.post("/upload", response_model=rule_schemas.RuleUploadResponse)
async def upload_pdf_rules(
    file: UploadFile = File(...),
    source: str = Query(..., description="Rule source (e.g., UCP600, ISBP)"),
    db: Session = Depends(get_db)
):
    """
    Upload PDF and extract rules, classify them, and store in database
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Read PDF content
        pdf_content = await file.read()

        # Initialize services
        pdf_parser = PDFParser()
        llm_classifier = LLMClassifier()

        # Validate PDF
        if not pdf_parser.validate_pdf_content(pdf_content):
            raise HTTPException(status_code=400, detail="Invalid PDF file")

        # Parse rules from PDF
        parsed_rules = pdf_parser.parse_pdf_file(pdf_content, source)

        if not parsed_rules:
            raise HTTPException(status_code=400, detail="No rules found in PDF")

        # Classify rules using LLM
        classified_rules = llm_classifier.batch_classify_rules(parsed_rules)

        # Store rules in database
        created_rules = []
        for rule_data in classified_rules:
            # Check if rule already exists
            existing_rule = db.query(Rule).filter(Rule.rule_id == rule_data["rule_id"]).first()
            if existing_rule:
                continue  # Skip duplicates

            # Map string type to enum
            rule_type = RuleType.CODABLE if rule_data["type"] == "codable" else RuleType.AI_ASSISTED

            new_rule = Rule(
                rule_id=rule_data["rule_id"],
                source=rule_data["source"],
                article=rule_data["article"],
                title=rule_data.get("title"),
                text=rule_data["text"],
                type=rule_type,
                logic=rule_data.get("logic"),
                version=rule_data.get("version", "1.0")
            )

            db.add(new_rule)
            created_rules.append(new_rule)

        db.commit()

        # Convert to response schema
        rule_responses = [rule_schemas.Rule.from_orm(rule) for rule in created_rules]

        return rule_schemas.RuleUploadResponse(
            message=f"Successfully processed {len(created_rules)} rules from {file.filename}",
            rules_created=len(created_rules),
            rules=rule_responses
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/", response_model=List[rule_schemas.Rule])
async def get_rules(
    source: Optional[str] = Query(None, description="Filter by rule source"),
    domain: Optional[str] = Query(None, description="Filter by domain (e.g., LC for Letter of Credit)"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type (codable/ai_assisted)"),
    skip: int = Query(0, ge=0, description="Number of rules to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of rules to return"),
    db: Session = Depends(get_db)
):
    """
    Get rules with optional filtering
    """
    query = db.query(Rule)

    # Apply filters
    if source:
        query = query.filter(Rule.source == source)

    if domain == "LC":
        # Letter of Credit domain includes UCP600, ISBP, eUCP
        query = query.filter(Rule.source.in_(["UCP600", "ISBP", "eUCP"]))

    if rule_type:
        if rule_type == "codable":
            query = query.filter(Rule.type == RuleType.CODABLE)
        elif rule_type == "ai_assisted":
            query = query.filter(Rule.type == RuleType.AI_ASSISTED)

    # Apply pagination
    rules = query.offset(skip).limit(limit).all()

    return [rule_schemas.Rule.from_orm(rule) for rule in rules]

@router.get("/{rule_id}", response_model=rule_schemas.Rule)
async def get_rule(rule_id: str, db: Session = Depends(get_db)):
    """
    Get a specific rule by ID
    """
    rule = db.query(Rule).filter(Rule.rule_id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return rule_schemas.Rule.from_orm(rule)

@router.put("/{rule_id}", response_model=rule_schemas.Rule)
async def update_rule(
    rule_id: str,
    rule_update: rule_schemas.RuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific rule
    """
    rule = db.query(Rule).filter(Rule.rule_id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Update fields if provided
    update_data = rule_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "type" and value:
            # Convert string to enum
            value = RuleType.CODABLE if value == "codable" else RuleType.AI_ASSISTED
        setattr(rule, field, value)

    try:
        db.commit()
        db.refresh(rule)
        return rule_schemas.Rule.from_orm(rule)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific rule
    """
    rule = db.query(Rule).filter(Rule.rule_id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    try:
        db.delete(rule)
        db.commit()
        return {"message": f"Rule {rule_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting rule: {str(e)}")

@router.get("/{rule_id}/explain")
async def explain_rule(rule_id: str, db: Session = Depends(get_db)):
    """
    Get plain-English explanation of a rule
    """
    rule = db.query(Rule).filter(Rule.rule_id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    try:
        llm_classifier = LLMClassifier()
        explanation = llm_classifier.explain_rule(rule.text)

        return {
            "rule_id": rule.rule_id,
            "rule_text": rule.text,
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")