"""
Golden Dataset Module

This module provides structures and utilities for managing the golden dataset
used for evaluation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import logging

from app.evaluation.metrics import RiskPoint, GroundTruthAnnotation

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of contracts in the dataset"""
    EMPLOYMENT = "employment"
    SALES = "sales"
    LEASE = "lease"
    SERVICE = "service"
    PURCHASE = "purchase"
    OTHER = "other"


class RiskCategory(Enum):
    """Categories of legal risks"""
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


class SeverityLevel(Enum):
    """Severity levels for risks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GoldenDatasetContract:
    """A contract in the golden dataset"""
    id: str
    title: str
    contract_type: ContractType
    contract_text: str
    file_type: str  # 'pdf', 'docx', 'txt'
    risk_points: List[RiskPoint] = field(default_factory=list)
    overall_risk: SeverityLevel = SeverityLevel.MEDIUM
    compliance_status: str = "compliant"
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class DatasetInfo:
    """Information about the golden dataset"""
    name: str
    version: str
    total_contracts: int
    total_risk_points: int
    contract_type_distribution: Dict[str, int] = field(default_factory=dict)
    severity_distribution: Dict[str, int] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class GoldenDataset:
    """Manage the golden dataset for evaluation"""

    def __init__(self, dataset_dir: str = "data/evaluation/golden"):
        """
        Initialize golden dataset manager.

        Args:
            dataset_dir: Directory containing the dataset
        """
        self.dataset_dir = Path(dataset_dir)
        self.contracts: Dict[str, GoldenDatasetContract] = {}
        self.dataset_info: Optional[DatasetInfo] = None
        self._load_dataset()

    def _load_dataset(self):
        """Load dataset from files"""
        contracts_dir = self.dataset_dir / "contracts"
        info_file = self.dataset_dir / "dataset_info.json"

        # Load contracts
        if contracts_dir.exists():
            for contract_file in contracts_dir.glob("*.json"):
                try:
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        contract = self._parse_contract_data(data)
                        self.contracts[contract.id] = contract
                        logger.info(f"Loaded contract: {contract.id}")
                except Exception as e:
                    logger.error(f"Failed to load contract {contract_file}: {e}")

        # Load dataset info
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info_data = json.load(f)
                    self.dataset_info = DatasetInfo(**info_data)
                    logger.info(f"Loaded dataset info: {self.dataset_info.name}")
            except Exception as e:
                logger.error(f"Failed to load dataset info: {e}")

    def _parse_contract_data(self, data: Dict[str, Any]) -> GoldenDatasetContract:
        """Parse contract data from JSON"""
        # Parse risk points
        risk_points = []
        for rp_data in data.get('risk_points', []):
            risk_point = RiskPoint(
                id=rp_data['id'],
                category=rp_data['category'],
                severity=rp_data['severity'],
                description=rp_data['description'],
                clause_text=rp_data.get('clause_text', ''),
                location=rp_data.get('location'),
                suggestion=rp_data.get('suggestion'),
                citation=rp_data.get('citation')
            )
            risk_points.append(risk_point)

        return GoldenDatasetContract(
            id=data['id'],
            title=data['title'],
            contract_type=ContractType(data['contract_type']),
            contract_text=data['contract_text'],
            file_type=data.get('file_type', 'txt'),
            risk_points=risk_points,
            overall_risk=SeverityLevel(data.get('overall_risk', 'medium')),
            compliance_status=data.get('compliance_status', 'compliant'),
            metadata=data.get('metadata', {}),
            version=data.get('version', '1.0'),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )

    def get_contract(self, contract_id: str) -> Optional[GoldenDatasetContract]:
        """Get a contract by ID"""
        return self.contracts.get(contract_id)

    def get_all_contracts(
        self,
        contract_type: Optional[ContractType] = None
    ) -> List[GoldenDatasetContract]:
        """
        Get all contracts, optionally filtered by type

        Args:
            contract_type: Optional contract type filter

        Returns:
            List of contracts
        """
        contracts = list(self.contracts.values())
        if contract_type:
            contracts = [c for c in contracts if c.contract_type == contract_type]
        return contracts

    def get_ground_truth_annotation(
        self,
        contract_id: str
    ) -> Optional[GroundTruthAnnotation]:
        """
        Get ground truth annotation for a contract

        Args:
            contract_id: Contract ID

        Returns:
            Ground truth annotation
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return None

        return GroundTruthAnnotation(
            contract_id=contract.id,
            contract_text=contract.contract_text,
            contract_type=contract.contract_type.value,
            risk_points=contract.risk_points,
            overall_risk=contract.overall_risk.value,
            compliance_status=contract.compliance_status,
            metadata=contract.metadata
        )

    def get_dataset_info(self) -> Optional[DatasetInfo]:
        """Get dataset information"""
        return self.dataset_info

    def create_sample_dataset(self, num_samples: int = 5) -> List[GoldenDatasetContract]:
        """
        Create a sample dataset for testing

        Args:
            num_samples: Number of sample contracts to create

        Returns:
            List of sample contracts
        """
        sample_contracts = []

        for i in range(num_samples):
            # Create sample contract
            contract = GoldenDatasetContract(
                id=f"sample-{i+1}",
                title=f"Sample Employment Contract {i+1}",
                contract_type=ContractType.EMPLOYMENT,
                contract_text=self._generate_sample_contract_text(i),
                file_type="txt",
                overall_risk=SeverityLevel.MEDIUM,
                compliance_status="mostly_compliant",
                version="1.0"
            )

            # Add sample risk points
            contract.risk_points = [
                RiskPoint(
                    id=f"risk-{i+1}-1",
                    category="compliance",
                    severity="medium",
                    description="Missing non-compete clause",
                    clause_text="Sample clause text...",
                    suggestion="Consider adding a non-compete clause",
                    citation="Section 3"
                ),
                RiskPoint(
                    id=f"risk-{i+1}-2",
                    category="financial",
                    severity="low",
                    description="Salary payment terms unclear",
                    clause_text="Payment will be made monthly",
                    suggestion="Specify exact payment date and method",
                    citation="Section 5"
                )
            ]

            sample_contracts.append(contract)
            self.contracts[contract.id] = contract

        # Update dataset info
        self.dataset_info = DatasetInfo(
            name="Sample Golden Dataset",
            version="1.0",
            total_contracts=num_samples,
            total_risk_points=num_samples * 2,
            contract_type_distribution={"employment": num_samples},
            severity_distribution={"low": num_samples, "medium": num_samples},
            created_at="",
            updated_at=""
        )

        return sample_contracts

    def _generate_sample_contract_text(self, index: int) -> str:
        """Generate sample contract text"""
        return f"""EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of the date of last signature below ("Effective Date"), by and between:

{index+1}. Company Name ("Employer")
and

John Doe ("Employee")

1. POSITION AND DUTIES
   The Employee shall serve as Software Engineer and perform such duties as are customarily incident to such position.

2. COMPENSATION
   The Employee shall receive an annual salary of $120,000, payable in monthly installments.

3. BENEFITS
   The Employee shall be entitled to participate in all benefit programs that the Employer establishes and makes available to its employees.

4. TERM
   This Agreement shall commence on the Effective Date and continue until terminated by either party.

5. TERMINATION
   Either party may terminate this Agreement at any time, with or without cause, upon {30 + index*10} days written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.
"""

    def save_contract(self, contract: GoldenDatasetContract):
        """Save a contract to the dataset"""
        # Create contracts directory if it doesn't exist
        contracts_dir = self.dataset_dir / "contracts"
        contracts_dir.mkdir(parents=True, exist_ok=True)

        # Serialize contract to dict
        contract_dict = {
            'id': contract.id,
            'title': contract.title,
            'contract_type': contract.contract_type.value,
            'contract_text': contract.contract_text,
            'file_type': contract.file_type,
            'risk_points': [
                {
                    'id': rp.id,
                    'category': rp.category,
                    'severity': rp.severity,
                    'description': rp.description,
                    'clause_text': rp.clause_text,
                    'location': rp.location,
                    'suggestion': rp.suggestion,
                    'citation': rp.citation
                }
                for rp in contract.risk_points
            ],
            'overall_risk': contract.overall_risk.value,
            'compliance_status': contract.compliance_status,
            'metadata': contract.metadata,
            'version': contract.version,
            'created_at': contract.created_at,
            'updated_at': contract.updated_at
        }

        # Save to file
        contract_file = contracts_dir / f"{contract.id}.json"
        with open(contract_file, 'w', encoding='utf-8') as f:
            json.dump(contract_dict, f, indent=2, ensure_ascii=False)

        # Update in-memory storage
        self.contracts[contract.id] = contract

        logger.info(f"Saved contract: {contract.id}")

    def save_dataset_info(self):
        """Save dataset information"""
        if not self.dataset_info:
            return

        info_file = self.dataset_dir / "dataset_info.json"

        # Serialize to dict
        info_dict = {
            'name': self.dataset_info.name,
            'version': self.dataset_info.version,
            'total_contracts': self.dataset_info.total_contracts,
            'total_risk_points': self.dataset_info.total_risk_points,
            'contract_type_distribution': self.dataset_info.contract_type_distribution,
            'severity_distribution': self.dataset_info.severity_distribution,
            'created_at': self.dataset_info.created_at,
            'updated_at': self.dataset_info.updated_at
        }

        # Save to file
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved dataset info: {info_file}")
