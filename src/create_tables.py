from src.core.database import engine
from src.core.models import WorkflowRun, WorkflowStepRun

if __name__ == "__main__":
    print("Creating database tables...")
    WorkflowRun.metadata.create_all(bind=engine)
    WorkflowStepRun.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
