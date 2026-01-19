# 数据生成和验证系统 - 使用指南

## 快速开始

本指南介绍如何使用 LegalOS 的模拟数据生成和验证系统。

## 1. 生成模拟数据

### 命令行使用

```bash
# 生成 100 个模拟合同（默认）
cd backend
python3 -m app.evaluation.data_generator

# 生成指定数量的合同
python3 -m app.evaluation.data_generator --num-contracts 200

# 使用随机种子（确保可重现性）
python3 -m app.evaluation.data_generator --seed 42

# 生成到自定义目录
python3 -m app.evaluation.data_generator --output-dir data/evaluation/custom
```

### Python API 使用

```python
from app.evaluation.data_generator import ContractDataGenerator

# 创建生成器（可选：指定随机种子）
generator = ContractDataGenerator(seed=42)

# 生成 100 个合同
contracts = generator.generate_contracts(num_contracts=100)

# 生成完整数据集（包含 dataset_info.json）
dataset_info = generator.generate_dataset(
    num_contracts=100,
    output_dir="data/evaluation/generated"
)

# 生成特定类型的合同
employment_contract = generator.generate_employment_contract(0)
sales_contract = generator.generate_sales_contract(1)
```

### 生成的数据结构

```
data/evaluation/generated/
├── contracts/
│   ├── EMP-0001.json
│   ├── SAL-0001.json
│   └── ...
└── dataset_info.json
```

每个合同 JSON 包含：
```json
{
  "id": "EMP-0001",
  "title": "合同标题",
  "contract_type": "employment",
  "contract_text": "完整合同文本",
  "file_type": "txt",
  "risk_points": [...],
  "overall_risk": "medium",
  "compliance_status": "needs_review",
  "metadata": {...}
}
```

## 2. 验证数据质量

### 命令行使用

```bash
# 验证已生成的数据集
python3 -m app.evaluation.data_validator

# 验证自定义数据集
python3 -m app.evaluation.data_validator --dataset-path data/evaluation/custom
```

### Python API 使用

```python
from app.evaluation.data_validator import DataValidator

# 创建验证器
validator = DataValidator()

# 验证整个数据集
report = validator.validate_dataset("data/evaluation/generated")

# 质量评分
quality_score = report.summary.get('data_quality_score', 0)
print(f"数据质量评分: {quality_score}")

# 查看详细问题
for issue in report.issues:
    if not issue.passed:
        print(f"[{issue.severity.value}] {issue.message}")
        if issue.location:
            print(f"  位置: {issue.location}")
```

### 验证检查项

- **结构验证**
  - 必填字段完整性
  - 目录结构正确性
  - 文件格式正确性

- **内容验证**
  - 合同文本长度合理性
  - 必需条款存在性
  - 占位符检测
  - TODO/FIXME 标记检测

- **数据验证**
  - 风险点结构完整性
  - 严重级别有效性
  - 元数据时间戳格式

- **一致性验证**
  - 合同数量一致性
  - 类型分布合理性
  - 数据集信息正确性

### 质量评分

- 100 分：完美
- 90-99 分：优秀
- 80-89 分：良好
- 70-79 分：一般
- < 70 分：需要改进

## 3. API 端点

### 3.1 生成数据

```bash
# 生成 100 个模拟合同
curl -X POST http://localhost:8000/api/v1/evaluation/data/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_contracts": 100,
    "output_dir": "data/evaluation/generated",
    "seed": 42
  }'

# 返回示例
{
  "message": "Mock data generated successfully",
  "dataset_info": {
    "name": "Mock Dataset",
    "version": "1.0",
    "total_contracts": 100,
    "total_risk_points": 250,
    "contract_type_distribution": {
      "employment": 20,
      "sales": 20,
      ...
    },
    "severity_distribution": {
      "low": 40,
      "endium": 40,
      "high": 20
    }
  }
}
```

### 3.2 验证数据

```bash
# 验证数据集
curl -X POST http://localhost:8000/api/v1/evaluation/data/validate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/evaluation/generated"
  }'

# 返回示例
{
  "validation_report": {
    "dataset_path": "data/evaluation/generated",
    "validation_date": "...",
    "summary": {
      "total_checks": 50,
      "passed_checks": 45,
      "failed_checks": 5,
      "data_quality_score": 90.0,
      "total_contracts": 100,
      "contract_type_distribution": {...},
      "severity_distribution": {...}
    },
    "issues": [
      {
        "check_name": "required_sections",
        "passed": false,
        "severity": "warning",
        "message": "Missing required sections: [违约责任]",
        "location": "contracts/EMP-0001.json",
        "details": {"missing_sections": [...]}
      },
      ...
    ]
  }
}
```

### 3.3 生成并验证（一键）

```bash
# 一键生成并验证数据
curl -X POST http://localhost:8000/api/v1/evaluation/data/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{
    "num_contracts": 100,
    "seed": 42
  }'

# 返回生成和验证的完整结果
{
  "generation": {...},
  "validation": {...}
}
```

### 3.4 获取质量报告

```bash
# 获取所有数据集的质量汇总
curl http://localhost:8000/api/v1/evaluation/data/quality-report

# 返回示例
{
  "total_datasets": 3,
  "average_quality_score": 88.5,
  "total_issues": 15,
  "total_checks": 150,
  "pass_rate": 0.90,
  "reports": [...]
}
```

### 3.5 获取验证报告

```bash
# 获取特定数据集的验证报告
curl "http://localhost:8000/api/v1/evaluation/data/validate/report?dataset_path=data/evaluation/generated"
```

## 4. 典型使用场景

### 场景 1: 生成测试数据

```bash
# 生成 50 个劳动合同用于测试
python3 -m app.evaluation.data_generator --num-contracts 50 --seed 100
```

### 场景 2: 验证数据质量

```bash
# 验证生成的数据
python3 -m app.evaluation.data_validator

# 如果质量评分低于 80，需要修复问题
```

### 场景 3: 通过 API 生成和验证

```bash
# 通过 API 生成 200 个合同
curl -X POST http://localhost:8000/api/v1/evaluation/data/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_contracts": 200,
    "seed": 123
  }' | jq .

# 验证数据质量
curl -X POST http://localhost:8000/api/v1/evaluation/data/validate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "data/evaluation/generated"
  }' | jq '.validation_report.summary.data_quality_score'
```

### 场景 4: 一键生成和验证（推荐）

```bash
# 生成 100 个合同并验证质量
curl -X POST http://localhost:8000/api/v1/evaluation/data/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{
    "num_contracts": 100,
    "seed": 42
  }' | jq '.validation.report.summary.data_quality_score'
```

## 5. 数据质量标准

### 推荐阈值

- **测试环境**：质量评分 ≥ 80 分
- **开发环境**：质量评分 ≥ 85 分
- **生产环境**：质量评分 ≥ 90 分

### 评分指南

| 评分范围 | 质量 | 建议 |
|---------|------|------|
| 90-100 | 优秀 | 可以用于生产 |
| 80-89 | 良好 | 可以用于测试 |
| 70-79 | 一般 | 需要修复 |
| < 70 | 差 | 不能使用 |

## 6. 故障排查

### 数据生成失败

**问题**：无法生成数据集

**解决方案**：
1. 检查输出目录权限
2. 确保有足够磁盘空间
3. 查看日志文件

### 验证报告无结果

**问题**：返回空报告

**解决方案**：
1. 确认数据集路径正确
2. 检查数据集是否包含 contracts 目录
3. 查看服务器日志

### API 调用失败

**问题**：404 或 500 错误

**解决方案**：
1. 确认后端服务正在运行
2. 检查 API 路由已注册
3. 查看 API 日志：`docker-compose logs backend`

## 7. 最佳实践

### 数据生成

1. **使用随机种子**：确保可重现性
2. **合理配置数量**：根据测试需求选择
3. **多样化类型**：生成多种合同类型
4. **定期更新模板**：根据实际案例改进

### 数据验证

1. **定期验证**：在数据生成后立即验证
2. **修复问题**：根据验证报告修复数据问题
3. **持续监控**：定期检查数据质量
4. **版本控制**：为不同版本的数据集打标签

### 性能优化

1. **批量操作**：避免逐个处理
2. **缓存结果**：验证报告可重用
3. **异步处理**：大数据集使用异步
4. **并行验证**：多个数据集可并行验证

## 8. 进阶使用

### 自定义合同模板

编辑 `backend/app/evaluation/data_generator.py` 中的模板常量：

```python
CUSTOM_TEMPLATE = """
自定义合同模板

甲方：{company_name}
...
"""

# 在 ContractDataGenerator 类中添加自定义生成方法
def generate_custom_contract(self, index: int) -> MockContract:
    # 使用自定义模板
    contract_text = self.CUSTOM_TEMPLATE.format(...)
    # ...
```

### 自定义验证规则

编辑 `backend/app/evaluation/data_validator.py` 中的验证逻辑：

```python
def custom_validation_check(self, contract_data: Dict[str, Any]) -> List[ValidationResult]:
    results = []
    # 自定义验证逻辑
    if "特定条件" not in contract_data:
        results.append(...)
    return results
```

### 集成到工作流

将数据生成和验证集成到 CI/CD 流程：

```yaml
# .github/workflows/generate-data.yml
name: Generate Test Data
on: [schedule]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Data
        run: |
          cd backend
          python3 -m app.evaluation.data_generator --num-contracts 100
      - name: Validate Data
        run: |
          python3 -m app.evaluation.data_validator
```

## 9. 相关文档

- [docs/DATA_GENERATION_VALIDATION_COMPLETE.md](DATA_GENERATION_VALIDATION_COMPLETE.md) - 完成报告
- [backend/app/evaluation/data_generator.py](backend/app/evaluation/data_generator.py) - 源代码
- [backend/app/evaluation/data_validator.py](backend/app/evaluation/data_validator.py) - 源代码
- [backend/app/api/v1/evaluation.py](backend/app/api/v1/evaluation.py) - API 端点

## 10. 联系与支持

如有问题或建议，请提交 GitHub Issue。
