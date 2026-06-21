import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import spacy

nlp = spacy.load("en_core_web_sm")


class AIDocumentExtractor:
    def extract_text_from_image(self, image_path: str) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        pages = convert_from_path(pdf_path)
        full_text = ""
        for page in pages:
            full_text += pytesseract.image_to_string(page)
        return full_text

    def classify_document(self, text: str) -> str:
        text_lower = text.lower()
        if "invoice" in text_lower:
            return "Invoice"
        if "resume" in text_lower or "curriculum vitae" in text_lower:
            return "Resume"
        if "receipt" in text_lower:
            return "Receipt"
        return "Generic Document"

    def extract_entities(self, text: str):
        doc = nlp(text)
        entities = {}
        for ent in doc.ents:
            entities.setdefault(ent.label_, []).append(ent.text)
        return entities

    def extract_key_fields(self, text: str):
        fields = {}

        invoice_no = re.search(r"invoice\s*no[:\-]?\s*(\w+)", text, re.I)
        total = re.search(r"total\s*[:\-]?\s*₹?\$?\s*([\d,.]+)", text, re.I)
        date = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)

        if invoice_no:
            fields["invoice_number"] = invoice_no.group(1)
        if total:
            fields["total_amount"] = total.group(1)
        if date:
            fields["date"] = date.group(1)

        return fields

    def process_document(self, file_path: str):
        if file_path.lower().endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)

        return {
            "document_type": self.classify_document(text),
            "text": text[:5000],  # limit output
            "entities": self.extract_entities(text),
            "key_fields": self.extract_key_fields(text),
        }
