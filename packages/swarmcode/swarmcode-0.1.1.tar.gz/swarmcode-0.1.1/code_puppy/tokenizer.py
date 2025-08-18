"""Token counting and context management utilities."""

import tiktoken
from typing import List, Dict, Any, Optional
from code_puppy.tools.tool_logger import log_tool

class TokenCounter:
    """Manages token counting and context limits for different models."""
    
    # Model context limits (in tokens)
    MODEL_LIMITS = {
        "gpt-4.1": 128000,
        "gpt-4.1-mini": 128000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "qwen3-coder-480b": 131072,  # Cerebras Qwen limit
        "qwen-3-coder-480b": 131072,  # Alias
        "llama-3.3-70b": 131072,  # Cerebras Llama limit
        "default": 32000  # Conservative default
    }
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize tokenizer for the specified model."""
        self.model_name = model_name
        self.context_limit = self._get_context_limit(model_name)
        
        # Try to get the appropriate tokenizer
        try:
            # For GPT models, use cl100k_base (GPT-4 tokenizer)
            if "gpt" in model_name.lower():
                self.encoder = tiktoken.get_encoding("cl100k_base")
            else:
                # For other models, use a reasonable default
                self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            log_tool(
                tool_name="tokenizer_init_error",
                input_data={"model": model_name},
                output_data=None,
                error=e,
                metadata={"fallback": "cl100k_base"}
            )
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def _get_context_limit(self, model_name: str) -> int:
        """Get the context limit for a model."""
        # Check exact match first
        if model_name in self.MODEL_LIMITS:
            return self.MODEL_LIMITS[model_name]
        
        # Check partial matches
        model_lower = model_name.lower()
        for key, limit in self.MODEL_LIMITS.items():
            if key.lower() in model_lower or model_lower in key.lower():
                return limit
        
        # Return conservative default
        return self.MODEL_LIMITS["default"]
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        if not text:
            return 0
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            log_tool(
                tool_name="token_count_fallback",
                input_data={"text_length": len(text)},
                output_data=None,
                error=e,
                metadata={"method": "character_estimate"}
            )
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Count tokens in a list of messages."""
        total_tokens = 0
        
        for message in messages:
            # Count role tokens (approximately 4 tokens for message structure)
            total_tokens += 4
            
            # Count content tokens
            if isinstance(message.get("content"), str):
                total_tokens += self.count_tokens(message["content"])
            elif isinstance(message.get("content"), list):
                # Handle multi-part messages
                for part in message["content"]:
                    if isinstance(part, dict) and "text" in part:
                        total_tokens += self.count_tokens(part["text"])
                    elif isinstance(part, str):
                        total_tokens += self.count_tokens(part)
        
        return total_tokens
    
    def get_context_usage(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed context usage statistics."""
        total_tokens = self.count_messages_tokens(messages)
        
        usage = {
            "total_tokens": total_tokens,
            "context_limit": self.context_limit,
            "used_percentage": (total_tokens / self.context_limit * 100) if self.context_limit > 0 else 0,
            "remaining_tokens": self.context_limit - total_tokens,
            "near_limit": total_tokens > (self.context_limit * 0.8),  # Warning at 80%
            "at_limit": total_tokens >= self.context_limit
        }
        
        # Log if we're near the limit
        if usage["near_limit"]:
            log_tool(
                tool_name="context_usage_warning",
                input_data={"model": self.model_name},
                output_data=usage,
                metadata={"warning": "approaching_context_limit"}
            )
        
        return usage
    
    def truncate_to_limit(self, messages: List[Dict[str, Any]], 
                         preserve_system: bool = True,
                         preserve_recent: int = 5) -> List[Dict[str, Any]]:
        """Truncate messages to fit within context limit."""
        current_tokens = self.count_messages_tokens(messages)
        
        if current_tokens <= self.context_limit:
            return messages
        
        log_tool(
            tool_name="context_truncation",
            input_data={
                "original_tokens": current_tokens,
                "limit": self.context_limit,
                "message_count": len(messages)
            },
            output_data=None,
            metadata={"action": "truncating_messages"}
        )
        
        result = []
        
        # Preserve system messages if requested
        if preserve_system:
            system_messages = [m for m in messages if m.get("role") == "system"]
            result.extend(system_messages)
            messages = [m for m in messages if m.get("role") != "system"]
        
        # Always preserve the most recent messages
        if preserve_recent > 0 and len(messages) > preserve_recent:
            recent = messages[-preserve_recent:]
            older = messages[:-preserve_recent]
        else:
            recent = messages
            older = []
        
        # Add recent messages first
        result.extend(recent)
        
        # Add older messages if there's room
        for message in reversed(older):
            test_messages = [message] + result
            if self.count_messages_tokens(test_messages) <= self.context_limit * 0.9:  # Leave 10% buffer
                result.insert(len(result) - len(recent), message)
            else:
                break
        
        final_tokens = self.count_messages_tokens(result)
        log_tool(
            tool_name="context_truncation_complete",
            input_data={"model": self.model_name},
            output_data={
                "final_tokens": final_tokens,
                "final_message_count": len(result),
                "dropped_messages": len(messages) - len(result) + len(system_messages) if preserve_system else 0
            },
            metadata={"success": True}
        )
        
        return result


def format_context_usage(usage: Dict[str, Any]) -> str:
    """Format context usage for display."""
    percentage = usage["used_percentage"]
    tokens = usage["total_tokens"]
    limit = usage["context_limit"]
    
    # Color coding based on usage
    if percentage >= 90:
        color = "red"
        emoji = "🔴"
    elif percentage >= 70:
        color = "yellow"
        emoji = "🟡"
    else:
        color = "green"
        emoji = "🟢"
    
    return f"{emoji} Context: [{color}]{tokens:,}/{limit:,} tokens ({percentage:.1f}%)[/{color}]"