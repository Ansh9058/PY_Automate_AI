import requests
import os
from PIL import Image, ImageDraw, ImageFont
import io

def test_document_processing():
    # URL of the document processing endpoint
    url = "http://127.0.0.1:8080/api/v1/documents/process"
    
    # Create a test image file with text
    test_image_path = "test_document.png"
    
    # Create an image with white background
    img = Image.new('RGB', (800, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text to the image
    text = "This is a test document.\nCreated for OCR testing.\nIt should be readable by Tesseract."
    draw.text((50, 50), text, fill='black')
    
    # Save the image
    img.save(test_image_path)
    
    try:
        # Open and send the file
        with open(test_image_path, 'rb') as f:
            files = {
                'file': ('test_document.png', f, 'image/png')
            }
            print("Sending request to process the document...")
            response = requests.post(url, files=files)
            
            # Print the response
            print("\nStatus Code:", response.status_code)
            if response.status_code == 200:
                print("Response:", response.json())
            else:
                print("Error:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the FastAPI server is running.")
        print("Run 'python main.py' in a separate terminal to start the server.")
    except Exception as e:
        print("\nError:", str(e))
    finally:
        # Clean up
        try:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
        except Exception as e:
            print(f"Could not remove temporary file: {e}")

if __name__ == "__main__":
    test_document_processing() 