"""
Report Agent - Structured report generation

This agent generates comprehensive contract analysis reports
in multiple formats (Markdown, JSON, HTML).
"""

import logging
from typing import Dict, Any
from .state import AgentState, TaskStatus, AgentStatus, WorkflowNodes
from ..core.tracing import get_span_manager, trace_function

logger = logging.getLogger(__name__)


REPORT_SYSTEM_PROMPT = """
你是一个报告生成智能体。你的任务是：

1. 综合所有智能体的分析结果
2. 生成结构化报告
3. 创建风险矩阵
4. 支持多种导出格式

报告结构：
- 执行摘要: 分析概述和关键发现
- 合同信息: 合同基本信息和实体
- 条款分析: 条款分类和内容
- 合规审查: 合规性问题和建议
- 风险评估: 风险矩阵和评估结果
- 验证结果: 验证状态和置信度
- 改进建议: 具体修改建议

导出格式：
- Markdown: 易读的文本格式
- JSON: 结构化数据格式
- HTML: 可打印的网页格式

请生成清晰、专业、易读的报告。
"""


@trace_function(name="report_node")
async def report_node(state: AgentState) -> AgentState:
    """Report agent node for LangGraph workflow
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with generated report
    """
    span_manager = get_span_manager()
    session_id = state.get("session_id", "unknown")
    
    logger.info("Report agent started")
    
    with span_manager.trace_agent_execution(
        agent_name="report",
        session_id=session_id,
        metadata={
            "contract_id": state.get("contract_id"),
            "contract_type": state.get("contract_type"),
        }
    ):
        try:
            contract_id = state.get("contract_id", "")
            contract_type = state.get("contract_type", "other")
            analysis_result = state.get("analysis_result", {})
            review_result = state.get("review_result", {})
            validation_result = state.get("validation_result", {})
            
            # Generate risk matrix
            risk_matrix = generate_risk_matrix(review_result)
            
            # Generate Markdown report
            markdown_report = generate_markdown_report(
                contract_id, contract_type, analysis_result, review_result, validation_result, risk_matrix
            )
            
            # Generate JSON report
            json_report = generate_json_report(
                contract_id, contract_type, analysis_result, review_result, validation_result, risk_matrix
            )
            
            # Determine available export formats
            export_formats = ["markdown", "json"]
            
            # Create report result
            report = {
                "contract_id": contract_id,
                "contract_type": contract_type,
                "format": "markdown",
                "markdown": markdown_report,
                "json": json_report,
                "risk_matrix": risk_matrix,
                "export_formats": export_formats,
                "generated_at": None,  # Will be set to current time
            }
            
            # Generate final answer (summary for user)
            final_answer = f"""
合同分析报告已生成。

**合同ID**: {contract_id}
**合同类型**: {contract_type}

**关键发现**:
- 识别了 {analysis_result.get('clause_count', 0)} 个条款
- 发现了 {review_result.get('issue_count', 0)} 个合规性问题
- 识别了 {review_result.get('risk_count', 0)} 个风险
- 总体风险等级: {review_result.get('overall_risk', 'unknown')}
- 验证置信度: {validation_result.get('overall_confidence', 0):.2f}

报告已生成，可以查看详细内容或导出。
"""
            
            # Collect final sources
            final_sources = state.get("retrieved_docs", [])
            
            # Update state
            state["agent_history"].append(WorkflowNodes.REPORT)
            state["current_agent"] = WorkflowNodes.REPORT
            state["report"] = report
            state["report_format"] = "markdown"
            state["risk_matrix"] = risk_matrix
            state["export_formats"] = export_formats
            state["report_agent_status"] = AgentStatus.COMPLETED
            state["final_answer"] = final_answer
            state["final_sources"] = final_sources
            state["task_status"] = TaskStatus.COMPLETED
            
            logger.info("Report agent completed successfully")
            logger.info(f"Report generated in {len(export_formats)} formats")

            return state

        except Exception as e:
            logger.error(f"Report agent failed: {e}", exc_info=True)
            state["error_message"] = f"报告生成失败: {str(e)}"
            state["report_agent_status"] = AgentStatus.FAILED
            state["current_agent"] = WorkflowNodes.ERROR_HANDLER
            return state


