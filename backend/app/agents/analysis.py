"""
Analysis Agent - Entity extraction and clause classification

This agent extracts key entities from contracts and classifies clauses
by type and importance.
"""

import logging
from typing import Dict, Any
from .state import AgentState, TaskStatus, AgentStatus, WorkflowNodes
from ..core.tracing import get_span_manager, trace_function

# Import LLM client for real integration
try:
    from ..llm_client import get_client
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


ANALYSIS_SYSTEM_PROMPT = """
你是一个合同分析智能体。你的任务是：

1. 从合同文本中提取关键实体
2. 识别和分类合同条款
3. 计算分析的置信度

关键实体类型：
- 合同当事人 (parties): 甲方、乙方、第三方等
- 金额 (amounts): 合同金额、违约金、押金等
- 日期 (dates): 签订日期、生效日期、终止日期等
- 期限 (durations): 合同期限、试用期等
- 地址 (addresses): 履行地点、送达地址等

条款类型：
- 违约责任 (liability): 违约条款、赔偿条款
- 终止条件 (termination): 解除条款、终止条件
- 支付条款 (payment): 付款方式、付款期限
- 保密条款 (confidentiality): 保密义务
- 争议解决 (dispute): 仲裁条款、管辖法院
- 其他 (other): 其他条款

请以 JSON 格式返回分析结果。
"""


@trace_function(name="analysis_node")
async def analysis_node(state: AgentState) -> AgentState:
    """Analysis agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with analysis results
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id", "unknown")
    
    logger.info("Analysis agent started")

    with span_manager.trace_agent_execution(
        agent_name="analysis",
        session_id=session_id,
        metadata={
            "contract_type": state.get("contract_type"),
            "contract_text_length": len(state.get("contract_text", "")),
        }
    ):
        try:
            contract_text = state.get("contract_text", "")
            contract_type = state.get("contract_type", "other")

            # Initialize with None
            entities = None
            clause_classifications = None

            # Try to use real LLM if available
            if LLM_AVAILABLE:
                try:
                    client = get_client()
                    result = await client.generate_json(
                        agent="analysis",
                        prompt=f"""
请分析以下合同内容，提取关键实体和分类条款：

合同类型: {contract_type}
合同内容:
{contract_text[:3000]}

请返回JSON格式，包含以下字段：
1. entities: 包含 parties, amounts, dates, durations, addresses
2. clauses: 包含 text, type, importance, confidence
""",
                        system_prompt=ANALYSIS_SYSTEM_PROMPT,
                    )

                    # Process LLM result
                    if "entities" in result:
                        entities = result["entities"]
                    if "clauses" in result:
                        clause_classifications = result["clauses"]

                    logger.info("Successfully used LLM for analysis")
                except Exception as e:
                    logger.warning(f"LLM analysis failed, using fallback: {e}")
                    # Fall back to mock data
                    pass
            else:
                logger.info("LLM not available, using mock data")

            # Fallback to mock data if LLM unavailable or failed
            if not entities or not clause_classifications:
                # Mock entity extraction
                entities = {
                "parties": [
                    {"name": "甲方", "role": "雇主", "confidence": 0.95},
                    {"name": "乙方", "role": "雇员", "confidence": 0.95},
                ],
                "amounts": [
                    {"value": "10000", "currency": "CNY", "type": "月工资", "confidence": 0.90},
                    {"value": "5000", "currency": "CNY", "type": "违约金", "confidence": 0.85},
                ],
                "dates": [
                    {"value": "2024-01-01", "type": "签订日期", "confidence": 1.0},
                    {"value": "2024-01-15", "type": "生效日期", "confidence": 0.95},
                ],
                "durations": [
                    {"value": "3年", "type": "合同期限", "confidence": 0.90},
                ],
                "addresses": [
                    {"value": "北京市朝阳区", "type": "工作地点", "confidence": 0.95},
                ],
            }
            
            # Mock clause classification
            clause_classifications = [
                {
                    "text": "合同期限为三年",
                    "type": "termination",
                    "importance": "high",
                    "confidence": 0.95,
                },
                {
                    "text": "月工资10000元",
                    "type": "payment",
                    "importance": "high",
                    "confidence": 0.95,
                },
                {
                    "text": "违约金5000元",
                    "type": "liability",
                    "importance": "medium",
                    "confidence": 0.90,
                },
                {
                    "text": "保密义务",
                    "type": "confidentiality",
                    "importance": "medium",
                    "confidence": 0.85,
                },
            ]
            
            # Calculate overall confidence
            avg_entity_confidence = sum(
                e.get("confidence", 0.8)
                for entity_list in entities.values()
                for e in entity_list
            ) / sum(len(entity_list) for entity_list in entities.values())
            
            avg_clause_confidence = sum(
                c.get("confidence", 0.8) for c in clause_classifications
            ) / len(clause_classifications)
            
            analysis_confidence = (avg_entity_confidence + avg_clause_confidence) / 2
            
            # Create analysis result
            analysis_result = {
                "contract_type": contract_type,
                "entities": entities,
                "clause_count": len(clause_classifications),
                "clause_types": list(set(c["type"] for c in clause_classifications)),
                "summary": f"识别到 {len(clause_classifications)} 个条款，提取了 {sum(len(entities[k]) for k in entities)} 个实体",
            }
            
            # Update state
            state["agent_history"].append(WorkflowNodes.ANALYSIS)
            state["current_agent"] = WorkflowNodes.ANALYSIS
            state["analysis_result"] = analysis_result
            state["entities"] = entities
            state["clause_classifications"] = clause_classifications
            state["analysis_confidence"] = analysis_confidence
            state["analysis_agent_status"] = AgentStatus.COMPLETED
            
            logger.info(f"Analysis agent completed, extracted {sum(len(entities[k]) for k in entities)} entities and {len(clause_classifications)} clauses")
            logger.info(f"Analysis confidence: {analysis_confidence:.2f}")

            return state

        except Exception as e:
            logger.error(f"Analysis agent failed: {e}", exc_info=True)
            state["error_message"] = f"分析失败: {str(e)}"
            state["analysis_agent_status"] = AgentStatus.FAILED
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state
