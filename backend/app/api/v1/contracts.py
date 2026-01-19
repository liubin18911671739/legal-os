"""
Contract Analysis API Routes

This module provides API endpoints for contract analysis using a multi-agent system.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import asyncio

from app.agents import (
    create_contract_analysis_graph,
    create_initial_state,
    ContractType,
)
from app.task_storage import (
    Task as StorageTask,
    TaskStatus,
    TaskType,
    create_task,
    get_task,
    update_task,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/contracts", tags=["Contracts"])


class ContractAnalysisRequest(BaseModel):
    """Request model for contract analysis"""
    
    contract_id: str = Field(..., description="Contract document ID")
    contract_text: str = Field(..., description="Contract text content")
    contract_type: str = Field(..., description="Contract type (employment, sales, etc.)")
    user_query: Optional[str] = Field(None, description="Optional user query")


class ContractAnalysisResponse(BaseModel):
    """Response model for contract analysis"""
    
    task_id: str = Field(..., description="Task ID for tracking")
    status: TaskStatus = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class AnalysisResult(BaseModel):
    """Contract analysis result"""
    
    task_id: str
    contract_id: str
    contract_type: str
    task_status: TaskStatus
    agent_history: List[str]
    analysis_confidence: float
    overall_risk: str
    validation_confidence: float
    final_answer: str
    report: Optional[Dict[str, Any]]


@router.post("/analyze", response_model=ContractAnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_contract(request: ContractAnalysisRequest) -> ContractAnalysisResponse:
    """Submit contract for analysis"""
    try:
        # Validate contract type
        try:
            contract_type_enum = ContractType(request.contract_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid contract type: {request.contract_type}",
            )
        
        # Create task
        task_id = generate_task_id()
        task = StorageTask(
            id=task_id,
            type=TaskType.CONTRACT_ANALYSIS,
            status=TaskStatus.PENDING,
            input_data={
                "contract_id": request.contract_id,
                "contract_text": request.contract_text,
                "contract_type": request.contract_type,
                "user_query": request.user_query,
            },
        )
        await create_task(task)
        
        logger.info(f"Created analysis task: {task_id}")
        
        # Start analysis in background
        asyncio.create_task(run_analysis_task(task_id, request, contract_type_enum))
        
        return ContractAnalysisResponse(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            message="Contract analysis started",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start contract analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}",
        )


@router.get("/analysis/{task_id}", response_model=AnalysisResult)
async def get_analysis_result(task_id: str) -> AnalysisResult:
    """Get contract analysis result"""
    try:
        task = await get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )
        
        # Check if task is complete
        if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return AnalysisResult(
                task_id=task.id,
                contract_id=task.input_data.get("contract_id", ""),
                contract_type=task.input_data.get("contract_type", ""),
                task_status=task.status,
                agent_history=[],
                analysis_confidence=0.0,
                overall_risk="unknown",
                validation_confidence=0.0,
                final_answer="",
                report=None,
            )
        
        # Return full result
        output_data = task.output_data or {}
        
        return AnalysisResult(
            task_id=task.id,
            contract_id=task.input_data.get("contract_id", ""),
            contract_type=task.input_data.get("contract_type", ""),
            task_status=task.status,
            agent_history=output_data.get("agent_history", []),
            analysis_confidence=output_data.get("analysis_confidence", 0.0),
            overall_risk=output_data.get("overall_risk", "unknown"),
            validation_confidence=output_data.get("validation_confidence", 0.0),
            final_answer=output_data.get("final_answer", ""),
            report=output_data.get("report"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get result: {str(e)}",
        )


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status (for polling)"""
    task = await get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return {
        "task_id": task.id,
        "status": task.status,
        "input_data": task.input_data,
        "output_data": task.output_data,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


async def run_analysis_task(
    task_id: str,
    request: ContractAnalysisRequest,
    contract_type: ContractType,
) -> None:
    """Run contract analysis workflow"""
    try:
        # Update task status to processing
        await update_task(task_id, status=TaskStatus.PROCESSING)
        
        # Create workflow graph
        graph = create_contract_analysis_graph()
        
        # Initialize state
        state = create_initial_state(
            contract_id=request.contract_id,
            contract_text=request.contract_text,
            contract_type=contract_type,
            user_query=request.user_query,
        )
        
        # Execute workflow
        logger.info(f"Starting analysis workflow for task: {task_id}")
        result = await graph.ainvoke(state)
        
        # Prepare output data
        output_data = {
            "agent_history": [str(agent) for agent in result.get("agent_history", [])],
            "analysis_confidence": result.get("analysis_confidence", 0.0),
            "overall_risk": str(result.get("review_result", {}).get("overall_risk", "unknown")),
            "validation_confidence": result.get("validation_result", {}).get("overall_confidence", 0.0),
            "final_answer": result.get("final_answer", ""),
            "report": result.get("report"),
            "error_message": result.get("error_message"),
        }
        
        # Update task with results
        await update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            output_data=output_data,
            result=output_data.get("final_answer", ""),
        )
        
        logger.info(f"Analysis completed for task: {task_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for task {task_id}: {e}", exc_info=True)
        
        # Update task with error
        await update_task(
            task_id,
            status=TaskStatus.FAILED,
            error_message=str(e),
        )


def generate_task_id() -> str:
    """Generate a simple task ID"""
    import uuid
    import time
    
    timestamp = int(time.time())
    short_uuid = str(uuid.uuid4())[:8]
    return f"TASK-{timestamp}-{short_uuid}"
