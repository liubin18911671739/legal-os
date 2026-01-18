from typing import Optional, Dict, Any
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    CreateCollection,
)

logger = logging.getLogger(__name__)


class CollectionManager:
    """Manager for Qdrant collection lifecycle"""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
    ):
        """Initialize collection manager

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
        logger.info(f"CollectionManager initialized with Qdrant at {url}")

    async def create_knowledge_collection(
        self,
        collection_name: str = "knowledge_base",
        vector_size: int = 1024,
        distance: str = "cosine",
        recreate: bool = False,
    ) -> bool:
        """Create or recreate knowledge base collection

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors (1024 for BGE-large-zh-v1.5)
            distance: Distance metric (cosine, euclid, dot)
            recreate: If True, delete existing collection first

        Returns:
            True if collection exists after operation
        """
        try:
            # Check if collection exists
            exists = await self.client.collection_exists(collection_name)
            
            if exists:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    await self.client.delete_collection(collection_name)
                    exists = False
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    return True
            
            # Create collection
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
            
            logger.info(
                f"Created collection '{collection_name}' "
                f"(vector_size={vector_size}, distance={distance})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    async def ensure_collection(
        self,
        collection_name: str = "knowledge_base",
        vector_size: int = 1024,
        distance: str = "cosine",
    ) -> bool:
        """Ensure collection exists, create if not

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors
            distance: Distance metric

        Returns:
            True if collection exists
        """
        if await self.client.collection_exists(collection_name):
            return True
        
        return await self.create_knowledge_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            distance=distance,
        )

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection

        Args:
            collection_name: Name of collection to delete

        Returns:
            True if deleted successfully
        """
        try:
            if await self.client.collection_exists(collection_name):
                await self.client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
                return True
            else:
                logger.warning(f"Collection not found: {collection_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    async def get_collection_info(
        self,
        collection_name: str = "knowledge_base",
    ) -> Optional[Dict[str, Any]]:
        """Get information about a collection

        Args:
            collection_name: Name of collection

        Returns:
            Dictionary with collection info or None if not found
        """
        try:
            if not await self.client.collection_exists(collection_name):
                return None
            
            info = await self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vector_size": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance),
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

    async def list_collections(self) -> list[str]:
        """List all collections

        Returns:
            List of collection names
        """
        try:
            collections = await self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    async def clear_collection(self, collection_name: str) -> bool:
        """Clear all points from a collection (keeps collection)

        Args:
            collection_name: Name of collection

        Returns:
            True if cleared successfully
        """
        try:
            if await self.client.collection_exists(collection_name):
                # Get all point IDs and delete them
                info = await self.get_collection_info(collection_name)
                if info and info["points_count"] > 0:
                    await self.client.delete(
                        collection_name=collection_name,
                        points_selector=None,  # Delete all points
                    )
                    logger.info(f"Cleared collection: {collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
