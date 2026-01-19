"""
Review Agent - Compliance checking and risk assessment

This agent reviews contracts against company templates and regulations,
checking for compliance issues and assessing risks.
"""

import logging
from typing import Dict, Any
from .state import AgentState, TaskStatus, AgentStatus, WorkflowNodes, RiskLevel
from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)


REVIEW_SYSTEM_PROMPT = """
你是一个合同审查智能体。你的任务是：

1. 对照公司模板和法规检查合同
2. 识别合规性问题
3. 评估风险等级
4. 提供修改建议

审查维度：
- 强制条款检查: 必须包含的条款是否存在
- 合规性验证: 是否违反相关法律法规
- 风险评估: 条款是否存在潜在风险
- 修改建议: 如何改进合同

风险等级：
- 高风险 (high): 可能导致重大损失或法律后果
- 中风险 (medium): 需要注意和改进
- 低风险 (low): 轻微问题或建议性改进

请以 JSON 格式返回审查结果。
"""


@trace_function(name="review_node")
async def review_node(state: AgentState) -> AgentState:
    """Review agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with review results
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id", "unknown")
    
    logger.info("Review agent started")
    
    with span_manager.trace_agent_execution(
        agent_name="review",
        session_id=session_id,
        metadata={
            "contract_type": state.get("contract_type"),
            "contract_text_length": len(state.get("contract_text", "")),
        }
    ):
        try:
            contract_text = state.get("contract_text", "")
            contract_type = state.get("contract_type", "other")
            entities = state.get("entities", {})
            clause_classifications = state.get("clause_classifications", [])
            
            # TODO: Implement actual compliance checking using company templates and regulations
            # For now, return mock review results
            
            # Mock compliance issues
            compliance_issues = [
                {
                    "category": "mandatory_clauses",
                    "issue": "缺少争议解决条款",
                    "severity": "high",
                    "description": "劳动合同应包含争议解决方式",
                    "location": "全文",
                    "reference": "劳动合同法第7条",
                },
                {
                    "category": "mandatory_clauses",
                    "issue": "缺少工作内容描述",
                    "severity": "medium",
                    "description": "应明确工作岗位和工作内容",
                    "location": "第2条",
                    "reference": "公司劳动合同模板",
                },
                {
                    "category": "compliance",
                    "issue": "试用期期限不符合规定",
                    "severity": "high",
                    "description": "三年期合同试用期不应超过6个月",
                    "location": "第3条",
                    "reference": "劳动合同法第19条",
                },
            ]
            
            # Mock risk assessments
            risk_assessments = [
                {
                    "risk_type": "legal_risk",
                    "description": "缺乏争议解决条款可能导致纠纷难以解决",
                    "level": RiskLevel.HIGH,
                    "probability": 0.8,
                    "impact": "high",
                    "mitigation": "增加争议解决条款，明确仲裁或诉讼管辖",
                },
                {
                    "risk_type": "operational_risk",
                    "description": "工作内容不明确可能导致职责不清",
                    "level": RiskLevel.MEDIUM,
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "详细描述工作内容和岗位要求",
                },
                {
                    "risk_type": "compliance_risk",
                    "description": "试用期期限可能违反劳动法规定",
                    "level": RiskLevel.HIGH,
                    "probability": 0.9,
                    "impact": "high",
                    "mitigation": "调整试用期期限至法定范围内",
                },
            ]
            
            # Generate suggestions
            suggestions = [
                "增加争议解决条款，明确仲裁机构或管辖法院",
                "完善工作内容描述，明确岗位职责和考核标准",
                "调整试用期期限至6个月以内",
                "增加保密条款，保护商业秘密",
                "完善违约责任条款，明确违约情形和赔偿标准",
            ]
            
            # Calculate overall risk level
            high_risk_count = sum(1 for r in risk_assessments if r["level"] == RiskLevel.HIGH)
            medium_risk_count = sum(1 for r in risk_assessments if r["level"] == RiskLevel.MEDIUM)
            
            if high_risk_count >= 2:
                overall_risk = RiskLevel.HIGH
            elif high_risk_count >= 1 or medium_risk_count >= 2:
                overall_risk = RiskLevel.MEDIUM
            else:
                overall_risk = RiskLevel.LOW
            
            # Create review result
            review_result = {
                "compliance_issues": compliance_issues,
                "risk_assessments": risk_assessments,
                "suggestions": suggestions,
                "overall_risk": overall_risk,
                "issue_count": len(compliance_issues),
                "risk_count": len(risk_assessments),
                "suggestion_count": len(suggestions),
                "summary": f"发现 {len(compliance_issues)} 个合规性问题，{len(risk_assessments)} 个风险，总体风险等级：{overall_risk.value}",
            }
            
            # Update state
            state["agent_history"].append(WorkflowNodes.REVIEW)
            state["current_agent"] = WorkflowNodes.REVIEW
            state["review_result"] = review_result
            state["compliance_issues"] = compliance_issues
            state["risk_assessments"] = risk_assessments
            state["suggestions"] = suggestions
            state["review_agent_status"] = AgentStatus.COMPLETED
            
            logger.info(f"Review agent completed, found {len(compliance_issues)} compliance issues and {len(risk_assessments)} risks")
            logger.info(f"Overall risk level: {overall_risk.value}")

            return state

        except Exception as e:
            logger.error(f"Review agent failed: {e}", exc_info=True)
            state["error_message"] = f"审查失败: {str(e)}"
            state["review_agent_status"] = AgentStatus.FAILED
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state
