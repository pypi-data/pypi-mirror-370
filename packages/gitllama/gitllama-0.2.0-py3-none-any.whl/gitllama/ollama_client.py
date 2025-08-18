"""Ollama API client for terminal chat interface."""

import json
import requests
from typing import Dict, List, Optional, Generator, Tuple
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.
        
        Args:
            base_url: The base URL for the Ollama API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.model_context_sizes = {
            # Common Ollama models and their approximate context sizes
            "llama3.2:3b": 4096,
            "llama3.2:1b": 2048,
            "llama3.1:8b": 8192,
            "codellama:7b": 4096,
            "mistral:7b": 8192,
            "gemma2:2b": 8192,
            "phi3:mini": 4096,
            "gemma3:4b": 124000,

            # Default fallback
            "default": 4096
        }
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException:
            return []
    
    def get_model_context_size(self, model: str) -> int:
        """Get the context window size for a model.
        
        Args:
            model: Model name
            
        Returns:
            Context size in tokens (estimated)
        """
        # Try to get from our known models first
        for known_model, size in self.model_context_sizes.items():
            if known_model in model.lower():
                return size
        
        # Try to get from API
        try:
            details = self.get_model_details(model)
            # Some models report context_length in their details
            if 'context_length' in details:
                return details['context_length']
        except:
            pass
        
        # Default fallback
        return self.model_context_sizes["default"]
    
    def count_tokens(self, text: str, model: str = None) -> int:
        """
        Estimate token count for text. 
        Simple estimation: ~4 characters per token for English text.
        
        Args:
            text: Text to count tokens for
            model: Model name (unused but kept for compatibility)
            
        Returns:
            Estimated token count
        """
        # Simple estimation: average of 4 characters per token
        # This is a rough approximation but works reasonably well for English
        return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Total estimated token count
        """
        total_tokens = 0
        for message in messages:
            # Add tokens for message structure (role, etc.)
            total_tokens += 4
            # Add content tokens
            for value in message.values():
                if isinstance(value, str):
                    total_tokens += self.count_tokens(value)
        return total_tokens
    
    def trim_to_context_window(self, text: str, max_tokens: int) -> str:
        """Trim text to fit within token limit.
        
        Args:
            text: Text to trim
            max_tokens: Maximum token count
            
        Returns:
            Trimmed text
        """
        estimated_chars = max_tokens * 4  # Reverse estimation
        if len(text) > estimated_chars:
            return text[:estimated_chars] + "...[truncated]"
        return text
    
    def split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks that fit within token limit.
        
        Args:
            text: Text to split
            chunk_size: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        max_chars = chunk_size * 4  # Convert tokens to approximate characters
        chunks = []
        
        # Split by lines first to maintain structure
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            if current_size + line_size > max_chars and current_chunk:
                # Save current chunk and start new one
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def get_model_details(self, model: str) -> Dict:
        """Get details for a specific model."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}
    
    def pull_model(self, model: str) -> bool:
        """Pull a model if it's not available locally."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        print(f"\r{data['status']}", end='', flush=True)
                    if data.get('status') == 'success':
                        print()  # New line after completion
                        return True
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]], 
                   system: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat responses from Ollama.
        
        Args:
            model: The model to use for chat
            messages: List of message dicts with 'role' and 'content'
            system: Optional system message
            
        Yields:
            Response chunks as strings
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        if system:
            payload["system"] = system
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
                    if data.get('done', False):
                        break
                        
        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"