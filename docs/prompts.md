
请帮我搭建一个基于多Agent的RAG法律分析与合同审查系统，具体要求如下：

### 一、项目基本信息

**项目名称：** LegalOS - 企业级法律智能分析系统

**技术栈：**
- 前端：Next.js 14 + React 18 + TypeScript + Tailwind CSS + shadcn/ui
- 后端：Python 3.11 + FastAPI + Pydantic v2
- 数据库：PostgreSQL 15 + pgvector (向量存储)
- 向量库：Qdrant 或 Chroma
- LLM：智谱清言 GLM-4-Plus API
- 框架：LangChain / LangGraph (多Agent编排)
- 检索：混合检索 (向量 + BM25 + Reranker)
- 监控：LangSmith / LangFuse (可观测性)

**项目结构：**
```

legal-os/

├── frontend/                 # Next.js前端

│   ├── src/

│   │   ├── app/             # App Router

│   │   ├── components/      # React组件

│   │   ├── lib/             # 工具函数

│   │   └── types/           # TypeScript类型

│   ├── package.json

│   └── tsconfig.json

├── backend/                  # FastAPI后端

│   ├── app/

│   │   ├── agents/          # 多Agent定义

│   │   ├── rag/             # RAG检索模块

│   │   ├── models/          # 数据模型

│   │   ├── api/             # API路由

│   │   ├── services/        # 业务逻辑

│   │   └── utils/           # 工具函数

│   ├── tests/               # 测试代码

│   ├── requirements.txt

│   └── [main.py](http://main.py)

├── data/                     # 数据目录

│   ├── contracts/           # 合同文档

│   ├── regulations/         # 法规文档

│   └── templates/           # 合同模板

├── docker-compose.yml       # Docker编排

└── [README.md](http://README.md)

```

### 二、核心功能模块

#### 2.1 多Agent协作架构

使用LangGraph实现以下Agent：

**1. 协调Agent (Coordinator Agent)**
- 职责：接收用户请求，理解意图，分配任务给专业Agent
- 输入：用户查询 + 上传的合同文件
- 输出：任务分解计划

**2. 检索Agent (Retrieval Agent)**
- 职责：从公司知识库中检索相关法律条款、案例、模板
- 策略：
  - 查询改写（Query Rewriting）
  - 混合检索（向量相似度 + BM25）
  - 重排序（使用bge-reranker-v2-m3）
- 输出：Top-K相关文档片段（带置信度分数）

**3. 分析Agent (Analysis Agent)**
- 职责：分析合同条款，识别关键要素
- 任务：
  - 实体抽取（甲乙方、金额、期限、违约条款等）
  - 条款分类（权利义务、违约责任、争议解决等）
  - 风险点识别
- 输出：结构化分析结果

**4. 审查Agent (Review Agent)**
- 职责：对照公司标准模板和法规进行合规性审查
- 检查项：
  - 必备条款完整性
  - 条款措辞合规性
  - 与公司政策的一致性
  - 潜在法律风险
- 输出：审查意见列表（每条带风险等级：高/中/低）

**5. 验证Agent (Validation Agent)**
- 职责：交叉验证分析结果，检测幻觉
- 方法：
  - 多次采样一致性检查
  - 引用溯源验证
  - 置信度评分
- 输出：验证通过/失败 + 置信度分数

**6. 报告Agent (Report Agent)**
- 职责：生成结构化审查报告
- 格式：
  - 执行摘要
  - 详细发现（分类呈现）
  - 修改建议（具体条款 + 改写方案）
  - 风险等级矩阵
- 输出：Markdown格式报告 + JSON结构化数据

Agent流程图（使用LangGraph State Machine）：
```

用户请求 → 协调Agent → 检索Agent → 分析Agent → 审查Agent → 验证Agent → 报告Agent → 返回结果

↓                                              ↑

└──────────── (失败重试/人工介入) ──────────────┘

```

#### 2.2 RAG检索增强模块

**数据处理Pipeline：**

