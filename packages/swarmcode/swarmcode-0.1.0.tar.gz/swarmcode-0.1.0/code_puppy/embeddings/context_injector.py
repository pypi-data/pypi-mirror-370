"""
Context injection for embeddings.
"""

class ContextInjector:
    """Injects contextual information into embeddings."""
    
    def __init__(self):
        self.contexts = {}
    
    def add_context(self, key: str, value: any):
        """Add context information."""
        self.contexts[key] = value
    
    def get_context(self, key: str):
        """Get context information."""
        return self.contexts.get(key)
    
    def inject(self, text: str) -> str:
        """Inject context into text."""
        # For now, just return the text as-is
        return text