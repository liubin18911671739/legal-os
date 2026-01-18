from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np


class BaseEmbeddingModel(ABC):
    """Base class for embedding models"""

    @abstractmethod
    async def embed(self, texts: List[str], **kwargs) -> np.ndarray:
        """Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed
            **kwargs: Additional model-specific parameters

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        pass

    @abstractmethod
    async def embed_query(self, text: str, **kwargs) -> np.ndarray:
        """Generate embedding for a single query text

        Args:
            text: Query text to embed
            **kwargs: Additional model-specific parameters

        Returns:
            numpy array of shape (embedding_dim,)
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embeddings"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model"""
        pass
