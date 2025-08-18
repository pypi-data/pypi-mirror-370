"""
AI Coordinator for GitLlama
Manages AI decision-making at each step of the git workflow
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AICoordinator:
    """Coordinates AI decisions throughout the git workflow"""
    
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.client = OllamaClient(base_url)
        self.context_window = []
        
        # Get model's context size
        self.max_context_size = self.client.get_model_context_size(model)
        # Reserve space for prompt and response
        self.usable_context_size = int(self.max_context_size * 0.7)
        
        logger.info(f"Initialized AI with model: {model}")
        logger.info(f"Context window size: {self.max_context_size} tokens")
        logger.info(f"Usable context size: {self.usable_context_size} tokens")
    
    def gather_repository_data(self, repo_path: Path) -> Tuple[List[Dict], int]:
        """Gather all repository data for analysis.
        
        Returns:
            Tuple of (list of file data dicts, total token count)
        """
        logger.info(f"Gathering repository data from {repo_path}")
        
        all_files = []
        total_tokens = 0
        
        # Define file extensions to analyze
        text_extensions = {'.py', '.js', '.tsx', '.jsx', '.md', '.txt', '.json', 
                          '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                          '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd',
                          '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go',
                          '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
                          '.html', '.css', '.scss', '.less', '.xml'}
        
        for file_path in repo_path.rglob("*"):
            # Skip hidden directories and files
            if any(part.startswith('.') for part in file_path.parts):
                continue
            
            if file_path.is_file() and file_path.suffix in text_extensions:
                try:
                    # Check file size first
                    file_size = file_path.stat().st_size
                    if file_size > 100000:  # Skip files larger than 100KB
                        logger.debug(f"Skipping large file: {file_path}")
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    relative_path = file_path.relative_to(repo_path)
                    file_tokens = self.client.count_tokens(content)
                    
                    all_files.append({
                        'path': str(relative_path),
                        'content': content,
                        'tokens': file_tokens
                    })
                    total_tokens += file_tokens
                    
                except Exception as e:
                    logger.debug(f"Could not read {file_path}: {e}")
        
        logger.info(f"Found {len(all_files)} files with {total_tokens} total tokens")
        return all_files, total_tokens
    
    def create_file_chunks(self, files: List[Dict], chunk_size: int) -> List[List[Dict]]:
        """Organize files into chunks that fit within context window.
        
        Args:
            files: List of file data dictionaries
            chunk_size: Maximum tokens per chunk
            
        Returns:
            List of file chunks
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        # Sort files by path for better organization
        sorted_files = sorted(files, key=lambda x: x['path'])
        
        for file_data in sorted_files:
            file_tokens = file_data['tokens']
            
            # If single file is too large, split it
            if file_tokens > chunk_size:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0
                
                # Split the large file
                content_chunks = self.client.split_into_chunks(
                    file_data['content'], 
                    chunk_size
                )
                for i, content_chunk in enumerate(content_chunks):
                    chunks.append([{
                        'path': f"{file_data['path']} (part {i+1}/{len(content_chunks)})",
                        'content': content_chunk,
                        'tokens': self.client.count_tokens(content_chunk)
                    }])
            
            # If adding this file would exceed chunk size, start new chunk
            elif current_tokens + file_tokens > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [file_data]
                current_tokens = file_tokens
            
            # Add file to current chunk
            else:
                current_chunk.append(file_data)
                current_tokens += file_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def analyze_chunk(self, chunk: List[Dict], chunk_index: int, total_chunks: int) -> Dict:
        """Analyze a single chunk of files.
        
        Args:
            chunk: List of file data in this chunk
            chunk_index: Index of this chunk (1-based)
            total_chunks: Total number of chunks
            
        Returns:
            Analysis result dictionary
        """
        logger.info(f"Analyzing chunk {chunk_index}/{total_chunks} with {len(chunk)} files")
        
        # Build context from chunk
        context_parts = []
        for file_data in chunk:
            context_parts.append(f"=== File: {file_data['path']} ===")
            # Limit content preview to save tokens for analysis
            content_preview = file_data['content'][:2000]
            if len(file_data['content']) > 2000:
                content_preview += "\n... [content truncated]"
            context_parts.append(content_preview)
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # Calculate actual tokens for logging
        context_tokens = self.client.count_tokens(context)
        logger.info(f"  Chunk {chunk_index} context: {context_tokens} tokens")
        
        prompt = f"""Analyze this portion of a code repository (chunk {chunk_index} of {total_chunks}):

{context}

Provide a comprehensive analysis including:
1. Main purpose/functionality of these files
2. Technologies and frameworks used
3. Code quality observations
4. Key patterns or architectural decisions
5. Notable features or issues

Response in JSON format:
{{
    "chunk_index": {chunk_index},
    "file_count": {len(chunk)},
    "main_purpose": "",
    "technologies": [],
    "patterns": [],
    "quality_notes": "",
    "key_features": []
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk_text in self.client.chat_stream(self.model, messages):
            response += chunk_text
        
        try:
            analysis = json.loads(response)
            logger.info(f"  Chunk {chunk_index} analysis complete")
            return analysis
        except json.JSONDecodeError:
            logger.warning(f"  Chunk {chunk_index} JSON parse failed, using raw response")
            return {
                "chunk_index": chunk_index,
                "file_count": len(chunk),
                "raw_analysis": response[:500]
            }
    
    def merge_summaries(self, summaries: List[Dict], level: int = 1) -> Dict:
        """Merge multiple summaries into a higher-level summary.
        
        Args:
            summaries: List of summary dictionaries
            level: Current merge level (for logging)
            
        Returns:
            Merged summary dictionary
        """
        logger.info(f"Merging {len(summaries)} summaries at level {level}")
        
        # If only one summary, return it
        if len(summaries) == 1:
            return summaries[0]
        
        # Build context from summaries
        context_parts = []
        for i, summary in enumerate(summaries, 1):
            context_parts.append(f"=== Summary {i} ===")
            context_parts.append(json.dumps(summary, indent=2))
            context_parts.append("")
        
        context = "\n".join(context_parts)
        context_tokens = self.client.count_tokens(context)
        
        # If context is too large, recursively merge in smaller groups
        if context_tokens > self.usable_context_size:
            logger.info(f"  Context too large ({context_tokens} tokens), splitting merge")
            mid = len(summaries) // 2
            left_summary = self.merge_summaries(summaries[:mid], level)
            right_summary = self.merge_summaries(summaries[mid:], level)
            return self.merge_summaries([left_summary, right_summary], level + 1)
        
        logger.info(f"  Merge context: {context_tokens} tokens")
        
        prompt = f"""Merge these {len(summaries)} analyses into a unified summary:

{context}

Create a comprehensive merged analysis that:
1. Identifies the overall project type and purpose
2. Lists all technologies used across the codebase
3. Describes the project architecture and structure
4. Highlights key features and patterns
5. Assesses overall code quality and state

Response in JSON format:
{{
    "merge_level": {level},
    "summaries_merged": {len(summaries)},
    "project_type": "",
    "overall_purpose": "",
    "all_technologies": [],
    "architecture": "",
    "key_patterns": [],
    "overall_quality": "",
    "state": ""
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        try:
            merged = json.loads(response)
            logger.info(f"  Level {level} merge complete")
            return merged
        except json.JSONDecodeError:
            logger.warning(f"  Level {level} merge JSON parse failed")
            return {
                "merge_level": level,
                "summaries_merged": len(summaries),
                "raw_analysis": response[:500]
            }
    
    def explore_repository(self, repo_path: Path) -> Dict[str, str]:
        """Explore the repository with hierarchical summarization."""
        logger.info(f"Starting hierarchical repository exploration at {repo_path}")
        logger.info("=" * 60)
        
        # Step 1: Gather all repository data
        all_files, total_tokens = self.gather_repository_data(repo_path)
        
        if not all_files:
            logger.warning("No analyzable files found in repository")
            return {
                "project_type": "empty",
                "technologies": [],
                "state": "No analyzable files found"
            }
        
        logger.info(f"Total repository size: {total_tokens} tokens across {len(all_files)} files")
        logger.info(f"Context window: {self.max_context_size} tokens (usable: {self.usable_context_size})")
        
        # Step 2: Create chunks that fit in context window
        # Reserve space for prompt (roughly 500 tokens)
        chunk_size = self.usable_context_size - 500
        chunks = self.create_file_chunks(all_files, chunk_size)
        
        logger.info(f"Created {len(chunks)} chunks for analysis")
        for i, chunk in enumerate(chunks, 1):
            chunk_tokens = sum(f['tokens'] for f in chunk)
            logger.info(f"  Chunk {i}: {len(chunk)} files, {chunk_tokens} tokens")
        
        logger.info("=" * 60)
        
        # Step 3: Analyze each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}...")
            summary = self.analyze_chunk(chunk, i, len(chunks))
            chunk_summaries.append(summary)
        
        logger.info("=" * 60)
        logger.info("All chunks analyzed, starting hierarchical merge")
        
        # Step 4: Hierarchically merge summaries
        final_summary = self.merge_summaries(chunk_summaries)
        
        logger.info("=" * 60)
        logger.info("Repository exploration complete!")
        
        # Store in context window for future reference
        self.context_window.append({
            "type": "exploration",
            "chunks_analyzed": len(chunks),
            "total_tokens": total_tokens,
            "total_files": len(all_files),
            "analysis": final_summary
        })
        
        # Convert to expected format
        result = {
            "project_type": final_summary.get("project_type", "unknown"),
            "technologies": final_summary.get("all_technologies", []),
            "state": final_summary.get("state", final_summary.get("overall_purpose", "analyzed")),
            "detailed_analysis": final_summary
        }
        
        return result
    
    # ... rest of the methods remain unchanged ...
    def decide_branch_name(self, project_info: Dict[str, str]) -> str:
        """AI decides on an appropriate branch name"""
        logger.info("AI deciding on branch name")
        
        prompt = f"""Based on this project analysis:
{json.dumps(project_info, indent=2)}

Suggest a meaningful branch name for making an improvement to this repository.
The branch name should be specific and descriptive.
Do NOT suggest 'main' or 'master'.

Respond with ONLY the branch name, no explanation."""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        branch_name = response.strip().replace(' ', '-').lower()
        
        # Ensure we don't use main/master
        if branch_name in ['main', 'master']:
            branch_name = 'feature-improvement'
        
        self.context_window.append({
            "type": "branch_decision",
            "branch": branch_name
        })
        
        return branch_name
    
    
    def decide_file_operations(self, repo_path: Path, project_info: Dict[str, str]) -> List[Dict[str, str]]:
        """AI decides what file operations to perform"""
        logger.info("AI deciding on file operations")
        
        # Get current context
        context_summary = f"""Project Analysis:
{json.dumps(project_info, indent=2)}

Previous decisions:
{json.dumps(self.context_window[-2:], indent=2) if len(self.context_window) > 1 else 'None'}"""
        
        prompt = f"""{context_summary}

Based on this project, suggest ONE file operation that would improve the repository.
Choose one of these operations:
1. CREATE a new file (like documentation, config, or utility)
2. MODIFY an existing file (improve code, fix issues, add features)
3. DELETE an unnecessary file

Respond in JSON format:
{{
    "operation": "CREATE|MODIFY|DELETE",
    "file_path": "path/to/file",
    "content": "file content here (for CREATE/MODIFY)",
    "reason": "brief explanation"
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        try:
            operation = json.loads(response)
            self.context_window.append({
                "type": "file_operation",
                "operation": operation
            })
            return [operation]
        except json.JSONDecodeError:
            # Fallback: create a simple improvements file
            fallback = {
                "operation": "CREATE",
                "file_path": "IMPROVEMENTS.md",
                "content": "# Improvements\n\nThis file tracks potential improvements for the project.\n\n- [ ] Add more documentation\n- [ ] Improve test coverage\n- [ ] Optimize performance\n",
                "reason": "Document improvement ideas"
            }
            self.context_window.append({
                "type": "file_operation",
                "operation": fallback
            })
            return [fallback]
    
    def generate_commit_message(self, operations: List[Dict[str, str]]) -> str:
        """AI generates a commit message based on the operations performed"""
        logger.info("AI generating commit message")
        
        prompt = f"""Generate a concise, professional git commit message for these operations:
{json.dumps(operations, indent=2)}

Follow conventional commit format (feat:, fix:, docs:, etc.)
Keep it under 72 characters.

Respond with ONLY the commit message, no explanation."""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        commit_message = response.strip()
        
        # Fallback if response is too long or empty
        if not commit_message or len(commit_message) > 72:
            if operations and operations[0].get('operation') == 'CREATE':
                commit_message = f"feat: add {Path(operations[0]['file_path']).name}"
            elif operations and operations[0].get('operation') == 'MODIFY':
                commit_message = f"fix: update {Path(operations[0]['file_path']).name}"
            else:
                commit_message = "chore: automated improvements by GitLlama"
        
        self.context_window.append({
            "type": "commit_message",
            "message": commit_message
        })
        
        return commit_message
    
    def execute_file_operations(self, repo_path: Path, operations: List[Dict[str, str]]) -> List[str]:
        """Execute the file operations decided by the AI"""
        modified_files = []
        
        for op in operations:
            file_path = repo_path / op['file_path']
            
            if op['operation'] == 'CREATE':
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(op.get('content', ''))
                logger.info(f"Created file: {op['file_path']}")
                modified_files.append(op['file_path'])
                
            elif op['operation'] == 'MODIFY':
                if file_path.exists():
                    with open(file_path, 'w') as f:
                        f.write(op.get('content', ''))
                    logger.info(f"Modified file: {op['file_path']}")
                    modified_files.append(op['file_path'])
                else:
                    logger.warning(f"File to modify does not exist: {op['file_path']}")
                    
            elif op['operation'] == 'DELETE':
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted file: {op['file_path']}")
                    modified_files.append(op['file_path'])
                else:
                    logger.warning(f"File to delete does not exist: {op['file_path']}")
        
        return modified_files