from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from src.core.database import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    workflow_id = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    input_data = Column(JSON)
    output_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    steps = relationship("WorkflowStepRun", back_populates="workflow_run")


class WorkflowStepRun(Base):
    __tablename__ = "workflow_step_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    workflow_run_id = Column(
        String, ForeignKey("workflow_runs.id"), nullable=False
    )
    step_name = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    input_data = Column(JSON)
    output_data = Column(JSON)
    error = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    workflow_run = relationship("WorkflowRun", back_populates="steps")
