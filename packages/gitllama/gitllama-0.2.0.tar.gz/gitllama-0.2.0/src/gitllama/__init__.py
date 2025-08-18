"""
GitLlama - AI-powered Git Automation Tool

Simple git automation with AI decision-making: clone, branch, change, commit, push.
"""

__version__ = "0.2.0"

from .git_operations import GitAutomator, GitOperationError
from .ai_coordinator import AICoordinator
from .ollama_client import OllamaClient

__all__ = [
    "GitAutomator",
    "GitOperationError", 
    "AICoordinator",
    "OllamaClient",
]