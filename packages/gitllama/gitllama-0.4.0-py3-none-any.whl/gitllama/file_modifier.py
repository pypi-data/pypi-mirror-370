"""
File Modifier for GitLlama
Handles AI-driven file operations: create, modify, delete up to 5 files
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from .ai_decision_formatter import AIDecisionFormatter
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class FileModifier:
    """AI-driven file modification system"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        """Initialize the File Modifier.
        
        Args:
            client: OllamaClient instance
            model: Model name to use for decisions
        """
        self.client = client
        self.model = model
        self.decision_formatter = AIDecisionFormatter()
        self.selected_files: List[Dict[str, Any]] = []
        
        logger.info(f"FileModifier initialized with model: {model}")
    
    def select_files_to_modify(self, repo_path: Path, project_info: Dict, max_files: int = 5) -> List[Dict[str, Any]]:
        """AI selects up to 5 files to create, modify, or delete.
        
        Args:
            repo_path: Path to repository
            project_info: Project analysis information
            max_files: Maximum number of files to select
            
        Returns:
            List of file operation dictionaries
        """
        logger.info(f"AI selecting up to {max_files} files to modify")
        
        # Get existing files for context
        existing_files = list(repo_path.rglob("*"))
        existing_files = [f for f in existing_files if f.is_file() and not any(part.startswith('.') for part in f.parts)]
        
        # Prepare context for AI
        context = self._build_file_selection_context(project_info, existing_files)
        
        # Ask AI to decide how many files to work with (1-5)
        num_files_decision = self.decision_formatter.make_ai_decision(
            client=self.client,
            model=self.model,
            context=context,
            question="How many files should we work with for maximum impact?",
            options=["1", "2", "3", "4", "5"],
            additional_context="Consider the project size and complexity."
        )
        
        num_files = int(num_files_decision[0])
        logger.info(f"AI decided to work with {num_files} files")
        
        # For each file, make individual decisions
        file_operations = []
        for i in range(num_files):
            logger.info(f"Selecting file operation {i+1}/{num_files}")
            
            # Decide operation type
            operation = self._decide_operation_type(context, i+1, num_files)
            
            # Decide on file path
            file_path = self._decide_file_path(context, operation, existing_files, i+1)
            
            # Generate content if needed
            content = ""
            if operation in ["CREATE", "MODIFY"]:
                content = self._generate_file_content(repo_path, project_info, file_path, operation)
            
            file_op = {
                "operation": operation,
                "file_path": file_path,
                "content": content,
                "reason": f"AI selected for {operation.lower()} operation"
            }
            
            file_operations.append(file_op)
            logger.info(f"Selected: {operation} {file_path}")
        
        self.selected_files = file_operations
        return file_operations
    
    def _build_file_selection_context(self, project_info: Dict, existing_files: List[Path]) -> str:
        """Build context for file selection decisions."""
        context_parts = [
            f"Project Type: {project_info.get('project_type', 'unknown')}",
            f"Technologies: {', '.join(project_info.get('technologies', [])[:5])}",
            f"Has TODO.md: {project_info.get('has_todo', False)}",
            f"Existing files: {len(existing_files)}",
        ]
        
        # Add synthesis info if available
        synthesis = project_info.get('synthesis', {})
        if synthesis:
            context_parts.extend([
                f"Next Priority: {synthesis.get('next_priority', 'unknown')}",
                f"Immediate Tasks: {', '.join(synthesis.get('immediate_tasks', [])[:3])}"
            ])
        
        return "; ".join(context_parts)
    
    def _decide_operation_type(self, context: str, file_num: int, total_files: int) -> str:
        """AI decides what type of operation to perform."""
        question = f"What operation should we perform for file {file_num} of {total_files}?"
        
        operation, _ = self.decision_formatter.make_ai_decision(
            client=self.client,
            model=self.model,
            context=context,
            question=question,
            options=["CREATE", "MODIFY", "DELETE"],
            additional_context="CREATE=new file, MODIFY=change existing, DELETE=remove file"
        )
        
        return operation
    
    def _decide_file_path(self, context: str, operation: str, existing_files: List[Path], file_num: int) -> str:
        """AI decides on the file path for the operation."""
        if operation == "DELETE":
            # For DELETE, pick from existing files
            if existing_files:
                # Get a few file options
                file_options = [str(f.name) for f in existing_files[:10]]
                
                selected_file, _ = self.decision_formatter.make_ai_decision(
                    client=self.client,
                    model=self.model,
                    context=context,
                    question=f"Which existing file should we delete?",
                    options=file_options[:5],  # Limit to 5 options
                    additional_context=f"Available files: {', '.join(file_options)}"
                )
                
                # Find the full path
                for f in existing_files:
                    if f.name == selected_file:
                        return str(f.relative_to(f.parents[len(f.parents)-1]))
                
                return str(existing_files[0].relative_to(existing_files[0].parents[len(existing_files[0].parents)-1]))
            else:
                return "temp_file.txt"  # Fallback
        
        else:
            # For CREATE/MODIFY, generate appropriate path
            file_type_decision, _ = self.decision_formatter.make_ai_decision(
                client=self.client,
                model=self.model,
                context=context,
                question=f"What type of file should we {operation.lower()} for operation {file_num}?",
                options=["DOCUMENTATION", "CONFIG", "CODE", "TEST", "UTILITY"],
                additional_context="Choose the most impactful file type"
            )
            
            # Generate path based on type
            return self._generate_file_path_by_type(file_type_decision)
    
    def _generate_file_path_by_type(self, file_type: str) -> str:
        """Generate a file path based on the file type."""
        type_mappings = {
            "DOCUMENTATION": "docs/AI_IMPROVEMENTS.md",
            "CONFIG": "config/ai_settings.json",
            "CODE": "src/ai_helpers.py",
            "TEST": "tests/test_ai_integration.py",
            "UTILITY": "scripts/ai_utilities.sh"
        }
        
        return type_mappings.get(file_type, "AI_GENERATED.txt")
    
    def _generate_file_content(self, repo_path: Path, project_info: Dict, file_path: str, operation: str) -> str:
        """Generate content for a file using AI."""
        logger.info(f"🤖 AI: Generating content for {operation} {file_path}")
        
        # Build context for content generation
        context_parts = [
            f"Operation: {operation} {file_path}",
            f"Project: {project_info.get('project_type', 'unknown')}",
            f"Technologies: {', '.join(project_info.get('technologies', [])[:3])}"
        ]
        
        # Add TODO.md context if available
        if project_info.get('has_todo') and project_info.get('vibe', {}).get('todo_content'):
            todo_content = project_info['vibe']['todo_content'][:300]
            context_parts.append(f"TODO.md guidance: {todo_content}")
        
        context = "\n".join(context_parts)
        
        # If MODIFY, try to read existing content
        existing_content = ""
        if operation == "MODIFY":
            try:
                full_path = repo_path / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        existing_content = f.read()[:1000]  # First 1000 chars
            except Exception as e:
                logger.debug(f"Could not read existing file {file_path}: {e}")
        
        prompt = f"""Generate content for this file operation:

