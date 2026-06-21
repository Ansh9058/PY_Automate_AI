from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["Task Monitoring"])


@router.get("/{task_id}/status")
def get_task_status(task_id: str):
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Mock task status (Celery not enabled)",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/{task_id}/result")
def get_task_result(task_id: str):
    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "result": {"message": "Mock result"},
    }