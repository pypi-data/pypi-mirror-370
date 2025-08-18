"""Smart truncation using AI to summarize large outputs."""

import os
from typing import Optional
from openai import OpenAI
from code_puppy.tools.tool_logger import log_smart_truncate


def smart_truncate(content: str, max_length: int = 50000, chunk_size: int = 100000) -> str:
    """
    Intelligently truncate large content using AI summarization.
    
    Args:
        content: The content to potentially truncate
        max_length: Maximum desired output length
        chunk_size: Size of chunks to process with AI
    
    Returns:
        Original content if under max_length, otherwise AI-summarized version
    """
    input_size = len(content)
    
    if input_size <= max_length:
        log_smart_truncate(
            input_size=input_size,
            output_size=input_size,
            method="no_truncation",
            details={"reason": "content under limit", "limit": max_length}
        )
        return content
    
    # Check if smart truncation is enabled
    from code_puppy.config import get_smart_truncate
    smart_enabled = get_smart_truncate()
    
    if not smart_enabled:
        result = simple_truncate(content, max_length)
        log_smart_truncate(
            input_size=input_size,
            output_size=len(result),
            method="simple_truncate",
            details={"reason": "smart_truncate disabled in config"}
        )
        return result
    
    # Check if we have Cerebras API configured
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        result = simple_truncate(content, max_length)
        log_smart_truncate(
            input_size=input_size,
            output_size=len(result),
            method="simple_truncate",
            details={"reason": "no CEREBRAS_API_KEY found"}
        )
        return result
    
    try:
        log_smart_truncate(
            input_size=input_size,
            output_size=0,
            method="ai_summary_starting",
            details={
                "max_length": max_length,
                "chunk_size": chunk_size,
                "api_key_prefix": api_key[:10] + "..." if api_key else None,
                "base_url": "https://api.cerebras.ai/v1"
            }
        )
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1"
        )
        
        # For very large content, chunk it up
        chunks = []
        for i in range(0, input_size, chunk_size):
            chunks.append(content[i:i + chunk_size])
        
        log_smart_truncate(
            input_size=input_size,
            output_size=0,
            method="chunking_complete",
            chunks=len(chunks),
            details={"chunk_sizes": [len(c) for c in chunks]}
        )
        
        if len(chunks) == 1:
            # Single chunk - just summarize it
            result = summarize_chunk(client, content, max_length)
            log_smart_truncate(
                input_size=input_size,
                output_size=len(result),
                method="ai_summary_single",
                chunks=1,
                api_calls=1,
                details={"success": True}
            )
            return result
        
        # Multiple chunks - summarize each then combine
        summaries = []
        api_calls = 0
        
        for i, chunk in enumerate(chunks):
            try:
                summary = summarize_chunk(
                    client, 
                    chunk, 
                    max_length // len(chunks),  # Distribute length budget
                    chunk_num=i+1,
                    total_chunks=len(chunks)
                )
                summaries.append(summary)
                api_calls += 1
                
                log_smart_truncate(
                    input_size=len(chunk),
                    output_size=len(summary),
                    method=f"chunk_{i+1}_summarized",
                    details={"chunk_num": i+1, "total_chunks": len(chunks)}
                )
            except Exception as chunk_error:
                log_smart_truncate(
                    input_size=len(chunk),
                    output_size=0,
                    method=f"chunk_{i+1}_failed",
                    error=chunk_error,
                    details={"chunk_num": i+1, "error": str(chunk_error)}
                )
                # Use simple truncate for failed chunk
                summaries.append(simple_truncate(chunk, max_length // len(chunks)))
        
        # Combine summaries
        combined = "\n\n".join(summaries)
        
        # If combined is still too long, summarize again
        if len(combined) > max_length:
            final = summarize_chunk(client, combined, max_length, is_final=True)
            api_calls += 1
            log_smart_truncate(
                input_size=input_size,
                output_size=len(final),
                method="ai_summary_multi_final",
                chunks=len(chunks),
                api_calls=api_calls,
                details={"final_summary": True, "combined_size": len(combined)}
            )
            return final
        
        log_smart_truncate(
            input_size=input_size,
            output_size=len(combined),
            method="ai_summary_multi",
            chunks=len(chunks),
            api_calls=api_calls,
            details={"combined_summaries": True}
        )
        return combined
        
    except Exception as e:
        # If AI summarization fails, fall back to simple truncation
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        
        print(f"Smart truncation failed: {e}")
        result = simple_truncate(content, max_length)
        
        log_smart_truncate(
            input_size=input_size,
            output_size=len(result),
            method="simple_truncate_fallback",
            error=e,
            details=error_details
        )
        return result


def summarize_chunk(
    client: OpenAI, 
    content: str, 
    target_length: int,
    chunk_num: Optional[int] = None,
    total_chunks: Optional[int] = None,
    is_final: bool = False
) -> str:
    """Use AI to summarize a chunk of content."""
    
    # Estimate tokens (rough: 1 token ≈ 4 chars)
    target_tokens = min(target_length // 4, 8000)  # Cap at 8k tokens
    
    log_smart_truncate(
        input_size=len(content),
        output_size=0,
        method="summarize_chunk_starting",
        details={
            "target_length": target_length,
            "target_tokens": target_tokens,
            "chunk_num": chunk_num,
            "total_chunks": total_chunks,
            "is_final": is_final
        }
    )
    
    if is_final:
        prompt = f"""Summarize this combined output into {target_tokens} tokens or less.
Preserve the most important information, structure, and any error messages.
Keep code snippets and file paths intact where critical.

Content:
{content[:10000]}..."""  # Truncate prompt to avoid API errors
    elif chunk_num and total_chunks:
        prompt = f"""This is part {chunk_num} of {total_chunks} of a large output.
Summarize it into {target_tokens} tokens or less, preserving:
- File paths and structure
- Important code elements
- Error messages
- Key patterns and relationships

Content:
{content[:10000]}..."""
    else:
        prompt = f"""Summarize this output into {target_tokens} tokens or less.
Preserve the most important information, especially:
- Directory/file structure
- Code signatures (functions, classes)
- Any errors or warnings
- Key relationships

Content:
{content[:10000]}..."""
    
    try:
        log_smart_truncate(
            input_size=len(content),
            output_size=0,
            method="api_call_starting",
            details={
                "model": "llama-3.3-70b",
                "max_tokens": target_tokens,
                "prompt_size": len(prompt)
            }
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b",  # Use fast model for summarization
            messages=[
                {"role": "system", "content": "You are a concise technical summarizer. Preserve structure and important details."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=target_tokens,
            temperature=0.3  # Low temp for consistent summaries
        )
        
        summary = response.choices[0].message.content
        
        log_smart_truncate(
            input_size=len(content),
            output_size=len(summary),
            method="api_call_success",
            api_calls=1,
            details={
                "response_length": len(summary),
                "chunk_num": chunk_num,
                "is_final": is_final
            }
        )
        
        # Add markers to show this was summarized
        if chunk_num and total_chunks:
            return f"[AI Summary - Part {chunk_num}/{total_chunks}]\n{summary}"
        else:
            return f"[AI Summary - {len(content):,} chars → {len(summary):,} chars]\n{summary}"
            
    except Exception as e:
        log_smart_truncate(
            input_size=len(content),
            output_size=0,
            method="api_call_failed",
            error=e,
            details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "chunk_num": chunk_num
            }
        )
        print(f"Summarization failed: {e}")
        return simple_truncate(content, target_length)


def simple_truncate(content: str, max_length: int) -> str:
    """Simple truncation fallback - show beginning and end."""
    if len(content) <= max_length:
        return content
    
    # Take first part and last part
    first_part = content[:max_length//2]
    last_part = content[-(max_length//2):]
    
    result = f"{first_part}\n\n... [Truncated: {len(content):,} chars total, showing {max_length:,} chars] ...\n\n{last_part}"
    
    log_smart_truncate(
        input_size=len(content),
        output_size=len(result),
        method="simple_truncate",
        details={"first_part_size": len(first_part), "last_part_size": len(last_part)}
    )
    
    return result