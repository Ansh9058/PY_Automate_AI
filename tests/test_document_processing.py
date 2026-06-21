import requests
import os
import sys
from PIL import Image, ImageDraw, ImageFont

def test_document_processing(filepath):
    # URL of the document processing endpoint
    url = "http://127.0.0.1:8080/api/v1/documents/process"

    # Open and send the file
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, 'application/octet-stream')}
        print(f"Sending request to process: {filepath}")
        response = requests.post(url, files=files)
        print("\nStatus Code:", response.status_code)
        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Error:", response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/test_document_processing.py <your_document_file>")
    else:
        test_document_processing(sys.argv[1])
