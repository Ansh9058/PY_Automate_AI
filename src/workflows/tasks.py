from core.celery_app import celery_app
from src.workflows.workflow_engine import WorkflowEngine
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def execute_workflow_task(self, workflow_id: str, initial_data: dict):
    """
    Celery task to execute workflow asynchronously
    """
    try:
        logger.info(f"Starting workflow {workflow_id}")

        engine = WorkflowEngine()
        results = engine.execute_workflow(workflow_id, initial_data)

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "results": results
        }

    except Exception as e:
        logger.exception("Workflow execution failed")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
