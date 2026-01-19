# LegalOS - Enterprise Legal Intelligence Analysis System

A multi-agent RAG (Retrieval-Augmented Generation) system for contract analysis and legal review, built with LangGraph, FastAPI, and Next.js.

## Project Status

✅ **Phase 1-6 Complete** | 🚀 **Production Ready**

- All 6 phases implemented and tested
- 163+ tests passing
- Type checking complete
- Full monitoring and security
- Production deployment ready

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - High-quality React components

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **SQLAlchemy** - ORM for database operations
- **LangChain** - LLM application framework
- **LangGraph** - Multi-agent orchestration

### Database & Storage
- **PostgreSQL 15** - Relational database
- **pgvector** - Vector similarity search extension
- **Qdrant** - Vector database for embeddings
- **Redis** - Caching and task queue

### AI/ML
- **ZhipuAI GLM-4** - Chinese language model
- **BGE-large-zh-v1.5** - Chinese text embeddings
- **BGE-reranker-v2-m3** - Reranking model

### Monitoring & Operations
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboard
- **Loki** - Log aggregation
- **Promtail** - Log collector
- **structlog** - Structured logging
- **Locust** - Load testing

### Security
- **JWT Authentication** - Token-based auth
- **Rate Limiting** - Sliding window algorithm
- **RBAC** - Role-based access control
- **bcrypt** - Password hashing

## Project Structure

```
legal-os/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/         # App Router pages
│   │   │   ├── upload/      # Contract upload page
│   │   │   ├── analysis/    # Analysis progress page
│   │   │   ├── report/      # Report viewing page
│   │   │   ├── contracts/   # Contract list page
│   │   │   ├── knowledge/   # Knowledge base page
│   │   │   └── evaluation/  # Evaluation dashboard
│   │   ├── components/  # React components
│   │   ├── lib/         # Utility functions
│   │   └── types/      # TypeScript types
│   └── public/          # Static assets
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── agents/      # Multi-agent definitions (6 agents)
│   │   │   ├── coordinator.py    # Task orchestration
│   │   │   ├── retrieval.py     # RAG retrieval
│   │   │   ├── analysis.py      # Contract analysis
│   │   │   ├── review.py        # Risk review
│   │   │   ├── validation.py    # Validation checks
│   │   │   ├── report.py        # Report generation
│   │   │   └── workflow.py      # LangGraph workflow
│   │   ├── rag/         # RAG retrieval module
│   │   │   ├── embeddings/      # BGE embeddings
│   │   │   ├── retrievers/      # Hybrid retrieval
│   │   │   └── rerankers/       # BGE reranker
│   │   ├── evaluation/   # Evaluation module
│   │   │   ├── golden_dataset.py  # Golden dataset
│   │   │   ├── metrics.py         # Evaluation metrics
│   │   │   ├── baselines.py       # Baseline experiments
│   │   │   ├── data_generator.py  # Data generation
│   │   │   └── data_validator.py  # Data validation
│   │   ├── api/         # API endpoints
│   │   │   ├── v1/          # API v1 routes
│   │   │   │   ├── contracts.py    # Contract analysis API
│   │   │   │   ├── knowledge.py     # Knowledge base API
│   │   │   │   ├── evaluation.py    # Evaluation API
│   │   │   │   ├── websocket.py     # WebSocket endpoints
│   │   │   │   └── export.py       # Export API
│   │   │   └── __init__.py
│   │   ├── models/      # Database models
│   │   ├── core/        # Core configuration
│   │   │   ├── config.py       # App configuration
│   │   │   ├── logging.py      # Structured logging
│   │   │   ├── prometheus.py   # Metrics collection
│   │   │   ├── security.py     # Auth & security
│   │   │   └── tracing.py      # Distributed tracing
│   │   ├── services/    # Business logic
│   │   │   └── export_service.py  # Export service
│   │   ├── monitoring/   # Monitoring module
│   │   │   ├── logging.py       # Logging utilities
│   │   │   └── metrics.py       # Metrics definitions
│   │   ├── llm_client.py      # ZhipuAI client
│   │   └── task_storage.py    # In-memory task storage
│   └── tests/           # Test files
│       ├── test_agents.py
│       ├── test_contracts_api.py
│       ├── test_e2e_analysis.py
│       ├── test_task_storage.py
│       ├── test_zhipu_client.py
│       └── test_workflow_integration.py
├── data/                # Data directory
│   ├── contracts/       # Contract documents
│   ├── regulations/     # Legal regulations
│   ├── templates/       # Contract templates
│   └── evaluation/     # Evaluation datasets
├── docs/                # Documentation
│   ├── PHASE_*_COMPLETE.md  # Phase completion reports
│   └── DATA_GENERATION_VALIDATION_COMPLETE.md
├── tests/               # Load testing
│   └── load/
│       └── load_test.py     # Locust load tests
├── monitoring/          # Monitoring configs
│   └── prometheus.yml
├── docker-compose.yml   # Development Docker compose
├── docker-compose.prod.yml  # Production Docker compose
├── AGENTS.md           # Agent development guide
├── DEPLOYMENT.md       # Deployment guide
└── TODO.md             # Project TODO
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- ZhipuAI API key ([Get one here](https://open.bigmodel.cn/))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legal-os
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your ZHIPU_API_KEY
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - Qdrant Dashboard: http://localhost:6333/dashboard
   - Redis: localhost:6379

### Development

**Frontend development:**
```bash
cd frontend
npm install
npm run dev
```

**Backend development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Core Features

### Multi-Agent Architecture
- **Coordinator Agent**: Task decomposition, contract type classification, execution planning
- **Retrieval Agent**: Query rewriting, hybrid retrieval (vector + BM25), relevance filtering
- **Analysis Agent**: Entity extraction, clause classification, confidence scoring
- **Review Agent**: Compliance checking, risk assessment, modification suggestions
- **Validation Agent**: Consistency validation, hallucination detection, confidence calculation
- **Report Agent**: Markdown report generation, JSON structured output, risk visualization

### RAG System
- Hybrid retrieval (vector + BM25 with Reciprocal Rank Fusion)
- Reranking with BGE-reranker-v2-m3
- Query rewriting and expansion
- Context window management
- Embedding caching with Redis (24h TTL)
- Batch embedding generation

### Document Processing
- Support for PDF, DOCX, TXT formats
- Smart chunking strategies (RecursiveCharacter & Semantic)
- Metadata extraction
- Batch processing with progress tracking

### Evaluation System
- Golden dataset management
- Baseline experiments (No RAG, Simple RAG, Multi-Agent RAG)
- Comprehensive metrics: Accuracy, Precision, Recall, F1, Hallucination Rate
- Data generation and validation
- Evaluation dashboard UI

### Frontend Features
- Contract upload with drag-and-drop
- Real-time analysis progress (WebSocket + polling fallback)
- Comprehensive report viewing with tabbed interface
- JSON report export
- Evaluation dashboard with baseline comparison
- Responsive design with Tailwind CSS

### Monitoring & Operations
- Structured logging with structlog (JSON format)
- Prometheus metrics collection (RAG, LLM, Agent, API, DB, System)
- Grafana dashboards for visualization
- Log aggregation with Loki
- Load testing with Locust
- Health checks and monitoring

### Security
- JWT-based authentication (Access Token + Refresh Token)
- Role-based access control (RBAC)
- Rate limiting (sliding window algorithm)
- API key authentication
- Password hashing with bcrypt
- Input validation and sanitization

## API Documentation

API documentation is auto-generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

**Contract Analysis:**
- `POST /api/v1/contracts/analyze` - Analyze contract (async task)
- `GET /api/v1/contracts/analysis/{task_id}` - Get analysis result
- `GET /api/v1/contracts/tasks/{task_id}` - Get task status
- `WS /api/v1/ws/tasks/{task_id}/stream` - Real-time progress updates

**Knowledge Base:**
- `POST /api/v1/knowledge/upload` - Upload document
- `GET /api/v1/knowledge/documents` - List documents
- `POST /api/v1/knowledge/search` - Search knowledge base
- `DELETE /api/v1/knowledge/documents/{doc_id}` - Delete document

**Evaluation:**
- `GET /api/v1/evaluation/dataset/info` - Get dataset info
- `GET /api/v1/evaluation/dataset/contracts` - Get dataset contracts
- `POST /api/v1/evaluation/run` - Run evaluation
- `GET /api/v1/evaluation/results/{evaluation_id}` - Get evaluation results
- `POST /api/v1/evaluation/data/generate` - Generate test data
- `POST /api/v1/evaluation/data/validate` - Validate data quality

## Testing

```bash
# Backend tests
cd backend
pytest                                          # Run all tests
pytest tests/test_llm.py::TestOpenAILLM::test_generate -xvs  # Single test
black app/ tests/                               # Format code
isort app/ tests/                               # Sort imports
mypy app/                                       # Type check
flake8 app/                                     # Lint

