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
from .ai_output_parser import ai_output_parser

logger = logging.getLogger(__name__)


class FileModifier:
    """AI-driven file modification system"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b", report_generator=None):
        """Initialize the File Modifier.
        
        Args:
            client: OllamaClient instance
            model: Model name to use for decisions
            report_generator: Optional ReportGenerator instance for report hooks
        """
        self.client = client
        self.model = model
        self.decision_formatter = AIDecisionFormatter(report_generator)
        self.selected_files: List[Dict[str, Any]] = []
        self.report_generator = report_generator
        
        # Track parsing results for report generation
        self.parsing_results = {}
        
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
Operation: {operation} (COMPLETE FILE OVERWRITE)

{f'Existing content preview: {existing_content}' if existing_content else ''}

Generate appropriate file content that:
1. Serves the project's needs
2. Is well-formatted and professional  
3. Includes helpful comments/documentation
4. Follows best practices for the file type

IMPORTANT: You MUST wrap the complete file content in a markdown code block using the appropriate language identifier. For example:

```python
# Your complete file content here
def example():
    pass
```

The content inside the code block will be written directly to the file. Any text outside the code block will be ignored.

Generate the complete file content now:"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="file_modification"):
            response += chunk
        
        # Parse the AI output to extract clean code content
        parse_result = ai_output_parser.parse_for_file_content(response, file_path)
        
        # Store parsing info for reporting
        self._store_parsing_result(file_path, operation, parse_result)
        
        return parse_result.content
    
    def _generate_todo_update(self, repo_path: Path, project_info: Dict, completed_operations: List[Dict[str, Any]]) -> str:
        """Generate updated TODO.md content based on what was accomplished."""
        logger.info("🤖 AI: Generating updated TODO.md content")
        
        # Read existing TODO.md if it exists
        todo_path = repo_path / "TODO.md"
        existing_todo = ""
        if todo_path.exists():
            try:
                with open(todo_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_todo = f.read()
            except Exception as e:
                logger.debug(f"Could not read existing TODO.md: {e}")
        
        # Build context for AI
        context_parts = [
            f"Project Type: {project_info.get('project_type', 'unknown')}",
            f"Technologies: {', '.join(project_info.get('technologies', [])[:5])}",
            f"Operations Completed: {len(completed_operations)} files modified/created"
        ]
        
        # Add synthesis info if available
        synthesis = project_info.get('synthesis', {})
        if synthesis:
            context_parts.extend([
                f"Previous Priority: {synthesis.get('next_priority', 'unknown')}",
                f"Completed Tasks: {', '.join(synthesis.get('immediate_tasks', [])[:3])}"
            ])
        
        # Summarize what was accomplished
        operations_summary = []
        for op in completed_operations:
            operations_summary.append(f"- {op['operation']}: {op['file_path']} ({op.get('reason', 'AI decision')})")
        
        context = "\n".join(context_parts)
        operations_text = "\n".join(operations_summary)
        
        prompt = f"""You are helping maintain a TODO.md file for a software project. Based on the recent work completed, update the TODO.md to reflect the current state and next priorities.

PROJECT CONTEXT:
{context}

WORK JUST COMPLETED:
{operations_text}

EXISTING TODO.md CONTENT:
{existing_todo if existing_todo else "[No existing TODO.md file]"}

INSTRUCTIONS:
1. Review what was just completed and update/remove those items if they're done
2. Keep any existing TODO items that are still relevant and not completed
3. Add new logical next steps based on what was just accomplished
4. Prioritize the most impactful next actions
5. Use clear, actionable language
6. Organize by priority (high/medium/low or similar)
7. Don't remove items unless you're confident they're no longer needed
8. Focus on maintaining project momentum - what should happen next?

IMPORTANT: Wrap your complete TODO.md content in a markdown code block:

```markdown
# TODO

Your complete TODO.md content here...
```