def generate_risk_matrix(review_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate risk matrix from review results
    
    Args:
        review_result: Review agent results
    
    Returns:
        Risk matrix dictionary
    """
    risk_assessments = review_result.get("risk_assessments", [])
    
    # Categorize risks by level
    high_risks = [r for r in risk_assessments if r.get("level") == "high"]
    medium_risks = [r for r in risk_assessments if r.get("level") == "medium"]
    low_risks = [r for r in risk_assessments if r.get("level") == "low"]
    
    return {
        "high": {
            "count": len(high_risks),
            "risks": high_risks,
        },
        "medium": {
            "count": len(medium_risks),
            "risks": medium_risks,
        },
        "low": {
            "count": len(low_risks),
            "risks": low_risks,
        },
        "summary": f"高风险: {len(high_risks)}, 中风险: {len(medium_risks)}, 低风险: {len(low_risks)}",
    }


def generate_markdown_report(
    contract_id: str,
    contract_type: str,
    analysis_result: Dict[str, Any],
    review_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    risk_matrix: Dict[str, Any],
) -> str:
    """Generate Markdown format report
    
    Args:
        contract_id: Contract identifier
        contract_type: Contract type
        analysis_result: Analysis agent results
        review_result: Review agent results
        validation_result: Validation agent results
        risk_matrix: Risk matrix
    
    Returns:
        Markdown formatted report
    """
    report = f"""# 合同分析报告

## 执行摘要

本报告对合同 `{contract_id}` (类型: {contract_type}) 进行了全面分析。

### 关键指标

- **条款数量**: {analysis_result.get('clause_count', 0)}
- **实体数量**: {sum(len(analysis_result.get('entities', {}).get(k, [])) for k in analysis_result.get('entities', {}))}
- **合规性问题**: {review_result.get('issue_count', 0)}
- **风险总数**: {review_result.get('risk_count', 0)}
- **总体风险等级**: {review_result.get('overall_risk', 'unknown').upper()}
- **验证置信度**: {validation_result.get('overall_confidence', 0):.2%}

---

## 1. 合同信息

- **合同ID**: {contract_id}
- **合同类型**: {contract_type}
- **分析状态**: 已完成

### 关键实体

"""
    
    # Add entities
    entities = analysis_result.get("entities", {})
    if entities.get("parties"):
        report += "#### 当事人\n"
        for party in entities["parties"]:
            report += f"- {party.get('name')} ({party.get('role')})\n"
        report += "\n"
    
    if entities.get("amounts"):
        report += "#### 金额信息\n"
        for amount in entities["amounts"]:
            report += f"- {amount.get('type')}: {amount.get('value')} {amount.get('currency')}\n"
        report += "\n"
    
    if entities.get("dates"):
        report += "#### 重要日期\n"
        for date in entities["dates"]:
            report += f"- {date.get('type')}: {date.get('value')}\n"
        report += "\n"
    
    # Add clause analysis
    report += "## 2. 条款分析\n\n"
    report += f"共识别 {analysis_result.get('clause_count', 0)} 个条款，类型包括：\n\n"
    
    clause_types = analysis_result.get("clause_types", [])
    for clause_type in clause_types:
        report += f"- {clause_type}\n"
    
    report += "\n### 详细条款\n\n"
    clause_classifications = analysis_result.get("clause_classifications", [])
    for clause in clause_classifications:
        report += f"**{clause.get('type')}** (重要性: {clause.get('importance')}): {clause.get('text')}\n\n"
    
    # Add compliance review
    report += "## 3. 合规审查\n\n"
    compliance_issues = review_result.get("compliance_issues", [])
    
    for issue in compliance_issues:
        severity = issue.get("severity", "unknown").upper()
        report += f"### {severity} - {issue.get('issue')}\n\n"
        report += f"**描述**: {issue.get('description')}\n\n"
        report += f"**位置**: {issue.get('location')}\n\n"
        report += f"**参考**: {issue.get('reference')}\n\n"
    
    # Add risk assessment
    report += "## 4. 风险评估\n\n"
    report += f"**总体风险等级**: {review_result.get('overall_risk', 'unknown').upper()}\n\n"
    report += "### 风险矩阵\n\n"
    report += f"- **高风险**: {risk_matrix.get('high', {}).get('count', 0)}\n"
    report += f"- **中风险**: {risk_matrix.get('medium', {}).get('count', 0)}\n"
    report += f"- **低风险**: {risk_matrix.get('low', {}).get('count', 0)}\n\n"
    
    # Add validation results
    report += "## 5. 验证结果\n\n"
    report += f"**验证状态**: {validation_result.get('validation_status', 'unknown').upper()}\n\n"
    report += f"**置信度**: {validation_result.get('overall_confidence', 0):.2%}\n\n"
    report += f"**引用准确率**: {validation_result.get('citation_accuracy', 0):.2%}\n\n"
    report += f"**幻觉评分**: {validation_result.get('hallucination_score', 0):.2%}\n\n"
    
    # Add suggestions
    report += "## 6. 改进建议\n\n"
    suggestions = review_result.get("suggestions", [])
    for i, suggestion in enumerate(suggestions, 1):
        report += f"{i}. {suggestion}\n"
    
    report += "\n---\n\n"
    report += "*本报告由 LegalOS 多智能体系统自动生成*"
    
    return report


def generate_json_report(
    contract_id: str,
    contract_type: str,
    analysis_result: Dict[str, Any],
    review_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    risk_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate JSON format report
    
    Args:
        contract_id: Contract identifier
        contract_type: Contract type
        analysis_result: Analysis agent results
        review_result: Review agent results
        validation_result: Validation agent results
        risk_matrix: Risk matrix
    
    Returns:
        JSON formatted report
    """
    return {
        "metadata": {
            "contract_id": contract_id,
            "contract_type": contract_type,
            "generated_at": None,  # Will be set to current time
        },
        "executive_summary": {
            "clause_count": analysis_result.get("clause_count", 0),
            "entity_count": sum(
                len(analysis_result.get("entities", {}).get(k, []))
                for k in analysis_result.get("entities", {})
            ),
            "compliance_issues": review_result.get("issue_count", 0),
            "risk_count": review_result.get("risk_count", 0),
            "overall_risk": review_result.get("overall_risk", "unknown"),
            "validation_confidence": validation_result.get("overall_confidence", 0),
        },
        "analysis": analysis_result,
        "review": review_result,
        "validation": validation_result,
        "risk_matrix": risk_matrix,
    }
