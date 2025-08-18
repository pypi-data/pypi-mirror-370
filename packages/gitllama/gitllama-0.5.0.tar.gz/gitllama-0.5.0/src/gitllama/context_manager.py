"""
Context Window Manager for GitLlama
Tracks and manages AI context windows throughout the execution lifecycle
"""

import json
import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContextWindowUsage:
    """Tracks usage of a specific context window"""
    name: str
    content: str
    created_at: datetime
    usage_count: int = 0
    last_used: Optional[datetime] = None
    memory_size_bytes: int = 0
    
    def __post_init__(self):
        self.memory_size_bytes = sys.getsizeof(self.content.encode('utf-8'))
    
    def mark_used(self):
        """Mark this context as used"""
        self.usage_count += 1
        self.last_used = datetime.now()
        logger.info(f"🔄 Context window '{self.name}' used (total: {self.usage_count} times)")
    
    def update_content(self, new_content: str):
        """Update context content (allowed per requirements)"""
        self.content = new_content
        self.memory_size_bytes = sys.getsizeof(new_content.encode('utf-8'))
        logger.info(f"📝 Context window '{self.name}' content updated ({self.memory_size_bytes} bytes)")


class ContextWindowManager:
    """Manages all context windows for AI API calls"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single manager instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the context manager (only once)"""
        if not self._initialized:
            self.contexts: Dict[str, ContextWindowUsage] = {}
            self.api_call_log: List[Dict[str, Any]] = []
            self.total_calls = 0
            ContextWindowManager._initialized = True
            logger.info("🧠 Context Window Manager initialized")
    
    def get_or_create_context(self, name: str, content: str = "") -> str:
        """Get existing context or create new one. Returns the context name."""
        if name in self.contexts:
            # Reuse existing context
            logger.info(f"♻️ Reusing existing context window: {name}")
            return name
        else:
            # Create new context
            self.contexts[name] = ContextWindowUsage(
                name=name,
                content=content,
                created_at=datetime.now()
            )
            logger.info(f"🆕 Created new context window: {name} ({len(content)} chars)")
            return name
    
    def update_context_content(self, name: str, content: str):
        """Update content of existing context window"""
        if name in self.contexts:
            self.contexts[name].update_content(content)
        else:
            logger.warning(f"⚠️ Attempted to update non-existent context: {name}")
    
    def use_context(self, context_name: str, operation_description: str = "") -> str:
        """Mark a context as used and log the API call"""
        if context_name not in self.contexts:
            logger.error(f"❌ Attempted to use non-existent context: {context_name}")
            # Create emergency context to prevent crashes
            self.get_or_create_context(context_name, "Emergency context created")
        
        # Mark as used
        self.contexts[context_name].mark_used()
        
        # Log the API call
        api_call = {
            "timestamp": datetime.now(),
            "context_name": context_name,
            "operation": operation_description,
            "call_number": self.total_calls + 1
        }
        self.api_call_log.append(api_call)
        self.total_calls += 1
        
        logger.info(f"🤖 AI API call #{self.total_calls} using context '{context_name}': {operation_description}")
        
        return self.contexts[context_name].content
    
    def get_context_content(self, name: str) -> str:
        """Get context content without marking as used"""
        if name in self.contexts:
            return self.contexts[name].content
        return ""
    
    def get_total_context_windows(self) -> int:
        """Get total number of context windows created"""
        return len(self.contexts)
    
    def get_total_memory_usage_gb(self) -> float:
        """Calculate total memory usage of all contexts in gigabytes"""
        total_bytes = sum(ctx.memory_size_bytes for ctx in self.contexts.values())
        return total_bytes / (1024 ** 3)  # Convert to GB
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of all context windows for reporting"""
        return {
            "total_contexts": len(self.contexts),
            "total_api_calls": self.total_calls,
            "total_memory_gb": self.get_total_memory_usage_gb(),
            "contexts": {
                name: {
                    "usage_count": ctx.usage_count,
                    "memory_size_bytes": ctx.memory_size_bytes,
                    "created_at": ctx.created_at.isoformat(),
                    "last_used": ctx.last_used.isoformat() if ctx.last_used else None,
                    "content_preview": ctx.content[:200] + "..." if len(ctx.content) > 200 else ctx.content
                }
                for name, ctx in self.contexts.items()
            },
            "api_calls": [
                {
                    "timestamp": call["timestamp"].isoformat(),
                    "context_name": call["context_name"],
                    "operation": call["operation"],
                    "call_number": call["call_number"]
                }
                for call in self.api_call_log
            ]
        }
    
    def get_context_list_for_runtime_display(self) -> str:
        """Get formatted context list for end-of-runtime display"""
        if not self.contexts:
            return "No context windows were used during execution."
        
        lines = [
            f"📊 Context Windows Summary ({len(self.contexts)} total):",
            f"💾 Total Memory Usage: {self.get_total_memory_usage_gb():.6f} GB",
            f"🔢 Total API Calls: {self.total_calls}",
            "",
            "Context Window Details:"
        ]
        
        for name, ctx in self.contexts.items():
            lines.extend([
                f"  📋 {name}:",
                f"    📈 Used: {ctx.usage_count} times",
                f"    💾 Size: {ctx.memory_size_bytes:,} bytes",
                f"    🕐 Created: {ctx.created_at.strftime('%H:%M:%S')}",
                f"    🕐 Last used: {ctx.last_used.strftime('%H:%M:%S') if ctx.last_used else 'Never'}",
                f"    📝 Content preview: {ctx.content[:100]}{'...' if len(ctx.content) > 100 else ''}",
                ""
            ])
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset the context manager (for testing purposes)"""
        self.contexts.clear()
        self.api_call_log.clear()
        self.total_calls = 0
        logger.info("🔄 Context Window Manager reset")


# Global instance
context_manager = ContextWindowManager()