import openai
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMClassifier:
    """
    LLM service for classifying rules and assisting with validation
    """

    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o-mini"

    def classify_rule(self, rule_text: str, rule_id: str) -> Dict[str, Any]:
        """
        Classify a rule as codable or AI-assisted and generate logic if codable
        """
        prompt = f"""
        You are an expert in ICC trade finance rules. Analyze the following rule and classify it.

        Rule ID: {rule_id}
        Rule Text: {rule_text}

        Classify this rule as either:
        1. "codable" - Can be checked deterministically with code (dates, amounts, currencies, document presence, etc.)
        2. "ai_assisted" - Requires human judgment or AI interpretation (content quality, authenticity, compliance nuances)

        If codable, provide pseudo-code logic using variables like:
        - expiry_date, shipment_date, presentation_date
        - amount, currency
        - documents (array of document types)
        - beneficiary, applicant

        Respond in JSON format:
        {{
            "type": "codable" or "ai_assisted",
            "reasoning": "Brief explanation of classification",
            "logic": "pseudo-code if codable, null if ai_assisted"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in ICC trade finance rules and document validation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            # Fallback classification
            return {
                "type": "ai_assisted",
                "reasoning": f"Error in classification: {str(e)}",
                "logic": None
            }

    def validate_with_ai(self, rule_text: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to validate a document against a rule that requires human judgment
        """
        prompt = f"""
        You are validating a Letter of Credit document against ICC rules.

        Rule: {rule_text}

        Document Data: {json.dumps(document_data, indent=2)}

        Evaluate if the document complies with this rule. Consider:
        - Does the document content meet the rule requirements?
        - Are there any discrepancies or issues?
        - What is your confidence level?

        Respond in JSON format:
        {{
            "status": "pass", "fail", or "warning",
            "details": "Specific explanation of compliance or discrepancies",
            "confidence_score": "high", "medium", or "low"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert trade finance document examiner following ICC rules strictly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "status": "warning",
                "details": f"AI validation error: {str(e)}",
                "confidence_score": "low"
            }

    def explain_rule(self, rule_text: str) -> str:
        """
        Generate a plain-English explanation of a rule
        """
        prompt = f"""
        Explain this ICC trade finance rule in simple, clear language:

        {rule_text}

        Provide a concise explanation that a non-expert could understand.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a trade finance expert who explains complex rules in simple terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def batch_classify_rules(self, rules: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Classify multiple rules in batch for efficiency
        """
        classified_rules = []

        for rule in rules:
            classification = self.classify_rule(rule["text"], rule["rule_id"])

            # Update rule with classification results
            rule["type"] = classification["type"]
            rule["logic"] = classification.get("logic")

            classified_rules.append(rule)

        return classified_rules

    def test_connection(self) -> bool:
        """
        Test if OpenAI API connection is working
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False