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
    
    def _run_git_command(self, command: list, cwd: Optional[Path] = None) -> str:
        """Execute a git command and return the output."""
        work_dir = cwd or self.repo_path or self.working_dir
        
        try:
            logger.info(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {' '.join(command)}\nError: {e.stderr}"
            logger.error(error_msg)
            raise GitOperationError(error_msg) from e
    
    def clone_repository(self, git_url: str) -> Path:
        """Clone a git repository."""
        logger.info(f"Cloning repository: {git_url}")
        
        # Extract repository name from URL
        repo_name = git_url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        self.repo_path = self.working_dir / repo_name
        
        self._run_git_command(['git', 'clone', git_url, str(self.repo_path)], cwd=self.working_dir)
        logger.info(f"Successfully cloned to {self.repo_path}")
        return self.repo_path
    
    def checkout_branch(self, branch_name: str) -> str:
        """Create and checkout a new branch."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info(f"Creating and checking out branch: {branch_name}")
        self._run_git_command(['git', 'checkout', '-b', branch_name])
        logger.info(f"Successfully checked out branch: {branch_name}")
        return branch_name
    
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
    
    def commit_changes(self, message: Optional[str] = None) -> str:
        """Commit changes to the repository with AI-generated or custom message."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info("Committing changes")
        
        # Add all changes
        self._run_git_command(['git', 'add', '.'])
        
        # Create commit message
        if not message:
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
                    message = "Automated changes by GitLlama"
            else:
                message = "Automated changes by GitLlama"
        
        # Commit changes
        self._run_git_command(['git', 'commit', '-m', message])
        
        # Get commit hash
        commit_hash = self._run_git_command(['git', 'rev-parse', 'HEAD'])
        logger.info(f"Successfully committed: {commit_hash[:8]}")
        
        return commit_hash
    
    def push_changes(self, branch: Optional[str] = None) -> str:
        """Push changes to the remote repository."""
        if not self.repo_path:
            raise GitOperationError("No repository cloned. Call clone_repository first.")
        
        logger.info("Pushing changes")
        
        # Get current branch if not specified
        if not branch:
            branch = self._run_git_command(['git', 'branch', '--show-current'])
        
        # Push changes
        push_output = self._run_git_command(['git', 'push', 'origin', branch])
        logger.info("Successfully pushed changes")
        
        return push_output
    
    def run_full_workflow(self, git_url: str, branch_name: Optional[str] = None, 
                         commit_message: Optional[str] = None) -> dict:
        """Run the complete git automation workflow with AI integration."""
        logger.info("Starting AI-powered GitLlama workflow")
        
        try:
            # Step 1: Clone repository
            repo_path = self.clone_repository(git_url)
            
            # AI Step: Explore and understand the project
            project_info = {}
            if self.ai_coordinator:
                project_info = self.ai_coordinator.explore_repository(repo_path)
                logger.info(f"AI Project Analysis: {project_info}")
            
            # Step 2: Checkout branch (AI decides if coordinator available)
            if not branch_name and self.ai_coordinator:
                branch_name = self.ai_coordinator.decide_branch_name(project_info)
                logger.info(f"AI selected branch name: {branch_name}")
            elif not branch_name:
                branch_name = "gitllama-automation"
            
            self.checkout_branch(branch_name)
            
            # Step 3: Make changes (AI-powered if coordinator available)
            modified_files = self.make_changes()
            
            # Step 4: Commit changes (AI generates message if coordinator available)
            commit_hash = self.commit_changes(commit_message)
            
            # Step 5: Push changes
            push_output = self.push_changes(branch=branch_name)
            
            logger.info("Workflow completed successfully")
            
            result = {
                "success": True,
                "repo_path": str(repo_path),
                "branch": branch_name,
                "modified_files": modified_files,
                "commit_hash": commit_hash[:8],
                "message": "Workflow completed successfully"
            }
            
            if project_info:
                result["ai_analysis"] = project_info
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }