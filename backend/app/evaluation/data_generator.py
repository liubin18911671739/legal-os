"""
Mock Data Generator for LegalOS

This module generates realistic mock contract data for testing and validation.
"""

import random
import string
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of contracts"""
    EMPLOYMENT = "employment"
    SALES = "sales"
    LEASE = "lease"
    SERVICE = "service"
    PURCHASE = "purchase"


class RiskCategory(Enum):
    """Categories of legal risks"""
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"


class SeverityLevel(Enum):
    """Severity levels for risks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskPoint:
    """A risk point in a contract"""
    category: RiskCategory
    severity: SeverityLevel
    description: str
    clause_reference: str
    suggested_fix: str


@dataclass
class MockContract:
    """Generated mock contract"""
    id: str
    title: str
    contract_type: ContractType
    contract_text: str
    file_type: str = "txt"
    risk_points: List[RiskPoint] = field(default_factory=list)
    overall_risk: SeverityLevel = SeverityLevel.MEDIUM
    compliance_status: str = "compliant"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContractDataGenerator:
    """Generate realistic mock contract data"""
    
    # Templates for different contract types
    EMPLOYMENT_TEMPLATE = """
劳动合同

甲方：{company_name}
乙方：{employee_name}

第一条 合同期限
本合同期限为{duration}，自{start_date}起至{end_date}止。

第二条 工作内容
乙方担任{position}岗位，负责{responsibilities}。

第三条 劳动报酬
乙方的月工资为{salary}元，甲方于每月{pay_day}日支付上月工资。

第四条 工作时间
乙方实行{work_schedule}工作制。

第五条 保密义务
乙方应当保守甲方的商业秘密和技术秘密，不得泄露给第三方。

第六条 违约责任
任何一方违反本合同约定，应向对方支付{penalty_amount}元违约金。

第七条 争议解决
本合同履行过程中发生争议，双方应协商解决；协商不成的，可向劳动争议仲裁委员会申请仲裁。

甲方（盖章）：{company_name}
乙方（签字）：{employee_name}
日期：{signing_date}
"""

    SALES_TEMPLATE = """
销售合同

买方：{buyer_name}
卖方：{seller_name}

第一条 产品信息
产品名称：{product_name}
规格型号：{product_spec}
数量：{quantity}
单价：{unit_price}元
总价：{total_price}元

第二条 交付方式
卖方应于{delivery_date}前将产品交付至{delivery_address}。

第三条 付款方式
买方应于{payment_deadline}前支付货款{payment_percentage}%。

第四条 质量保证
卖方保证产品质量符合国家标准，如有质量问题应承担{quality_guarantee}责任。

第五条 违约责任
{default_penalty_clause}

买方（盖章）：{buyer_name}
卖方（盖章）：{seller_name}
日期：{signing_date}
"""

    LEASE_TEMPLATE = """
租赁合同

出租方（甲方）：{landlord_name}
承租方（乙方）：{tenant_name}

第一条 租赁物
甲方将位于{property_address}的房产出租给乙方使用。

第二条 租赁期限
租赁期限为{duration}，自{start_date}起至{end_date}止。

第三条 租金
每月租金：{monthly_rent}元
支付方式：{payment_method}
押金：{deposit_amount}元

第四条 使用范围
乙方仅可将租赁物用于{usage_purpose}，不得擅自转租。

第五条 维修责任
{maintenance_clause}

第六条 违约责任
{default_penalty_clause}

甲方（签字）：{landlord_name}
乙方（签字）：{tenant_name}
日期：{signing_date}
"""

    SERVICE_TEMPLATE = """
服务合同

委托方（甲方）：{client_name}
服务方（乙方）：{provider_name}

第一条 服务内容
乙方向甲方提供{service_type}服务。

第二条 服务标准
服务标准：{service_standard}
服务质量要求：{quality_requirements}

第三条 服务期限
服务期限：{duration}，自{start_date}起至{end_date}止。

第四条 服务费用
服务费用：{service_fee}元
支付方式：{payment_method}

第五条 权利义务
甲方权利义务：{client_rights_duties}
乙方权利义务：{provider_rights_duties}

第六条 违约责任
{default_penalty_clause}

甲方（盖章）：{client_name}
乙方（盖章）：{provider_name}
日期：{signing_date}
"""

    PURCHASE_TEMPLATE = """
采购合同

采购方（甲方）：{buyer_name}
供应方（乙方）：{supplier_name}

第一条 采购标的
产品名称：{product_name}
规格型号：{product_spec}
数量：{quantity}
单价：{unit_price}元
总价：{total_price}元

第二条 质量标准
产品质量应符合{quality_standard}标准。

第三条 交货
交货时间：{delivery_date}
交货地点：{delivery_address}

第四条 验收
验收标准：{acceptance_criteria}
验收期限：{acceptance_deadline}

第五条 付款方式
付款时间：{payment_deadline}
付款方式：{payment_method}

第六条 违约责任
{default_penalty_clause}

甲方（盖章）：{buyer_name}
乙方（盖章）：{supplier_name}
日期：{signing_date}
"""

    DEFAULT_PENALTY_CLAUSE = """
任何一方违反本合同约定，应向对方支付合同总金额{penalty_percentage}%的违约金，并赔偿对方因此遭受的全部损失。
"""

    def __init__(self, seed: Optional[int] = None):
        """Initialize data generator
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            random.seed(seed)
        
        # Company names
        self.company_names = [
            "北京科技有限公司", "上海智能科技有限公司", 
            "深圳创新技术有限公司", "杭州数据服务有限公司",
            "广州智能科技有限公司", "成都云计算有限公司",
            "武汉物联网技术有限公司", "南京大数据有限公司",
        ]
        
        # Person names
        self.person_names = [
            "张三", "李四", "王五", "赵六", "孙七",
            "周八", "吴九", "郑十", "刘一", "陈二",
        ]
        
        # Product names
        self.product_names = [
            "智能办公设备", "云计算服务", "数据分析平台",
            "网络安全系统", "企业管理系统",
        ]
        
        # Service types
        self.service_types = [
            "技术支持", "系统集成", "数据服务",
            "咨询服务", "培训服务",
        ]
        
        # Risk templates
        self.risk_templates = {
            RiskCategory.COMPLIANCE: [
                "合同条款不符合《劳动合同法》相关规定",
                "缺少法定必备条款",
                "工作时间安排超出法定标准",
                "保密期限过长，可能违反法律规定",
            ],
            RiskCategory.FINANCIAL: [
                "付款条款不明确，可能导致争议",
                "违约金计算方式不合理",
                "价格调整机制缺失",
                "保证金条款存在风险",
            ],
            RiskCategory.LEGAL: [
                "管辖法院约定可能影响维权",
                "适用法律选择不当",
                "知识产权归属约定不明确",
                "责任限制条款可能无效",
            ],
            RiskCategory.OPERATIONAL: [
                "服务标准定义模糊",
                "交付时间设置不合理",
                "验收标准不具体",
                "变更管理机制缺失",
            ],
        }

    def _generate_random_string(self, length: int = 10) -> str:
        """Generate random string
        
        Args:
            length: String length
            
        Returns:
            Random string
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def _generate_random_date(self, start_offset_days: int = -365, end_offset_days: int = 365) -> str:
        """Generate random date
        
        Args:
            start_offset_days: Days from today to start range
            end_offset_days: Days from today to end range
            
        Returns:
            Date string in YYYY-MM-DD format
        """
        offset_days = random.randint(start_offset_days, end_offset_days)
        date = datetime.now() + timedelta(days=offset_days)
        return date.strftime("%Y-%m-%d")

    def _generate_money(self, min_amount: int = 1000, max_amount: int = 100000) -> str:
        """Generate random money amount
        
        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount
            
        Returns:
            Money string
        """
        amount = random.randint(min_amount, max_amount)
        return f"{amount:,}元"

    def _generate_risk_points(self, contract_type: ContractType, severity: str = "random") -> List[RiskPoint]:
        """Generate risk points for contract
        
        Args:
            contract_type: Type of contract
            severity: Risk severity level
            
        Returns:
            List of risk points
        """
        risks = []
        
        # Determine number of risks based on severity
        if severity == "low":
            num_risks = random.randint(0, 2)
        elif severity == "medium":
            num_risks = random.randint(1, 3)
        else:
            num_risks = random.randint(2, 5)
        
        # Generate risks
        for i in range(num_risks):
            category = random.choice(list(RiskCategory))
            severity_level = random.choice(list(SeverityLevel))
            
            # Get risk description template
            template = random.choice(self.risk_templates[category])
            
            risk = RiskPoint(
                category=category,
                severity=severity_level,
                description=template,
                clause_reference=f"第{random.randint(1, 10)}条",
                suggested_fix="建议修改相关条款以符合法律规定"
            )
            risks.append(risk)
        
        return risks

    def generate_employment_contract(self, index: int) -> MockContract:
        """Generate employment contract
        
        Args:
            index: Contract index
            
        Returns:
            Generated contract
        """
        company = random.choice(self.company_names)
        employee = random.choice(self.person_names)
        
        contract_text = self.EMPLOYMENT_TEMPLATE.format(
            company_name=company,
            employee_name=employee,
            duration=random.choice(["一年", "两年", "三年"]),
            start_date=self._generate_random_date(-30, 0),
            end_date=self._generate_random_date(365, 1095),
            position=random.choice(["软件工程师", "产品经理", "数据分析师", "运营专员"]),
            responsibilities="负责相关岗位的日常工作",
            salary=self._generate_money(5000, 20000),
            pay_day=random.randint(10, 25),
            work_schedule="标准工时制",
            penalty_amount=random.randint(2000, 10000),
            signing_date=self._generate_random_date(-60, -1),
        )
        
        # Generate risk points
        risk_points = self._generate_risk_points(ContractType.EMPLOYMENT)
        
        # Determine overall risk
        if risk_points:
            severity_levels = [r.severity for r in risk_points]
            if any(s == SeverityLevel.HIGH for s in severity_levels):
                overall_risk = SeverityLevel.HIGH
            elif any(s == SeverityLevel.MEDIUM for s in severity_levels):
                overall_risk = SeverityLevel.MEDIUM
            else:
                overall_risk = SeverityLevel.LOW
        else:
            overall_risk = SeverityLevel.LOW
        
        return MockContract(
            id=f"EMP-{index:04d}",
            title=f"{company}与{employee}劳动合同",
            contract_type=ContractType.EMPLOYMENT,
            contract_text=contract_text,
            file_type="txt",
            risk_points=risk_points,
            overall_risk=overall_risk,
            compliance_status="compliant" if overall_risk == SeverityLevel.LOW else "needs_review",
            metadata={
                "company_name": company,
                "employee_name": employee,
                "generated_at": datetime.now().isoformat(),
            }
        )

    def generate_sales_contract(self, index: int) -> MockContract:
        """Generate sales contract
        
        Args:
            index: Contract index
            
        Returns:
            Generated contract
        """
        buyer = random.choice(self.company_names)
        seller = random.choice(self.company_names)
        product = random.choice(self.product_names)
        
        quantity = random.randint(1, 100)
        unit_price = random.randint(1000, 100000)
        total_price = quantity * unit_price
        
        contract_text = self.SALES_TEMPLATE.format(
            buyer_name=buyer,
            seller_name=seller,
            product_name=product,
            product_spec="标准配置",
            quantity=quantity,
            unit_price=f"{unit_price:,}",
            total_price=f"{total_price:,}",
            delivery_date=self._generate_random_date(30, 180),
            delivery_address="北京市朝阳区xxx路xxx号",
            payment_deadline=self._generate_random_date(15, 30),
            payment_percentage=random.choice([30, 50, 100]),
            quality_guarantee="退货、换货、维修",
            default_penalty_clause=self.DEFAULT_PENALTY_CLAUSE.format(penalty_percentage=random.choice([10, 15, 20])),
            signing_date=self._generate_random_date(-60, -1),
        )
        
        risk_points = self._generate_risk_points(ContractType.SALES)
        severity_levels = [r.severity for r in risk_points]
        overall_risk = SeverityLevel.MEDIUM if risk_points else SeverityLevel.LOW
        
        return MockContract(
            id=f"SAL-{index:04d}",
            title=f"{buyer}与{seller}销售合同",
            contract_type=ContractType.SALES,
            contract_text=contract_text,
            file_type="txt",
            risk_points=risk_points,
            overall_risk=overall_risk,
            compliance_status="compliant" if overall_risk == SeverityLevel.LOW else "needs_review",
            metadata={
                "buyer_name": buyer,
                "seller_name": seller,
                "product_name": product,
                "total_price": total_price,
                "generated_at": datetime.now().isoformat(),
            }
        )

    def generate_lease_contract(self, index: int) -> MockContract:
        """Generate lease contract
        
        Args:
            index: Contract index
            
        Returns:
            Generated contract
        """
        landlord = random.choice(self.person_names)
        tenant = random.choice(self.person_names)
        
        contract_text = self.LEASE_TEMPLATE.format(
            landlord_name=landlord,
            tenant_name=tenant,
            property_address="北京市海淀区xxx路xxx号",
            duration=random.choice(["一年", "两年", "三年"]),
            start_date=self._generate_random_date(0, 30),
            end_date=self._generate_random_date(365, 1095),
            monthly_rent=self._generate_money(3000, 15000),
            payment_method="银行转账",
            deposit_amount=self._generate_money(5000, 20000),
            usage_purpose="居住",
            maintenance_clause="甲方负责房屋主体结构维修，乙方负责日常维护",
            default_penalty_clause=self.DEFAULT_PENALTY_CLAUSE.format(penalty_percentage=random.choice([10, 20, 30])),
            signing_date=self._generate_random_date(-60, -1),
        )
        
        risk_points = self._generate_risk_points(ContractType.LEASE)
        severity_levels = [r.severity for r in risk_points]
        overall_risk = SeverityLevel.MEDIUM if risk_points else SeverityLevel.LOW
        
        return MockContract(
            id=f"LEA-{index:04d}",
            title=f"{landlord}与{tenant}租赁合同",
            contract_type=ContractType.LEASE,
            contract_text=contract_text,
            file_type="txt",
            risk_points=risk_points,
            overall_risk=overall_risk,
            compliance_status="compliant" if overall_risk == SeverityLevel.LOW else "needs_review",
            metadata={
                "landlord_name": landlord,
                "tenant_name": tenant,
                "monthly_rent": random.randint(3000, 15000),
                "generated_at": datetime.now().isoformat(),
            }
        )

    def generate_service_contract(self, index: int) -> MockContract:
        """Generate service contract
        
        Args:
            index: Contract index
            
        Returns:
            Generated contract
        """
        client = random.choice(self.company_names)
        provider = random.choice(self.company_names)
        service = random.choice(self.service_types)
        
        contract_text = self.SERVICE_TEMPLATE.format(
            client_name=client,
            provider_name=provider,
            service_type=service,
            service_standard="行业标准",
            quality_requirements="符合双方约定的服务标准",
            duration=random.choice(["六个月", "一年", "两年"]),
            start_date=self._generate_random_date(0, 30),
            end_date=self._generate_random_date(180, 730),
            service_fee=self._generate_money(50000, 500000),
            payment_method="分期付款",
            client_rights_duties="提供必要的协助和支持",
            provider_rights_duties="提供符合约定的服务",
            default_penalty_clause=self.DEFAULT_PENALTY_CLAUSE.format(penalty_percentage=random.choice([10, 15, 20])),
            signing_date=self._generate_random_date(-60, -1),
        )
        
        risk_points = self._generate_risk_points(ContractType.SERVICE)
        severity_levels = [r.severity for r in risk_points]
        overall_risk = SeverityLevel.MEDIUM if risk_points else SeverityLevel.LOW
        
        return MockContract(
            id=f"SVC-{index:04d}",
            title=f"{client}与{provider}服务合同",
            contract_type=ContractType.SERVICE,
            contract_text=contract_text,
            file_type="txt",
            risk_points=risk_points,
            overall_risk=overall_risk,
            compliance_status="compliant" if overall_risk == SeverityLevel.LOW else "needs_review",
            metadata={
                "client_name": client,
                "provider_name": provider,
                "service_type": service,
                "generated_at": datetime.now().isoformat(),
            }
        )

    def generate_purchase_contract(self, index: int) -> MockContract:
        """Generate purchase contract
        
        Args:
            index: Contract index
            
        Returns:
            Generated contract
        """
        buyer = random.choice(self.company_names)
        supplier = random.choice(self.company_names)
        product = random.choice(self.product_names)
        
        quantity = random.randint(10, 1000)
        unit_price = random.randint(100, 50000)
        total_price = quantity * unit_price
        
        contract_text = self.PURCHASE_TEMPLATE.format(
            buyer_name=buyer,
            supplier_name=supplier,
            product_name=product,
            product_spec="标准配置",
            quantity=quantity,
            unit_price=f"{unit_price:,}",
            total_price=f"{total_price:,}",
            quality_standard="国家标准",
            delivery_date=self._generate_random_date(30, 180),
            delivery_address="北京市朝阳区xxx路xxx号",
            acceptance_criteria="符合国家标准和双方约定",
            acceptance_deadline=self._generate_random_date(30, 45),
            payment_deadline=self._generate_random_date(45, 60),
            payment_method="银行承兑汇票",
            default_penalty_clause=self.DEFAULT_PENALTY_CLAUSE.format(penalty_percentage=random.choice([5, 10, 15])),
            signing_date=self._generate_random_date(-60, -1),
        )
        
        risk_points = self._generate_risk_points(ContractType.PURCHASE)
        severity_levels = [r.severity for r in risk_points]
        overall_risk = SeverityLevel.MEDIUM if risk_points else SeverityLevel.LOW
        
        return MockContract(
            id=f"PUR-{index:04d}",
            title=f"{buyer}与{supplier}采购合同",
            contract_type=ContractType.PURCHASE,
            contract_text=contract_text,
            file_type="txt",
            risk_points=risk_points,
            overall_risk=overall_risk,
            compliance_status="compliant" if overall_risk == SeverityLevel.LOW else "needs_review",
            metadata={
                "buyer_name": buyer,
                "supplier_name": supplier,
                "product_name": product,
                "total_price": total_price,
                "generated_at": datetime.now().isoformat(),
            }
        )

    def generate_contracts(
        self,
        num_contracts: int = 100,
        contract_types: Optional[List[ContractType]] = None
    ) -> List[MockContract]:
        """Generate multiple contracts
        
        Args:
            num_contracts: Number of contracts to generate
            contract_types: Types of contracts to generate (all if None)
            
        Returns:
            List of generated contracts
        """
        if contract_types is None:
            contract_types = list(ContractType)
        
        contracts = []
        for i in range(num_contracts):
            contract_type = random.choice(contract_types)
            
            if contract_type == ContractType.EMPLOYMENT:
                contract = self.generate_employment_contract(i)
            elif contract_type == ContractType.SALES:
                contract = self.generate_sales_contract(i)
            elif contract_type == ContractType.LEASE:
                contract = self.generate_lease_contract(i)
            elif contract_type == ContractType.SERVICE:
                contract = self.generate_service_contract(i)
            elif contract_type == ContractType.PURCHASE:
                contract = self.generate_purchase_contract(i)
            else:
                # Default to employment
                contract = self.generate_employment_contract(i)
            
            contracts.append(contract)
        
        logger.info(f"Generated {len(contracts)} mock contracts")
        return contracts

    def generate_dataset(
        self,
        num_contracts: int = 100,
        output_dir: str = "data/evaluation/mock"
    ) -> Dict[str, Any]:
        """Generate complete dataset
        
        Args:
            num_contracts: Number of contracts to generate
            output_dir: Directory to save dataset
            
        Returns:
            Dataset information
        """
        from pathlib import Path
        
        # Generate contracts
        contracts = self.generate_contracts(num_contracts)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save contracts
        contracts_dir = output_path / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        
        # Save each contract as JSON
        contract_data = []
        for contract in contracts:
            import json
            
            contract_file = contracts_dir / f"{contract.id}.json"
            with open(contract_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "id": contract.id,
                    "title": contract.title,
                    "contract_type": contract.contract_type.value,
                    "contract_text": contract.contract_text,
                    "file_type": contract.file_type,
                    "risk_points": [
                        {
                            "category": r.category.value,
                            "severity": r.severity.value,
                            "description": r.description,
                            "clause_reference": r.clause_reference,
                            "suggested_fix": r.suggested_fix,
                        }
                        for r in contract.risk_points
                    ],
                    "overall_risk": contract.overall_risk.value,
                    "compliance_status": contract.compliance_status,
                    "metadata": contract.metadata,
                }, f, ensure_ascii=False, indent=2)
            
            contract_data.append({
                "id": contract.id,
                "file_path": str(contract_file),
                "contract_type": contract.contract_type.value,
                "overall_risk": contract.overall_risk.value,
                "num_risks": len(contract.risk_points),
            })
        
        # Generate dataset info
        from collections import Counter
        
        type_distribution = Counter([c.contract_type.value for c in contracts])
        severity_distribution = Counter([c.overall_risk.value for c in contracts])
        
        dataset_info = {
            "name": "Mock Dataset",
            "version": "1.0",
            "total_contracts": len(contracts),
            "total_risk_points": sum(len(c.risk_points) for c in contracts),
            "contract_type_distribution": dict(type_distribution),
            "severity_distribution": dict(severity_distribution),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Save dataset info
        info_file = output_path / "dataset_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dataset saved to {output_path}")
        logger.info(f"Total contracts: {dataset_info['total_contracts']}")
        logger.info(f"Type distribution: {dataset_info['contract_type_distribution']}")
        
        return dataset_info


def main():
    """Generate sample dataset"""
    generator = ContractDataGenerator(seed=42)
    
    # Generate 100 contracts
    dataset_info = generator.generate_dataset(
        num_contracts=100,
        output_dir="data/evaluation/mock"
    )
    
    print(f"✅ Dataset generated successfully!")
    print(f"   Total contracts: {dataset_info['total_contracts']}")
    print(f"   Output directory: data/evaluation/mock")
    print(f"   Type distribution: {dataset_info['contract_type_distribution']}")
    print(f"   Severity distribution: {dataset_info['severity_distribution']}")


if __name__ == "__main__":
    main()
