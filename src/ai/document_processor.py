import cv2
import pytesseract
import numpy as np
import logging
import os
import tempfile
import shutil
from typing import Dict, Any
from pdf2image import convert_from_path

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# TESSERACT CONFIG
# --------------------------------------------------
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break
else:
    raise ImportError("Tesseract OCR not found")

# --------------------------------------------------
# POPPLER CONFIG
# --------------------------------------------------
POPPLER_PATH = os.path.join(os.path.expanduser("~"), "poppler", "bin")
POPPLER_EXE = os.path.join(POPPLER_PATH, "pdftoppm.exe")

if not os.path.exists(POPPLER_EXE):
    raise ImportError("Poppler not found. Install poppler-windows.")

# --------------------------------------------------
# DOCUMENT PROCESSOR
# --------------------------------------------------
class DocumentProcessor:
    def __init__(self):
        self.supported_formats = [".pdf", ".png", ".jpg", ".jpeg"]

    # ---------------- IMAGE PREPROCESS ----------------
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return gray

    # ---------------- OCR TEXT ----------------
    def extract_text(self, image_path: str) -> str:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Invalid image file")

        processed = self.preprocess_image(image)
        text = pytesseract.image_to_string(processed)
        return text.strip()

    # ---------------- PDF PROCESSING ----------------
    def process_pdf(self, pdf_path: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pdf = os.path.join(tmp, "document.pdf")
            shutil.copy(pdf_path, tmp_pdf)

            images = convert_from_path(
                tmp_pdf,
                dpi=300,
                poppler_path=POPPLER_PATH,
            )

            pages_text = []
            for i, img in enumerate(images):
                img_path = os.path.join(tmp, f"page_{i}.png")
                img.save(img_path)
                pages_text.append(self.extract_text(img_path))

            return "\n".join(pages_text)

    # ==================================================
    # 🧠 AI ENTRY POINT (STEP-6)
    # ==================================================
    def extract_ai(self, file_path: str, command: str) -> Dict[str, Any]:
        if file_path.lower().endswith(".pdf"):
            text = self.process_pdf(file_path)
        else:
            text = self.extract_text(file_path)

        from ai.document_ai_parser import DocumentAIParser

        parser = DocumentAIParser(text)
        result = parser.run(command)

        return {
            "command": command,
            "result": result,
        }
