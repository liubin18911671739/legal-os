# Phase 3 启动文档

## 执行摘要

**状态**: 进行中
**开始时间**: 2026-01-18
**阶段**: Phase 3: 多智能体系统开发 (Week 5-6)

---

## 已完成工作

### Phase 2 回顾 (✅ 100%)

**Stage 2.1: 文档加载与处理**
- ✅ PDF/DOCX/TXT 加载器实现
- ✅ 多种分块策略
- ✅ 元数据提取和保留
- Token 估算

**Stage 2.3: 嵌入与向量存储**
- ✅ BGE-large-zh-v1.5 中文嵌入模型
- ✅ Redis 持久化缓存 (24h TTL, SHA256 键)
- ✅ Qdrant 向量存储集成 (1024 维)
- ✅ 集合生命周期管理

**Stage 2.4: BM25 检索**
- ✅ jieba 中文分词器 (50+ 停用词)
- ✅ BM25 索引器 (k1=1.5, b=0.75)
- ✅ Redis 持久化索引
- ✅ 索引增量更新

**Stage 2.5: 混合检索与重排序**
- ✅ RRF 融合算法 (k=60)
- ✅ Weighted Score Fusion (可选)
- ✅ 混合检索器 (并行向量 + BM25)
- ✅ BGE-reranker-v2-m3 重排序模型
- ✅ 上下文窗口管理 (合并 + 智能裁剪)
- ✅ 可配置权重 (0.7 向量, 0.3 BM25)

**Stage 2.6: RAG API 端点**
- ✅ 知识库上传 API (`POST /api/v1/knowledge/upload`)
- ✅ 知识库搜索 API (`POST /api/v1/knowledge/search`)
- ✅ 统计信息 API (`GET /api/v1/knowledge/stats`)
- ✅ 文档管理 API (CRUD)
- ✅ RAG 查询 API (`POST /api/v1/query`)
- ✅ 流式查询 API (`POST /api/v1/query/stream`)
- ✅ 健康检查端点

**Stage 2.7: RAG 测试 UI**
- ✅ 知识库页面增强
- ✅ 实时搜索功能
- ✅ 搜索结果展示 (分数、来源)
- ✅ 文档列表完善
- ✅ 加载状态和错误处理

---

## Phase 3 进行中工作

### Stage 3.1: LangGraph 工作流设置 (进行中)

**已完成**:
- ✅ 定义 AgentState TypedDict (state.py)
  - 任务信息、合同类型、用户查询
  - 智能体执行状态和历史
  - 任务状态和重试计数
  - 分析/审查/验证/报告输出
  - 风险等级和置信度
  - 错误处理和人工干预机制

- ✅ 定义 WorkflowNodes 枚举
  - Coordinator, Retrieval, Analysis, Review, Validation, Report, Error_Handler
- ✅ 创建基本工作流图
  - Coordinator → Retrieval → Analysis → Review → Validation → Report → END
  - 条件边和错误路由

- ✅ 创建 StateGraph 示例
  - 导出编译后的图实例

**文件结构**:
```
backend/app/agents/
  ├── __init__.py          # 模块导出
  ├── state.py             # AgentState 定义
  ├── workflow.py          # 工作流图创建
  ├── coordinator.py      # 协调智能体 (占位)
  ├── retrieval.py          # 检索智能体 (占位)
  ├── analysis.py          # 分析智能体 (待创建)
  ├── review.py           # 审查智能体 (待创建)
  ├── validation.py       # 验证智能体 (待创建)
  ├── report.py          # 报告智能体 (待创建)
```

**核心功能**:
- 状态流转机制 (AgentState TypedDict)
- should_continue 决策函数
- 条件边动态路由
- 错误处理和重试逻辑
- 人工干预触发

**依赖**:
- langchain==0.0.350
- langgraph==0.2.0
````

### 已创建文件 (5 个)
```
backend/app/agents/
  ├── __init__.py
  ├── state.py
  ├── workflow.py
  ├── coordinator.py
  ├── retrieval.py
  ├── analysis.py
  ├── review.py
  ├── validation.py
  ├── report.py
```

---

## 待完成任务 (Phase 3)

### Stage 3.2: 协调智能体
- [ ] 意图识别逻辑 (使用 LLM)
- [ ] 合同类型分类 (使用规则 + LLM)
- [ ] 任务分解逻辑
- [ ] 智能体路由决策
- [ ] 错误恢复和重试策略
- [ ] 系统提示词编写

### Stage 3.3: 检索智能体
- [ ] 查询重写 (使用 glm-4-flash)
- [ ] 混合检索执行
- [ ] 相关性过滤
- [ ] 查询结果排序
- [ ] 上下文窗口管理

### Stage 3.4: 分析智能体
- [ ] 实体提取 (合同当事人、金额、日期等)
- [ ] 条款分类 (违约、责任、终止等)
- [ ] 置信度评分
- [ ] JSON 结构化输出
- [ ] 系统提示词

### Stage 3.5: 审查智能体
- [ ] 加载公司模板和法规
- [ ] 强制条款检查
- [ ] 合规性验证
- [ ] 风险评估 (高/中/低)
- [ ] 修改建议生成

### Stage 3.6: 验证智能体
- [ ] 多样本一致性检查
- [ ] 引用准确性验证
- [ ] 置信度计算
- [ ] 幻觉检测机制