1. **文档加载**
   - 支持格式：PDF, DOCX, TXT, HTML
   - 使用：PyMuPDF (PDF), python-docx (DOCX)
   - 元数据提取：文档类型、创建日期、作者、版本

2. **文档切分**
   - 策略：递归字符切分 + 语义切分
   - Chunk大小：512-1024 tokens (根据模型上下文窗口调整)
   - Overlap：100-200 tokens
   - 保留结构信息：章节标题、条款编号

3. **向量化**
   - Embedding模型：bge-large-zh-v1.5 或 m3e-base
   - 维度：1024 (bge) 或 768 (m3e)
   - 批处理大小：32-64

4. **混合检索**
```

# 伪代码

vector_results = vector_search(query_embedding, top_k=20)

bm25_results = bm25_search(query_text, top_k=20)

merged_results = reciprocal_rank_fusion(vector_results, bm25_results)

reranked_results = reranker(query, merged_results, top_k=5)

```

5. **后处理**
   - 去重
   - 上下文拼接（相邻Chunk合并）
   - 引用标注（chunk_id → 原文档位置）

**知识库结构：**
- **合同模板库**：公司标准合同模板（销售、采购、服务、保密等）
- **法规库**：民法典、合同法、公司法等相关法条
- **判例库**：相关领域典型案例（匿名化处理）
- **内部规范**：公司法务审批规范、条款库

#### 2.3 智谱清言大模型集成

**API配置：**
```

from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your-api-key")

# Agent使用的模型配置

AGENT_MODEL_CONFIG = {

"coordinator": "glm-4-plus",      # 需要强推理能力

"retrieval": "glm-4-flash",       # 查询改写，速度优先

"analysis": "glm-4-plus",         # 复杂分析任务

"review": "glm-4-plus",           # 需要专业判断

"validation": "glm-4-flash",      # 快速验证

"report": "glm-4-long",           # 长文本生成

}

# 通用调用函数

def call_zhipu_llm(

messages: list,

model: str = "glm-4-plus",

temperature: float = 0.1,

max_tokens: int = 2000,

stream: bool = False

):

response = [client.chat](http://client.chat).completions.create(

model=model,

messages=messages,

temperature=temperature,

max_tokens=max_tokens,

stream=stream

)

return response

```

**Prompt工程规范：**
- 系统提示词：定义Agent角色、专业领域、输出格式
- Few-shot示例：提供2-3个高质量示例
- 思维链（CoT）：引导逐步推理
- 结构化输出：使用JSON Schema约束输出格式

#### 2.4 前端界面设计

**核心页面：**

1. **合同上传页** (`/upload`)
   - 拖拽上传或点击选择
   - 支持多文件批量上传
   - 文件类型验证 + 大小限制（单个<10MB）
   - 上传进度条

2. **分析进度页** (`/analysis/[id]`)
   - 实时显示Agent执行状态
   - 进度条 + 阶段说明
   - WebSocket实时通信
   - 支持中途取消

3. **审查报告页** (`/report/[id]`)
   - 左侧：原文档预览（PDF.js）
   - 右侧：分析结果面板
     - Tab1: 执行摘要（风险等级、关键发现）
     - Tab2: 逐条审查意见（可筛选风险等级）
     - Tab3: 修改建议（对比视图）
     - Tab4: 引用溯源（点击跳转到知识库原文）
   - 支持导出：PDF、DOCX、JSON

4. **知识库管理页** (`/knowledge`)
   - 文档列表（搜索、筛选、分类）
   - 批量上传
   - 向量化状态监控
   - 文档预览 + 编辑

5. **评测面板页** (`/evaluation`)
   - 测试集管理
   - 评测任务配置（选择基线、对比版本）
   - 结果对比（准确率、召回率、F1、幻觉率）
   - 可视化图表（echarts）

**UI组件库（shadcn/ui）：**
- Button, Input, Textarea
- Card, Tabs, Dialog, Sheet
- Table, Badge, Progress
- Toast (消息提示)
- Skeleton (加载占位)