Context:
{context}

File: {file_path}
Operation: {operation}

{f'Existing content preview: {existing_content}' if existing_content else ''}

Generate appropriate file content that:
1. Serves the project's needs
2. Is well-formatted and professional
3. Includes helpful comments/documentation
4. Follows best practices for the file type

Content:"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        return response.strip()
    
    def execute_file_operations(self, repo_path: Path, file_operations: List[Dict[str, Any]]) -> List[str]:
        """Execute the file operations and return list of modified files.
        
        Args:
            repo_path: Repository path
            file_operations: List of operations to execute
            
        Returns:
            List of file paths that were modified
        """
        logger.info(f"Executing {len(file_operations)} file operations")
        modified_files = []
        
        for i, op in enumerate(file_operations, 1):
            logger.info(f"Executing operation {i}/{len(file_operations)}: {op['operation']} {op['file_path']}")
            
            file_path = repo_path / op['file_path']
            
            try:
                if op['operation'] == 'CREATE':
                    # Create directory if needed
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(op.get('content', ''))
                    
                    logger.info(f"✓ Created: {op['file_path']}")
                    modified_files.append(op['file_path'])
                
                elif op['operation'] == 'MODIFY':
                    if file_path.exists():
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(op.get('content', ''))
                        logger.info(f"✓ Modified: {op['file_path']}")
                        modified_files.append(op['file_path'])
                    else:
                        logger.warning(f"File to modify does not exist: {op['file_path']}")
                
                elif op['operation'] == 'DELETE':
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"✓ Deleted: {op['file_path']}")
                        modified_files.append(op['file_path'])
                    else:
                        logger.warning(f"File to delete does not exist: {op['file_path']}")
                
            except Exception as e:
                logger.error(f"Failed to execute {op['operation']} on {op['file_path']}: {e}")
        
        logger.info(f"Successfully executed operations on {len(modified_files)} files")
        return modified_files
    
    def commit_and_push_changes(self, repo_path: Path, modified_files: List[str], 
                               project_info: Dict) -> bool:
        """Commit and push the changes made.
        
        Args:
            repo_path: Repository path
            modified_files: List of files that were modified
            project_info: Project information for commit message
            
        Returns:
            True if successful, False otherwise
        """
        if not modified_files:
            logger.info("No files to commit")
            return True
        
        try:
            # Add files to git
            logger.info("Adding files to git...")
            for file_path in modified_files:
                result = subprocess.run(
                    ['git', 'add', file_path],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            # Generate commit message with AI
            commit_message = self._generate_commit_message(modified_files, project_info)
            
            # Commit changes
            logger.info(f"Committing changes: {commit_message}")
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Push changes
            logger.info("Pushing changes to remote...")
            result = subprocess.run(
                ['git', 'push'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✓ Successfully committed and pushed changes")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during commit/push: {e}")
            return False
    
    def _generate_commit_message(self, modified_files: List[str], project_info: Dict) -> str:
        """Generate a commit message for the changes."""
        # Use AI to decide on commit type
        file_operations_summary = f"Modified {len(modified_files)} files: {', '.join(modified_files[:3])}"
        if len(modified_files) > 3:
            file_operations_summary += f" and {len(modified_files) - 3} more"
        
        commit_type, _ = self.decision_formatter.make_ai_decision(
            client=self.client,
            model=self.model,
            context=file_operations_summary,
            question="What type of commit is this?",
            options=["feat", "fix", "docs", "chore", "refactor"],
            additional_context="Choose the most appropriate conventional commit type"
        )
        
        # Generate short description
        synthesis = project_info.get('synthesis', {})
        next_priority = synthesis.get('next_priority', 'improvements')
        
        # Create commit message
        if len(modified_files) == 1:
            commit_message = f"{commit_type}: update {Path(modified_files[0]).name}"
        else:
            commit_message = f"{commit_type}: update {len(modified_files)} files for {next_priority[:30]}"
        
        return commit_message
    
    def run_full_modification_workflow(self, repo_path: Path, project_info: Dict) -> Dict[str, Any]:
        """Run the complete file modification workflow.
        
        Args:
            repo_path: Repository path
            project_info: Project analysis information
            
        Returns:
            Dictionary with workflow results
        """
        logger.info("Starting full file modification workflow")
        
        # Step 1: Select files to modify
        file_operations = self.select_files_to_modify(repo_path, project_info)
        
        # Step 2: Execute operations
        modified_files = self.execute_file_operations(repo_path, file_operations)
        
        # Step 3: Commit and push
        success = self.commit_and_push_changes(repo_path, modified_files, project_info)
        
        # Generate summary
        result = {
            "file_operations": file_operations,
            "modified_files": modified_files,
            "commit_success": success,
            "decision_summary": self.decision_formatter.get_decision_summary(),
            "total_decisions": len(self.decision_formatter.decision_history)
        }
        
        logger.info(f"File modification workflow complete. Modified {len(modified_files)} files.")
        return result