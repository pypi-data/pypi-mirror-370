"""
Simplified TODO-driven Project Analyzer for GitLlama
Focuses on relating all code to TODO.md contents
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
from .ollama_client import OllamaClient
from .ai_query import AIQuery

logger = logging.getLogger(__name__)


class TodoAnalyzer:
    """Analyzes repository in relation to TODO.md"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.ai = AIQuery(client, model)
        self.max_context_size = self.client.get_model_context_size(model)
        self.usable_context_size = int(self.max_context_size * 0.7)
        
    def analyze_with_todo(self, repo_path: Path) -> Dict:
        """Main entry point for TODO-driven analysis"""
        logger.info("Starting TODO-driven repository analysis")
        
        # Step 1: Find and read TODO.md
        todo_content = self._read_todo(repo_path)
        if not todo_content:
            logger.warning("No TODO.md found - using fallback analysis")
            todo_content = "General improvements and maintenance"
        
        # Step 2: Gather all files
        all_files = self._gather_files(repo_path)
        logger.info(f"Found {len(all_files)} files to analyze")
        
        # Step 3: Create chunks
        chunks = self._create_simple_chunks(all_files)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 4: Ask TODO relation question for each chunk
        chunk_responses = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Analyzing chunk {i}/{len(chunks)} against TODO")
            response = self._ask_todo_relation(todo_content, chunk, i, len(chunks))
            chunk_responses.append(response)
        
        # Step 5: Summarize all responses
        summary = self._summarize_responses(chunk_responses, todo_content)
        
        # Step 6: Get file tree structure
        file_tree = self._get_file_tree(repo_path)
        
        return {
            "todo_content": todo_content,
            "chunk_responses": chunk_responses,
            "summary": summary,
            "file_tree": file_tree,
            "total_files": len(all_files),
            "total_chunks": len(chunks)
        }
    
    def _read_todo(self, repo_path: Path) -> str:
        """Read TODO.md file"""
        todo_path = repo_path / "TODO.md"
        if todo_path.exists():
            with open(todo_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _gather_files(self, repo_path: Path) -> List[Dict]:
        """Gather all readable files"""
        files = []
        text_extensions = {'.py', '.js', '.tsx', '.jsx', '.md', '.txt', '.json', 
                          '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                          '.sh', '.bash', '.java', '.c', '.cpp', '.go', '.rs'}
        
        for file_path in repo_path.rglob("*"):
            # Skip hidden directories
            if any(part.startswith('.') for part in file_path.parts):
                continue
            
            if file_path.is_file() and file_path.suffix in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    files.append({
                        'path': str(file_path.relative_to(repo_path)),
                        'content': content,
                        'tokens': self.client.count_tokens(content)
                    })
                except Exception as e:
                    logger.debug(f"Could not read {file_path}: {e}")
        
        return files
    
    def _create_simple_chunks(self, files: List[Dict]) -> List[List[Dict]]:
        """Create simple chunks that fit in context window"""
        chunk_size = self.usable_context_size - 1000  # Reserve space for TODO and prompt
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for file_data in files:
            file_tokens = file_data['tokens']
            
            # If file is too large, truncate it
            if file_tokens > chunk_size:
                truncated = file_data.copy()
                truncated['content'] = truncated['content'][:chunk_size * 4]  # Rough char estimate
                truncated['tokens'] = self.client.count_tokens(truncated['content'])
                chunks.append([truncated])
                continue
            
            # If adding would exceed, start new chunk
            if current_tokens + file_tokens > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [file_data]
                current_tokens = file_tokens
            else:
                current_chunk.append(file_data)
                current_tokens += file_tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _ask_todo_relation(self, todo_content: str, chunk: List[Dict], 
                          chunk_num: int, total_chunks: int) -> str:
        """Ask how chunk relates to TODO"""
        # Build context from chunk files
        context_parts = []
        for file_data in chunk:
            context_parts.append(f"=== File: {file_data['path']} ===")
            context_parts.append(file_data['content'][:2000])  # Limit per file
            if len(file_data['content']) > 2000:
                context_parts.append("... [truncated]")
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        prompt = f"""TODO.md contents:
{todo_content[:1500]}

Now analyzing chunk {chunk_num} of {total_chunks}.

How does the TODO contents relate to this code context? 
Specifically:
1. Are any of these files regions of interest for the TODO items?
2. Which files would likely need to be worked on?
3. What helpful information would you give someone implementing the TODO based on this code?

Be specific about file names and what needs to be done."""
        
        result = self.ai.open(
            prompt=prompt,
            context=context,
            context_name=f"todo_relation_chunk_{chunk_num}"
        )
        
        return result.content
    
    def _summarize_responses(self, responses: List[str], todo_content: str) -> str:
        """Summarize all chunk responses"""
        combined = "\n\n=== CHUNK RESPONSE ===\n".join(responses)
        
        prompt = f"""Summarize the following analysis of how different code chunks relate to the TODO:

{combined[:8000]}

Provide a concise summary that identifies:
1. The most important files to work on
2. Key insights about implementation approach
3. Potential challenges or dependencies
4. Recommended order of operations"""
        
        result = self.ai.open(
            prompt=prompt,
            context=f"TODO excerpt: {todo_content[:500]}",
            context_name="todo_summary"
        )
        
        return result.content
    
    def _get_file_tree(self, repo_path: Path) -> str:
        """Get simplified file tree structure"""
        tree_lines = []
        
        def add_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for i, item in enumerate(items):
                if item.name.startswith('.'):
                    continue
                
                is_last = i == len(items) - 1
                current = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{current}{item.name}")
                
                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    add_tree(item, prefix + extension, max_depth, current_depth + 1)
        
        tree_lines.append(repo_path.name)
        add_tree(repo_path)
        
        return "\n".join(tree_lines[:100])  # Limit to 100 lines