#### 2.5 后端API设计

**RESTful API端点：**

```

# 合同分析

POST /api/v1/contracts/analyze

Body: { file: File, options: AnalysisOptions }

Response: { task_id: str, status: "pending" }

# 查询任务状态

GET /api/v1/tasks/{task_id}

Response: { 

task_id: str, 

status: "pending" | "running" | "completed" | "failed",

progress: float,

current_stage: str,

result?: AnalysisResult

}

# WebSocket实时推送

WS /api/v1/tasks/{task_id}/stream

Events: 

- { type: "progress", stage: str, progress: float }
- { type: "result", data: AnalysisResult }
- { type: "error", message: str }

# 知识库管理

POST /api/v1/knowledge/upload

GET /api/v1/knowledge/documents

DELETE /api/v1/knowledge/documents/{doc_id}

# RAG检索测试

POST /api/v1/rag/search

Body: { query: str, top_k: int, filters?: dict }

Response: { results: [{ text: str, score: float, source: str }] }

# 评测

POST /api/v1/evaluation/run

GET /api/v1/evaluation/results/{eval_id}

```

**数据模型（Pydantic）：**

```

from pydantic import BaseModel, Field

from typing import List, Optional, Literal

from datetime import datetime

class DocumentChunk(BaseModel):

chunk_id: str

text: str

metadata: dict

embedding: Optional[List[float]] = None

class RetrievalResult(BaseModel):

chunk_id: str

text: str

score: float

source_doc: str

source_page: Optional[int] = None

class RiskItem(BaseModel):

category: str

description: str

severity: Literal["high", "medium", "low"]

clause_text: str

suggestion: Optional[str] = None

confidence: float

class AnalysisResult(BaseModel):

contract_id: str

summary: str

entities: dict  # {"parties": [...], "amount": ..., "duration": ...}

risks: List[RiskItem]

compliance_score: float

suggestions: List[str]

created_at: datetime

```

#### 2.6 评测体系设计

**评测数据集构建：**

1. **黄金标注集**（50-100个样本）
   - 真实合同样本（脱敏处理）
   - 人工标注：风险点、必备条款、合规性判断
   - 标注规范文档

2. **评测指标：**
   - **准确率**：风险点识别准确率
   - **召回率**：覆盖所有真实风险点的比例
   - **F1 Score**：准召综合指标
   - **幻觉率**：生成内容中不实信息的比例
   - **引用准确率**：引用是否对应正确的源文档
   - **响应时间**：端到端处理耗时
   - **成本**：单次分析的Token消耗

3. **对比基线：**
   - Baseline v1：无RAG，纯LLM直接分析
   - Baseline v2：简单RAG（仅向量检索）
   - Target：多Agent + 混合检索 + 验证机制

4. **评测脚本：**
```

# tests/eval_contract_[review.py](http://review.py)

import json

from app.agents import ContractReviewPipeline

from ragas import evaluate

from ragas.metrics import (

faithfulness,

answer_relevancy,

context_precision,

context_recall

)

def run_evaluation(test_set_path: str):

with open(test_set_path) as f:

test_cases = json.load(f)

results = []

for case in test_cases:

prediction = [ContractReviewPipeline.run](http://ContractReviewPipeline.run)(

contract_file=case["file"],

ground_truth=case["ground_truth"]

)

results.append({

"case_id": case["id"],

"prediction": prediction,

"ground_truth": case["ground_truth"],

"metrics": compute_metrics(prediction, case["ground_truth"])

})

return generate_report(results)

```

### 三、部署与运维

#### 3.1 Docker容器化

