"""
GitLlama - Git Operations Module with AI Integration

AI-powered git automation: clone, branch, change, commit, push.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class GitOperationError(Exception):
    """Custom exception for git operation errors."""
    pass


class GitAutomator:
    """AI-powered git automation class."""
    
    def __init__(self, working_dir: Optional[str] = None, ai_coordinator=None):
        """Initialize the GitAutomator with optional AI coordinator.
        
        Args:
            working_dir: Optional working directory path
            ai_coordinator: Optional AICoordinator instance for AI-powered operations
        """
        self.working_dir = Path(working_dir) if working_dir else Path(tempfile.mkdtemp())
        self.repo_path: Optional[Path] = None
        self.original_cwd = os.getcwd()
        self.ai_coordinator = ai_coordinator
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup temporary directories
        if self.repo_path and self.repo_path.exists():
            os.chdir(self.original_cwd)
            if str(self.working_dir).startswith(tempfile.gettempdir()):
                shutil.rmtree(self.working_dir, ignore_errors=True)
    
    def _run_git_command(self, command: list, cwd: Optional[Path] = None, 
                        capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Execute a git command and return the result.
        
        Args:
            command: Git command as list of strings
            cwd: Working directory (defaults to repo_path)
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero return code
            
        Returns:
            CompletedProcess object with returncode, stdout, stderr
        """
        work_dir = cwd or self.repo_path or self.working_dir
        
        try:
            logger.info(f"🔧 Git operation: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=capture_output,
                text=True,
                check=check
            )
            
            # For backward compatibility, if check=True and capture_output=True,
            # return the result object but also allow accessing stdout as before
            if check and capture_output:
                # Add a string representation for backward compatibility
                result.stdout_stripped = result.stdout.strip() if result.stdout else ""
                
            return result
            
        except subprocess.CalledProcessError as e:
            # Get both stderr and stdout for better error messages
            stderr_msg = e.stderr.strip() if e.stderr else "No error details available"
            stdout_msg = e.stdout.strip() if e.stdout else ""
            
            # Combine error messages
            error_details = stderr_msg
            if stdout_msg and stdout_msg != stderr_msg:
                error_details = f"{stderr_msg}\nOutput: {stdout_msg}"
            
            error_msg = f"Git command failed: {' '.join(command)}\nError: {error_details}"
            logger.error(error_msg)
            raise GitOperationError(error_msg) from e
    
    def clone_repository(self, git_url: str) -> Path:
        """Clone a git repository."""
        logger.info(f"🔧 Git: Cloning repository: {git_url}")
        
        # Extract repository name from URL
        repo_name = git_url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        self.repo_path = self.working_dir / repo_name
        
        self._run_git_command(['git', 'clone', git_url, str(self.repo_path)], cwd=self.working_dir)
        logger.info(f"Successfully cloned to {self.repo_path}")
        return self.repo_path
    
    def checkout_branch(self, branch_name: str) -> str:
        """Checkout a branch, creating it if it doesn't exist."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        # First check if the branch already exists (locally or remotely)
        try:
            # Check if branch exists locally
            result = self._run_git_command(['git', 'rev-parse', '--verify', branch_name], 
                                          capture_output=True, check=False)
            
            if result.returncode == 0:
                # Branch exists locally, just checkout (no -b)
                logger.info(f"🔧 Git: Checking out existing branch: {branch_name}")
                self._run_git_command(['git', 'checkout', branch_name])
                logger.info(f"Successfully checked out existing branch: {branch_name}")
                return branch_name
            
            # Check if branch exists as remote
            remote_branch = f"origin/{branch_name}"
            result = self._run_git_command(['git', 'rev-parse', '--verify', remote_branch],
                                          capture_output=True, check=False)
            
            if result.returncode == 0:
                # Remote branch exists, create tracking branch
                logger.info(f"🔧 Git: Creating tracking branch from remote: {branch_name}")
                self._run_git_command(['git', 'checkout', '-b', branch_name, remote_branch])
                logger.info(f"Successfully created and checked out tracking branch: {branch_name}")
                return branch_name
            
            # Branch doesn't exist anywhere, create new
            logger.info(f"🔧 Git: Creating new branch: {branch_name}")
            self._run_git_command(['git', 'checkout', '-b', branch_name])
            logger.info(f"Successfully created and checked out new branch: {branch_name}")
            return branch_name
            
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Failed to checkout branch {branch_name}: {e}")
    
    def make_changes(self) -> list:
        """
        Make changes to the repository using AI decisions.
        Falls back to simple change if no AI coordinator.
        """
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info("Making changes to repository")
        
        if self.ai_coordinator:
            # AI-powered changes
            logger.info("Using AI to determine changes")
            
            # Step 1: Explore the repository
            project_info = self.ai_coordinator.explore_repository(self.repo_path)
            logger.info(f"AI understanding: {project_info}")
            
            # Step 2: Decide on file operations
            operations = self.ai_coordinator.decide_file_operations(self.repo_path, project_info)
            
            # Step 3: Execute the operations
            modified_files = self.ai_coordinator.execute_file_operations(self.repo_path, operations)
            
            return modified_files
        else:
            # Simple default change - create a file
            filename = "gitllama_was_here.txt"
            content = "This file was created by GitLlama automation tool."
            
            file_path = self.repo_path / filename
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Created file: {filename}")
            return [filename]
    
    def commit_changes(self) -> str:
        """Commit changes to the repository with AI-generated commit message."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info("Committing changes")
        
        # Check if there are any changes to commit
        status_result = self._run_git_command(['git', 'status', '--porcelain'])
        if not status_result.stdout.strip():
            logger.warning("No changes to commit")
            # Return a dummy commit hash or raise an error
            return "no-changes"
        
        # Add all changes
        logger.info("🔧 Git: Adding all changes to staging")
        self._run_git_command(['git', 'add', '.'])
        
        # Check if there are staged changes
        diff_result = self._run_git_command(['git', 'diff', '--cached', '--stat'])
        if not diff_result.stdout.strip():
            logger.warning("No staged changes to commit after git add")
            return "no-changes"
        
        # Generate AI commit message (always)
        if self.ai_coordinator and hasattr(self.ai_coordinator, 'context_window'):
            # Get AI-generated commit message based on operations
            operations = None
            for ctx in reversed(self.ai_coordinator.context_window):
                if ctx.get('type') == 'file_operation':
                    operations = [ctx.get('operation')]
                    break
            
            if operations:
                message = self.ai_coordinator.generate_commit_message(operations)
            else:
                message = "feat: automated improvements by GitLlama AI"
        else:
            message = "feat: automated improvements by GitLlama AI"
        
        # Commit changes
        self._run_git_command(['git', 'commit', '-m', message])
        
        # Get commit hash
        result = self._run_git_command(['git', 'rev-parse', 'HEAD'])
        commit_hash = result.stdout.strip()
        logger.info(f"🔧 Git: Successfully committed: {commit_hash[:8]}")
        
        return commit_hash
    
    def push_changes(self, branch: Optional[str] = None) -> str:
        """Push changes to the remote repository."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info("🔧 Git: Pushing changes to remote")
        
        # Get current branch if not specified
        if not branch:
            result = self._run_git_command(['git', 'branch', '--show-current'])
            branch = result.stdout.strip()
        
        # Ensure branch is not None
        if not branch:
            branch = "main"
        
        # Push changes
        result = self._run_git_command(['git', 'push', 'origin', branch])
        logger.info("🔧 Git: Successfully pushed changes")
        
        return branch
    
    def run_full_workflow(self, git_url: str, branch_name: Optional[str] = None) -> dict:
        """Run the complete AI-powered git automation workflow."""
        logger.info("Starting AI-powered GitLlama workflow")
        
        if not self.ai_coordinator:
            logger.error("GitLlama requires an AI coordinator to function")
            return {
                "success": False,
                "error": "No AI coordinator available. GitLlama requires Ollama to be running."
            }
        
        try:
            # Step 1: Clone repository
            repo_path = self.clone_repository(git_url)
            
            # Step 2: AI Repository Analysis
            logger.info("🔍 Phase 1: AI Repository Analysis")
            project_info = self.ai_coordinator.explore_repository(repo_path, analyze_all_branches=True)
            logger.info("AI Project Analysis Complete")
            
            # Step 3: AI Branch Selection
            logger.info("🔀 Phase 2: AI Branch Selection")
            if not branch_name:
                branch_name = self.ai_coordinator.decide_branch_name(self.repo_path, project_info)
                logger.info(f"AI selected branch name: {branch_name}")
            else:
                logger.info(f"Using provided branch name: {branch_name}")
            
            # Ensure branch_name is not None
            if not branch_name:
                branch_name = "gitllama-automation"
            
            self.checkout_branch(branch_name)
            
            # Step 4: AI File Modification Workflow
            logger.info("📝 Phase 3: AI File Modification Workflow")
            workflow_result = self.ai_coordinator.run_file_modification_workflow(repo_path, project_info)
            
            # Extract results
            modified_files = workflow_result.get("modified_files", [])
            commit_success = workflow_result.get("commit_success", False)
            
            if not commit_success or not modified_files:
                # Fallback to traditional method if AI workflow didn't work
                logger.info("Falling back to traditional file operations")
                modified_files = self.make_changes()
                commit_hash = self.commit_changes()  # AI generates message
                
                if commit_hash != "no-changes":
                    self.push_changes(branch=branch_name)
                    logger.info(f"Successfully pushed to branch: {branch_name}")
                else:
                    logger.warning("No changes were committed, skipping push")
                    commit_hash = "no-changes"
            else:
                # Enhanced workflow already handled commit and push
                commit_hash = "ai-workflow"
            
            logger.info("AI workflow completed successfully")
            
            result = {
                "success": True,
                "repo_path": str(repo_path),
                "branch": branch_name,
                "modified_files": modified_files,
                "commit_hash": commit_hash,
                "message": "AI workflow completed successfully",
                "ai_analysis": project_info,
                "total_ai_decisions": workflow_result.get("total_decisions", 0)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
