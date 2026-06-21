from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from src.workflows.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["Workflow Engine"])

engine = WorkflowEngine()

# -----------------------------
# MODELS
# -----------------------------
class WorkflowCreateRequest(BaseModel):
    steps: List[Dict[str, Any]]


class WorkflowExecuteRequest(BaseModel):
    data: Dict[str, Any]


# -----------------------------
# CREATE WORKFLOW
# -----------------------------
@router.post("/create")
def create_workflow(request: WorkflowCreateRequest):
    workflow_id = engine.create_workflow(request.steps)
    return {"workflow_id": workflow_id}


# -----------------------------
# EXECUTE WORKFLOW
# -----------------------------
@router.post("/{workflow_id}/execute")
def execute_workflow(workflow_id: str, request: WorkflowExecuteRequest):
    try:
        return engine.execute_workflow(workflow_id, request.data)
    except Exception as e:
        raise HTTPException(400, str(e))