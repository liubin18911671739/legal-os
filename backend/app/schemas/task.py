from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.task import TaskType, TaskStatus
import uuid


class TaskBase(BaseModel):
    """Base task schema."""
    task_type: TaskType
    input_data: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    status: Optional[TaskStatus] = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    status: Optional[TaskStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    current_stage: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: uuid.UUID
    task_type: TaskType
    status: TaskStatus
    progress: int
    current_stage: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