Generate a complete, well-organized TODO.md file that builds on the progress made:"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="file_modification"):
            response += chunk
        
        # Parse the AI output to extract clean markdown content
        parse_result = ai_output_parser.parse_for_file_content(response, "TODO.md")
        
        # Store parsing info for reporting
        self._store_parsing_result("TODO.md", "UPDATE", parse_result)
        
        return parse_result.content
    
    def _update_todo_file(self, repo_path: Path, project_info: Dict, completed_operations: List[Dict[str, Any]]) -> bool:
        """Update the TODO.md file with next steps after completing operations.
        
        Args:
            repo_path: Repository path
            project_info: Project information
            completed_operations: List of operations that were completed
            
        Returns:
            True if TODO.md was updated, False otherwise
        """
        logger.info("Updating TODO.md with next steps")
        
        try:
            # Check if TODO.md exists before writing
            todo_path = repo_path / "TODO.md"
            file_existed = todo_path.exists()
            
            # Generate new TODO content
            new_todo_content = self._generate_todo_update(repo_path, project_info, completed_operations)
            
            # Write to TODO.md
            with open(todo_path, 'w', encoding='utf-8') as f:
                f.write(new_todo_content)
            
            logger.info("✓ Updated TODO.md with next priorities")
            
            # Hook into report generator
            if self.report_generator:
                operation_type = "MODIFY" if file_existed else "CREATE"
                
                # Get trimming info from stored parsing results
                parsing_info = self.parsing_results.get("TODO.md", {})
                was_trimmed = parsing_info.get('was_trimmed', False)
                trimming_details = parsing_info.get('detailed_info', '')
                
                self.report_generator.add_file_operation(
                    operation_type, "TODO.md", "AI updated project TODO list with next priorities",
                    content=new_todo_content,
                    trimmed=was_trimmed,
                    trimming_details=trimming_details
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update TODO.md: {e}")
            return False
    
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
                    # Check if file already exists
                    file_exists = file_path.exists()
                    warning_msg = ""
                    
                    if file_exists:
                        warning_msg = "⚠️ CREATE operation overwrote existing file"
                        logger.warning(f"CREATE operation will overwrite existing file: {op['file_path']}")
                    
                    # Create directory if needed
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(op.get('content', ''))
                    
                    logger.info(f"✓ Created: {op['file_path']}")
                    modified_files.append(op['file_path'])
                    
                    # Hook into report generator
                    if self.report_generator:
                        reason = op.get('reason', 'AI decision')
                        if warning_msg:
                            reason = f"{reason} ({warning_msg})"
                        
                        # Get trimming info from stored parsing results
                        parsing_info = self.parsing_results.get(op['file_path'], {})
                        was_trimmed = parsing_info.get('was_trimmed', False)
                        trimming_details = parsing_info.get('detailed_info', '')
                        
                        self.report_generator.add_file_operation(
                            "CREATE", op['file_path'], reason,
                            content=op.get('content', ''),
                            trimmed=was_trimmed,
                            trimming_details=trimming_details
                        )
                
                elif op['operation'] == 'MODIFY':
                    if file_path.exists():
                        # Read original content for diff
                        original_content = ""
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                original_content = f.read()
                        except:
                            pass
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(op.get('content', ''))
                        logger.info(f"✓ Modified: {op['file_path']}")
                        modified_files.append(op['file_path'])
                        
                        # Hook into report generator
                        if self.report_generator:
                            # Get trimming info from stored parsing results
                            parsing_info = self.parsing_results.get(op['file_path'], {})
                            was_trimmed = parsing_info.get('was_trimmed', False)
                            trimming_details = parsing_info.get('detailed_info', '')
                            
                            self.report_generator.add_file_operation(
                                "MODIFY", op['file_path'], op.get('reason', 'AI decision'),
                                content=op.get('content', ''),
                                trimmed=was_trimmed,
                                trimming_details=trimming_details,
                                diff=f"Original length: {len(original_content)}, New length: {len(op.get('content', ''))}"
                            )
                    else:
                        warning_msg = "⚠️ MODIFY operation attempted on non-existent file"
                        logger.warning(f"File to modify does not exist: {op['file_path']}")
                        
                        # Hook into report generator to record the failed operation
                        if self.report_generator:
                            reason = f"{op.get('reason', 'AI decision')} ({warning_msg})"
                            self.report_generator.add_file_operation(
                                "MODIFY", op['file_path'], reason,
                                content="[Operation failed - file not found]"
                            )
                
                elif op['operation'] == 'DELETE':
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"✓ Deleted: {op['file_path']}")
                        modified_files.append(op['file_path'])
                        
                        # Hook into report generator
                        if self.report_generator:
                            self.report_generator.add_file_operation(
                                "DELETE", op['file_path'], op.get('reason', 'AI decision')
                            )
                    else:
                        warning_msg = "⚠️ DELETE operation attempted on non-existent file"
                        logger.warning(f"File to delete does not exist: {op['file_path']}")
                        
                        # Hook into report generator to record the failed operation
                        if self.report_generator:
                            reason = f"{op.get('reason', 'AI decision')} ({warning_msg})"
                            self.report_generator.add_file_operation(
                                "DELETE", op['file_path'], reason,
                                content="[Operation failed - file not found]"
                            )
                
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
    
    def _store_parsing_result(self, file_path: str, operation: str, parse_result):
        """Store parsing result for report generation"""
        self.parsing_results[file_path] = {
            'operation': operation,
            'was_trimmed': parse_result.was_trimmed,
            'trimming_details': parse_result.trimming_details,
            'original_length': parse_result.original_length,
            'final_length': parse_result.final_length,
            'emoji_indicator': ai_output_parser.get_trimming_emoji_indicator(parse_result),
            'detailed_info': ai_output_parser.get_detailed_trimming_info(parse_result)
        }
        
        logger.info(f"📝 File {file_path}: {parse_result.original_length} → {parse_result.final_length} chars "
                   f"({ai_output_parser.get_trimming_emoji_indicator(parse_result)} trimmed: {parse_result.was_trimmed})")
    
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
        
        # Step 3: Update TODO.md with next steps
        todo_updated = self._update_todo_file(repo_path, project_info, file_operations)
        if todo_updated:
            modified_files.append("TODO.md")
        
        # Step 4: Commit and push
        success = self.commit_and_push_changes(repo_path, modified_files, project_info)
        
        # Generate summary
        result = {
            "file_operations": file_operations,
            "modified_files": modified_files,
            "todo_updated": todo_updated,
            "commit_success": success,
            "decision_summary": self.decision_formatter.get_decision_summary(),
            "total_decisions": len(self.decision_formatter.decision_history)
        }
        
        logger.info(f"File modification workflow complete. Modified {len(modified_files)} files.")
        return result