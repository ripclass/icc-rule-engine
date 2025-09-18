import PyPDF2
import re
from typing import List, Dict, Any
from io import BytesIO

class PDFParser:
    """
    PDF parser service using PyMuPDF to extract and structure rules from ICC documents
    """

    def __init__(self):
        self.article_patterns = [
            r'^Article\s+(\d+[a-z]?)\s*[-–—]?\s*(.*?)$',  # Article 14a - Title
            r'^(\d+[a-z]?)\.\s+(.*?)$',  # 14a. Title
            r'^UCP\s*(\d+[a-z]?)\s*[-–—]?\s*(.*?)$',  # UCP 14a - Title
        ]

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract raw text from PDF bytes
        """
        try:
            pdf_stream = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)

            full_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                full_text += text + "\n"

            return full_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def parse_rules_from_text(self, text: str, source: str = "Unknown") -> List[Dict[str, Any]]:
        """
        Parse rules from extracted text, identifying articles and sections
        """
        rules = []
        lines = text.split('\n')
        current_article = None
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line matches an article pattern
            article_match = self._match_article_pattern(line)

            if article_match:
                # Save previous article if exists
                if current_article and current_text:
                    rules.append(self._create_rule_dict(
                        source, current_article, current_text
                    ))

                # Start new article
                current_article = article_match
                current_text = []
            else:
                # Add to current article text
                if current_article:
                    current_text.append(line)

        # Don't forget the last article
        if current_article and current_text:
            rules.append(self._create_rule_dict(
                source, current_article, current_text
            ))

        return rules

    def _match_article_pattern(self, line: str) -> Dict[str, str] | None:
        """
        Check if line matches any article pattern and extract article info
        """
        for pattern in self.article_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return {
                    "article": match.group(1),
                    "title": match.group(2).strip() if len(match.groups()) > 1 else ""
                }
        return None

    def _create_rule_dict(self, source: str, article_info: Dict[str, str], text_lines: List[str]) -> Dict[str, Any]:
        """
        Create a structured rule dictionary
        """
        article = article_info["article"]
        title = article_info["title"]
        full_text = " ".join(text_lines).strip()

        # Generate rule ID
        rule_id = f"{source.upper()}-{article}"

        return {
            "rule_id": rule_id,
            "source": source,
            "article": article,
            "title": title if title else None,
            "text": full_text,
            "type": "ai_assisted",  # Default type, will be classified by LLM
            "logic": None,
            "version": "1.0"
        }

    def parse_pdf_file(self, pdf_content: bytes, source: str) -> List[Dict[str, Any]]:
        """
        Main method to parse PDF and return structured rules
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_content)

        # Parse rules from text
        rules = self.parse_rules_from_text(text, source)

        return rules

    def validate_pdf_content(self, pdf_content: bytes) -> bool:
        """
        Validate that the uploaded content is a valid PDF
        """
        try:
            pdf_stream = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            return len(pdf_reader.pages) > 0
        except:
            return False