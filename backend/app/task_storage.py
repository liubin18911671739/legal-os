"""
Simple in-memory task storage for contract analysis

This module provides a simple in-memory storage for tasks
until a proper database integration is implemented.
"""

import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    """Task type enum"""
    CONTRACT_ANALYSIS = "contract_analysis"
    RAG_QUERY = "rag_query"
    DOCUMENT_UPLOAD = "document_upload"


@dataclass
class Task:
    """Task data model"""
    
    id: str
    type: TaskType
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# In-memory storage
_tasks: Dict[str, Task] = {}


async def create_task(task: Task) -> Task:
    """Create a new task
    
    Args:
        task: Task to create
    
    Returns:
        Created task
    """
    _tasks[task.id] = task
    logger.info(f"Created task: {task.id}")
    return task


async def get_task(task_id: str) -> Optional[Task]:
    """Get task by ID
    
    Args:
        task_id: Task ID
    
    Returns:
        Task if found, None otherwise
    """
    return _tasks.get(task_id)


async def update_task(task_id: str, **kwargs) -> Optional[Task]:
    """Update task
    
    Args:
        task_id: Task ID
        **kwargs: Fields to update
    
    Returns:
        Updated task if found, None otherwise
    """
    if task_id not in _tasks:
        return None
    
    task = _tasks[task_id]
    
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    
    logger.info(f"Updated task: {task_id}")
    return task


async def list_tasks(limit: int = 100) -> List[Task]:
    """List all tasks
    
    Args:
        limit: Maximum number of tasks to return
    
    Returns:
        List of tasks
    """
    tasks = list(_tasks.values())
    
    # Sort by created_at (newest first)
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    return tasks[:limit]


async def delete_task(task_id: str) -> bool:
    """Delete task
    
    Args:
        task_id: Task ID
    
    Returns:
        True if deleted, False if not found
    """
    if task_id not in _tasks:
        return False
    
    del _tasks[task_id]
    logger.info(f"Deleted task: {task_id}")
    return True


def get_task_count() -> int:
    """Get total number of tasks
    
    Returns:
        Number of tasks
    """
    return len(_tasks)


def generate_task_id() -> str:
    """Generate a simple task ID"""
    import uuid
    import time
    
    timestamp = int(time.time())
    short_uuid = str(uuid.uuid4())[:8]
    return f"TASK-{timestamp}-{short_uuid}"
