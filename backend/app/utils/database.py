from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any
from uuid import UUID

from app.models import (
    Document,
    Contract,
    AnalysisResult,
    Task,
    KnowledgeChunk,
)
from app.schemas import (
    DocumentCreate,
    DocumentUpdate,
    ContractCreate,
    ContractUpdate,
    TaskCreate,
    TaskUpdate,
)
from app.models.document import DocumentStatus
from app.models.task import TaskStatus
import uuid


ModelType = TypeVar("ModelType")


async def create_document(
    db: AsyncSession,
    document_in: DocumentCreate,
) -> Document:
    """Create a new document."""
    document = Document(**document_in.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_document_by_id(
    db: AsyncSession,
    document_id: UUID,
) -> Optional[Document]:
    """Get document by ID."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def update_document_status(
    db: AsyncSession,
    document_id: UUID,
    status: DocumentStatus,
) -> Optional[Document]:
    """Update document status."""
    document = await get_document_by_id(db, document_id)
    if document:
        document.status = status
        await db.commit()
        await db.refresh(document)
    return document


async def get_documents(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Document]:
    """Get paginated documents."""
    result = await db.execute(
        select(Document)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def count_documents(db: AsyncSession) -> int:
    """Count total documents."""
    result = await db.execute(select(func.count()).select_from(Document))
    return result.scalar()


async def create_contract(
    db: AsyncSession,
    contract_in: ContractCreate,
) -> Contract:
    """Create a new contract."""
    contract = Contract(**contract_in.model_dump())
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract


async def get_contract_by_id(
    db: AsyncSession,
    contract_id: UUID,
) -> Optional[Contract]:
    """Get contract by ID."""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    task_in: TaskCreate,
) -> Task:
    """Create a new task."""
    task = Task(**task_in.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_progress(
    db: AsyncSession,
    task_id: UUID,
    progress: int,
    current_stage: Optional[str] = None,
) -> Optional[Task]:
    """Update task progress."""
    task = await get_task_by_id(db, task_id)
    if task:
        task.progress = progress
        if current_stage:
            task.current_stage = current_stage
        await db.commit()
        await db.refresh(task)
    return task


async def get_task_by_id(
    db: AsyncSession,
    task_id: UUID,
) -> Optional[Task]:
    """Get task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Task]:
    """Get paginated tasks."""
    result = await db.execute(
        select(Task)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_analysis_result(
    db: AsyncSession,
    contract_id: UUID,
    **kwargs,
) -> AnalysisResult:
    """Create a new analysis result."""
    analysis_result = AnalysisResult(contract_id=contract_id, **kwargs)
    db.add(analysis_result)
    await db.commit()
    await db.refresh(analysis_result)
    return analysis_result


async def get_analysis_result_by_contract_id(
    db: AsyncSession,
    contract_id: UUID,
) -> Optional[AnalysisResult]:
    """Get analysis result by contract ID."""
    result = await db.execute(
        select(AnalysisResult)
        .where(AnalysisResult.contract_id == contract_id)
        .order_by(AnalysisResult.created_at.desc())
    )
    return result.scalar_one_or_none()
