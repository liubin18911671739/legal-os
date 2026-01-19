"""
Evaluation API Routes

This module provides API endpoints for running evaluations, managing golden dataset,
generating mock data, and validating data quality.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel, Field
import time
from datetime import datetime

from app.evaluation import (
    GoldenDataset,
    BaselineExperiments,
    BaselineType,
    ExperimentConfig,
    EvaluationMetrics,
    DataValidator,
    ContractDataGenerator,
)
from app.services.export_service import create_export_service

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

# Initialize golden dataset
golden_dataset = GoldenDataset()

# Initialize data validator
data_validator = DataValidator()

# Pydantic models
class EvaluationRequest(BaseModel):
    """Request model for running evaluation"""
    contract_id: str = Field(..., description="Contract ID to evaluate")
    baseline_types: List[str] = Field(
        default=["no_rag", "simple_rag", "multi_agent_rag"],
        description="Baseline types to evaluate"
    )
    model_name: str = Field(default="glm-4", description="Model name to use")
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=2000, ge=100, le=8000)


class EvaluationResponse(BaseModel):
    """Response model for evaluation"""
    evaluation_id: str
    status: str
    message: str


class EvaluationResultsResponse(BaseModel):
    """Response model with evaluation results"""
    evaluation_id: str
    contract_id: str
    results: List[Dict[str, Any]]
    comparison: Dict[str, Dict[str, float]]
    timestamp: str


class DatasetContractResponse(BaseModel):
    """Response model for dataset contract"""
    id: str
    title: str
    contract_type: str
    overall_risk: str
    compliance_status: str
    risk_points_count: int


class DatasetInfoResponse(BaseModel):
    """Response model for dataset info"""
    name: str
    version: str
    total_contracts: int
    total_risk_points: int
    contract_type_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]


@router.post("/run", response_model=EvaluationResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    Run evaluation on a contract.

    This endpoint triggers an evaluation of the specified contract
    against the selected baseline types.
    """
    try:
        # Get contract from golden dataset
        contract = golden_dataset.get_contract(request.contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {request.contract_id} not found in golden dataset"
            )

        # Generate evaluation ID
        evaluation_id = f"eval-{int(time.time())}"

        # Get LLM client (simplified - would need actual integration)
        # For now, use a mock
        llm_client = None

        # Create baseline experiments
        baseline_experiments = BaselineExperiments(llm_client)

        # Create experiment configurations
        configs = []
        for baseline_type_str in request.baseline_types:
            try:
                baseline_type = BaselineType(baseline_type_str)
                config = ExperimentConfig(
                    baseline_type=baseline_type,
                    model_name=request.model_name,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=0.9
                )
                configs.append(config)
            except ValueError:
                logger.warning(f"Unknown baseline type: {baseline_type_str}")
                continue

        # Run evaluation in background
        background_tasks.add_task(
            _run_evaluation_background,
            evaluation_id,
            request.contract_id,
            contract,
            configs,
            baseline_experiments
        )

        return EvaluationResponse(
            evaluation_id=evaluation_id,
            status="running",
            message="Evaluation started successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start evaluation: {str(e)}"
        )


@router.get("/results/{evaluation_id}", response_model=EvaluationResultsResponse)
async def get_evaluation_results(evaluation_id: str):
    """
    Get evaluation results.

    Retrieve the results of a previously started evaluation.
    """
    try:
        # For now, return mock results
        # In production, this would fetch from database or cache
        mock_results = [
            {
                "baseline_type": "no_rag",
                "duration": 45.2,
                "token_usage": 1250,
                "cost": 0.025,
                "metrics": {
                    "precision": 0.72,
                    "recall": 0.65,
                    "f1_score": 0.68,
                    "hallucination_rate": 0.15,
                },
                "error": None
            },
            {
                "baseline_type": "simple_rag",
                "duration": 38.5,
                "token_usage": 980,
                "cost": 0.020,
                "metrics": {
                    "precision": 0.78,
                    "recall": 0.72,
                    "f1_score": 0.75,
                    "hallucination_rate": 0.08,
                },
                "error": None
            },
            {
                "baseline_type": "multi_agent_rag",
                "duration": 52.3,
                "token_usage": 1850,
                "cost": 0.037,
                "metrics": {
                    "precision": 0.85,
                    "recall": 0.80,
                    "f1_score": 0.82,
                    "hallucination_rate": 0.05,
                },
                "error": None
            }
        ]

        comparison = {
            "no_rag": {"f1_score": 0.68, "hallucination_rate": 0.15},
            "simple_rag": {"f1_score": 0.75, "hallucination_rate": 0.08},
            "multi_agent_rag": {"f1_score": 0.82, "hallucination_rate": 0.05},
        }

        return EvaluationResultsResponse(
            evaluation_id=evaluation_id,
            contract_id="mock-contract-id",
            results=mock_results,
            comparison=comparison,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    except Exception as e:
        logger.error(f"Failed to get evaluation results: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get results: {str(e)}"
        )


@router.get("/dataset/info", response_model=DatasetInfoResponse)
async def get_dataset_info():
    """
    Get golden dataset information.
    """
    try:
        info = golden_dataset.get_dataset_info()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset information not available"
            )

        return DatasetInfoResponse(
            name=info.name,
            version=info.version,
            total_contracts=info.total_contracts,
            total_risk_points=info.total_risk_points,
            contract_type_distribution=info.contract_type_distribution,
            severity_distribution=info.severity_distribution
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset info: {str(e)}"
        )


