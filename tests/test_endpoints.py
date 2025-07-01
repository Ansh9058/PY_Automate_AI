import requests
import json
from pathlib import Path

# Base URL of our API
BASE_URL = "http://127.0.0.1:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("\n1. Testing Root Endpoint:")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_web_scraping():
    """Test the web scraping endpoint"""
    print("\n2. Testing Web Scraping Endpoint:")
    
    # Data for web scraping
    data = {
        "url": "https://example.com",
        "selectors": {
            "title": "h1",
            "paragraph": "p"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/rpa/web-scrape",
        json=data
    )
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_document_processing():
    """Test the document processing endpoint"""
    print("\n3. Testing Document Processing Endpoint:")
    
    # Create a sample text file for testing
    test_file_path = Path("test_document.txt")
    test_file_path.write_text("This is a test document for OCR processing.")
    
    # Upload the file
    with open(test_file_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/api/v1/documents/process",
            files={"file": f}
        )
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Clean up
    test_file_path.unlink()

def test_workflow():
    """Test workflow creation and status endpoints"""
    print("\n4. Testing Workflow Endpoints:")
    
    # Create a workflow
    workflow_data = {
        "name": "Test Workflow",
        "steps": [
            {
                "name": "Extract Text",
                "action": "document_processing",
                "input": {"file": "test.pdf"}
            }
        ]
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/v1/workflows/create",
        json=workflow_data
    )
    print("Create Workflow Response:")
    print(json.dumps(create_response.json(), indent=2))
    
    # Get workflow status
    if create_response.status_code == 200:
        workflow_id = create_response.json()["workflow_id"]
        status_response = requests.get(
            f"{BASE_URL}/api/v1/workflows/{workflow_id}/status"
        )
        print("\nWorkflow Status Response:")
        print(json.dumps(status_response.json(), indent=2))

if __name__ == "__main__":
    print("Testing PyAutomate AI API Endpoints")
    print("=" * 50)
    
    try:
        # Test all endpoints
        test_root_endpoint()
        test_web_scraping()
        test_document_processing()
        test_workflow()
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server.")
        print("Make sure the server is running at http://127.0.0.1:8000")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
