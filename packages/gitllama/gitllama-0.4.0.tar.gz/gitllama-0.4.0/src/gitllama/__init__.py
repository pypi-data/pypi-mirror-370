"""
GitLlama - AI-powered Git Automation Tool

Simple git automation with AI decision-making: clone, branch, change, commit, push.
"""

__version__ = "0.4.0"

from .git_operations import GitAutomator, GitOperationError
from .ai_coordinator import AICoordinator
from .ollama_client import OllamaClient
from .ai_decision_formatter import AIDecisionFormatter
from .file_modifier import FileModifier

__all__ = [
    "GitAutomator",
    "GitOperationError", 
    "AICoordinator",
    "OllamaClient",
    "AIDecisionFormatter",
    "FileModifier",
]