```

# docker-compose.yml

version: '3.8'

services:

frontend:

build: ./frontend

ports:

- "3000:3000"

environment:

- NEXT_PUBLIC_API_URL=http://backend:8000

depends_on:

- backend

backend:

build: ./backend

ports:

- "8000:8000"

environment:

- DATABASE_URL=postgresql://legal_user:password@postgres:5432/legal_os
- ZHIPU_API_KEY=${ZHIPU_API_KEY}
- QDRANT_URL=http://qdrant:6333

depends_on:

- postgres
- qdrant

volumes:

- ./data:/app/data

postgres:

image: pgvector/pgvector:pg15

environment:

- POSTGRES_DB=legal_os
- POSTGRES_USER=legal_user
- POSTGRES_PASSWORD=password

volumes:

- postgres_data:/var/lib/postgresql/data

ports:

- "5432:5432"

qdrant:

image: qdrant/qdrant:latest

ports:

- "6333:6333"

volumes:

- qdrant_data:/qdrant/storage

redis:

image: redis:7-alpine

ports:

- "6379:6379"

volumes:

- redis_data:/data

volumes:

postgres_data:

qdrant_data:

redis_data:

```

#### 3.2 可观测性

**日志系统：**
- 使用structlog结构化日志
- 日志级别：DEBUG, INFO, WARNING, ERROR
- 记录关键节点：Agent调用、检索结果、LLM请求/响应、错误堆栈

**监控指标：**
- Agent执行成功率
- 各Agent平均耗时
- LLM API调用次数 + Token消耗
- 检索召回率（通过埋点测试集验证）
- 系统QPS、响应时间P50/P95/P99

**追踪系统：**
- 使用LangSmith或LangFuse
- 完整请求链路追踪
- 支持回放与调试

### 四、开发计划

**Phase 1（Week 1-2）：基础架构**
- [ ] 项目脚手架搭建
- [ ] 数据库设计 + ORM配置
- [ ] 基础API框架（FastAPI + CRUD）
- [ ] 前端页面框架（Next.js + 基础布局）
- [ ] Docker环境配置

**Phase 2（Week 3-4）：RAG模块**
- [ ] 文档加载与切分
- [ ] Embedding + 向量存储（Qdrant）
- [ ] 混合检索实现（向量 + BM25）
- [ ] 重排序集成
- [ ] 检索API + 前端测试界面

**Phase 3（Week 5-6）：多Agent系统**
- [ ] LangGraph工作流搭建
- [ ] 6个Agent的实现（协调、检索、分析、审查、验证、报告）
- [ ] 智谱清言API集成
- [ ] Agent间状态传递与错误处理

**Phase 4（Week 7-8）：功能完善**
- [ ] 合同上传 + 分析完整流程
- [ ] 实时进度推送（WebSocket）
- [ ] 审查报告生成与展示
- [ ] 报告导出功能（PDF/DOCX）

**Phase 5（Week 9-10）：评测与优化**
- [ ] 构建评测数据集（50个标注样本）
- [ ] 实现评测脚本
- [ ] Baseline对比实验
- [ ] 根据评测结果优化Prompt和检索策略
- [ ] 性能优化（缓存、异步处理、批处理）

**Phase 6（Week 11-12）：运维与交付**
- [ ] 日志与监控系统
- [ ] 用户文档编写
- [ ] 部署到生产环境
- [ ] 压力测试 + 稳定性验证

### 五、关键技术细节

#### 5.1 Prompt工程示例

**分析Agent的系统提示词：**

