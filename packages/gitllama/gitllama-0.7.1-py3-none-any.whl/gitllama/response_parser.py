"""
Response Parser for GitLlama
Handles parsing of AI responses for different use cases
"""

import re
import json
import logging
from typing import List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parse AI responses for various formats"""
    
    def parse_choice(self, response: str, options: List[str]) -> Tuple[int, float]:
        """
        Parse a multiple choice response.
        
        Returns:
            Tuple of (selected_index, confidence)
        """
        response = response.strip()
        
        # Try to find a number
        numbers = re.findall(r'\d+', response)
        if numbers:
            try:
                # Get first number, convert to 0-based index
                index = int(numbers[0]) - 1
                if 0 <= index < len(options):
                    return index, 1.0
            except ValueError:
                pass
        
        # Fallback: check if response contains option text
        response_lower = response.lower()
        for i, option in enumerate(options):
            if option.lower() in response_lower:
                return i, 0.7
        
        # Default to first option with low confidence
        logger.warning(f"Could not parse choice from: {response[:50]}")
        return 0, 0.1
    
    def clean_text(self, response: str) -> str:
        """Clean text response - remove common artifacts"""
        text = response.strip()
        
        # Remove thinking tags if present
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def extract_json(self, response: str) -> Optional[Any]:
        """Try to extract JSON from response"""
        # Look for JSON in code blocks
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try direct parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        return None
    
    def extract_code(self, response: str) -> str:
        """Extract code from markdown code blocks"""
        # Find code blocks
        pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            # Return the first/largest code block
            return max(matches, key=len).strip()
        
        # No code blocks found, return as-is
        return response.strip()