"""
Data Validation System for LegalOS

This module provides comprehensive data validation for contracts and evaluation data.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    location: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report for a dataset"""
    dataset_path: str
    validation_date: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    issues: List[ValidationResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class DataValidator:
    """Validate contract data quality and integrity"""
    
    # Contract type regex patterns
    CONTRACT_PATTERNS = {
        "email": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'),
        "phone": re.compile(r'1[3-9]\d{9}'),
        "id_card": re.compile(r'\d{17}[\dXx]'),
        "money": re.compile(r'[0-9,]+[元万千百十]'),
        "date": re.compile(r'\d{4}[年\-]\d{1,2}[月\-]\d{1,2}[日]'),
        "percentage": re.compile(r'\d+(\.\d+)?[%％]'),
    }
    
    # Required sections in contracts
    REQUIRED_SECTIONS = {
        "employment": ["合同期限", "工作内容", "劳动报酬", "违约责任"],
        "sales": ["产品信息", "交付方式", "付款方式", "违约责任"],
        "lease": ["租赁物", "租赁期限", "租金", "违约责任"],
        "service": ["服务内容", "服务标准", "服务期限", "服务费用"],
        "purchase": ["采购标的", "质量标准", "交货", "验收"],
    }
    
    def __init__(self):
        """Initialize data validator"""
        pass
    
    def validate_contract(
        self,
        contract_data: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate a single contract
        
        Args:
            contract_data: Contract data dictionary
            
        Returns:
            List of validation results
        """
        results = []
        
        # 1. Validate required fields
        results.extend(self._validate_required_fields(contract_data))
        
        # 2. Validate contract text
        if "contract_text" in contract_data:
            results.extend(
                self._validate_contract_text(
                    contract_data["contract_text"],
                    contract_data.get("contract_type", "employment")
                )
            )
        
        # 3. Validate risk points
        if "risk_points" in contract_data:
            results.extend(
                self._validate_risk_points(contract_data["risk_points"])
            )
        
        # 4. Validate metadata
        if "metadata" in contract_data:
            results.extend(
                self._validate_metadata(contract_data["metadata"])
            )
        
        return results

    def _validate_required_fields(
        self,
        contract_data: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate required contract fields
        
        Args:
            contract_data: Contract data
            
        Returns:
            Validation results
        """
        results = []
        required_fields = ["id", "title", "contract_type", "contract_text"]
        
        for field in required_fields:
            if field not in contract_data:
                results.append(ValidationResult(
                    check_name="required_field",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing required field: {field}",
                    location=field
                ))
            elif not contract_data[field]:
                results.append(ValidationResult(
                    check_name=f"{field}_empty",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Field {field} is empty",
                    location=field
                ))
        
        return results

    def _validate_contract_text(
        self,
        contract_text: str,
        contract_type: str
    ) -> List[ValidationResult]:
        """Validate contract text content
        
        Args:
            contract_text: Contract text content
            contract_type: Type of contract
            
        Returns:
            Validation results
        """
        results = []
        
        # Check text length
        if len(contract_text) < 100:
            results.append(ValidationResult(
                check_name="text_length",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Contract text is too short (< 100 characters)",
                details={"length": len(contract_text)}
            ))
        elif len(contract_text) > 50000:
            results.append(ValidationResult(
                check_name="text_length",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Contract text is too long (> 50000 characters)",
                details={"length": len(contract_text)}
            ))
        
        # Check for required sections
        required_sections = self.REQUIRED_SECTIONS.get(contract_type, [])
        missing_sections = []
        
        for section in required_sections:
            if section not in contract_text:
                missing_sections.append(section)
        
        if missing_sections:
            results.append(ValidationResult(
                check_name="required_sections",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Missing required sections: {', '.join(missing_sections)}",
                details={"missing_sections": missing_sections}
            ))
        
        # Check for suspicious patterns
        if "placeholder" in contract_text.lower():
            results.append(ValidationResult(
                check_name="placeholder_detected",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message="Contract contains placeholder text"
            ))
        
        if "[TODO]" in contract_text or "[FIXME]" in contract_text:
            results.append(ValidationResult(
                check_name="todo_markers",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Contract contains TODO/FIXME markers"
            ))
        
        return results

    def _validate_risk_points(
        self,
        risk_points: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate risk points
        
        Args:
            risk_points: List of risk points
            
        Returns:
            Validation results
        """
        results = []
        
        # Check if risk points exist
        if not risk_points:
            results.append(ValidationResult(
                check_name="no_risk_points",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Contract has no identified risks"
            ))
            return results
        
        # Validate each risk point
        for i, risk in enumerate(risk_points):
            # Check required fields
            required_fields = ["category", "severity", "description"]
            for field in required_fields:
                if field not in risk:
                    results.append(ValidationResult(
                        check_name=f"risk_point_{i}_missing_field",
                        passed=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Risk point {i}: Missing field {field}",
                        details={"risk_index": i, "field": field}
                    ))
            
            # Validate severity
            if "severity" in risk:
                valid_severities = ["low", "medium", "high", "critical"]
                if risk["severity"] not in valid_severities:
                    results.append(ValidationResult(
                        check_name=f"risk_point_{i}_invalid_severity",
                        passed=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Risk point {i}: Invalid severity '{risk['severity']}'",
                        details={"risk_index": i, "severity": risk["severity"]}
                    ))
        
        return results

    def _validate_metadata(
        self,
        metadata: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate metadata fields
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Validation results
        """
        results = []
        
        # Check for generated_at timestamp
        if "generated_at" in metadata:
            try:
                datetime.fromisoformat(metadata["generated_at"])
            except ValueError:
                results.append(ValidationResult(
                    check_name="invalid_timestamp",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message="Invalid generated_at timestamp format",
                    location="metadata.generated_at"
                ))
        
        return results

    def validate_dataset(
        self,
        dataset_path: str
    ) -> ValidationReport:
        """Validate entire dataset
        
        Args:
            dataset_path: Path to dataset directory
            
        Returns:
            Complete validation report
        """
        dataset_dir = Path(dataset_path)
        
        results = []
        total_contracts = 0
        contracts_by_type = {}
        
        # Validate dataset structure
        results.extend(self._validate_dataset_structure(dataset_dir))
        
        # Load and validate each contract
        contracts_dir = dataset_dir / "contracts"
        if contracts_dir.exists():
            for contract_file in contracts_dir.glob("*.json"):
                try:
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        contract_data = json.load(f)
                    
                    total_contracts += 1
                    contract_type = contract_data.get("contract_type", "unknown")
                    contracts_by_type[contract_type] = contracts_by_type.get(contract_type, 0) + 1
                    
                    # Validate individual contract
                    contract_results = self.validate_contract(contract_data)
                    results.extend(contract_results)
                    
                except json.JSONDecodeError as e:
                    results.append(ValidationResult(
                        check_name="json_parse_error",
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Invalid JSON in {contract_file.name}: {str(e)}",
                        location=str(contract_file)
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        check_name="file_read_error",
                        passed=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Error reading {contract_file.name}: {str(e)}",
                        location=str(contract_file)
                    ))
        
        # Validate dataset info file
        info_file = dataset_dir / "dataset_info.json"
        dataset_info = None
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    dataset_info = json.load(f)
                
                results.extend(self._validate_dataset_info(dataset_info, total_contracts))
            except Exception as e:
                results.append(ValidationResult(
                    check_name="dataset_info_error",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Error reading dataset info: {str(e)}",
                    location=str(info_file)
                ))
        
        # Generate summary
        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = sum(1 for r in results if not r.passed)
        
        summary = {
            "total_contracts": total_contracts,
            "contract_type_distribution": contracts_by_type,
            "issues_by_severity": {
                "critical": sum(1 for r in results if r.severity == ValidationSeverity.CRITICAL),
                "error": sum(1 for r in results if r.severity == ValidationSeverity.ERROR),
                "warning": sum(1 for r in results if r.severity == ValidationSeverity.WARNING),
                "info": sum(1 for r in results if r.severity == ValidationSeverity.INFO),
            },
            "data_quality_score": self._calculate_quality_score(results),
        }
        
        return ValidationReport(
            dataset_path=dataset_path,
            validation_date=datetime.now().isoformat(),
            total_checks=len(results),
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            issues=results,
            summary=summary
        )

    def _validate_dataset_structure(
        self,
        dataset_dir: Path
    ) -> List[ValidationResult]:
        """Validate dataset directory structure
        
        Args:
            dataset_dir: Dataset directory
            
        Returns:
            Validation results
        """
        results = []
        
        # Check if directory exists
        if not dataset_dir.exists():
            results.append(ValidationResult(
                check_name="directory_exists",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Dataset directory does not exist: {dataset_dir}"
            ))
            return results
        
        # Check for contracts subdirectory
        contracts_dir = dataset_dir / "contracts"
        if not contracts_dir.exists():
            results.append(ValidationResult(
                check_name="contracts_directory",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message="Missing contracts subdirectory"
            ))
        
        # Check for dataset_info.json
        info_file = dataset_dir / "dataset_info.json"
        if not info_file.exists():
            results.append(ValidationResult(
                check_name="dataset_info_file",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message="Missing dataset_info.json file"
            ))
        
        # Check if contracts directory has files
        if contracts_dir.exists():
            contract_files = list(contracts_dir.glob("*.json"))
            if not contract_files:
                results.append(ValidationResult(
                    check_name="empty_contracts_directory",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message="Contracts directory is empty"
                ))
        
        return results

    def _validate_dataset_info(
        self,
        dataset_info: Dict[str, Any],
        actual_contracts: int
    ) -> List[ValidationResult]:
        """Validate dataset info
        
        Args:
            dataset_info: Dataset info dictionary
            actual_contracts: Actual number of contracts
            
        Returns:
            Validation results
        """
        results = []
        
        # Check required fields
        required_fields = ["name", "version", "total_contracts"]
        for field in required_fields:
            if field not in dataset_info:
                results.append(ValidationResult(
                    check_name=f"dataset_info_{field}",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Dataset info missing field: {field}"
                ))
        
        # Check contract count consistency
        if "total_contracts" in dataset_info:
            if dataset_info["total_contracts"] != actual_contracts:
                results.append(ValidationResult(
                    check_name="contract_count_mismatch",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Contract count mismatch: info says {dataset_info['total_contracts']}, found {actual_contracts}",
                    details={
                        "reported": dataset_info["total_contracts"],
                        "actual": actual_contracts
                    }
                ))
        
        return results

    def _calculate_quality_score(
        self,
        results: List[ValidationResult]
    ) -> float:
        """Calculate data quality score
        
        Args:
            results: Validation results
            
        Returns:
            Quality score (0-100)
        """
        if not results:
            return 100.0
        
        # Weight different severity levels
        severity_weights = {
            ValidationSeverity.CRITICAL: -20,
            ValidationSeverity.ERROR: -10,
            ValidationSeverity.WARNING: -5,
            ValidationSeverity.INFO: 0,
        }
        
        # Calculate score
        score = 100.0
        for result in results:
            if not result.passed:
                score += severity_weights.get(result.severity, -5)
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))

    def generate_report(
        self,
        report: ValidationReport,
        output_path: str
    ) -> str:
        """Generate validation report file
        
        Args:
            report: Validation report
            output_path: Path to save report
            
        Returns:
            Path to generated report
        """
        from pathlib import Path
        
        output_file = Path(output_path)
        
        # Prepare report data
        report_data = {
            "dataset_path": report.dataset_path,
            "validation_date": report.validation_date,
            "summary": report.summary,
            "total_checks": report.total_checks,
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
            "quality_score": report.summary.get("data_quality_score", 0),
            "issues": [
                {
                    "check_name": r.check_name,
                    "passed": r.passed,
                    "severity": r.severity.value,
                    "message": r.message,
                    "location": r.location,
                    "details": r.details,
                }
                for r in report.issues
            ]
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Validation report saved to {output_file}")
        return str(output_file)

    def print_summary(self, report: ValidationReport):
        """Print validation summary to console
        
        Args:
            report: Validation report
        """
        print("\n" + "="*60)
        print("数据验证报告 (Data Validation Report)")
        print("="*60)
        print(f"数据集路径: {report.dataset_path}")
        print(f"验证时间: {report.validation_date}")
        print(f"\n检查统计:")
        print(f"  总检查数: {report.total_checks}")
        print(f"  通过: {report.passed_checks}")
        print(f"  失败: {report.failed_checks}")
        print(f"  数据质量评分: {report.summary.get('data_quality_score', 0):.1f}/100")
        print(f"\n问题分布:")
        for severity, count in report.summary.get("issues_by_severity", {}).items():
            print(f"  {severity.upper()}: {count}")
        print(f"\n合同类型分布:")
        for contract_type, count in report.summary.get("contract_type_distribution", {}).items():
            print(f"  {contract_type}: {count}")
        print("="*60 + "\n")


def main():
    """Validate dataset"""
    validator = DataValidator()
    
    # Validate mock dataset
    dataset_path = "data/evaluation/mock"
    print(f"正在验证数据集: {dataset_path}")
    
    report = validator.validate_dataset(dataset_path)
    validator.print_summary(report)
    
    # Generate report file
    report_file = validator.generate_report(
        report,
        "data/evaluation/validation_report.json"
    )
    print(f"✅ 验证报告已生成: {report_file}")


if __name__ == "__main__":
    main()