```

ANALYSIS_AGENT_PROMPT = """

你是一位资深法律分析师，专门负责合同条款分析和实体抽取。

【任务】

从用户提供的合同文本中，提取以下关键信息：

1. 合同主体：甲方、乙方的完整名称和基本信息
2. 合同标的：交易内容、数量、质量标准
3. 金额条款：总价、付款方式、付款节点
4. 时间条款：生效日期、履行期限、交付时间
5. 违约责任：违约情形、违约金、赔偿方式
6. 争议解决：管辖法院、仲裁机构

【上下文】

以下是从公司知识库中检索到的相关参考文档：

{retrieved_context}

【合同原文】

{contract_text}

【输出格式】

请严格按照以下JSON格式输出，不要添加任何额外的解释：

```json
{
  "parties": {
    "party_a": {"name": "...", "type": "...", "contact": "..."},
    "party_b": {"name": "...", "type": "...", "contact": "..."}
  },
  "subject": {"description": "...", "quantity": "...", "quality": "..."},
  "amount": {"total": "...", "currency": "CNY", "payment_terms": [...]},
  "timeline": {"effective_date": "YYYY-MM-DD", "duration": "...", "delivery": "..."},
  "liability": [{"scenario": "...", "consequence": "...", "penalty": "..."}],
  "dispute_resolution": {"method": "仲裁/诉讼", "jurisdiction": "..."}
}
```

【注意事项】

1. 只提取合同中明确出现的信息，不要推测或编造
2. 如果某项信息缺失，对应字段填写null
3. 金额数字保留两位小数
4. 日期统一格式为YYYY-MM-DD
5. 如果某条款存在歧义，在confidence字段标注0.0-1.0的置信度

"""

```

**审查Agent的系统提示词：**

```

REVIEW_AGENT_PROMPT = """

你是一位严谨的法律审查专员，负责对合同进行合规性审查。

【审查维度】

1. **必备条款完整性**：核对是否包含法律规定的必备条款
2. **条款措辞合规性**：检查是否存在违反法律法规的表述
3. **公司政策一致性**：对照公司标准模板，检查偏离项
4. **风险条款识别**：标记可能对公司不利的条款
5. **履约可行性**：评估条款是否具备可执行性

【参考标准】

公司标准合同模板：

{company_template}

相关法律法规：

{legal_regulations}

【待审查合同】

{contract_analysis}

【输出格式】

请按照以下结构输出审查意见：

```json
{
  "overall_score": 75.5,  // 0-100分，综合合规评分
  "risk_level": "medium",  // high/medium/low
  "findings": [
    {
      "id": "RISK-001",
      "category": "缺失必备条款",
      "severity": "high",  // high/medium/low
      "description": "合同未明确约定知识产权归属条款",
      "clause_reference": null,
      "legal_basis": "《民法典》第123条",
      "suggestion": "建议增加条款：本合同项下产生的知识产权归甲方所有",
      "confidence": 0.95
    },
    {
      "id": "RISK-002",
      "category": "不利条款",
      "severity": "medium",
      "description": "违约金比例过高（总价的30%），可能被法院调整",
      "clause_reference": "第8.2条",
      "legal_basis": "《民法典》第585条 - 违约金过高调整规则",
      "suggestion": "建议将违约金比例调整为10%-20%，符合司法实践",
      "confidence": 0.88
    }
  ],
  "compliance_checks": {
    "mandatory_clauses": {"score": 80, "missing": ["知识产权归属"]},
    "legal_compliance": {"score": 90, "issues": []},
    "company_policy": {"score": 70, "deviations": ["付款周期超出标准30天"]}
  },
  "summary": "该合同整体风险等级为中等。主要问题在于..."
}
```

【审查原则】

1. 客观：基于事实和法律条文，不带主观偏见
2. 严谨：引用具体法条和公司规范，可追溯
3. 实用：提供可操作的修改建议
4. 分级：准确标注风险等级，帮助优先处理

"""

```

#### 5.2 LangGraph工作流实现

