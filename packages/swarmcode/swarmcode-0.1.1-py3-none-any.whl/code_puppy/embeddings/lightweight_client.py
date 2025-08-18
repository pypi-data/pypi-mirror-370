"""
Lightweight client for HuggingFace + Qdrant embedding stack.
Connects to dockerized services for embeddings and vector storage.
"""

import os
import logging
import hashlib
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result from vector store."""
    id: str
    score: float
    payload: Dict[str, Any]
    text: Optional[str] = None

class LightweightEmbeddingClient:
    """
    Client for lightweight embedding stack.
    Connects to dockerized Qwen3 embedding service and Qdrant.
    """
    
    def __init__(
        self,
        project_name: str = "code_puppy",
        embedding_url: str = "http://localhost:8001",
        qdrant_url: str = "http://localhost:6333",
        collection_prefix: Optional[str] = None
    ):
        """
        Initialize lightweight embedding client.
        
        Args:
            project_name: Name of the project (used for collection naming)
            embedding_url: URL of the embedding service
            qdrant_url: URL of Qdrant service
            collection_prefix: Optional prefix for collections
        """
        self.project_name = project_name
        self.embedding_url = embedding_url
        self.qdrant_url = qdrant_url
        
        # Collection names
        prefix = collection_prefix or project_name
        self.code_collection = f"{prefix}_code"
        self.chat_collection = f"{prefix}_chat"
        
        # Initialize Qdrant client with compatibility check disabled
        self.qdrant = QdrantClient(url=qdrant_url, check_compatibility=False)
        
        # Embedding dimension (Qwen3-Embedding-0.6B)
        self.dimension = 1024
        
        # Ensure collections exist
        self._ensure_collections()
        
        logger.info(f"Initialized client for project: {project_name}")
    
    def _ensure_collections(self):
        """Ensure required collections exist in Qdrant."""
        collections = [self.code_collection, self.chat_collection]
        
        existing = [c.name for c in self.qdrant.get_collections().collections]
        
        for collection in collections:
            if collection not in existing:
                self.qdrant.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {collection}")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings using the embedding service.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            response = requests.post(
                f"{self.embedding_url}/embeddings",
                json={
                    "texts": texts,
                    "normalize": True,
                    "batch_size": 32
                },
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data["embeddings"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise
    
    def index_code(
        self,
        file_path: str,
        content: str,
        chunks: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Index code file with embeddings.
        
        Args:
            file_path: Path to the code file
            content: Full file content
            chunks: Optional pre-chunked code blocks
            
        Returns:
            Number of chunks indexed
        """
        # If no chunks provided, create simple chunks
        if chunks is None:
            chunks = self._simple_chunk(content, chunk_size=500, overlap=50)
        
        if not chunks:
            return 0
        
        # Create embeddings for chunks
        texts = [chunk.get("content", "") for chunk in chunks]
        embeddings = self.create_embeddings(texts)
        
        # Create points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique ID using hash converted to integer
            chunk_hash = hashlib.sha256(
                f"{file_path}:{i}:{chunk.get('content', '')[:100]}".encode()
            ).hexdigest()
            # Convert hex to integer and take modulo to ensure it fits in 64-bit
            chunk_id = int(chunk_hash[:16], 16) % (2**63)
            
            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "file_path": file_path,
                    "chunk_index": i,
                    "content": chunk.get("content", ""),
                    "start_line": chunk.get("start_line", 0),
                    "end_line": chunk.get("end_line", 0),
                    "type": chunk.get("type", "code")
                }
            )
            points.append(point)
        
        # Upsert to Qdrant
        self.qdrant.upsert(
            collection_name=self.code_collection,
            points=points
        )
        
        logger.info(f"Indexed {len(points)} chunks from {file_path}")
        return len(points)
    
    def index_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]]
    ) -> int:
        """
        Index conversation messages.
        
        Args:
            conversation_id: Unique conversation identifier
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Number of messages indexed
        """
        if not messages:
            return 0
        
        # Create embeddings for messages
        texts = [msg.get("content", "") for msg in messages]
        embeddings = self.create_embeddings(texts)
        
        # Create points
        points = []
        for i, (msg, embedding) in enumerate(zip(messages, embeddings)):
            # Generate unique ID using hash converted to integer
            msg_hash = hashlib.sha256(
                f"{conversation_id}:{i}:{msg.get('content', '')[:100]}".encode()
            ).hexdigest()
            # Convert hex to integer and take modulo to ensure it fits in 64-bit
            msg_id = int(msg_hash[:16], 16) % (2**63)
            
            point = PointStruct(
                id=msg_id,
                vector=embedding,
                payload={
                    "conversation_id": conversation_id,
                    "message_index": i,
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", "")
                }
            )
            points.append(point)
        
        # Upsert to Qdrant
        self.qdrant.upsert(
            collection_name=self.chat_collection,
            points=points
        )
        
        logger.info(f"Indexed {len(points)} messages from conversation {conversation_id}")
        return len(points)
    
    def search_code(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[SearchResult]:
        """
        Search code collection.
        
        Args:
            query: Search query
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        # Create query embedding
        query_embedding = self.create_embeddings([query])[0]
        
        # Search in Qdrant
        results = self.qdrant.search(
            collection_name=self.code_collection,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=str(result.id),
                score=result.score,
                payload=result.payload,
                text=result.payload.get("content", "")
            ))
        
        return search_results
    
    def search_conversations(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[SearchResult]:
        """
        Search conversation collection.
        
        Args:
            query: Search query
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        # Create query embedding
        query_embedding = self.create_embeddings([query])[0]
        
        # Search in Qdrant
        results = self.qdrant.search(
            collection_name=self.chat_collection,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=str(result.id),
                score=result.score,
                payload=result.payload,
                text=result.payload.get("content", "")
            ))
        
        return search_results
    
    def _simple_chunk(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Simple text chunking with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        lines = text.split('\n')
        
        current_chunk = []
        current_size = 0
        start_line = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "content": '\n'.join(current_chunk),
                    "start_line": start_line + 1,
                    "end_line": i,
                    "type": "code"
                })
                
                # Start new chunk with overlap
                overlap_lines = []
                overlap_size = 0
                for j in range(len(current_chunk) - 1, -1, -1):
                    line_len = len(current_chunk[j]) + 1
                    if overlap_size + line_len <= overlap:
                        overlap_lines.insert(0, current_chunk[j])
                        overlap_size += line_len
                    else:
                        break
                
                current_chunk = overlap_lines
                current_size = overlap_size
                start_line = i - len(overlap_lines) + 1
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add last chunk
        if current_chunk:
            chunks.append({
                "content": '\n'.join(current_chunk),
                "start_line": start_line + 1,
                "end_line": len(lines),
                "type": "code"
            })
        
        return chunks
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all services.
        
        Returns:
            Health status dictionary
        """
        health = {
            "embedding_service": False,
            "qdrant": False,
            "collections": []
        }
        
        # Check embedding service
        try:
            response = requests.get(f"{self.embedding_url}/health", timeout=5)
            health["embedding_service"] = response.status_code == 200
            if response.status_code == 200:
                health["embedding_info"] = response.json()
        except:
            pass
        
        # Check Qdrant
        try:
            collections = self.qdrant.get_collections()
            health["qdrant"] = True
            health["collections"] = [c.name for c in collections.collections]
        except:
            pass
        
        return health

# Convenience function for quick setup
def create_client(project_name: Optional[str] = None) -> LightweightEmbeddingClient:
    """
    Create a lightweight embedding client with default settings.
    
    Args:
        project_name: Optional project name (defaults to env or 'code_puppy')
        
    Returns:
        Configured client
    """
    if project_name is None:
        project_name = os.getenv("PROJECT_NAME", "code_puppy")
    
    embedding_port = os.getenv("EMBEDDING_PORT", "8001")
    qdrant_port = os.getenv("QDRANT_PORT", "6333")
    
    return LightweightEmbeddingClient(
        project_name=project_name,
        embedding_url=f"http://localhost:{embedding_port}",
        qdrant_url=f"http://localhost:{qdrant_port}"
    )