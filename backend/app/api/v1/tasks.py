from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.utils.database import get_task_by_id, get_tasks, create_task, update_task_progress

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task_endpoint(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    try:
        task = await create_task(db, task_in)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a task by ID."""
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with pagination."""
    skip = (page - 1) * size
    tasks = await get_tasks(db, skip=skip, limit=size)
    return tasks


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    return task
