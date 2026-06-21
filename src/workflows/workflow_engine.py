from typing import Dict, List, Any
import logging
import json
import os
from uuid import uuid4

logger = logging.getLogger(__name__)

# -----------------------------
# STORAGE
# -----------------------------
WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(WORKFLOWS_DIR, exist_ok=True)


# -----------------------------
# WORKFLOW STEP
# -----------------------------
class WorkflowStep:
    def __init__(self, name: str, action: str):
        self.name = name
        self.action = action

    def to_dict(self):
        return {"name": self.name, "action": self.action}

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(name=data["name"], action=data["action"])


# -----------------------------
# WORKFLOW ENGINE
# -----------------------------
class WorkflowEngine:
    def __init__(self):
        self.workflows = {}

    def create_workflow(self, steps: List[Dict[str, Any]]) -> str:
        workflow_id = str(uuid4())

        self.workflows[workflow_id] = [
            WorkflowStep.from_dict(step) for step in steps
        ]

        return workflow_id

    def execute_workflow(self, workflow_id: str, data: Dict[str, Any]):
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        result = data

        for step in self.workflows[workflow_id]:
            if step.action == "log":
                logger.info(result)

            elif step.action == "uppercase":
                result = {k: str(v).upper() for k, v in result.items()}

            elif step.action == "add":
                result = {"sum": result.get("a", 0) + result.get("b", 0)}

            else:
                return {"error": f"Unknown action {step.action}"}

        return {"result": result}