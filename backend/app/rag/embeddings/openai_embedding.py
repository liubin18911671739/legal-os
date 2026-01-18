from typing import List, Optional
import numpy as np
from openai import AsyncOpenAI
from .base import BaseEmbeddingModel


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    """OpenAI embedding model implementation"""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimension: Optional[int] = None,
    ):
        """Initialize OpenAI embedding model

        Args:
            api_key: OpenAI API key
            model: Model name (text-embedding-3-small, text-embedding-3-large, etc.)
            dimension: Desired embedding dimension (None for model default)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._dimension = dimension

    async def embed(
        self,
        texts: List[str],
        **kwargs
    ) -> np.ndarray:
        """Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed
            **kwargs: Additional parameters (dimensions, encoding_format, etc.)

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)

        params = {
            "input": texts,
            "model": self._model,
        }

        if self._dimension is not None:
            params["dimensions"] = self._dimension

        params.update(kwargs)

        try:
            response = await self.client.embeddings.create(**params)
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {e}")

    async def embed_query(self, text: str, **kwargs) -> np.ndarray:
        """Generate embedding for a single query text

        Args:
            text: Query text to embed
            **kwargs: Additional parameters

        Returns:
            numpy array of shape (embedding_dim,)
        """
        embeddings = await self.embed([text], **kwargs)
        return embeddings[0]

    @property
    def dimension(self) -> int:
        """Return the dimension of the embeddings"""
        if self._dimension is not None:
            return self._dimension
        
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        
        return model_dimensions.get(
            self._model,
            1536  # Default dimension
        )

    @property
    def model_name(self) -> str:
        """Return the name of the model"""
        return self._model
