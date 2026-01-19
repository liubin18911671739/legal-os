"""
Retrieval Agent - Document retrieval with query enhancement

This agent retrieves relevant documents and regulations
using the RAG system with query rewriting.
"""

import logging
from typing import Dict, Any
from .state import AgentState, TaskStatus, WorkflowNodes
from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)


RETRIEVAL_SYSTEM_PROMPT = """
你是一个文档检索智能体。你的任务是：

1. 理解用户的查询
2. 重写查询以提高检索效果
3. 使用 RAG 系统检索相关文档
4. 返回最相关的文档片段

检索策略：
- 识别查询中的关键概念
- 扩展同义词和相关术语
- 结合上下文优化查询
- 优先检索相关法规和类似合同

返回格式应为包含文档内容、来源和相关性分数的 JSON。
"""


@trace_function(name="retrieval_node")
async def retrieval_node(state: AgentState) -> AgentState:
    """Retrieval agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with retrieved documents
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id", "unknown")
    
    logger.info("Retrieval agent started")
    
    with span_manager.trace_agent_execution(
        agent_name="retrieval",
        session_id=session_id,
        metadata={
            "query": state.get("user_query", ""),
            "contract_type": state.get("contract_type"),
        }
    ):
        try:
            # TODO: Implement actual retrieval with RAG system
            # For now, return mock results
            
            query = state.get("user_query", "")
            
            # Mock retrieval results
            if query:
                retrieved_docs = [
                    {
                        "content": f"关于{query}的相关条款内容...",
                        "document_id": f"doc_{i}",
                        "score": 0.9 - (i * 0.05),
                        "source": f"regulation_{i + 1}",
                        "metadata": {
                            "section": f"第{i + 1}条",
                            "document_type": "regulation",
                        }
                    }
                    for i in range(5)
                ]
                retrieval_count = len(retrieved_docs)
                retrieval_success = True
            else:
                # Full contract analysis - retrieve regulations and similar contracts
                retrieved_docs = [
                    {
                        "content": f"劳动合同相关条款示例 {i}",
                        "document_id": f"regulation_{i}",
                        "score": 0.85,
                        "source": "knowledge_base",
                        "metadata": {
                            "type": "regulation",
                        }
                    }
                    for i in range(10)
                ] + [
                    {
                        "content": f"相似合同条款 {i}",
                        "document_id": f"contract_{i}",
                        "score": 0.8,
                        "source": "document_database",
                        "metadata": {
                            "type": "similar_contract",
                        }
                    }
                    for i in range(5)
                ]
                retrieval_count = len(retrieved_docs)
                retrieval_success = True
            
            # Update state
            state["agent_history"].append(WorkflowNodes.RETRIEVAL)
            state["current_agent"] = WorkflowNodes.RETRIEVAL
            state["retrieved_docs"] = retrieved_docs
            state["retrieval_count"] = state.get("retrieval_count", 0) + retrieval_count
            state["retrieval_success"] = retrieval_success
            
            logger.info(f"Retrieval agent completed, retrieved {retrieval_count} documents")

            return state

        except Exception as e:
            logger.error(f"Retrieval agent failed: {e}", exc_info=True)
            state["error_message"] = f"检索失败: {str(e)}"
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state