# LegalOS - Agent Guidelines

Guidelines for agentic coding assistants working on LegalOS (multi-agent RAG system for contract analysis).

## Build, Lint, and Test Commands

### Backend (Python/FastAPI)
```bash
cd backend
pytest                                          # Run all tests
pytest tests/test_llm.py::TestOpenAILLM::test_generate -xvs  # Single test
black app/ tests/                               # Format
isort app/ tests/                               # Sort imports
mypy app/                                       # Type check
flake8 app/                                     # Lint
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000     # Dev server
```

### Frontend (Next.js/TypeScript)
```bash
cd frontend
npm run dev           # Development server
npm run build         # Production build
npm run lint          # Lint
npm run type-check    # Type check
```

## Code Style Guidelines

### Python (Backend)
- Use `isort` (profile: black) to organize imports; import from `__init__.py` for clean interfaces
- Type hints required: `List[str]`, `Dict[str, Any]`, `Optional[int]`; prefer `Optional[T]` over `T | None`
- Naming: `PascalCase` classes, `snake_case` functions, `_private` members, `UPPER_SNAKE_CASE` constants
- Use custom exceptions from `app.core.exceptions`: `RAGException`, `RetrievalException`, `EmbeddingException`, `VectorStoreException`, `DocumentProcessingException`, `PipelineNotInitializedError`, `ConfigurationError`, `ValidationError`, `ContextTooLongError`, `RateLimitError`, `TimeoutError`
- Raise `HTTPException` with status codes in API routes; log errors: `rag_logger`, `api_logger`, `db_logger`
- All I/O operations must be async with `async def`/`await`; use `AsyncMock` for tests

### TypeScript (Frontend)
- Use absolute imports with `@/*` path alias; named exports for components, types, utilities
- All components require props interface; use `React.ReactNode`, `React.FC`; export interfaces for shared types
- Naming: `PascalCase` components/types, `camelCase` functions, `use*` hooks, `UPPER_SNAKE_CASE` constants
- Use Tailwind CSS utility classes and `cn()` utility to merge classnames
- Server components by default, client components with `'use client'`

## Architecture Patterns

### Backend
- Abstract base classes: `BaseLLM`, `BaseEmbeddingModel`
- Pydantic schemas for API: `class QueryRequest(BaseModel):`
- LangGraph for multi-agent orchestration

### Frontend
- App Router (`src/app/`), custom hooks in `src/hooks/`, utilities in `src/lib/`

## Testing Guidelines

### Python Tests
- Use pytest with `@pytest.mark.asyncio` for async tests, `@pytest.fixture` for setup
- Mock external services: `@patch("module.Class")` or `AsyncMock`
- Test both success and error paths

### Frontend Tests
- Use Jest (configured by Next.js), React Testing Library
- Mock API calls in tests

## Important Reminders

**NEVER:**
- Commit without tests passing
- Disable type checking (`mypy` or `tsc --noEmit`)
- Disable linters/formatters
- Commit code that doesn't compile
- Use `--no-verify` to bypass git hooks
- Make circular imports

**ALWAYS:**
- Run formatters/linters before committing
- Add type hints (Python) or types (TypeScript)
- Test both happy path and error cases
- Use custom exceptions from `app.core.exceptions`
- Prefer async over blocking I/O
- Follow existing patterns in codebase

## Project Structure

```
legal-os/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── agents/       # Multi-agent definitions (LangGraph)
│   │   ├── rag/          # RAG retrieval module
│   │   ├── api/          # FastAPI routes and schemas
│   │   ├── models/       # Database models (SQLAlchemy)
│   │   ├── core/         # Config, exceptions, monitoring
│   │   └── utils/        # Utility functions
│   └── tests/            # Test files mirroring app structure
├── frontend/             # Next.js application
│   └── src/
│       ├── app/         # App Router pages
│       ├── components/  # React components
│       ├── lib/         # Utility functions and API client
│       └── types/      # TypeScript type definitions
└── data/                # Documents and data files
```

## Common Patterns

```python
# Abstract base class (Python)
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Pydantic schema for API
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    text: str = Field(..., description="Query text")
    limit: int = Field(default=5, ge=1, le=100)
```

```typescript
// React component with TypeScript (Frontend)
'use client'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex">
      {children}
    </div>
  )
}

// Utility function for classnames
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```
