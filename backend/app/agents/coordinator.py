"""
Coordinator Agent - Task decomposition and routing

This agent analyzes the user's request, identifies the contract type,
and creates an execution plan for other agents.
"""

import logging
from typing import Dict, Any, List, Optional
from .state import AgentState, ContractType, TaskStatus, AgentStatus, WorkflowNodes
from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)

# System prompt for coordinator
COORDINATOR_SYSTEM_PROMPT = """
你是一个合同分析系统的协调智能体。你的任务是：

1. 理解用户的查询或请求
2. 识别合同类型
3. 制定执行计划
4. 路由到合适的智能体

合同类型包括：
- employment (劳动合同)
- sales (销售合同)
- service (服务合同)
- partnership (合作合同)
- procurement (采购合同)
- other (其他类型)

执行计划应包括需要执行的智能体序列，按优先级排列。

根据查询内容，选择最合适的智能体：
- 简单查询 → 直接检索
- 复杂分析 → 检索 + 分析 + 审查 + 验证 + 报告
- 仅信息查询 → 检索

请以 JSON 格式返回你的分析和计划。
"""


@trace_function(name="coordinator_node")
async def coordinator_node(state: AgentState) -> AgentState:
    """Coordinator agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with coordinator's decisions
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id") or "unknown"
    
    logger.info("Coordinator agent started")
    logger.info(f"Contract type: {state.get('contract_type')}")
    logger.info(f"User query: {state.get('user_query')}")
    
    with span_manager.trace_agent_execution(
        agent_name="coordinator",
        session_id=session_id,
        metadata={
            "contract_type": state.get("contract_type"),
            "user_query_length": len(state.get("user_query") or ""),
            "contract_text_length": len(state.get("contract_text") or ""),
        }
    ):
        try:
            # Determine task type based on user query
            user_query = state.get("user_query", "")
            contract_text = state.get("contract_text", "")
            
            # Analyze request and create execution plan
            if user_query:
                # User has a specific question - direct retrieval path
                execution_plan = [
                    {
                        "agent": "retrieval",
                        "purpose": "answer_user_query",
                        "description": f"回答用户问题: {user_query[:100]}...",
                    }
                ]
                agent_sequence = ["retrieval"]
                
                logger.info(f"Simple query detected, direct retrieval path")
            else:
                # Full contract analysis - full agent pipeline
                execution_plan = [
                    {
                        "agent": "coordinator",
                        "purpose": "analyze_contract",
                        "description": "分析合同类型和内容",
                    },
                    {
                        "agent": "retrieval",
                        "purpose": "retrieve_regulations",
                        "description": "检索相关法规和模板",
                    },
                    {
                        "agent": "retrieval",
                        "purpose": "retrieve_similar_clauses",
                        "description": "检索相似合同条款",
                    },
                    {
                        "agent": "analysis",
                        "purpose": "extract_entities",
                        "description": "提取实体和关键信息",
                    },
                    {
                        "agent": "analysis",
                        "purpose": "classify_clauses",
                        "description": "分类合同条款类型",
                    },
                    {
                        "agent": "review",
                        "purpose": "check_compliance",
                        "description": "检查合规性和风险",
                    },
                    {
                        "agent": "validation",
                        "purpose": "validate_results",
                        "description": "验证分析结果的准确性",
                    },
                    {
                        "agent": "report",
                        "purpose": "generate_report",
                        "description": "生成结构化报告",
                    },
                ]
                agent_sequence = [
                    "coordinator",
                    "retrieval",
                    "retrieval",
                    "analysis",
                    "review",
                    "validation",
                    "report",
                ]
                
                logger.info(f"Full analysis path with {len(execution_plan)} steps")
            
            # Identify contract type from text (simplified for now)
            # TODO: Implement contract type classification using LLM
            if not state.get("contract_type") and contract_text:
                # Default to OTHER for now
                logger.info("Contract type not specified, defaulting to OTHER")
                contract_type = ContractType.OTHER
            else:
                contract_type = state.get("contract_type", ContractType.OTHER)
            
            # Update state
            state["agent_history"].append(WorkflowNodes.COORDINATOR)
            state["current_agent"] = WorkflowNodes.COORDINATOR
            state["execution_plan"] = execution_plan
            state["agent_sequence"] = agent_sequence
            state["contract_type"] = contract_type
            state["task_status"] = TaskStatus.PROCESSING
            state["analysis_agent_status"] = AgentStatus.PENDING
            state["review_agent_status"] = AgentStatus.PENDING
            state["validation_agent_status"] = AgentStatus.PENDING
            state["report_agent_status"] = AgentStatus.PENDING
            state["retrieval_count"] = 0
            state["retrieval_success"] = False
            
            logger.info("Coordinator agent completed successfully")
            logger.info(f"Execution plan: {len(execution_plan)} agents")

            return state

        except Exception as e:
            logger.error(f"Coordinator agent failed: {e}", exc_info=True)
            state["error_message"] = f"协调失败: {str(e)}"
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state
