import requests
import json
import time

def test_workflow_management():
    # URL of the workflow management endpoint
    base_url = "http://127.0.0.1:8080/api/v1/workflows"
    
    # Create a new workflow
    print("Creating a new workflow...")
    workflow_data = {
        "name": "Data Processing Workflow",
        "steps": [
            {
                "name": "Step 1: Data Collection",
                "action": "collect_data",
                "input": {
                    "source": "web",
                    "url": "https://example.com/data"
                }
            },
            {
                "name": "Step 2: Data Processing",
                "action": "process_data",
                "input": {
                    "format": "json",
                    "filters": ["clean", "validate"]
                }
            },
            {
                "name": "Step 3: Data Storage",
                "action": "store_data",
                "input": {
                    "location": "database",
                    "table": "processed_data"
                }
            }
        ]
    }
    
    try:
        # Create workflow
        response = requests.post(f"{base_url}/create", json=workflow_data)
        print("\nStatus Code:", response.status_code)
        
        if response.status_code == 200:
            result = response.json()
            workflow_id = result.get("workflow_id")
            print(f"Workflow created with ID: {workflow_id}")
            
            # Check workflow status
            print("\nChecking workflow status...")
            status_response = requests.get(f"{base_url}/{workflow_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json()
                print("\nWorkflow Status:")
                print(json.dumps(status, indent=2))
                
                # Execute workflow
                print("\nExecuting workflow...")
                execution_data = {
                    "initial_data": {
                        "source_url": "https://example.com/data",
                        "processing_options": {
                            "format": "json",
                            "compress": True,
                            "validate": True
                        },
                        "storage_options": {
                            "database": "main_db",
                            "table": "processed_data"
                        }
                    }
                }
                
                execution_response = requests.post(
                    f"{base_url}/{workflow_id}/execute",
                    json=execution_data
                )
                
                if execution_response.status_code == 200:
                    execution_result = execution_response.json()
                    print("\nExecution Results:")
                    print(json.dumps(execution_result, indent=2))
                    
                    # Check if any steps failed
                    if any(result.get('status') == 'error' for result in execution_result.get('results', [])):
                        print("\nWorkflow execution completed with errors.")
                    else:
                        print("\nWorkflow executed successfully!")
                else:
                    print("Error executing workflow:", execution_response.text)
            else:
                print("Error checking workflow status:", status_response.text)
        else:
            print("Error creating workflow:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the FastAPI server is running.")
        print("Run 'python main.py' in a separate terminal to start the server.")
    except Exception as e:
        print("\nError:", str(e))

if __name__ == "__main__":
    test_workflow_management() 