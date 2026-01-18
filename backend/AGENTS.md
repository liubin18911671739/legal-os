# LegalOS Backend - Agent Guidelines

Guidelines for agentic coding assistants working on the LegalOS RAG backend.

## Build, Lint, and Test Commands

```bash
# Run all tests
pytest

# Run single test (recommended for iteration)
pytest tests/test_llm.py::TestOpenAILLM::test_generate -xvs

# Format and lint
black app/ tests/ && isort app/ tests/
mypy app/
flake8 app/
```

## Code Style Guidelines

### Imports
- Use `isort` (profile: black) to organize
- Import from `__init__.py` for clean interfaces
- Use lazy imports in `__init__.py` to avoid circular dependencies

### Type Hints
- All functions require type hints: `List[str]`, `Dict[str, Any]`, `Optional[int]`
- Prefer `Optional[T]` over `T | None`
- Return types required for public methods

### Naming Conventions
- Classes: `PascalCase` (`OpenAILLM`, `RetrievalConfig`)
- Functions: `snake_case` (`get_pipeline`, `build_context`)
- Private: `_leading_underscore` (`_model`, `_temperature`)
- Constants: `UPPER_SNAKE_CASE` (`DATABASE_URL`)
- Tests: `Test{ClassName}`, `test_{method_name}`

### Error Handling
- Use custom exceptions from `app.core.exceptions`:
  - `RAGException` (base)
  - `RetrievalException`, `EmbeddingException`, `VectorStoreException`
  - `ConfigurationError`, `ValidationError`, `ContextTooLongError`
- Raise `HTTPException` with status codes in API routes
- Log errors: `rag_logger`, `api_logger`, `db_logger`

### Documentation
- All public classes/methods require Google-style docstrings
- Include Args/Returns/Yields sections

```python
class OpenAILLM(BaseLLM):
    """OpenAI GPT model implementation"""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
        Returns:
            Generated text
        """
        pass
```

### Async/Await
- All I/O operations must be async
- Use `async def`, `await`, and `AsyncMock` for tests

```python
async def query(self, text: str) -> str:
    result = await self.llm.generate(text)
    return result
```

### Architecture Patterns
- Abstract base classes: `BaseLLM`, `BaseEmbeddingModel`
- Dataclasses for simple data: `@dataclass class RAGResponse:`
- Pydantic schemas for API: `class QueryRequest(BaseModel):`
- Singleton pattern: `RAGService.get_instance()`
- Use `@property` for computed attributes

### Testing Guidelines
- Use pytest with `@pytest.mark.asyncio` for async tests
- Use `@pytest.fixture` for setup
- Mock external: `@patch("module.Class")` or `unittest.mock.Mock`
- Test both success and error paths

```python
class TestOpenAILLM:
    """Test cases for OpenAILLM"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client"""
        with patch("app.rag.llm.openai_llm.AsyncOpenAI") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_client):
        """Test text generation"""
        pass
```

### Project Structure
- `app/rag/` - RAG pipeline (embeddings, retrieval, LLM)
- `app/api/` - FastAPI routes and schemas
- `app/core/` - Config, exceptions, monitoring
- `app/models/` - Database models
- `tests/` - Test files mirroring app structure

## Important Reminders

- **NEVER** commit without tests passing
- **ALWAYS** run black/isort before committing
- **ALWAYS** add type hints
- **ALWAYS** use custom exceptions from `app.core.exceptions`
- **NEVER** disable mypy type checking
- **PREFER** async over blocking I/O
- **AVOID** circular dependencies
- **TEST** both happy path and error cases

## Common Patterns

```python
# Abstract base class
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Configuration class
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = "default"
    class Config:
        env_file = ".env"

# Singleton service
class Service:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```
