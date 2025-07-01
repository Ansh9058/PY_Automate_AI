import cv2
import pytesseract
import numpy as np
from typing import Dict, List, Any
import logging
from pathlib import Path
import os
from pdf2image import convert_from_path
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract path
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Tesseract-OCR\tesseract.exe'
]

# Try to find Tesseract installation
tesseract_found = False
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        break

if not tesseract_found:
    raise ImportError("Tesseract not found. Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki")

# Configure Poppler path
POPPLER_PATH = os.path.join(os.path.expanduser("~"), "poppler", "bin")
if not os.path.exists(POPPLER_PATH):
    os.makedirs(POPPLER_PATH, exist_ok=True)
    logger.warning(f"Poppler directory created at {POPPLER_PATH}. Please extract Poppler files here.")

# Verify Poppler installation
POPPLER_EXE = os.path.join(POPPLER_PATH, "pdftoppm.exe")
if not os.path.exists(POPPLER_EXE):
    raise ImportError(f"Poppler not found at {POPPLER_PATH}. Please install Poppler from https://github.com/oschwartz10612/poppler-windows/releases/")

logger.info(f"Using Poppler from: {POPPLER_PATH}")

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with OCR and preprocessing capabilities."""
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Apply dilation to connect text components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            gray = cv2.dilate(gray, kernel, iterations=1)
            
            return gray
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
            
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a PDF file and extract text from all pages."""
        try:
            # Create a temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy the PDF to the temporary directory
                temp_pdf_path = os.path.join(temp_dir, os.path.basename(pdf_path))
                shutil.copy2(pdf_path, temp_pdf_path)
                
                logger.info(f"Processing PDF: {pdf_path}")
                logger.info(f"Using Poppler from: {POPPLER_PATH}")
                
                # Convert PDF to images
                images = convert_from_path(
                    temp_pdf_path,
                    poppler_path=POPPLER_PATH,
                    dpi=300,
                    fmt='png'
                )
                
                all_text = []
                all_structured_data = []
                
                # Process each page
                for i, image in enumerate(images):
                    # Save the image temporarily
                    temp_image_path = os.path.join(temp_dir, f"page_{i+1}.png")
                    image.save(temp_image_path, 'PNG')
                    
                    try:
                        # Extract text from the page
                        page_text = self.extract_text(temp_image_path)
                        all_text.append(f"Page {i+1}:\n{page_text}")
                        
                        # Extract structured data from the page
                        page_data = self.extract_structured_data(temp_image_path)
                        all_structured_data.append({
                            'page': i+1,
                            'data': page_data
                        })
                    except Exception as e:
                        logger.error(f"Error processing page {i+1}: {str(e)}")
                        continue
            
            return {
                'text': '\n\n'.join(all_text),
                'structured_data': all_structured_data
            }
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
            
    def extract_text(self, image_path: str) -> str:
        """Extract text from document using OCR."""
        try:
            # Read image using opencv
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image)
            
            logger.info(f"Successfully extracted text from {image_path}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {str(e)}")
            raise
            
    def extract_structured_data(self, image_path: str) -> Dict[str, Any]:
        """Extract structured data (tables, key-value pairs) from document."""
        try:
            # Read image using opencv
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Extract structured data using pytesseract
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Process the extracted data
            structured_data = {
                'text_blocks': [],
                'confidence_scores': [],
                'bounding_boxes': []
            }
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60:  # Filter by confidence score
                    text = data['text'][i].strip()
                    if text:
                        structured_data['text_blocks'].append(text)
                        structured_data['confidence_scores'].append(data['conf'][i])
                        structured_data['bounding_boxes'].append({
                            'left': data['left'][i],
                            'top': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        })
            
            logger.info(f"Successfully extracted structured data from {image_path}")
            return structured_data
        except Exception as e:
            logger.error(f"Error extracting structured data from {image_path}: {str(e)}")
            raise
            
    def batch_process(self, directory: str) -> List[Dict[str, Any]]:
        """Process multiple documents in a directory."""
        try:
            results = []
            directory_path = Path(directory)
            
            for file_path in directory_path.glob('*'):
                if file_path.suffix.lower() in self.supported_formats:
                    result = {
                        'file_name': file_path.name,
                        'text': self.extract_text(str(file_path)),
                        'structured_data': self.extract_structured_data(str(file_path))
                    }
                    results.append(result)
                    
            logger.info(f"Successfully processed {len(results)} documents in {directory}")
            return results
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise
