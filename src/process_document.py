import requests
import os
import sys

def process_document(file_path):
    """
    Process a document using the document processing API
    """
    # URL of the document processing endpoint
    url = "http://127.0.0.1:8080/api/v1/documents/process"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    try:
        # Open and send the file
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'application/octet-stream')
            }
            print(f"Processing document: {file_path}")
            response = requests.post(url, files=files)
            
            # Print the response
            print("\nStatus Code:", response.status_code)
            if response.status_code == 200:
                result = response.json()
                print("\nExtracted Text:")
                print("-" * 50)
                print(result.get('text', 'No text extracted'))
                print("\nStructured Data:")
                print("-" * 50)
                print(result.get('structured_data', 'No structured data extracted'))
            else:
                print("Error:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the FastAPI server is running.")
        print("Run 'python main.py' in a separate terminal to start the server.")
    except Exception as e:
        print("\nError:", str(e))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_document.py <path_to_document>")
        print("Example: python process_document.py my_document.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    process_document(file_path) 