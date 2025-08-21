"""
Simplified File Executor for GitLlama
Executes the planned file operations
"""

import logging
from pathlib import Path
from typing import Dict, List
from .ollama_client import OllamaClient
from .ai_query import AIQuery

logger = logging.getLogger(__name__)


class TodoExecutor:
    """Executes planned file operations"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.ai = AIQuery(client, model)
    
    def execute_plan(self, repo_path: Path, action_plan: Dict) -> List[str]:
        """Execute the action plan"""
        logger.info(f"Executing plan with {len(action_plan['files_to_modify'])} files")
        
        modified_files = []
        
        for file_info in action_plan['files_to_modify']:
            file_path = repo_path / file_info['path']
            operation = file_info['operation']
            
            logger.info(f"Executing {operation} on {file_info['path']}")
            
            if operation == 'CREATE':
                content = self._generate_file_content(
                    file_info['path'],
                    action_plan['plan'],
                    action_plan['todo_excerpt']
                )
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                modified_files.append(file_info['path'])
                
            elif operation == 'MODIFY':
                if file_path.exists():
                    original = file_path.read_text()
                    content = self._modify_file_content(
                        file_info['path'],
                        original,
                        action_plan['plan'],
                        action_plan['todo_excerpt']
                    )
                    file_path.write_text(content)
                    modified_files.append(file_info['path'])
                else:
                    logger.warning(f"File to modify doesn't exist: {file_info['path']}")
                    
            elif operation == 'DELETE':
                if file_path.exists():
                    file_path.unlink()
                    modified_files.append(file_info['path'])
                else:
                    logger.warning(f"File to delete doesn't exist: {file_info['path']}")
        
        return modified_files
    
    def _generate_file_content(self, file_path: str, plan: str, todo: str) -> str:
        """Generate content for a new file"""
        prompt = f"""Generate complete content for this new file: {file_path}

Based on this plan:
{plan[:1000]}

To help implement this TODO:
{todo[:500]}

Generate professional, working code with comments.
Wrap the content in appropriate markdown code blocks."""
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="file_generation"
        )
        
        # Extract code from markdown blocks
        content = result.content
        if '```' in content:
            import re
            matches = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            if matches:
                content = matches[0]
        
        return content
    
    def _modify_file_content(self, file_path: str, original: str, plan: str, todo: str) -> str:
        """Modify existing file content"""
        prompt = f"""Modify this file according to the plan: {file_path}

Current content:
{original[:2000]}

Plan excerpt:
{plan[:1000]}

TODO excerpt:
{todo[:500]}

Generate the COMPLETE modified file content.
Wrap in appropriate markdown code blocks."""
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="file_modification"
        )
        
        # Extract code from markdown blocks
        content = result.content
        if '```' in content:
            import re
            matches = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            if matches:
                content = matches[0]
        
        return content