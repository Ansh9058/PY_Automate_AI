import re
import json
from typing import Dict, List

# OPTIONAL LLM (safe import)
try:
    from ai.llm_client import LLMClient
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


class DocumentAIParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.text_lower = self.text.lower()

    # ==================================================
    # COMMON UTILITIES
    # ==================================================
    def extract_email(self) -> str:
        match = re.search(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            self.text
        )
        return match.group(0) if match else ""

    def extract_phone(self) -> str:
        match = re.search(r"(\+?\d{1,3}[\s-]?)?\d{10}", self.text)
        return match.group(0) if match else ""

    def extract_dates(self) -> List[str]:
        return re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", self.text)

    # ==================================================
    # DOCUMENT TYPE DETECTION (CORE LOGIC)
    # ==================================================
    def detect_document_type(self) -> str:
        if any(k in self.text_lower for k in ["experience", "education", "skills", "resume"]):
            return "resume"

        if any(k in self.text_lower for k in ["invoice", "gst", "total amount", "bill"]):
            return "invoice"

        if any(k in self.text_lower for k in ["certificate", "certify", "issued"]):
            return "certificate"

        return "generic"

    # ==================================================
    # RESUME EXTRACTION (RULE-BASED)
    # ==================================================
    def extract_resume(self) -> Dict:
        skills_db = [
            "Python", "FastAPI", "Django", "Flask", "Selenium",
            "SQL", "MongoDB", "AWS", "Docker", "Git",
            "Machine Learning", "NLP"
        ]

        name = self.lines[0] if self.lines else "Unknown"

        skills = [
            skill for skill in skills_db
            if skill.lower() in self.text_lower
        ]

        return {
            "document_type": "resume",
            "name": name,
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "skills": skills,
            "confidence": 0.75
        }

    # ==================================================
    # INVOICE EXTRACTION
    # ==================================================
    def extract_invoice(self) -> Dict:
        amount_match = re.search(
            r"(total|amount)\s*[:₹$]*\s*([\d,]+\.\d{2})",
            self.text,
            re.I,
        )

        return {
            "document_type": "invoice",
            "invoice_reference": self._find_keyword_value("invoice"),
            "total_amount": amount_match.group(2) if amount_match else "",
            "dates": self.extract_dates(),
            "email": self.extract_email(),
            "confidence": 0.7
        }

    # ==================================================
    # GENERIC KEY-VALUE EXTRACTION
    # ==================================================
    def extract_key_values(self) -> Dict:
        data = {}
        for line in self.lines:
            if ":" in line:
                key, value = line.split(":", 1)
                if len(key) < 40:
                    data[key.strip()] = value.strip()
        return {
            "document_type": "generic",
            "fields": data,
            "confidence": 0.6
        }

    # ==================================================
    # SUMMARY
    # ==================================================
    def extract_summary(self) -> str:
        return " ".join(self.lines[:5])

    # ==================================================
    # LLM-BASED SEMANTIC EXTRACTION (OPTIONAL)
    # ==================================================
    def extract_llm(self, command: str) -> Dict:
        if not LLM_AVAILABLE:
            return {
                "error": "LLM not configured",
                "fallback": self.run(command.replace("_llm", ""))
            }

        prompt = f"""
        You are an AI document understanding engine.
        Task: {command}
        Extract structured JSON only.

        TEXT:
        {self.text[:6000]}
        """

        response = LLMClient.ask(prompt)
        return self._safe_json(response)

    # ==================================================
    # HELPERS
    # ==================================================
    def _find_keyword_value(self, keyword: str) -> str:
        for line in self.lines:
            if keyword.lower() in line.lower():
                return line
        return ""

    def _safe_json(self, text: str) -> Dict:
        try:
            return json.loads(text)
        except Exception:
            return {"raw_output": text}

    # ==================================================
    # COMMAND ROUTER (FINAL BRAIN)
    # ==================================================
    def run(self, command: str) -> Dict:
        command = command.lower()

        # 🔥 LLM COMMANDS
        if command.endswith("_llm"):
            return self.extract_llm(command)

        # 🔹 EXPLICIT COMMANDS
        if command == "extract_resume":
            return self.extract_resume()

        if command == "extract_invoice":
            return self.extract_invoice()

        if command == "extract_key_values":
            return self.extract_key_values()

        if command == "extract_summary":
            return {"summary": self.extract_summary()}

        # 🔹 AUTO-DETECTION FALLBACK
        doc_type = self.detect_document_type()

        if doc_type == "resume":
            return self.extract_resume()

        if doc_type == "invoice":
            return self.extract_invoice()

        return {
            "document_type": "generic",
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "summary": self.extract_summary(),
            "confidence": 0.5
        }
