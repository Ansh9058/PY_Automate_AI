from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create a test image with text
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text to the image
    text = "This is a test document.\nCreated for OCR testing.\nIt should be readable by Tesseract."
    draw.text((50, 50), text, fill='black')
    
    # Save the image
    image_path = "test_document.png"
    img.save(image_path)
    print(f"Created test image at: {os.path.abspath(image_path)}")
    return image_path

if __name__ == "__main__":
    create_test_image() 