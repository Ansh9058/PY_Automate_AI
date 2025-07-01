from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
from core.config import settings
from typing import Dict, List, Any, Optional
import sys
import logging
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Try to import required modules
try:
    import cv2
    import pytesseract
    from PIL import Image
    import numpy as np
    from pdf2image import convert_from_path
except ImportError as e:
    logger.error(f"Missing required module: {str(e)}")
    logger.error("Please install required packages using: pip install opencv-python-headless pytesseract pillow numpy pdf2image")

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/")
async def root():
    return {
        "message": "Welcome to PyAutomate AI",
        "version": "1.0.0",
        "status": "operational"
    }

# RPA Endpoints
class WebAutomationTask(BaseModel):
    url: str
    selectors: Dict[str, str]

class ProductScrapingTask(BaseModel):
    url: str
    selectors: Dict[str, str] = {
        'product_container': '.product',                # Product card
        'title': '.product-title',                     # Title
        'price': '.product-price',                     # Price
        'image': '.product-image img',                 # Image
        'description': '.product-description'          # Description
    }

@app.post("/api/v1/rpa/web-scrape")
async def web_scrape(task: WebAutomationTask):
    """
    Scrape data from a website using provided selectors
    """
    try:
        # Lazy import
        from rpa.web_automation import WebAutomation
        
        automation = WebAutomation(headless=True)
        automation.navigate(task.url)
        data = automation.extract_data(task.selectors)
        automation.close()
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rpa/scrape-products")
async def scrape_products(task: ProductScrapingTask):
    """
    Scrape product information from an e-commerce website
    
    Example request:
    {
        "url": "https://www.amazon.com/s?k=laptop",
        "selectors": {
            "product_container": "div[data-component-type=\"s-search-result\"]",
            "title": "h2 a span",
            "price": ".a-price .a-offscreen",
            "image": "img.s-image",
            "description": ".a-size-base"
        }
    }
    """
    try:
        # Validate URL
        if not task.url.startswith('http'):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
            
        # Lazy import
        from rpa.web_automation import WebAutomation
        
        automation = WebAutomation(headless=True)
        automation.navigate(task.url)
        products = automation.extract_products(task.selectors)
        automation.close()
        
        return JSONResponse(content={
            "status": "success",
            "count": len(products),
            "products": products
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document Processing Endpoints
@app.post("/api/v1/documents/process")
async def process_document(file: UploadFile = File(...)):
    """
    Process a document (image/PDF) and extract text and structured data
    """
    file_path = None
    try:
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file temporarily
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            try:
                # Import here to catch import errors
                from ai.document_processor import DocumentProcessor
                
                # Process the document
                processor = DocumentProcessor()
                
                # Check if it's a PDF
                if file.filename.lower().endswith('.pdf'):
                    result = processor.process_pdf(file_path)
                    return {
                        "status": "success",
                        "text": result['text'],
                        "structured_data": result['structured_data']
                    }
                else:
                    # Process as image
                    text = processor.extract_text(file_path)
                    structured_data = processor.extract_structured_data(file_path)
                    return {
                        "status": "success",
                        "text": text,
                        "structured_data": structured_data
                    }
            except ImportError as e:
                logger.error(f"Import error: {str(e)}")
                missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
                installation_cmd = f"pip install {missing_module}"
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": f"Missing required module: {missing_module}. Please install it using: {installation_cmd}"
                    }
                )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Endpoints
class WorkflowRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    initial_data: Dict[str, Any]

@app.post("/api/v1/workflows/create")
async def create_workflow(workflow: WorkflowRequest):
    """
    Create a new workflow
    """
    try:
        # Lazy import
        from workflows.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        workflow_id = engine.create_workflow(workflow.name, workflow.steps)
        return {"status": "success", "workflow_id": workflow_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the current status of a workflow"""
    try:
        # Lazy import
        from workflows.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        status = engine.get_workflow_status(workflow_id)
        return {"status": "success", "workflow": status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, execution: WorkflowExecutionRequest):
    """Execute a workflow with initial data"""
    try:
        # Lazy import
        from workflows.workflow_engine import WorkflowEngine
        
        engine = WorkflowEngine()
        results = engine.execute_workflow(workflow_id, execution.initial_data)
        return {"status": "success", "results": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Test endpoint is working"}

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )
