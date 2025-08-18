#!/usr/bin/env python3
"""
Embedding tool for Code Puppy - provides semantic search and context retrieval.
"""

import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

from code_puppy.embeddings.lightweight_client import create_client, LightweightEmbeddingClient

logger = logging.getLogger(__name__)

class EmbeddingTool:
    """
    Tool for semantic search and context retrieval in Code Puppy.
    """
    
    def __init__(self, project_name: str = None):
        """Initialize the embedding tool."""
        self.project_name = project_name or os.getenv("PROJECT_NAME", "code_puppy")
        self.client = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize the embedding client."""
        try:
            self.client = create_client(self.project_name)
            health = self.client.health_check()
            
            if health['embedding_service'] and health['qdrant']:
                self._initialized = True
                logger.info(f"Embedding tool initialized for project: {self.project_name}")
                return True
            else:
                logger.warning("Embedding services not healthy")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize embedding tool: {e}")
            return False
    
    def search_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant code based on query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results with metadata
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            results = self.client.search_code(query, limit=limit, score_threshold=0.3)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'file_path': result.payload.get('file_path', ''),
                    'content': result.payload.get('content', ''),
                    'start_line': result.payload.get('start_line', 0),
                    'end_line': result.payload.get('end_line', 0),
                    'score': result.score,
                    'type': result.payload.get('type', 'code')
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return []
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search conversation history.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of conversation results
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            results = self.client.search_conversations(query, limit=limit, score_threshold=0.3)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'conversation_id': result.payload.get('conversation_id', ''),
                    'role': result.payload.get('role', ''),
                    'content': result.payload.get('content', ''),
                    'message_index': result.payload.get('message_index', 0),
                    'score': result.score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def index_file(self, file_path: str, content: str) -> bool:
        """
        Index a file for semantic search.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            True if successful
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            chunks = self.client.index_code(file_path, content)
            logger.info(f"Indexed {chunks} chunks from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            return False
    
    def index_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        """
        Index a conversation for later retrieval.
        
        Args:
            conversation_id: Unique conversation ID
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            True if successful
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            msg_count = self.client.index_conversation(conversation_id, messages)
            logger.info(f"Indexed {msg_count} messages from conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error indexing conversation {conversation_id}: {e}")
            return False
    
    def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """
        Get relevant context for a query.
        
        Args:
            query: User query
            max_context_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        # Search both code and conversations
        code_results = self.search_code(query, limit=3)
        conv_results = self.search_conversations(query, limit=2)
        
        context_parts = []
        
        # Add code context
        if code_results:
            context_parts.append("=== Relevant Code ===")
            for result in code_results[:2]:
                context_parts.append(f"\nFrom {result['file_path']} (relevance: {result['score']:.2f}):")
                content_preview = result['content'][:400]
                context_parts.append(content_preview)
        
        # Add conversation context
        if conv_results:
            context_parts.append("\n=== Relevant Conversation History ===")
            for result in conv_results[:2]:
                context_parts.append(f"\n{result['role'].capitalize()}: {result['content'][:200]}")
        
        # Join and truncate if needed
        context = "\n".join(context_parts)
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        return context if context_parts else ""

# Global instance for easy access
_embedding_tool = None

def get_embedding_tool(project_name: str = None) -> EmbeddingTool:
    """Get or create the global embedding tool instance."""
    global _embedding_tool
    if _embedding_tool is None:
        _embedding_tool = EmbeddingTool(project_name)
    return _embedding_tool

def search_relevant_code(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Quick function to search relevant code."""
    tool = get_embedding_tool()
    return tool.search_code(query, limit)

def get_context(query: str) -> str:
    """Quick function to get context for a query."""
    tool = get_embedding_tool()
    return tool.get_context_for_query(query)