# LegalOS - Enterprise Legal Intelligence Analysis System

A multi-agent RAG (Retrieval-Augmented Generation) system for contract analysis and legal review, built with LangGraph, FastAPI, and Next.js.

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

## Project Structure

```
legal-os/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/         # App Router pages
│   │   ├── components/  # React components
│   │   ├── lib/         # Utility functions
│   │   └── types/      # TypeScript types
│   └── public/          # Static assets
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── agents/      # Multi-agent definitions
│   │   ├── rag/         # RAG retrieval module
│   │   ├── models/      # Database models
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   └── tests/           # Test files
├── data/                # Data directory
│   ├── contracts/       # Contract documents
│   ├── regulations/     # Legal regulations
│   ├── templates/       # Contract templates
│   └── evaluation/     # Evaluation datasets
└── docker-compose.yml   # Docker orchestration
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
- **Coordinator Agent**: Task decomposition and routing
- **Retrieval Agent**: Enhanced RAG with hybrid search
- **Analysis Agent**: Entity extraction and clause classification
- **Review Agent**: Compliance checking and risk assessment
- **Validation Agent**: Hallucination detection and cross-validation
- **Report Agent**: Structured report generation

### RAG System
- Hybrid retrieval (vector + BM25)
- Reranking with BGE-reranker
- Query rewriting and expansion
- Context window management

### Document Processing
- Support for PDF, DOCX, TXT formats
- Smart chunking strategies
- Metadata extraction
- Batch processing

## API Documentation

API documentation is auto-generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Development Roadmap

See [IMPLEMENTATION_PLAN.md](.opencode/plans/legal-os-implementation.md) for detailed development phases and milestones.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Her]e

## Support

For issues and questions, please open an issue on the repository.
# legal-os