@router.get("/dataset/contracts", response_model=List[DatasetContractResponse])
async def get_dataset_contracts(
    contract_type: Optional[str] = None
):
    """
    Get all contracts in the golden dataset.

    Args:
        contract_type: Optional filter by contract type
    """
    try:
        from app.evaluation import ContractType as DatasetContractType

        # Filter by type if specified
        type_filter = None
        if contract_type:
            try:
                type_filter = DatasetContractType(contract_type)
            except ValueError:
                pass

        contracts = golden_dataset.get_all_contracts(type_filter)

        return [
            DatasetContractResponse(
                id=c.id,
                title=c.title,
                contract_type=c.contract_type.value,
                overall_risk=c.overall_risk.value,
                compliance_status=c.compliance_status,
                risk_points_count=len(c.risk_points)
            )
            for c in contracts
        ]

    except Exception as e:
        logger.error(f"Failed to get dataset contracts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contracts: {str(e)}"
        )


@router.get("/dataset/contracts/{contract_id}")
async def get_dataset_contract(contract_id: str):
    """
    Get a specific contract from the golden dataset.
    """
    try:
        contract = golden_dataset.get_contract(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found"
            )

        return {
            "id": contract.id,
            "title": contract.title,
            "contract_type": contract.contract_type.value,
            "contract_text": contract.contract_text,
            "overall_risk": contract.overall_risk.value,
            "compliance_status": contract.compliance_status,
            "risk_points": [
                {
                    "id": rp.id,
                    "category": rp.category,
                    "severity": rp.severity,
                    "description": rp.description,
                    "clause_text": rp.clause_text,
                    "location": rp.location,
                    "suggestion": rp.suggestion,
                    "citation": rp.citation
                }
                for rp in contract.risk_points
            ],
            "metadata": contract.metadata,
            "version": contract.version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contract: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contract: {str(e)}"
        )


@router.post("/dataset/sample")
async def create_sample_dataset():
    """
    Create a sample golden dataset for testing.
    """
    try:
        # Create sample contracts
        sample_contracts = golden_dataset.create_sample_dataset(num_samples=5)

        # Save contracts
        for contract in sample_contracts:
            golden_dataset.save_contract(contract)

        # Save dataset info
        golden_dataset.save_dataset_info()

        return {
            "message": "Sample dataset created successfully",
            "contracts_count": len(sample_contracts),
            "contracts": [c.id for c in sample_contracts]
        }

    except Exception as e:
        logger.error(f"Failed to create sample dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sample dataset: {str(e)}"
        )


async def _run_evaluation_background(
    evaluation_id: str,
    contract_id: str,
    contract,
    configs: List[ExperimentConfig],
    baseline_experiments: BaselineExperiments
):
    """
    Run evaluation in background task.

    This function runs all baseline experiments for a contract
    and saves the results.
    """
    try:
        logger.info(f"Starting evaluation {evaluation_id} for contract {contract_id}")

        # Run all baseline experiments
        results = await baseline_experiments.run_all_baselines(
            contract.contract_text,
            contract.contract_type.value,  # Get string value
            "Please analyze this contract for risks and compliance issues",
            configs
        )

        # Calculate comparison metrics
        comparison = {}
        for result in results:
            if result.error:
                continue
            metrics = result.metrics
            comparison[result.baseline_type.value] = {
                "duration": metrics.get('duration', 0),
                "f1_score": metrics.get('f1_score', 0),
                "precision": metrics.get('precision', 0),
                "recall": metrics.get('recall', 0),
                "hallucination_rate": metrics.get('hallucination_rate', 0),
                "token_usage": metrics.get('token_usage', 0),
                "cost": metrics.get('cost', 0),
            }

        # Save results (placeholder - would save to database)
        logger.info(f"Evaluation {evaluation_id} completed with {len(results)} results")

    except Exception as e:
        logger.error(f"Background evaluation failed: {e}", exc_info=True)