### Stage 3.7: 报告智能体
- [ ] 结构化报告生成 (执行摘要、发现、建议)
- [ ] 风险矩阵可视化
- [ ] 支持 Markdown 和 JSON 导出
- [ ] 报告格式化

### Stage 3.8: 智能体编排
- [ ] 条件边动态路由
- [ ] 错误处理和恢复
- [ ] 重试机制 (指数退避)
- [ ] 人工干预触发

### Stage 3.9: 智谱 AI 集成
- [ ] 安装 zhipuai SDK
- [ ] 创建 ZhipuAIClient 包装器
- [ ] 配置智能体模型选择
- [ ] 实现 call_zhipu_llm 函数
- [ ] 流式生成支持
- [ ] 令牌计数和成本跟踪

### Stage 3.10: 合同分析 API
- [ ] 创建 /api/v1/contracts 路由
- [ ] POST /analyze 端点 (异步任务创建)
- [ ] GET /tasks/{id} 端点
- [ ] WebSocket /tasks/{id}/stream 实时更新
- [ ] 任务队列集成 (Celery)
- [ ] 进度跟踪存储

---

## 技术架构

### Phase 2 RAG 系统 (已完成)
```
用户查询
    ↓
    中文分词器
        ↓
    BM25 索引器
        ↓
    BGE 嵌入模型 (bge-large-zh-v1.5)
        ↓
    Redis 缓存
        ↓
    Qdrant 向量库
        ↓
    混合检索器 (RRF 融合)
        ↓
    BGE 重排序
        ↓
    上下文构建器
        ↓
    智谱 AI GLM-4
        ↓
    用户回答
```

存储层:
┌──────────┐    ┌──────────────┐
│  Qdrant     │    │   Redis     │
│ (Vectors)    │    │ (Cache+Index)│
└──────────┘    └──────────┘
```

### Phase 3 多智能体系统 (进行中)
```
用户查询
    ↓
┌──────────────────────┐
│  Coordinator Agent   │
│  (意图识别、路由)       │
└──────┬────────────┘
           ↓
    ┌──────────────┐
    │  Retrieval Agent  │
    │  (查询增强、检索)       │
└──────┬────────────┘
           ↓
    ┌──────────────┐
    │  Analysis Agent    │
    │  (实体提取、分类)       │
└──────┬────────────┘
           ↓
    ┌──────────────┐
    │  Review Agent     │
    │  (合规检查、风险)       │
└──────┬────────────┘
           ↓
    ┌──────────────┐
    │  Validation Agent  │
    │  (一致性、准确性)       │
    └──────┬────────────┘
           ↓
    ┌──────────────┐
    │  Report Agent    │
    │  (报告生成)       │
    └──────┬────────────┘
           ↓
    ┌──────────────┐
    │  ZhipuAI GLM-4   │
    │  (响应生成)       │
└──────┬────────────┘
           ↓
    ┌──────────────┐
    │   用户回答             │
    └────────────────────┘
```

---

## 下一步

### 立即任务
1. 实现协调智能体的完整逻辑 (coordinator.py)
   - 集成真实 RAG 检索
   - 使用 GLM-4-flash 生成执行计划
   - 添加合同类型识别

2. 实现检索智能体的查询重写
   - 使用 glm-4-flash
   - 实现相关性过滤
   - 结果排序和裁剪

3. 创建分析智能体 (analysis.py)
   - 实现实体提取逻辑
   - 实现条款分类
   - - 加载合同模板和法规
   - 实现 JSON 结构化输出

4. 创建审查智能体 (review.py)
   - 加载公司模板
   - 实现强制条款检查
   - 实现风险等级评估
   - 生成修改建议

5. 实现验证智能体 (validation.py)
   - 多样本一致性检查
   - 引用验证
   - 幻觉检测

6. 实现报告智能体 (report.py)
   - 结构化报告生成
   - Markdown 格式化
   - 风险矩阵
   - 多格式导出

7. 集成智谱 AI
   - 安装 zhipuai SDK
   - 实现流式生成
   - 配置成本跟踪

8. 创建合同分析 API
   - 路由集成到 main.py
   - 任务队列集成
   - WebSocket 支持

---

## 已知问题

1. **LSP 错误**: 存在一些类型提示问题 (main.py)
2. **Agent 节点占位符**: 所有智能体仅为占位实现
3. **无真实 LLM 调用**: 使用模拟数据
4. **无实际处理**: 上传/检索未真正执行

---

## 文件统计

### 新增文件 (23 个)
```
backend/app/agents/                    # 5 个智能体文件
backend/app/rag/embeddings/         # 2 个文件
backend/app/rag/retrieval/          # 6 个文件
backend/app/rag/services/             # 2 个文件
backend/app/rag/llm/               # 3 个文件
backend/app/api/v1/               # 4 个文件
backend/tests/                        # 12+ 个测试文件
```

### 总代码行数
- Phase 2 新增: ~4,700 行
- Phase 3 新增: ~400 行
- **总计**: ~5,100+ 行

---

## 文档更新

- ✅ `STAGE_2_COMPLETE.md` - Phase 2 完成报告
- ✅ `TODO.md` - 更新 Phase 2 状态为 100%
- ✅ `PHASE_3_START.md` - Phase 3 启动文档 (新建)

---

**目标**: Week 5-6 (多智能体系统开发)
**预计完成**: Week 6-8 (评估阶段)

**进度**: 5% (已完成基础架构)