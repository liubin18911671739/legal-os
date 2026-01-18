from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import numpy as np


@dataclass
class SearchResult:
    """Result from vector similarity search"""
    id: str
    score: float
    payload: Dict[str, Any]


class QdrantVectorStore:
    """Vector store using Qdrant for similarity search"""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
    ):
        """Initialize Qdrant vector store

        Args:
            url: Qdrant server URL
            api_key: Optional API key for authentication
            prefer_grpc: Use gRPC instead of REST API
        """
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=prefer_grpc,
        )

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "cosine",
    ) -> None:
        """Create a new collection

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors
            distance: Distance metric (cosine, euclid, dot)
        """
        distance_map = {
            "cosine": Distance.COSINE,
            "euclid": Distance.EUCLID,
            "dot": Distance.DOT,
        }

        if distance not in distance_map:
            raise ValueError(f"Invalid distance metric: {distance}")

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance_map[distance],
            ),
        )

    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection

        Args:
            collection_name: Name of the collection to delete
        """
        await self.client.delete_collection(collection_name)

    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists

        Args:
            collection_name: Name of the collection

        Returns:
            True if collection exists, False otherwise
        """
        collections = await self.client.get_collections()
        return any(
            col.name == collection_name
            for col in collections.collections
        )

    async def add_points(
        self,
        collection_name: str,
        vectors: np.ndarray,
        payloads: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Add points to a collection

        Args:
            collection_name: Name of the collection
            vectors: numpy array of shape (n, vector_size)
            payloads: List of payload dictionaries
            ids: List of point IDs
        """
        if len(vectors) != len(payloads) or len(vectors) != len(ids):
            raise ValueError(
                "vectors, payloads, and ids must have the same length"
            )

        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i].tolist(),
                payload=payloads[i],
            )
            for i in range(len(vectors))
        ]

        await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

    async def search(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors

        Args:
            collection_name: Name of the collection
            query_vector: Query vector to search with
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filter_conditions: Optional filter conditions for payload fields

        Returns:
            List of search results sorted by score (descending)
        """
        query_filter = None
        if filter_conditions:
            conditions = [
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value),
                )
                for key, value in filter_conditions.items()
            ]
            query_filter = Filter(must=conditions)

        results = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            SearchResult(
                id=str(result.id),
                score=result.score,
                payload=result.payload,
            )
            for result in results
        ]

    async def delete_points(
        self,
        collection_name: str,
        ids: List[str],
    ) -> None:
        """Delete points by IDs

        Args:
            collection_name: Name of the collection
            ids: List of point IDs to delete
        """
        await self.client.delete(
            collection_name=collection_name,
            points_selector=ids,
        )

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection info
        """
        info = await self.client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vector_size": info.config.params.vectors.size,
            "distance": str(info.config.params.vectors.distance),
            "points_count": info.points_count,
        }
