"""
Validation Agent - Result verification and hallucination detection

This agent validates the analysis results from other agents,
checking for consistency, accuracy, and hallucinations.
"""

import logging
from typing import Dict, Any
from .state import AgentState, TaskStatus, AgentStatus, WorkflowNodes
from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)


VALIDATION_SYSTEM_PROMPT = """
你是一个结果验证智能体。你的任务是：

1. 检查多个智能体结果的一致性
2. 验证引用的准确性
3. 检测幻觉（无根据的陈述）
4. 计算整体置信度

验证维度：
- 多样本一致性: 不同智能体是否得出一致结论
- 引用准确性: 引用的法规和条款是否准确
- 幻觉检测: 检测无根据或错误的陈述
- 交叉验证: 检查分析结果之间的矛盾

置信度计算：
- 高置信度 (>0.8): 所有验证通过，结果可靠
- 中置信度 (0.6-0.8): 部分验证通过，需要确认
- 低置信度 (<0.6): 验证失败，结果不可靠

请以 JSON 格式返回验证结果。
"""


@trace_function(name="validation_node")
async def validation_node(state: AgentState) -> AgentState:
    """Validation agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with validation results
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id", "unknown")
    
    logger.info("Validation agent started")
    
    with span_manager.trace_agent_execution(
        agent_name="validation",
        session_id=session_id,
        metadata={
            "contract_type": state.get("contract_type"),
        }
    ):
        try:
            analysis_result = state.get("analysis_result", {})
            review_result = state.get("review_result", {})
            retrieved_docs = state.get("retrieved_docs", [])
            
            # TODO: Implement actual validation with LLM
            # For now, return mock validation results
            
            # Mock consistency checks
            consistency_checks = [
                {
                    "check": "实体一致性",
                    "status": "passed",
                    "description": "分析智能体和审查智能体识别的实体一致",
                    "details": {
                        "analysis_entities": 8,
                        "review_entities": 8,
                        "matched": 8,
                    },
                },
                {
                    "check": "条款分类一致性",
                    "status": "passed",
                    "description": "条款分类结果一致",
                    "details": {
                        "analysis_clauses": 4,
                        "review_clauses": 4,
                        "matched": 4,
                    },
                },
                {
                    "check": "风险等级一致性",
                    "status": "warning",
                    "description": "分析智能体未评估风险，审查智能体评估为高风险",
                    "details": {
                        "analysis_risk": None,
                        "review_risk": "high",
                    },
                },
            ]
            
            # Mock citation accuracy checks
            citation_checks = [
                {
                    "citation": "劳动合同法第7条",
                    "accuracy": 0.95,
                    "context": "争议解决条款",
                    "status": "accurate",
                },
                {
                    "citation": "劳动合同法第19条",
                    "accuracy": 0.98,
                    "context": "试用期期限",
                    "status": "accurate",
                },
                {
                    "citation": "公司劳动合同模板",
                    "accuracy": 1.0,
                    "context": "工作内容描述",
                    "status": "accurate",
                },
            ]
            
            # Calculate citation accuracy
            citation_accuracy = sum(
                check["accuracy"] for check in citation_checks
            ) / len(citation_checks)
            
            # Mock hallucination detection
            hallucination_checks = [
                {
                    "claim": "合同期限为三年",
                    "evidence": "合同第1条明确约定",
                    "supported": True,
                    "confidence": 1.0,
                },
                {
                    "claim": "月工资10000元",
                    "evidence": "合同第4条明确约定",
                    "supported": True,
                    "confidence": 1.0,
                },
                {
                    "claim": "违约金5000元",
                    "evidence": "合同第7条明确约定",
                    "supported": True,
                    "confidence": 0.95,
                },
                {
                    "claim": "试用期违反规定",
                    "evidence": "劳动合同法第19条",
                    "supported": True,
                    "confidence": 0.98,
                },
            ]
            
            # Calculate hallucination score (lower is better)
            unsupported_claims = sum(1 for check in hallucination_checks if not check["supported"])
            hallucination_score = unsupported_claims / len(hallucination_checks) if hallucination_checks else 0
            
            # Calculate overall cross-validation score
            passed_checks = sum(1 for check in consistency_checks if check["status"] == "passed")
            cross_validation_score = passed_checks / len(consistency_checks) if consistency_checks else 0
            
            # Determine overall validation result
            if (
                cross_validation_score >= 0.8
                and citation_accuracy >= 0.9
                and hallucination_score < 0.2
            ):
                validation_status = "passed"
            elif (
                cross_validation_score >= 0.6
                and citation_accuracy >= 0.8
                and hallucination_score < 0.3
            ):
                validation_status = "warning"
            else:
                validation_status = "failed"
            
            # Calculate overall confidence
            overall_confidence = (
                cross_validation_score * 0.4
                + citation_accuracy * 0.4
                + (1 - hallucination_score) * 0.2
            )
            
            # Create validation result
            validation_result = {
                "validation_status": validation_status,
                "consistency_checks": consistency_checks,
                "citation_checks": citation_checks,
                "citation_accuracy": citation_accuracy,
                "hallucination_checks": hallucination_checks,
                "hallucination_score": hallucination_score,
                "cross_validation_score": cross_validation_score,
                "overall_confidence": overall_confidence,
                "summary": f"验证结果: {validation_status}，置信度: {overall_confidence:.2f}",
                "recommendations": [],
            }
            
            # Add recommendations based on validation status
            if validation_status == "failed":
                validation_result["recommendations"].append("验证失败，建议人工审核")
            elif validation_status == "warning":
                validation_result["recommendations"].append("存在验证警告，建议重点检查")
            
            # Update state
            state["agent_history"].append(WorkflowNodes.VALIDATION)
            state["current_agent"] = WorkflowNodes.VALIDATION
            state["validation_result"] = validation_result
            state["citation_accuracy"] = citation_accuracy
            state["hallucination_score"] = hallucination_score
            state["cross_validation_passed"] = validation_status in ["passed", "warning"]
            state["validation_agent_status"] = AgentStatus.COMPLETED
            
            logger.info(f"Validation agent completed, status: {validation_status}, confidence: {overall_confidence:.2f}")

            return state

        except Exception as e:
            logger.error(f"Validation agent failed: {e}", exc_info=True)
            state["error_message"] = f"验证失败: {str(e)}"
            state["validation_agent_status"] = AgentStatus.FAILED
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state
