"""
Qdrant vector store implementation for Code Puppy embeddings.

This module provides the interface to Qdrant for storing and searching
code and conversation embeddings.
"""

import os
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue,
        SearchRequest, ScoredPoint
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("qdrant-client not installed. Vector store functionality will be limited.")

@dataclass
class SearchResult:
    """Search result from vector store."""
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None

class QdrantVectorStore:
    """
    Vector store implementation using Qdrant.
    
    Manages two collections:
    - codebase: For code file embeddings
    - conversations: For chat message embeddings
    """
    
    def __init__(
        self, 
        workspace_path: str,
        url: str = 'http://localhost:6333',
        vector_size: int = 896,  # Qwen 2.5 0.5B typical dimension
        timeout: int = 30
    ):
        """
        Initialize Qdrant vector store.
        
        Args:
            workspace_path: Path to the workspace being indexed
            url: Qdrant server URL
            vector_size: Dimension of embedding vectors
            timeout: Request timeout in seconds
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("qdrant-client is required for vector store functionality")
        
        self.workspace_path = os.path.abspath(workspace_path)
        self.url = url
        self.vector_size = vector_size
        self.timeout = timeout
        
        # Collection names based on workspace
        workspace_hash = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.workspace_path))[:8]
        self.codebase_collection = f"codebase_{workspace_hash}"
        self.conversation_collection = f"conversations_{workspace_hash}"
        
        # Initialize client
        self.client = QdrantClient(url=url, timeout=timeout)
        self.logger = logging.getLogger(__name__)
        
        # Create collections if they don't exist
        self._ensure_collections()
    
    def _ensure_collections(self):
        """Ensure required collections exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            # Create codebase collection if needed
            if self.codebase_collection not in collection_names:
                self.create_collection(self.codebase_collection)
                self.logger.info(f"Created codebase collection: {self.codebase_collection}")
            
            # Create conversation collection if needed
            if self.conversation_collection not in collection_names:
                self.create_collection(self.conversation_collection)
                self.logger.info(f"Created conversation collection: {self.conversation_collection}")
                
        except Exception as e:
            self.logger.error(f"Failed to ensure collections: {e}")
            raise
    
    def create_collection(self, collection_name: str):
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name: Name of the collection to create
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            self.logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                self.logger.error(f"Failed to create collection {collection_name}: {e}")
                raise
    
    def upsert_embeddings(
        self,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        collection: Optional[str] = None
    ) -> bool:
        """
        Insert or update embeddings in the vector store.
        
        Args:
            ids: List of unique identifiers
            vectors: List of embedding vectors
            payloads: List of metadata dictionaries
            collection: Collection name (defaults to codebase)
            
        Returns:
            True if successful
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            points = [
                PointStruct(
                    id=id_,
                    vector=vector,
                    payload=payload
                )
                for id_, vector, payload in zip(ids, vectors, payloads)
            ]
            
            self.client.upsert(
                collection_name=collection,
                points=points
            )
            
            self.logger.debug(f"Upserted {len(points)} points to {collection}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upsert embeddings: {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        collection: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in the store.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            collection: Collection to search (defaults to codebase)
            filter_dict: Optional filters for the search
            
        Returns:
            List of search results
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            # Build filter if provided
            search_filter = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    search_filter = Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=False
            )
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    id=str(result.id),
                    score=result.score,
                    payload=result.payload or {}
                )
                for result in results
            ]
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def delete_by_file_path(self, file_path: str, collection: Optional[str] = None) -> bool:
        """
        Delete all embeddings for a specific file path.
        
        Args:
            file_path: Path of the file to delete embeddings for
            collection: Collection name (defaults to codebase)
            
        Returns:
            True if successful
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            # Delete points matching the file path
            self.client.delete(
                collection_name=collection,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="file_path",
                            match=MatchValue(value=file_path)
                        )
                    ]
                )
            )
            
            self.logger.debug(f"Deleted embeddings for {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete by file path: {e}")
            return False
    
    def get_collection_stats(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection: Collection name (defaults to codebase)
            
        Returns:
            Dictionary with collection statistics
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            info = self.client.get_collection(collection_name=collection)
            
            return {
                'name': collection,
                'vectors_count': info.vectors_count,
                'indexed_vectors_count': info.indexed_vectors_count,
                'points_count': info.points_count,
                'segments_count': info.segments_count,
                'status': info.status,
                'config': {
                    'vector_size': info.config.params.vectors.size,
                    'distance': info.config.params.vectors.distance
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def clear_collection(self, collection: Optional[str] = None) -> bool:
        """
        Clear all data from a collection.
        
        Args:
            collection: Collection name (defaults to codebase)
            
        Returns:
            True if successful
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            # Delete and recreate the collection
            self.client.delete_collection(collection_name=collection)
            self.create_collection(collection)
            self.logger.info(f"Cleared collection: {collection}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_all_file_paths(self, collection: Optional[str] = None) -> List[str]:
        """
        Get all unique file paths in the collection.
        
        Args:
            collection: Collection name (defaults to codebase)
            
        Returns:
            List of unique file paths
        """
        if not collection:
            collection = self.codebase_collection
        
        try:
            # Scroll through all points to get unique file paths
            file_paths = set()
            offset = None
            
            while True:
                results = self.client.scroll(
                    collection_name=collection,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                points, offset = results
                
                for point in points:
                    if point.payload and 'file_path' in point.payload:
                        file_paths.add(point.payload['file_path'])
                
                if offset is None:
                    break
            
            return sorted(list(file_paths))
            
        except Exception as e:
            self.logger.error(f"Failed to get file paths: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if Qdrant server is healthy.
        
        Returns:
            True if server is healthy
        """
        try:
            # Try to get collections as a health check
            self.client.get_collections()
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False