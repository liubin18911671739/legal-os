"""
LangGraph workflow orchestration for multi-agent RAG system

This module sets up LangGraph StateGraph and defines workflow
that orchestrates all agents for contract analysis.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
import logging

from .state import (
    AgentState,
    TaskStatus,
    AgentStatus,
    ContractType,
    RiskLevel,
    WorkflowNodes,
    create_initial_state,
    should_continue,
)

# Import agent nodes
from .coordinator import coordinator_node
from .retrieval import retrieval_node
from .analysis import analysis_node
from .review import review_node
from .validation import validation_node
from .report import report_node

from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)


@trace_function(name="create_contract_analysis_graph")
def create_contract_analysis_graph():
    """Create LangGraph StateGraph for contract analysis workflow

    Returns:
        Compiled StateGraph for contract analysis
    """
    # Create state graph
    graph = StateGraph(AgentState)

    # Add all agent nodes (use string names for LangGraph)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("review", review_node)
    graph.add_node("validation", validation_node)
    graph.add_node("report", report_node)

    # Define edges (sequential workflow flow)

    # Coordinator → Retrieval
    graph.set_entry_point("coordinator")
    graph.add_edge("coordinator", "retrieval")

    # Retrieval → Analysis
    graph.add_edge("retrieval", "analysis")

    # Analysis → Review
    graph.add_edge("analysis", "review")

    # Review → Validation
    graph.add_edge("review", "validation")

    # Validation → Report
    graph.add_edge("validation", "report")

    # Report → END
    graph.add_edge("report", "__end__")

    # Compile graph
    compiled_graph = graph.compile()

    logger.info("Contract analysis workflow graph created successfully")
    logger.info(f"Nodes: {list(graph.nodes)}")

    return compiled_graph


def get_workflow_info():
    """Get information about the workflow graph

    Returns:
        Dictionary with workflow details
    """
    return {
        "name": "Contract Analysis Multi-Agent Workflow",
        "version": "1.0.0",
        "nodes": [
            WorkflowNodes.COORDINATOR,
            WorkflowNodes.RETRIEVAL,
            WorkflowNodes.ANALYSIS,
            WorkflowNodes.REVIEW,
            WorkflowNodes.VALIDATION,
            WorkflowNodes.REPORT,
        ],
        "flow": [
            "coordinator",
            "retrieval",
            "analysis",
            "review",
            "validation",
            "report",
        ],
        "description": "Multi-agent system for automated contract analysis using LangGraph",
    }
