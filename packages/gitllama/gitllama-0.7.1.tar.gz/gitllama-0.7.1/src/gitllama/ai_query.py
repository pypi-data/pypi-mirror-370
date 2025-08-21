"""
AI Query Interface for GitLlama
Simple, clean interface for multiple choice and open response queries
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .ollama_client import OllamaClient
from .context_manager import context_manager
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


@dataclass
class ChoiceResult:
    """Result from a multiple choice query"""
    index: int
    value: str
    confidence: float
    raw: str


@dataclass 
class OpenResult:
    """Result from an open response query"""
    content: str
    raw: str


class AIQuery:
    """Simple interface for AI queries - either multiple choice or open response"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.parser = ResponseParser()
    
    def choice(
        self, 
        question: str,
        options: List[str],
        context: str = "",
        context_name: str = "choice"
    ) -> ChoiceResult:
        """
        Ask AI to pick from options.
        
        Args:
            question: What to ask
            options: List of options to choose from
            context: Optional context
            context_name: For tracking
            
        Returns:
            ChoiceResult with the selection
        """
        # Build simple prompt
        prompt = self._build_choice_prompt(question, options, context)
        
        # Make the query
        messages = [{"role": "user", "content": prompt}]
        
        logger.info(f"🎯 Choice: {question[:50]}... ({len(options)} options)")
        context_manager.get_or_create_context(context_name, f"Choice context for: {question[:50]}")
        context_manager.use_context(context_name, f"Choice: {question[:50]}")
        
        # Get response
        response = ""
        for chunk in self.client.chat_stream(self.model, messages, context_name=context_name):
            response += chunk
        
        # Parse the choice
        index, confidence = self.parser.parse_choice(response, options)
        
        result = ChoiceResult(
            index=index,
            value=options[index] if index >= 0 else options[0],
            confidence=confidence,
            raw=response.strip()
        )
        
        logger.info(f"✅ Selected: {result.value} (confidence: {confidence:.2f})")
        return result
    
    def open(
        self,
        prompt: str,
        context: str = "",
        context_name: str = "open"
    ) -> OpenResult:
        """
        Ask AI for open response.
        
        Args:
            prompt: What to ask
            context: Optional context
            context_name: For tracking
            
        Returns:
            OpenResult with the response
        """
        # Build prompt
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        messages = [{"role": "user", "content": full_prompt}]
        
        logger.info(f"📝 Open: {prompt[:50]}...")
        context_manager.get_or_create_context(context_name, f"Open context for: {prompt[:50]}")
        context_manager.use_context(context_name, f"Open: {prompt[:50]}")
        
        # Get response
        response = ""
        for chunk in self.client.chat_stream(self.model, messages, context_name=context_name):
            response += chunk
        
        # Clean the response
        content = self.parser.clean_text(response)
        
        result = OpenResult(
            content=content,
            raw=response.strip()
        )
        
        logger.info(f"✅ Response: {len(content)} chars")
        return result
    
    def _build_choice_prompt(self, question: str, options: List[str], context: str) -> str:
        """Build a simple choice prompt"""
        parts = []
        
        if context:
            parts.append(f"Context: {context}\n")
        
        parts.append(question)
        parts.append("\nOptions:")
        
        for i, option in enumerate(options):
            parts.append(f"{i+1}. {option}")
        
        parts.append("\nRespond with ONLY the number (1, 2, 3, etc) of your choice:")
        
        return "\n".join(parts)