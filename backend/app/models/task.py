from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class TaskType(str, enum.Enum):
    """Task types."""
    DOCUMENT_UPLOAD = "document_upload"
    CONTRACT_ANALYSIS = "contract_analysis"
    RAG_SEARCH = "rag_search"
    REPORT_GENERATION = "report_generation"


class TaskStatus(str, enum.Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Task model for async processing."""
    
    __tablename__ = "tasks"
    
    task_type = Column(
        Enum(TaskType),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        index=True,
    )
    progress = Column(Integer, default=0)
    current_stage = Column(String(100), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Task(id={self.id}, type='{self.task_type}', status='{self.status}', progress={self.progress})>"