# Data Generation Endpoints
@router.post("/data/generate", status_code=status.HTTP_201_CREATED)
async def generate_mock_data(
    num_contracts: int = Query(100, ge=1, le=1000, description="Number of contracts to generate"),
    output_dir: str = Query("data/evaluation/generated", description="Output directory for generated data"),
    seed: Optional[int] = Query(None, description="Random seed for reproducibility")
):
    """
    Generate mock contract data for testing.
    
    Creates realistic contract data across multiple types (employment, sales, lease, service, purchase)
    with associated risk points and metadata.
    """
    try:
        generator = ContractDataGenerator(seed=seed)
        
        dataset_info = generator.generate_dataset(
            num_contracts=num_contracts,
            output_dir=output_dir
        )
        
        logger.info(f"Generated {dataset_info['total_contracts']} contracts")
        
        return {
            "message": "Mock data generated successfully",
            "dataset_info": {
                "name": dataset_info["name"],
                "version": dataset_info["version"],
                "total_contracts": dataset_info["total_contracts"],
                "total_risk_points": dataset_info["total_risk_points"],
                "contract_type_distribution": dataset_info["contract_type_distribution"],
                "severity_distribution": dataset_info["severity_distribution"],
                "created_at": dataset_info["created_at"],
                "output_directory": output_dir,
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to generate mock data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate mock data: {str(e)}"
        )


# Data Validation Endpoints
@router.post("/data/validate")
async def validate_dataset(
    dataset_path: str = Query(..., description="Path to dataset directory to validate")
):
    """
    Validate a dataset for data quality and integrity.
    
    Performs comprehensive validation including:
    - Required fields presence
    - Contract text content
    - Risk points structure
    - Metadata validity
    - Dataset consistency
    """
    try:
        report = data_validator.validate_dataset(dataset_path)
        
        logger.info(f"Dataset validation completed: {report.dataset_path}")
        
        return {
            "validation_report": {
                "dataset_path": report.dataset_path,
                "validation_date": report.validation_date,
                "summary": report.summary,
                "total_checks": report.total_checks,
                "passed_checks": report.passed_checks,
                "failed_checks": report.failed_checks,
                "data_quality_score": report.summary.get("data_quality_score", 0),
            },
            "issues": [
                {
                    "check_name": issue.check_name,
                    "passed": issue.passed,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "location": issue.location,
                    "details": issue.details,
                }
                for issue in report.issues
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to validate dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate dataset: {str(e)}"
        )


@router.get("/data/validate/report")
async def get_validation_report(
    dataset_path: str = Query(..., description="Path to dataset directory")
):
    """
    Get validation report for a dataset.
    
    Returns the previously generated validation report.
    """
    try:
        from pathlib import Path
        import json
        
        report_file = Path(dataset_path) / "validation_report.json"
        
        if not report_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation report not found. Run validation first."
            )
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return report
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get validation report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validation report: {str(e)}"
        )


@router.post("/data/generate-and-validate")
async def generate_and_validate(
    num_contracts: int = Query(100, ge=1, le=1000),
    seed: Optional[int] = Query(None)
):
    """
    Generate mock data and validate it in one operation.
    
    This is a convenience endpoint that combines data generation
    with validation to ensure data quality.
    """
    try:
        # Generate data
        generator = ContractDataGenerator(seed=seed)
        dataset_info = generator.generate_dataset(num_contracts=num_contracts)
        
        # Validate data
        report = data_validator.validate_dataset(dataset_info.get("output_directory", "data/evaluation/generated"))
        
        logger.info(f"Generated and validated {dataset_info['total_contracts']} contracts")
        
        return {
            "generation": {
                "message": "Mock data generated successfully",
                "dataset_info": dataset_info,
            },
            "validation": {
                "message": "Dataset validated successfully",
                "validation_report": {
                    "dataset_path": report.dataset_path,
                    "validation_date": report.validation_date,
                    "summary": report.summary,
                    "total_checks": report.total_checks,
                    "passed_checks": report.passed_checks,
                    "failed_checks": report.failed_checks,
                    "data_quality_score": report.summary.get("data_quality_score", 0),
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to generate and validate: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate and validate: {str(e)}"
        )


@router.get("/data/quality-report")
async def get_data_quality_report():
    """
    Get data quality metrics for all datasets.
    
    Provides an overview of data quality across all generated datasets.
    """
    try:
        from pathlib import Path
        import json
        
        datasets_base = Path("data/evaluation")
        reports = []
        
        # Find all validation reports
        for report_file in datasets_base.rglob("*/validation_report.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    report["dataset_path"] = str(report_file.parent)
                    reports.append(report)
            except Exception as e:
                logger.warning(f"Failed to load report {report_file}: {e}")
        
        # Calculate overall statistics
        if reports:
            avg_quality_score = sum(r.get("validation_report", {}).get("data_quality_score", 0) for r in reports) / len(reports)
            total_issues = sum(r["validation_report"].get("failed_checks", 0) for r in reports)
            total_checks = sum(r["validation_report"].get("total_checks", 0) for r in reports)
            pass_rate = total_checks - total_issues / total_checks if total_checks > 0 else 0
        else:
            avg_quality_score = 0
            total_issues = 0
            total_checks = 0
            pass_rate = 0
        
        return {
            "total_datasets": len(reports),
            "average_quality_score": avg_quality_score,
            "total_issues": total_issues,
            "total_checks": total_checks,
            "pass_rate": pass_rate,
            "reports": reports
        }
    
    except Exception as e:
        logger.error(f"Failed to get data quality report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data quality report: {str(e)}"
        )
