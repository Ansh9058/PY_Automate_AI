from typing import Dict, List, Any, Callable
import logging
from datetime import datetime
from uuid import uuid4
from celery import Celery
from core.config import settings
import json
import os

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('workflows', broker=settings.REDIS_URL)

# Create workflows directory if it doesn't exist
WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'workflows')
os.makedirs(WORKFLOWS_DIR, exist_ok=True)

class WorkflowStep:
    def __init__(self, name: str, action: str, input_schema: Dict = None):
        self.name = name
        self.action = action
        self.input_schema = input_schema or {}
        
    def to_dict(self):
        return {
            'name': self.name,
            'action': self.action,
            'input_schema': self.input_schema
        }
        
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data['name'],
            action=data['action'],
            input_schema=data.get('input_schema', {})
        )

class WorkflowEngine:
    def __init__(self):
        """Initialize the workflow engine."""
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self._load_workflows()
        
    def _load_workflows(self):
        """Load all workflows from disk."""
        for filename in os.listdir(WORKFLOWS_DIR):
            if filename.endswith('.json'):
                workflow_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(WORKFLOWS_DIR, filename), 'r') as f:
                        data = json.load(f)
                        self.workflows[workflow_id] = [
                            WorkflowStep.from_dict(step) for step in data['steps']
                        ]
                except Exception as e:
                    logger.error(f"Error loading workflow {workflow_id}: {str(e)}")
        
    def _save_workflow(self, workflow_id: str, steps: List[WorkflowStep]):
        """Save workflow to disk."""
        try:
            data = {
                'steps': [step.to_dict() for step in steps]
            }
            with open(os.path.join(WORKFLOWS_DIR, f"{workflow_id}.json"), 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving workflow {workflow_id}: {str(e)}")
        
    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> str:
        """Create a new workflow."""
        workflow_id = str(uuid4())
        workflow_steps = [WorkflowStep.from_dict(step) for step in steps]
        self.workflows[workflow_id] = workflow_steps
        self._save_workflow(workflow_id, workflow_steps)
        logger.info(f"Created new workflow: {name} (ID: {workflow_id})")
        return workflow_id
        
    def add_step(self, workflow_id: str, step: WorkflowStep) -> None:
        """Add a step to an existing workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} does not exist")
        
        self.workflows[workflow_id].append(step)
        self._save_workflow(workflow_id, self.workflows[workflow_id])
        logger.info(f"Added step {step.name} to workflow {workflow_id}")
        
    def _execute_step(self, step: WorkflowStep, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            # Here you would implement the actual step execution logic
            # For now, we'll just simulate it
            result = {
                'status': 'success',
                'message': f"Executed {step.action} with input {input_data}",
                'timestamp': datetime.utcnow().isoformat()
            }
            return result
        except Exception as e:
            logger.error(f"Error executing step {step.name}: {str(e)}")
            return {
                'status': 'error',
                'step_name': step.name,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            
    def execute_workflow(self, workflow_id: str, initial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all steps in a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} does not exist")
            
        results = []
        current_data = initial_data
        
        for step in self.workflows[workflow_id]:
            try:
                # Execute step synchronously
                result = self._execute_step(step, current_data)
                results.append(result)
                
                if result['status'] == 'error':
                    logger.error(f"Workflow {workflow_id} failed at step {step.name}")
                    break
                    
                # Update data for next step
                if 'result' in result:
                    current_data.update(result['result'])
                    
            except Exception as e:
                logger.error(f"Error in workflow {workflow_id} at step {step.name}: {str(e)}")
                results.append({
                    'status': 'error',
                    'step_name': step.name,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
                break
                
        return results
        
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} does not exist")
            
        return {
            'workflow_id': workflow_id,
            'total_steps': len(self.workflows[workflow_id]),
            'steps': [step.to_dict() for step in self.workflows[workflow_id]]
        }