```

from langgraph.graph import StateGraph, END

from typing import TypedDict, Annotated, Sequence

import operator

class AgentState(TypedDict):

contract_text: str

retrieved_docs: list

analysis_result: dict

review_result: dict

validation_result: dict

final_report: str

errors: Sequence[str]

def coordinator_node(state: AgentState):

"""协调节点：任务分解"""

# 这里可以添加意图识别逻辑

return state

def retrieval_node(state: AgentState):

"""检索节点"""

query = state["contract_text"][:500]  # 使用前500字作为查询

retrieved = hybrid_search(query, top_k=5)

return {"retrieved_docs": retrieved}

def analysis_node(state: AgentState):

"""分析节点"""

prompt = ANALYSIS_AGENT_PROMPT.format(

contract_text=state["contract_text"],

retrieved_context="n".join([doc["text"] for doc in state["retrieved_docs"]])

)

response = call_zhipu_llm(

messages=[{"role": "user", "content": prompt}],

model="glm-4-plus"

)

analysis = parse_json_response(response)

return {"analysis_result": analysis}

def review_node(state: AgentState):

"""审查节点"""

prompt = REVIEW_AGENT_PROMPT.format(

contract_analysis=state["analysis_result"],

company_template=load_company_template(),

legal_regulations=load_regulations()

)

response = call_zhipu_llm(

messages=[{"role": "user", "content": prompt}],

model="glm-4-plus"

)

review = parse_json_response(response)

return {"review_result": review}

def validation_node(state: AgentState):

"""验证节点：检测幻觉"""

# 多次采样验证关键结论的一致性

validation = cross_validate(

analysis=state["analysis_result"],

review=state["review_result"],

source_text=state["contract_text"]

)

return {"validation_result": validation}

def report_node(state: AgentState):

"""报告节点"""

report = generate_markdown_report(

analysis=state["analysis_result"],

review=state["review_result"],

validation=state["validation_result"]

)

return {"final_report": report}

def should_continue(state: AgentState):

"""决策函数：是否需要重试"""

if state.get("errors"):

return "retry"

if state["validation_result"]["confidence"] < 0.7:

return "human_review"

return "end"

# 构建工作流图

workflow = StateGraph(AgentState)

workflow.add_node("coordinator", coordinator_node)

workflow.add_node("retrieval", retrieval_node)

workflow.add_node("analysis", analysis_node)

workflow.add_node("review", review_node)

workflow.add_node("validation", validation_node)

workflow.add_node("report", report_node)

workflow.set_entry_point("coordinator")

workflow.add_edge("coordinator", "retrieval")

workflow.add_edge("retrieval", "analysis")

workflow.add_edge("analysis", "review")

workflow.add_edge("review", "validation")

workflow.add_conditional_edges(

"validation",

should_continue,

{

"retry": "retrieval",

"human_review": "report",

"end": "report"

}

)

workflow.add_edge("report", END)

app = workflow.compile()

```

#### 5.3 混合检索实现

```

from rank_bm25 import BM25Okapi

import numpy as np

from qdrant_client import QdrantClient

from sentence_transformers import SentenceTransformer

class HybridRetriever:

def **init**(self):

self.vector_client = QdrantClient(url="http://localhost:6333")

self.embedder = SentenceTransformer("BAAI/bge-large-zh-v1.5")

[self.bm](http://self.bm)25 = None  # 在索引时初始化

self.documents = []

def index_documents(self, docs: list):

"""索引文档"""

# 1. 向量索引

embeddings = self.embedder.encode([doc["text"] for doc in docs])

self.vector_client.upsert(

collection_name="legal_docs",

points=[

{

"id": doc["id"],

"vector": emb.tolist(),

"payload": doc["metadata"]

}

for doc, emb in zip(docs, embeddings)

]

)

# 2. BM25索引

self.documents = docs

tokenized_docs = [doc["text"].split() for doc in docs]

[self.bm](http://self.bm)25 = BM25Okapi(tokenized_docs)

def search(self, query: str, top_k: int = 5):

"""混合检索"""

# 1. 向量检索

query_embedding = self.embedder.encode(query)

vector_results = self.vector_[client.search](http://client.search)(

collection_name="legal_docs",

query_vector=query_embedding.tolist(),

limit=20

)

# 2. BM25检索

tokenized_query = query.split()

bm25_scores = [self.bm](http://self.bm)25.get_scores(tokenized_query)

bm25_top_indices = np.argsort(bm25_scores)[-20:][::-1]

# 3. 倒排融合（Reciprocal Rank Fusion）

def rrf_score(rank, k=60):

return 1 / (k + rank)

doc_scores = {}

for rank, result in enumerate(vector_results):

doc_scores[[result.id](http://result.id)] = doc_scores.get([result.id](http://result.id), 0) + rrf_score(rank)

for rank, idx in enumerate(bm25_top_indices):

doc_id = self.documents[idx]["id"]

doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score(rank)

# 4. 重排序（可选）

sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

top_docs = [self.get_doc_by_id(doc_id) for doc_id, _ in sorted_docs[:top_k]]

# 5. 使用Reranker进一步优化（可选）

if hasattr(self, 'reranker'):

top_docs = self.rerank(query, top_docs)

return top_docs

```

