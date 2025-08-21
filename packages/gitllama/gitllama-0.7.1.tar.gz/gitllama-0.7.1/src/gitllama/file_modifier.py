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
from .ai_query import AIQuery  # NEW: Simple query interface
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
        self.ai = AIQuery(client, model)  # NEW: Simple query interface
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
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="file_generation"
        )
        response = result.raw
        
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
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="todo_update"
        )
        response = result.raw
        
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
            try:
                result = subprocess.run(
                    ['git', 'push'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                # Check if this is an upstream branch issue
                if "has no upstream branch" in str(e.stderr) or "no upstream branch" in str(e.stderr):
                    logger.info("Setting upstream branch...")
                    # Get current branch name
                    branch_result = subprocess.run(
                        ['git', 'branch', '--show-current'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    current_branch = branch_result.stdout.strip() or "main"
                    
                    # Push with upstream
                    result = subprocess.run(
                        ['git', 'push', '--set-upstream', 'origin', current_branch],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    logger.info("Successfully pushed with upstream set")
                else:
                    raise
            
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
    
    def _should_continue_modifying(self, repo_path: Path, project_info: Dict, modified_files: List[str]) -> bool:
        """Ask AI if we should continue modifying files."""
        logger.info("🤔 Asking AI if more modifications are needed")
        
        context = f"Project type: {project_info.get('project_type', 'unknown')}\n"
        context += f"Files already modified: {modified_files if modified_files else 'None'}"
        
        result = self.ai.choice(
            question="Should we continue modifying more files?",
            options=["YES - Continue modifying", "NO - Changes are sufficient"],
            context=context
        )
        
        decision = "YES" in result.value
        
        if self.report_generator:
            self.report_generator.add_ai_decision(
                "Continue Modifying Files",
                result.value,
                f"Modified {len(modified_files)} files so far"
            )
        
        return decision
    
    def _select_single_file_to_modify(self, repo_path: Path, project_info: Dict, already_modified: List[str]) -> Optional[Dict[str, Any]]:
        """AI selects a single file to work on."""
        logger.info("📋 AI selecting file to modify")
        
        context = self._build_file_selection_context(project_info, list(repo_path.rglob("*")))
        modified_summary = "\n".join([f"- {f}" for f in already_modified]) if already_modified else "None"
        
        prompt = f"""Select ONE file to create or modify that will have the most impact on the project.

PROJECT CONTEXT:
{context}

FILES ALREADY MODIFIED (don't select these again):
{modified_summary}

Choose an operation:
- CREATE a new file (documentation, config, utility, test)
- MODIFY an existing file (improve code, fix issues, add features)

Respond in JSON format:
{{
    "operation": "CREATE" or "MODIFY",
    "file_path": "path/to/file.ext",
    "goal": "Clear description of what this file should accomplish",
    "reason": "Why this file is important for the project"
}}"""
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="file_selection"
        )
        response = result.raw
        
        try:
            file_decision = json.loads(response)
            logger.info(f"AI selected: {file_decision['operation']} {file_decision['file_path']}")
            
            if self.report_generator:
                self.report_generator.add_ai_decision(
                    f"Select File #{len(already_modified) + 1}",
                    f"{file_decision['operation']} {file_decision['file_path']}",
                    file_decision.get('reason', '')
                )
            
            return file_decision
        except json.JSONDecodeError:
            logger.error(f"Failed to parse file selection: {response}")
            return None
    
    def _generate_file_content_with_goal_reminder(self, repo_path: Path, project_info: Dict, 
                                                 target_file: Dict, retry_num: int) -> str:
        """Generate file content with goal reminder for retries."""
        file_path = target_file['file_path']
        goal = target_file.get('goal', 'Improve the project')
        
        context = f"Project Type: {project_info.get('project_type', 'unknown')}\n"
        context += f"File: {file_path}\n"
        context += f"Goal: {goal}"
        
        if retry_num > 0:
            context += f"\nThis is retry attempt {retry_num + 1}/3. Previous attempt did not meet requirements."
        
        # Get language for the file
        language = self._get_language_from_path(file_path)
        
        prompt = f"Generate complete content for this file. Wrap in ```{language} code blocks."
        
        result = self.ai.open(prompt=prompt, context=context)
        
        # Extract code from response
        from .response_parser import ResponseParser
        parser = ResponseParser()
        content = parser.extract_code(result.content)
        
        return content
    
    def _write_single_file(self, repo_path: Path, target_file: Dict, content: str) -> bool:
        """Write a single file to disk."""
        try:
            file_path = repo_path / target_file['file_path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✍️ Wrote {len(content)} chars to {target_file['file_path']}")
            
            # Add to report
            if self.report_generator:
                parsing_info = self.parsing_results.get(target_file['file_path'], {})
                self.report_generator.add_file_operation(
                    target_file['operation'],
                    target_file['file_path'],
                    target_file.get('reason', 'AI selected file'),
                    content=content,
                    trimmed=parsing_info.get('was_trimmed', False),
                    trimming_details=parsing_info.get('detailed_info', '')
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to write file {target_file['file_path']}: {e}")
            return False
    
    def _validate_file_change(self, repo_path: Path, target_file: Dict, content: str, project_info: Dict) -> Dict[str, Any]:
        """AI validates if the file change was successful."""
        logger.info(f"🔍 Validating {target_file['file_path']}")
        
        goal = target_file.get('goal', 'Improve the project')
        
        result = self.ai.choice(
            question="Does this file change meet its goal?",
            options=[
                "Perfect - No changes needed",
                "Good - Minor improvements possible", 
                "Needs work - Retry required",
                "Failed - Major issues"
            ],
            context=f"File: {target_file['file_path']}\nGoal: {goal}\nContent length: {len(content)} chars"
        )
        
        success = "Perfect" in result.value or "Good" in result.value
        
        if self.report_generator:
            self.report_generator.add_ai_decision(
                f"Validate {target_file['file_path']}",
                "PASS" if success else "RETRY",
                result.value
            )
        
        return {
            "success": success,
            "reason": result.value
        }
    
    def _perform_initial_validation(self, target_file: Dict, actual_content: str, goal: str) -> Dict[str, Any]:
        """Perform the initial validation check."""
        prompt = f"""Validate if this file modification achieved its goal.

FILE: {target_file['file_path']}
OPERATION: {target_file['operation']}
STATED GOAL: {goal}

FILE CONTENT (first 2000 chars):
{actual_content[:2000]}

Questions to consider:
1. Does the file content achieve the stated goal?
2. Is the code/content complete and functional?
3. Are there any obvious errors or missing pieces?
4. Does it follow good practices for this type of file?

Respond in JSON format:
{{
    "success": true or false,
    "reason": "Brief explanation of your validation decision"
}}"""
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="initial_validation"
        )
        response = result.raw
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse initial validation response: {response}")
            return {"success": False, "reason": "Could not parse validation response"}
    
    def _perform_warning_aware_validation(self, target_file: Dict, actual_content: str, goal: str, 
                                        initial_validation: Dict) -> Dict[str, Any]:
        """Perform a second validation with awareness of potential warnings."""
        initial_reason = initial_validation.get('reason', '')
        
        prompt = f"""SECOND VALIDATION: You are double-checking this file because the initial validation raised concerns.

FILE: {target_file['file_path']}
OPERATION: {target_file['operation']}
STATED GOAL: {goal}

INITIAL VALIDATION CONCERN: {initial_reason}

FILE CONTENT (first 2000 chars):
{actual_content[:2000]}

Please carefully re-examine this file with the following in mind:
1. Is the initial concern actually a real problem that prevents the file from working?
2. Does the file achieve its stated goal despite the concern?
3. Are there false positives or overly strict interpretations?
4. Is this file good enough to proceed, or does it genuinely need fixes?

Be more lenient if the file accomplishes its core purpose, even if it's not perfect.
Only fail if there are genuine functional problems or the goal is clearly not met.

Respond in JSON format:
{{
    "success": true or false,
    "reason": "Your final decision after double-checking",
    "warning_eliminated": true or false,
    "double_check_notes": "What you reconsidered during this second look"
}}"""
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="warning_validation"
        )
        response = result.raw
        
        try:
            double_check_result = json.loads(response)
            
            # Log the double-check decision
            if self.report_generator:
                status = "PASS (Double-Check)" if double_check_result['success'] else "RETRY (Confirmed)"
                notes = double_check_result.get('double_check_notes', '')
                self.report_generator.add_ai_decision(
                    f"Double-Check {target_file['file_path']}",
                    status,
                    f"{double_check_result.get('reason', '')} | Notes: {notes}"
                )
            
            # Return result with double-check metadata
            return {
                "success": double_check_result['success'],
                "reason": double_check_result.get('reason', ''),
                "double_checked": True,
                "warning_eliminated": double_check_result.get('warning_eliminated', False),
                "initial_concern": initial_reason,
                "double_check_notes": double_check_result.get('double_check_notes', '')
            }
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse double-check validation response: {response}")
            # Fall back to initial validation but mark as double-checked
            return {
                "success": initial_validation['success'],
                "reason": initial_validation.get('reason', ''),
                "double_checked": True,
                "warning_eliminated": False,
                "error": "Could not parse double-check response"
            }
    
    def _get_language_from_path(self, file_path: str) -> str:
        """Get language identifier from file path for markdown code blocks."""
        ext_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.md': 'markdown',
            '.sh': 'bash',
            '.sql': 'sql',
        }
        
        for ext, lang in ext_mapping.items():
            if file_path.endswith(ext):
                return lang
        
        # Special cases
        if 'Dockerfile' in file_path:
            return 'dockerfile'
        if 'Makefile' in file_path:
            return 'makefile'
        
        return 'text'
    
    def run_full_modification_workflow(self, repo_path: Path, project_info: Dict) -> Dict[str, Any]:
        """Run the iterative file modification workflow with validation.
        
        Args:
            repo_path: Repository path
            project_info: Project analysis information
            
        Returns:
            Dictionary with workflow results
        """
        logger.info("🔄 Starting iterative file modification workflow")
        
        MAX_FILES = 10
        MAX_RETRIES_PER_FILE = 3
        
        all_modified_files = []
        all_file_operations = []
        iteration_history = []
        
        # Main loop: Continue until AI says we're done (up to MAX_FILES)
        for file_num in range(MAX_FILES):
            logger.info(f"\n📁 File iteration {file_num + 1}/{MAX_FILES}")
            
            # Ask AI if we should continue modifying files
            should_continue = self._should_continue_modifying(repo_path, project_info, all_modified_files)
            
            if not should_continue:
                logger.info("✅ AI decided modifications are complete")
                break
            
            # AI selects which file to work on
            target_file = self._select_single_file_to_modify(repo_path, project_info, all_modified_files)
            
            if not target_file:
                logger.info("⚠️ AI couldn't select a file to modify")
                break
            
            # Retry loop for this specific file
            file_success = False
            for retry_num in range(MAX_RETRIES_PER_FILE):
                logger.info(f"  🔧 Attempt {retry_num + 1}/{MAX_RETRIES_PER_FILE} for {target_file['file_path']}")
                
                # Generate/modify the file content
                file_content = self._generate_file_content_with_goal_reminder(
                    repo_path, project_info, target_file, retry_num
                )
                
                # Write the file
                written_success = self._write_single_file(repo_path, target_file, file_content)
                
                if not written_success:
                    logger.warning(f"  ❌ Failed to write {target_file['file_path']}")
                    continue
                
                # AI validates the change
                validation_result = self._validate_file_change(
                    repo_path, target_file, file_content, project_info
                )
                
                # Store iteration info for reporting
                iteration_info = {
                    "file_num": file_num + 1,
                    "file_path": target_file['file_path'],
                    "operation": target_file['operation'],
                    "retry_num": retry_num + 1,
                    "validation_success": validation_result['success'],
                    "validation_reason": validation_result.get('reason', '')
                }
                iteration_history.append(iteration_info)
                
                if validation_result['success']:
                    logger.info(f"  ✅ Validation passed: {validation_result.get('reason', 'File meets requirements')}")
                    file_success = True
                    all_modified_files.append(target_file['file_path'])
                    all_file_operations.append(target_file)
                    break
                else:
                    logger.info(f"  ⚠️ Validation failed: {validation_result.get('reason', 'Need to retry')}")
            
            if not file_success:
                logger.warning(f"❌ Failed to successfully modify {target_file['file_path']} after {MAX_RETRIES_PER_FILE} attempts")
        
        # Update TODO.md with next steps
        todo_updated = self._update_todo_file(repo_path, project_info, all_file_operations)
        if todo_updated:
            all_modified_files.append("TODO.md")
        
        # Update report with iteration history
        if self.report_generator:
            self.report_generator.set_iteration_history(
                iteration_history, len(iteration_history), file_num + 1
            )
        
        # Commit and push
        success = self.commit_and_push_changes(repo_path, all_modified_files, project_info)
        
        # Generate summary with iteration history
        result = {
            "file_operations": all_file_operations,
            "modified_files": all_modified_files,
            "todo_updated": todo_updated,
            "commit_success": success,
            "iteration_history": iteration_history,
            "total_iterations": len(iteration_history),
            "files_attempted": file_num + 1,
            "decision_summary": self.decision_formatter.get_decision_summary(),
            "total_decisions": len(self.decision_formatter.decision_history)
        }
        
        logger.info(f"🎯 Iterative workflow complete. Modified {len(all_modified_files)} files in {len(iteration_history)} iterations.")
        return result