# Frontend tests
cd frontend
npm test

# Load testing (Locust)
python tests/load/load_test.py 50 5  # 50 users, 5 spawn rate
```

### Test Coverage
- 163+ tests passing
- Unit tests for all major components
- Integration tests for API endpoints
- End-to-end tests for contract analysis workflow
- Tests for agents, RAG, evaluation, and monitoring modules

## Deployment

### Production Deployment

```bash
# Configure environment variables
cp .env.example .env
# Edit .env with production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Monitor services
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Production Services

- **Frontend**: Nginx + Next.js (HTTPS on ports 80/443)
- **Backend**: FastAPI with Gunicorn workers
- **PostgreSQL**: pgvector with data persistence
- **Qdrant**: Vector database with persistence
- **Redis**: Cache with AOF persistence
- **Prometheus**: Metrics collection (30-day retention)
- **Grafana**: Monitoring dashboards
- **Loki**: Log aggregation
- **Promtail**: Log collector
- **Nginx**: Reverse proxy with SSL termination

### Monitoring

Access monitoring dashboards:
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Qdrant Dashboard: http://localhost:6333/dashboard

### Backup & Recovery

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed backup and recovery procedures.

## Development Roadmap

### Completed Phases ✅

- **Phase 1**: Project Scaffolding & Infrastructure
- **Phase 2**: RAG Module Implementation
- **Phase 3**: Multi-Agent System
- **Phase 4**: Frontend & Integration
- **Phase 5**: Evaluation & Optimization
- **Phase 6**: Operations & Deployment

### Future Enhancements 🚧

- Distributed tracing (LangSmith/LangFuse)
- PDF/DOCX report export
- Enhanced visualizations
- Multi-node deployment
- CI/CD pipeline
- Automated backups
- WAF integration
- DDoS protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Documentation

- [AGENTS.md](AGENTS.md) - Agent development guidelines
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [TODO.md](TODO.md) - Project TODO and status
- [docs/PHASE_*_COMPLETE.md](docs/) - Phase completion reports
- [docs/DATA_GENERATION_VALIDATION_COMPLETE.md](docs/DATA_GENERATION_VALIDATION_COMPLETE.md) - Data generation guide

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the repository.

## Project Status

**Last Updated**: 2026-01-19
**Version**: 1.0.0 (Production Ready)
**Maintainers**: Development Team
