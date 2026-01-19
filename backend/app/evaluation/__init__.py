"""
Evaluation Module

This module provides tools and utilities for evaluating contract analysis systems.
"""

from app.evaluation.metrics import (
    MetricType,
    MetricValue,
    EvaluationResult,
    EvaluationMetrics,
    RiskPoint,
    GroundTruthAnnotation,
)

from app.evaluation.baselines import (
    BaselineType,
    ExperimentConfig,
    ExperimentResult,
    BaselineExperiments,
)

from app.evaluation.golden_dataset import (
    ContractType as DatasetContractType,
    RiskCategory,
    SeverityLevel,
    GoldenDatasetContract,
    DatasetInfo,
    GoldenDataset,
)

from app.evaluation.data_generator import (
    ContractType as GeneratorContractType,
    RiskCategory as GeneratorRiskCategory,
    SeverityLevel as GeneratorSeverityLevel,
    MockContract,
    ContractDataGenerator,
)

from app.evaluation.data_validator import (
    ValidationSeverity,
    ValidationResult,
    ValidationReport,
    DataValidator,
)

__all__ = [
    # Metrics
    'MetricType',
    'MetricValue',
    'EvaluationResult',
    'EvaluationMetrics',
    'RiskPoint',
    'GroundTruthAnnotation',
    # Baselines
    'BaselineType',
    'ExperimentConfig',
    'ExperimentResult',
    'BaselineExperiments',
    # Golden Dataset
    'DatasetContractType',
    'RiskCategory',
    'SeverityLevel',
    'GoldenDatasetContract',
    'DatasetInfo',
    'GoldenDataset',
    # Data Generator
    'GeneratorContractType',
    'GeneratorRiskCategory',
    'GeneratorSeverityLevel',
    'MockContract',
    'ContractDataGenerator',
    # Data Validator
    'ValidationSeverity',
    'ValidationResult',
    'ValidationReport',
    'DataValidator',
]
