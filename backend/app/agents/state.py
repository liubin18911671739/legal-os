"""
Agent state definition for multi-agent RAG system

This module defines the shared state that flows between all agents
in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class AgentStatus(str, Enum):
    """Agent execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContractType(str, Enum):
    """Contract type enum"""
    EMPLOYMENT = "employment"
    SALES = "sales"
    SERVICE = "service"
    PARTNERSHIP = "partnership"
    PROCUREMENT = "procurement"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk level enum"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkflowNodes(str, Enum):
    """Workflow node names for LangGraph"""
    COORDINATOR = "coordinator"
    RETRIEVAL = "retrieval"
    ANALYSIS = "analysis"
    REVIEW = "review"
    VALIDATION = "validation"
    REPORT = "report"
    ERROR_HANDLER = "error_handler"


class AgentState(TypedDict):
    """Main agent state that flows between all nodes in graph"""
    
    # Input data
    contract_id: Optional[str]
    contract_text: Optional[str]
    contract_type: Optional[ContractType]
    user_query: Optional[str]
    session_id: Optional[str]
    
    # Task information
    task_id: Optional[str]
    task_status: TaskStatus
    current_agent: Optional[str]
    agent_history: List[str]
    
    # Coordinator outputs
    execution_plan: Optional[List[Dict[str, Any]]]
    agent_sequence: Optional[List[str]]
    
    # Retrieval outputs
    query_rewrites: Optional[List[str]]
    retrieved_docs: Optional[List[Dict[str, Any]]]
    retrieval_count: int
    retrieval_success: bool
    
    # Analysis outputs
    analysis_result: Optional[Dict[str, Any]]
    entities: Optional[Dict[str, Any]]
    clause_classifications: Optional[List[Dict[str, Any]]]
    analysis_confidence: float
    analysis_agent_status: AgentStatus
    
    # Review outputs
    review_result: Optional[Dict[str, Any]]
    compliance_issues: Optional[List[Dict[str, Any]]]
    risk_assessments: Optional[List[Dict[str, Any]]]
    suggestions: Optional[List[str]]
    review_agent_status: AgentStatus
    
    # Validation outputs
    validation_result: Optional[Dict[str, Any]]
    hallucination_score: float
    citation_accuracy: float
    cross_validation_passed: bool
    validation_agent_status: AgentStatus
    
    # Report outputs
    report: Optional[Dict[str, Any]]
    report_format: Optional[str]
    risk_matrix: Optional[Dict[str, Any]]
    export_formats: Optional[List[str]]
    report_agent_status: AgentStatus
    
    # Error handling
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    requires_human_intervention: bool
    intervention_reason: Optional[str]
    
    # Final output
    final_answer: Optional[str]
    final_sources: Optional[List[Dict[str, Any]]]
    execution_time: Optional[float]


def create_initial_state(
    contract_id: str,
    contract_text: str,
    contract_type: ContractType,
    user_query: Optional[str] = None,
    session_id: Optional[str] = None,
) -> AgentState:
    """Create initial state for contract analysis
    
    Args:
        contract_id: Contract document ID
        contract_text: Contract text content
        contract_type: Type of contract
        user_query: Optional user query for Q&A
        session_id: Optional session ID for tracing
    
    Returns:
        Initialized AgentState
    """
    return {
        "contract_id": contract_id,
        "contract_text": contract_text,
        "contract_type": contract_type,
        "user_query": user_query,
        "session_id": session_id,
        
        # Task information
        "task_id": contract_id,
        "task_status": TaskStatus.PENDING,
        "current_agent": None,
        "agent_history": [],
        
        # Coordinator outputs
        "execution_plan": None,
        "agent_sequence": None,
        
        # Retrieval outputs
        "query_rewrites": None,
        "retrieved_docs": None,
        "retrieval_count": 0,
        "retrieval_success": False,
        
        # Analysis outputs
        "analysis_result": None,
        "entities": None,
        "clause_classifications": None,
        "analysis_confidence": 0.0,
        "analysis_agent_status": AgentStatus.PENDING,
        
        # Review outputs
        "review_result": None,
        "compliance_issues": None,
        "risk_assessments": None,
        "suggestions": None,
        "review_agent_status": AgentStatus.PENDING,
        
        # Validation outputs
        "validation_result": None,
        "hallucination_score": 0.0,
        "citation_accuracy": 0.0,
        "cross_validation_passed": False,
        "validation_agent_status": AgentStatus.PENDING,
        
        # Report outputs
        "report": None,
        "report_format": None,
        "risk_matrix": None,
        "export_formats": None,
        "report_agent_status": AgentStatus.PENDING,
        
        # Error handling
        "error_message": None,
        "retry_count": 0,
        "max_retries": 3,
        "requires_human_intervention": False,
        "intervention_reason": None,
        
        # Final output
        "final_answer": None,
        "final_sources": None,
        "execution_time": None,
    }


def should_continue(state: AgentState) -> str:
    """Decide whether to continue or stop based on state
    
    Args:
        state: Current agent state
    
    Returns:
        "continue" or "stop"
    """
    # Check if we need human intervention
    if state["requires_human_intervention"]:
        return "stop"
    
    # Check if we've reached max retries
    if state["retry_count"] >= state["max_retries"]:
        return "stop"
    
    # Check if we have a final answer
    if state["final_answer"] and state["task_status"] == TaskStatus.COMPLETED:
        return "stop"
    
    # Continue if task is still pending or processing
    if state["task_status"] in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
        return "continue"
    
    # Stop if task failed
    if state["task_status"] == TaskStatus.FAILED:
        return "stop"
    
    # Otherwise continue
    return "continue"
