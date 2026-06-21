from fastapi import APIRouter, UploadFile, File, Query
import tempfile
import os

router = APIRouter(
    prefix="/document-ai",
    tags=["Document AI"]
)

# Dummy processor (safe fallback)
from PyPDF2 import PdfReader

def simple_extract(file_path: str, command: str):
    extracted_text = ""

    try:
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""

        else:
            extracted_text = "Unsupported file type for real extraction"

    except Exception as e:
        extracted_text = f"Error reading file: {str(e)}"

    return {
        "file": os.path.basename(file_path),
        "type": "document",
        "command": command,
        "extracted_text": extracted_text[:1000],  # limit for demo
        "summary": extracted_text[:200] if extracted_text else "No text found",
        "status": "processed"
    }


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    command: str = Query("extract_summary")
):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, file.filename)

        with open(path, "wb") as f:
            f.write(await file.read())

        result = simple_extract(path, command)

        return {
            "status": "success",
            "result": result
        }