"""
WebSocket endpoints for real-time task updates.

This module provides WebSocket connections for streaming task progress updates.
"""

import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.task_storage import get_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/tasks/{task_id}/stream")
async def stream_task_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming task progress updates.

    This endpoint establishes a WebSocket connection and streams
    real-time updates for a specific task.
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for task: {task_id}")

    try:
        # Send initial task status
        task = await get_task(task_id)
        if task:
            await websocket.send_json({
                "type": "task_update",
                "task_id": task_id,
                "status": task.status.value if hasattr(task.status, 'value') else task.status,
                "progress": task.progress,
                "current_stage": task.input_data.get("current_stage") if task.input_data else None,
                "agent_history": task.input_data.get("agent_history", []) if task.input_data else [],
                "error_message": task.error_message,
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Task {task_id} not found",
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Keep connection alive and send updates
        # Note: In a production environment, you would use a proper
        # notification system (e.g., Redis Pub/Sub) instead of polling
        import asyncio

        while True:
            await asyncio.sleep(2)  # Poll every 2 seconds

            # Get latest task status
            task = await get_task(task_id)
            if task:
                # Send update
                await websocket.send_json({
                    "type": "task_update",
                    "task_id": task_id,
                    "status": task.status.value if hasattr(task.status, 'value') else task.status,
                    "progress": task.progress,
                    "current_stage": task.input_data.get("current_stage") if task.input_data else None,
                    "agent_history": task.input_data.get("agent_history", []) if task.input_data else [],
                    "error_message": task.error_message,
                })

                # Check if task is complete or failed
                if task.status in ["completed", "failed", "cancelled"]:
                    logger.info(f"Task {task_id} reached terminal state: {task.status}")
                    await websocket.send_json({
                        "type": "task_complete",
                        "task_id": task_id,
                        "status": task.status.value if hasattr(task.status, 'value') else task.status,
                    })
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task: {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
            })
        except:
            pass  # Connection might already be closed
    finally:
        try:
            await websocket.close()
        except:
            pass
