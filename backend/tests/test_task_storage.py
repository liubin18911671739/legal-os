"""
Simple tests for contract analysis API components
"""
import pytest
from app.task_storage import (
    Task,
    TaskStatus,
    TaskType,
    create_task,
    get_task,
    update_task,
    generate_task_id,
)


@pytest.mark.asyncio
async def test_task_storage():
    """Test task storage operations"""
    # Create task
    task_id = generate_task_id()
    task = Task(
        id=task_id,
        type=TaskType.CONTRACT_ANALYSIS,
        status=TaskStatus.PENDING,
        input_data={"test": "data"},
    )
    
    created = await create_task(task)
    assert created.id == task_id
    
    # Get task
    retrieved = await get_task(task_id)
    assert retrieved is not None
    assert retrieved.id == task_id
    assert retrieved.status == TaskStatus.PENDING
    
    # Update task
    updated = await update_task(task_id, status=TaskStatus.PROCESSING)
    assert updated.status == TaskStatus.PROCESSING
    
    print("✅ Task storage test passed")


def test_generate_task_id():
    """Test task ID generation"""
    task_id1 = generate_task_id()
    task_id2 = generate_task_id()
    
    assert task_id1.startswith("TASK-")
    assert task_id2.startswith("TASK-")
    assert task_id1 != task_id2
    
    print("✅ Task ID generation test passed")


if __name__ == "__main__":
    import asyncio
    
    print("Running task storage tests...\n")
    
    asyncio.run(test_task_storage())
    test_generate_task_id()
    
    print("\n✅ All storage tests passed!")
