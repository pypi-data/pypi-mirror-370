"""
GitLlama - AI-powered Git Automation Tool

Simple git automation with AI decision-making: clone, branch, change, commit, push.
"""

__version__ = "0.7.1"

from .git_operations import GitAutomator, GitOperationError
from .ai_coordinator import AICoordinator
from .ollama_client import OllamaClient
from .ai_decision_formatter import AIDecisionFormatter
from .file_modifier import FileModifier
from .simplified_coordinator import SimplifiedCoordinator
from .todo_analyzer import TodoAnalyzer
from .todo_planner import TodoPlanner
from .todo_executor import TodoExecutor

__all__ = [
    "GitAutomator",
    "GitOperationError", 
    "AICoordinator",
    "OllamaClient",
    "AIDecisionFormatter",
    "FileModifier",
    "SimplifiedCoordinator",
    "TodoAnalyzer",
    "TodoPlanner",
    "TodoExecutor",
]