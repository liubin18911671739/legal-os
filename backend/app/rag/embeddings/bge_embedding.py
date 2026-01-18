from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from .base import BaseEmbeddingModel


class BGEEmbeddingModel(BaseEmbeddingModel):
    """BGE (BAAI General Embedding) embedding model implementation for Chinese text"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-zh-v1.5",
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        batch_size: int = 32,
    ):
        """Initialize BGE embedding model

        Args:
            model_name: Model name or path (BAAI/bge-large-zh-v1.5, BAAI/bge-base-zh-v1.5, etc.)
            device: Device to load model on (cuda, cpu, or None for auto-detection)
            normalize_embeddings: Whether to normalize embeddings to unit length
            batch_size: Default batch size for embedding generation
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self._device = device
        self._normalize = normalize_embeddings
        self._batch_size = batch_size
        
        print(f"Loading BGE model: {model_name} on {device}")
        self.model = SentenceTransformer(model_name, device=device)
        print(f"BGE model loaded successfully")
        
        self._dimension = self.model.get_sentence_embedding_dimension()

    async def embed(
        self,
        texts: List[str],
        **kwargs
    ) -> np.ndarray:
        """Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed
            **kwargs: Additional parameters (batch_size, etc.)

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)

        batch_size = kwargs.get("batch_size", self._batch_size)
        normalize = kwargs.get("normalize", self._normalize)

        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            
            return embeddings
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
        """Return dimension of embeddings"""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Return name of model"""
        return self.model._first_module().__class__.__name__
    
    def get_model_info(self) -> dict:
        """Get model information

        Returns:
            Dictionary with model details
        """
        return {
            "model_name": self.model.get_sentence_embedding_dimension(),
            "dimension": self._dimension,
            "device": self._device,
            "max_seq_length": self.model.max_seq_length,
            "normalize": self._normalize,
            "batch_size": self._batch_size,
        }