### 六、质量保障

#### 6.1 单元测试

```

# tests/test_[rag.py](http://rag.py)

import pytest

from app.rag import HybridRetriever

def test_hybrid_retrieval():

retriever = HybridRetriever()

# 准备测试文档

test_docs = [

{"id": "1", "text": "合同应明确约定双方权利义务", "metadata": {}},

{"id": "2", "text": "违约金不得超过实际损失的30%", "metadata": {}},

]

retriever.index_documents(test_docs)

# 测试检索

results = [retriever.search](http://retriever.search)("违约责任如何约定", top_k=2)

assert len(results) > 0

assert "违约" in results[0]["text"]

# tests/test_[agents.py](http://agents.py)

def test_analysis_agent():

from app.agents import AnalysisAgent

agent = AnalysisAgent()

test_contract = "甲方：某某公司，乙方：另一公司，合同金额100万元..."

result = [agent.run](http://agent.run)(test_contract)

assert "parties" in result

assert result["parties"]["party_a"]["name"] == "某某公司"

assert result["amount"]["total"] == "1000000"

```

#### 6.2 集成测试

```

# tests/test_[e2e.py](http://e2e.py)

def test_full_contract_review_pipeline():

from app.main import ContractReviewPipeline

# 加载测试合同

with open("tests/fixtures/test_contract.pdf", "rb") as f:

contract_file = [f.read](http://f.read)()

# 运行完整流程

result = [ContractReviewPipeline.run](http://ContractReviewPipeline.run)(contract_file)

# 验证输出结构

assert "analysis_result" in result

assert "review_result" in result

assert "final_report" in result

# 验证关键字段

assert result["review_result"]["overall_score"] >= 0

assert result["review_result"]["overall_score"] <= 100

assert len(result["review_result"]["findings"]) > 0

```

### 七、交付标准

**最终交付物清单：**

✅ **代码仓库**
- 完整源代码（前端 + 后端）
- [README.md](http://README.md)（项目说明、快速开始）
- requirements.txt / package.json
- .env.example（环境变量模板）

✅ **文档**
- 系统架构设计文档
- API接口文档（Swagger自动生成）
- 部署指南（Docker / K8s）
- 用户操作手册
- Prompt工程文档（各Agent提示词说明）

✅ **测试**
- 单元测试覆盖率 > 70%
- 集成测试用例 > 10个
- 评测报告（Baseline对比、指标汇总）

✅ **数据**
- 示例合同数据（脱敏）
- 黄金标注评测集（50个样本）
- 知识库初始数据（法规、模板）

✅ **部署包**
- Docker镜像
- docker-compose.yml
- 数据库迁移脚本
- 健康检查脚本

---

## 开始开发

请按照以上需求，逐步实现系统功能。优先级：

**P0（第一周）：** 项目脚手架 + 数据库 + 基础API
**P1（第二周）：** RAG检索模块 + 向量存储
**P2（第三周）：** 多Agent工作流 + LLM集成
**P3（第四周）：** 前端页面 + 完整流程打通
**P4（第五周）：** 评测体系 + 优化迭代

在开发过程中，请遵循：
- 代码规范：PEP 8 (Python), Airbnb Style (JavaScript)
- Git提交规范：feat / fix / docs / test / refactor
- 文档更新：代码变更同步更新README和API文档
- 测试驱动：关键模块先写测试再实现

如有任何技术问题或需要澄清的需求，请随时提问。Let's build this! 🚀
