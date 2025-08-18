"""
Project Analyzer for GitLlama
Hierarchical AI-powered repository analysis with clearly defined steps
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """Analyzes repositories using hierarchical summarization"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b", report_generator=None):
        """Initialize the Project Analyzer.
        
        Args:
            client: OllamaClient instance
            model: Model name to use for analysis
            report_generator: Optional ReportGenerator instance for report hooks
        """
        self.client = client
        self.model = model
        self.guided_questions = []  # Store guided questions and answers
        self.report_generator = report_generator
        
        # Get model's context size
        self.max_context_size = self.client.get_model_context_size(model)
        # Reserve space for prompt and response (use 70% of context)
        self.usable_context_size = int(self.max_context_size * 0.7)
        
        logger.info(f"ProjectAnalyzer initialized with model: {model}")
        logger.info(f"Context window size: {self.max_context_size} tokens")
        logger.info(f"Usable context size: {self.usable_context_size} tokens")
    
    def analyze_all_branches(self, repo_path: Path) -> Tuple[str, Dict[str, Dict]]:
        """Analyze all branches in the repository.
        
        This method analyzes the current branch and all other branches.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Tuple of (current_branch_name, dict of branch_name -> analysis)
        """
        logger.info("=" * 60)
        logger.info("ANALYZING ALL REPOSITORY BRANCHES")
        logger.info("=" * 60)
        
        # Get current branch
        current_branch = self._get_current_branch(repo_path)
        logger.info(f"Current branch: {current_branch}")
        
        # Get all branches
        all_branches = self._get_all_branches(repo_path)
        logger.info(f"Found {len(all_branches)} total branches")
        
        # Log all discovered branches before starting analysis
        if all_branches:
            logger.info("Discovered branches:")
            for branch in all_branches:
                is_current = " (current)" if branch == current_branch else ""
                logger.info(f"  - {branch}{is_current}")
        else:
            logger.warning("No branches found in repository!")
            return current_branch, {}
        
        # Analyze each branch
        branch_analyses = {}
        
        for i, branch in enumerate(all_branches, 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"ANALYZING BRANCH {i}/{len(all_branches)}: {branch}")
            logger.info(f"{'=' * 60}")
            
            # Checkout the branch if different from current
            if branch != current_branch:
                logger.info(f"🔧 Git: Switching from '{current_branch}' to '{branch}'...")
                if not self._checkout_branch(repo_path, branch):
                    logger.error(f"  Failed to checkout branch '{branch}', skipping analysis")
                    continue
            else:
                logger.info(f"  Already on branch '{branch}', no checkout needed")
            
            # Analyze the branch
            logger.info(f"  Starting analysis of branch '{branch}'...")
            analysis = self.analyze_repository(repo_path, branch_context=branch)
            branch_analyses[branch] = analysis
            
            logger.info(f"  Branch '{branch}' analysis complete")
        
        # Return to original branch
        logger.info(f"\n{'=' * 60}")
        if current_branch in all_branches:
            logger.info(f"🔧 Git: Returning to original branch: {current_branch}")
            if self._checkout_branch(repo_path, current_branch):
                logger.info(f"🔧 Git: Successfully returned to branch: {current_branch}")
            else:
                logger.error(f"Failed to return to original branch: {current_branch}")
        else:
            logger.warning(f"Original branch '{current_branch}' not found in branch list, staying on current branch")
        
        logger.info(f"{'=' * 60}")
        logger.info(f"ALL BRANCHES ANALYZED SUCCESSFULLY")
        logger.info(f"  Total branches analyzed: {len(branch_analyses)}")
        logger.info(f"  Current branch: {current_branch}")
        logger.info(f"{'=' * 60}\n")
        
        return current_branch, branch_analyses
    
    def _get_current_branch(self, repo_path: Path) -> str:
        """Get the current branch name."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current branch: {e}")
            return "unknown"
    
    def _get_all_branches(self, repo_path: Path) -> List[str]:
        """Get all local and remote branches."""
        try:
            # Get ALL branches (local and remote) using git branch -a
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches_set = set()  # Use set to avoid duplicates
            local_branches = []
            remote_branches = []
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Remove the * marker for current branch
                if line.startswith('*'):
                    line = line[1:].strip()
                
                if line.startswith('remotes/'):
                    # Handle remote branches
                    # Skip HEAD references (like "remotes/origin/HEAD -> origin/main")
                    if '->' in line or 'HEAD' in line:
                        continue
                    
                    # Extract branch name from remotes/origin/branch-name
                    parts = line.split('/')
                    if len(parts) >= 3:
                        # Get everything after 'remotes/origin/'
                        branch_name = '/'.join(parts[2:])
                        remote_branches.append(branch_name)
                        branches_set.add(branch_name)
                else:
                    # Local branch
                    local_branches.append(line)
                    branches_set.add(line)
            
            # Log what we found
            logger.debug(f"Found {len(local_branches)} local branches: {local_branches}")
            logger.debug(f"Found {len(remote_branches)} remote branches: {remote_branches}")
            
            # Convert set to sorted list for consistent ordering
            all_branches = sorted(list(branches_set))
            
            # If we only found one branch and it's main/master, try to fetch all remote branches
            if len(all_branches) == 1 and all_branches[0] in ['main', 'master']:
                logger.info("Only found main/master branch, fetching all remote branches...")
                try:
                    # Fetch all remote branches
                    subprocess.run(
                        ['git', 'fetch', '--all'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    # Recursively call ourselves to get the updated branch list
                    return self._get_all_branches(repo_path)
                except subprocess.CalledProcessError:
                    logger.warning("Failed to fetch remote branches")
            
            return all_branches
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get branches: {e.stderr if e.stderr else str(e)}")
            return []
    
    def _checkout_branch(self, repo_path: Path, branch: str) -> bool:
        """Checkout a specific branch, creating local tracking branch if needed."""
        try:
            # First check if the branch already exists locally
            check_local = subprocess.run(
                ['git', 'rev-parse', '--verify', branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if check_local.returncode == 0:
                # Local branch exists, just checkout (no -b flag)
                result = subprocess.run(
                    ['git', 'checkout', branch],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info(f"    Successfully checked out existing local branch: {branch}")
                    if result.stderr:
                        logger.debug(f"    Git output: {result.stderr.strip()}")
                    return True
                else:
                    logger.error(f"    Failed to checkout existing branch {branch}: {result.stderr}")
                    return False
            
            # Branch doesn't exist locally, check if it exists as a remote branch
            logger.debug(f"    Branch {branch} not found locally, checking remote...")
            
            remote_branch = f"origin/{branch}"
            check_remote = subprocess.run(
                ['git', 'rev-parse', '--verify', remote_branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if check_remote.returncode == 0:
                # Remote branch exists, create local tracking branch with -b
                logger.info(f"    Creating local tracking branch from {remote_branch}...")
                result = subprocess.run(
                    ['git', 'checkout', '-b', branch, remote_branch],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info(f"    Created and checked out tracking branch: {branch} -> {remote_branch}")
                    return True
                else:
                    # If that failed, maybe the branch name has special characters
                    # Try alternative: checkout with --track
                    result = subprocess.run(
                        ['git', 'checkout', '--track', remote_branch],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"    Successfully checked out tracking branch: {branch}")
                        return True
                    else:
                        logger.error(f"    Failed to create tracking branch: {result.stderr}")
                        return False
            
            # Branch doesn't exist locally or remotely
            logger.error(f"    Branch {branch} not found locally or remotely")
            return False
            
        except Exception as e:
            logger.error(f"    Unexpected error checking out branch {branch}: {str(e)}")
            return False
    
    def analyze_repository(self, repo_path: Path, branch_context: Optional[str] = None) -> Dict:
        """Main entry point for repository analysis.
        
        This method orchestrates the entire analysis pipeline.
        Each step is clearly separated for easy extension.
        
        Args:
            repo_path: Path to the repository
            branch_context: Optional branch name for context in prompts
            
        Returns:
            Complete analysis dictionary
        """
        logger.info(f"Starting hierarchical repository analysis")
        if branch_context:
            logger.info(f"Branch context: {branch_context}")
        logger.info("=" * 60)
        
        # ============================================================
        # STEP 1: DATA GATHERING & VIBE DETECTION
        # Collect all relevant files from the repository
        # ============================================================
        logger.info("STEP 1: DATA GATHERING & VIBE DETECTION")
        if self.report_generator:
            self.report_generator.start_phase("Data Gathering", "Scanning repository files and detecting project structure")
        all_files, total_tokens, vibe_info = self._step1_gather_repository_data(repo_path)
        if self.report_generator:
            self.report_generator.add_phase_detail("Data Gathering", f"Found {len(all_files)} files with {total_tokens} tokens")
            self.report_generator.end_phase("Data Gathering")
        
        # Run initial guided questions on repository structure
        self._ask_guided_question(
            "What branches and tags exist? Does this suggest active development?",
            f"Found {len(vibe_info.get('directory_structure', []))} directories, "
            f"{len(vibe_info.get('file_types', []))} file types. "
            f"TODO.md exists: {vibe_info.get('has_todo', False)}"
        )
        
        if not all_files:
            logger.warning("No analyzable files found in repository")
            return {
                "project_type": "empty",
                "technologies": [],
                "state": "No analyzable files found",
                "vibe": vibe_info,
                "analysis_metadata": {
                    "total_files": 0,
                    "total_tokens": 0,
                    "chunks_created": 0,
                    "branch": branch_context
                }
            }
        
        # ============================================================
        # STEP 2: CHUNKING & FILE SAMPLING
        # Organize files into context-window-sized chunks
        # ============================================================
        logger.info("STEP 2: CHUNKING & FILE SAMPLING")
        if self.report_generator:
            self.report_generator.start_phase("Chunking Strategy", "Organizing files into context-sized chunks for analysis")
        chunks = self._step2_create_chunks(all_files)
        if self.report_generator:
            self.report_generator.add_phase_detail("Chunking Strategy", f"Created {len(chunks)} chunks for analysis")
            self.report_generator.end_phase("Chunking Strategy")
        
        # Sample first few files for functional overview
        self._sample_files_for_vibe(all_files, vibe_info)
        
        # ============================================================
        # STEP 3: CHUNK ANALYSIS WITH GUIDED QUESTIONS
        # Analyze each chunk independently
        # ============================================================
        logger.info("STEP 3: CHUNK ANALYSIS WITH GUIDED QUESTIONS")
        if self.report_generator:
            self.report_generator.start_phase("AI Analysis", f"Analyzing {len(chunks)} chunks with AI for deep understanding")
        chunk_summaries = self._step3_analyze_chunks(chunks, branch_context, vibe_info)
        if self.report_generator:
            self.report_generator.add_phase_detail("AI Analysis", f"Completed analysis of {len(chunks)} chunks")
            self.report_generator.end_phase("AI Analysis")
        
        # ============================================================
        # STEP 4: HIERARCHICAL MERGING & SYNTHESIS
        # Merge all chunk summaries into final analysis
        # ============================================================
        logger.info("STEP 4: HIERARCHICAL MERGING & SYNTHESIS")
        if self.report_generator:
            self.report_generator.start_phase("Hierarchical Merging", "Combining chunk analyses into unified understanding")
        final_summary = self._step4_merge_summaries(chunk_summaries)
        
        # Perform final synthesis with recommendations
        synthesis = self._generate_final_synthesis(final_summary, vibe_info, branch_context)
        if self.report_generator:
            self.report_generator.add_phase_detail("Hierarchical Merging", "Generated synthesis and recommendations")
            self.report_generator.end_phase("Hierarchical Merging")
        
        # ============================================================
        # STEP 5: FORMAT RESULTS WITH RECOMMENDATIONS
        # Format the final analysis for consumption
        # ============================================================
        logger.info("STEP 5: FORMAT RESULTS WITH RECOMMENDATIONS")
        if self.report_generator:
            self.report_generator.start_phase("Final Synthesis", "Formatting results and generating recommendations")
        result = self._step5_format_results(final_summary, all_files, chunks, vibe_info, synthesis)
        if self.report_generator:
            self.report_generator.add_phase_detail("Final Synthesis", f"Generated final analysis for {result['project_type']} project")
            self.report_generator.end_phase("Final Synthesis")
        
        # Add branch context to result
        if branch_context:
            result["branch"] = branch_context
            result["analysis_metadata"]["branch"] = branch_context
        
        logger.info("=" * 60)
        logger.info("Repository analysis complete!")
        
        # Add guided questions to result
        result["guided_questions"] = self.guided_questions
        
        return result
    
    # ============================================================
    # STEP 1: DATA GATHERING
    # ============================================================
    
    def _step1_gather_repository_data(self, repo_path: Path) -> Tuple[List[Dict], int, Dict]:
        """STEP 1: Gather all repository data for analysis.
        
        This step scans the repository and collects all relevant files.
        Also performs initial "vibe" detection including TODO.md check.
        
        Returns:
            Tuple of (list of file data dicts, total token count, vibe info)
        """
        logger.info(f"  Gathering repository data from {repo_path}")
        
        all_files = []
        total_tokens = 0
        vibe_info = {
            "has_todo": False,
            "todo_content": None,
            "directory_structure": [],
            "key_files": [],
            "file_types": set()
        }
        
        # Define file extensions to analyze
        text_extensions = {'.py', '.js', '.tsx', '.jsx', '.md', '.txt', '.json', 
                          '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                          '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd',
                          '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go',
                          '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
                          '.html', '.css', '.scss', '.less', '.xml', '.vue',
                          '.Dockerfile', '.dockerignore', '.gitignore',
                          '.env.example', 'Makefile', 'CMakeLists.txt'}
        
        # Also check for files without extensions
        special_files = {'Dockerfile', 'Makefile', 'README', 'LICENSE', 
                        'CHANGELOG', 'AUTHORS', 'CONTRIBUTORS'}
        
        for file_path in repo_path.rglob("*"):
            # Skip hidden directories and files
            if any(part.startswith('.') for part in file_path.parts[:-1]):
                continue
            
            # Check if file should be analyzed
            should_analyze = (
                file_path.is_file() and 
                (file_path.suffix in text_extensions or 
                 file_path.name in special_files)
            )
            
            if should_analyze:
                try:
                    # Check file size first
                    file_size = file_path.stat().st_size
                    if file_size > 100000:  # Skip files larger than 100KB
                        logger.debug(f"  Skipping large file: {file_path}")
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    relative_path = file_path.relative_to(repo_path)
                    file_tokens = self.client.count_tokens(content)
                    
                    all_files.append({
                        'path': str(relative_path),
                        'content': content,
                        'tokens': file_tokens,
                        'extension': file_path.suffix,
                        'size_bytes': file_size
                    })
                    total_tokens += file_tokens
                    
                    # Track file types for vibe
                    if file_path.suffix:
                        vibe_info["file_types"].add(file_path.suffix)
                    
                    # Identify key files for vibe
                    if file_path.name in ['README.md', 'package.json', 'requirements.txt', 
                                         'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle']:
                        vibe_info["key_files"].append(str(relative_path))
                    
                except Exception as e:
                    logger.debug(f"  Could not read {file_path}: {e}")
        
        # Check for TODO.md file specifically
        todo_path = repo_path / "TODO.md"
        if todo_path.exists():
            try:
                with open(todo_path, 'r', encoding='utf-8', errors='ignore') as f:
                    todo_content = f.read()
                vibe_info["has_todo"] = True
                vibe_info["todo_content"] = todo_content
                logger.info(f"  ✓ Found TODO.md with guidance from project owner")
            except Exception as e:
                logger.debug(f"  Could not read TODO.md: {e}")
        else:
            logger.info(f"  No TODO.md found - will infer next steps from context")
        
        # Get directory structure for vibe analysis
        dirs_seen = set()
        for file_path in repo_path.rglob("*"):
            if file_path.is_dir() and not any(part.startswith('.') for part in file_path.parts):
                rel_dir = str(file_path.relative_to(repo_path))
                dirs_seen.add(rel_dir)
        vibe_info["directory_structure"] = sorted(list(dirs_seen))[:20]  # Top 20 dirs
        
        # Track file types for vibe
        vibe_info["file_types"] = sorted(list(vibe_info["file_types"]))[:15]  # Top 15 types
        
        logger.info(f"  Found {len(all_files)} files with {total_tokens} total tokens")
        logger.info(f"  Directory vibe: {len(vibe_info['directory_structure'])} directories")
        logger.info(f"  File type vibe: {len(vibe_info['file_types'])} distinct types")
        return all_files, total_tokens, vibe_info
    
    # ============================================================
    # STEP 2: CHUNKING
    # ============================================================
    
    def _step2_create_chunks(self, files: List[Dict]) -> List[List[Dict]]:
        """STEP 2: Organize files into chunks that fit within context window.
        
        This step groups files intelligently to maximize context usage.
        Future enhancements could include:
        - Semantic grouping (keep related files together)
        - Priority-based chunking (important files first)
        - Language-specific chunking strategies
        
        Args:
            files: List of file data dictionaries
            
        Returns:
            List of file chunks
        """
        logger.info(f"  Creating chunks (max {self.usable_context_size} tokens each)")
        
        # Reserve space for prompt (roughly 500 tokens)
        chunk_size = self.usable_context_size - 500
        
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
                        'tokens': self.client.count_tokens(content_chunk),
                        'extension': file_data['extension']
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
        
        logger.info(f"  Created {len(chunks)} chunks for analysis")
        for i, chunk in enumerate(chunks, 1):
            chunk_tokens = sum(f['tokens'] for f in chunk)
            logger.info(f"    Chunk {i}: {len(chunk)} files, {chunk_tokens} tokens")
        
        return chunks
    
    # ============================================================
    # STEP 3: CHUNK ANALYSIS
    # ============================================================
    
    def _ask_guided_question(self, question: str, context: str) -> str:
        """Ask a guided question and store the answer.
        
        Args:
            question: The guided question to ask
            context: Context to provide for answering
            
        Returns:
            The AI's answer
        """
        logger.info(f"📝 Guided Question: {question}")
        
        prompt = f"""Based on this context:
{context}

Answer this question concisely:
{question}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="project_analysis"):
            response += chunk
        
        answer = response.strip()
        logger.info(f"   Answer: {answer[:100]}..." if len(answer) > 100 else f"   Answer: {answer}")
        
        # Store in local list
        self.guided_questions.append({
            "question": question,
            "answer": answer,
            "context_summary": context[:200] + "..." if len(context) > 200 else context
        })
        
        # Hook into report generator
        if self.report_generator:
            self.report_generator.add_guided_question(question, context, answer)
        
        return answer
    
    def _sample_files_for_vibe(self, all_files: List[Dict], vibe_info: Dict) -> List[Dict]:
        """Sample key files for functional overview.
        
        Args:
            all_files: List of all files
            vibe_info: Vibe information
            
        Returns:
            List of sampled files
        """
        sampled = []
        
        # Priority files to sample
        priority_files = ['README.md', 'package.json', 'requirements.txt', 
                         'main.py', 'index.js', 'app.py', 'main.go']
        
        for file_data in all_files:
            file_name = Path(file_data['path']).name
            if file_name in priority_files:
                sampled.append(file_data)
                if len(sampled) >= 5:
                    break
        
        # If we don't have enough, add some regular code files
        if len(sampled) < 5:
            code_extensions = ['.py', '.js', '.tsx', '.go', '.rs', '.java']
            for file_data in all_files:
                if Path(file_data['path']).suffix in code_extensions and file_data not in sampled:
                    sampled.append(file_data)
                    if len(sampled) >= 10:
                        break
        
        if sampled:
            # Ask guided question about sampled content
            sample_context = "\n".join([f"File: {f['path']}\n{f['content'][:200]}..." 
                                       for f in sampled[:3]])
            self._ask_guided_question(
                "What core functionality do these files reveal? Is it a web app, CLI tool, library?",
                sample_context
            )
        
        return sampled
    
    def _generate_final_synthesis(self, final_summary: Dict, vibe_info: Dict, 
                                 branch_context: Optional[str] = None) -> Dict:
        """Generate final synthesis with recommendations.
        
        Args:
            final_summary: The merged analysis
            vibe_info: Vibe information
            branch_context: Current branch context
            
        Returns:
            Synthesis with recommendations
        """
        logger.info("  Generating final synthesis and recommendations")
        
        # Build context for synthesis
        context_parts = [
            f"Project type: {final_summary.get('project_type', 'unknown')}",
            f"Technologies: {', '.join(final_summary.get('all_technologies', [])[:5])}",
            f"Current state: {final_summary.get('state', 'unknown')}",
            f"Has TODO.md: {vibe_info.get('has_todo', False)}"
        ]
        
        if vibe_info.get('has_todo') and vibe_info.get('todo_content'):
            context_parts.append(f"TODO.md excerpt: {vibe_info['todo_content'][:500]}...")
        
        if branch_context:
            context_parts.append(f"Current branch: {branch_context}")
        
        context = "\n".join(context_parts)
        
        # Ask for synthesis
        logger.info(f"🤖 AI: Generating synthesis and next steps recommendation")
        
        prompt = f"""Based on this repository analysis:
{context}

Provide a synthesis with:
1. What is the immediate next development priority?
2. Which branch should be worked on (or should a new one be created)?
3. What specific tasks should be accomplished in the next coding session?
{"4. How does the TODO.md align with the current state?" if vibe_info.get('has_todo') else ""}

Response in JSON format:
{{
    "next_priority": "specific next development focus",
    "recommended_branch": "branch name or 'create new'",
    "immediate_tasks": ["task1", "task2", "task3"],
    "development_direction": "overall direction",
    {('"todo_alignment": "how TODO.md aligns with current state",' if vibe_info.get('has_todo') else '')}
    "confidence": "high|medium|low"
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="project_analysis"):
            response += chunk
        
        try:
            synthesis = json.loads(response)
            logger.info(f"  Synthesis complete: Next priority - {synthesis.get('next_priority', 'unknown')}")
            return synthesis
        except json.JSONDecodeError:
            logger.warning("  Synthesis JSON parse failed, using defaults")
            return {
                "next_priority": "Continue development based on context",
                "recommended_branch": branch_context or "main",
                "immediate_tasks": ["Review code", "Fix issues", "Add features"],
                "development_direction": "Incremental improvements",
                "confidence": "low"
            }
    
    def _step3_analyze_chunks(self, chunks: List[List[Dict]], branch_context: Optional[str] = None, 
                             vibe_info: Optional[Dict] = None) -> List[Dict]:
        """STEP 3: Analyze each chunk independently.
        
        This step performs AI analysis on each chunk.
        Future enhancements could include:
        - Parallel chunk processing
        - Different analysis strategies per file type
        - Code quality metrics extraction
        - Security vulnerability scanning
        
        Args:
            chunks: List of file chunks
            branch_context: Optional branch name for context
            
        Returns:
            List of chunk analysis summaries
        """
        logger.info(f"  Analyzing {len(chunks)} chunks")
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"    Processing chunk {i}/{len(chunks)}...")
            summary = self._analyze_single_chunk(chunk, i, len(chunks), branch_context)
            chunk_summaries.append(summary)
            
            # Ask guided question about chunk findings
            if i == 1 and vibe_info:
                self._ask_guided_question(
                    "What does the first chunk reveal about the project's main purpose?",
                    f"Technologies: {summary.get('technologies', [])}\n"
                    f"Purpose: {summary.get('main_purpose', 'unknown')}"
                )
            
            logger.info(f"    Chunk {i} analysis complete")
        
        return chunk_summaries
    
    def _analyze_single_chunk(self, chunk: List[Dict], chunk_index: int, total_chunks: int, 
                             branch_context: Optional[str] = None) -> Dict:
        """Analyze a single chunk of files."""
        
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
        logger.debug(f"      Chunk {chunk_index} context: {context_tokens} tokens")
        
        # Adjust prompt based on branch context
        branch_note = f" (Branch: {branch_context})" if branch_context else ""
        
        # Log AI query
        logger.info(f"🤖 AI: Analyzing chunk {chunk_index}/{total_chunks} for comprehensive project understanding")
        
        prompt = f"""Analyze this portion of a code repository{branch_note} (chunk {chunk_index} of {total_chunks}):

{context}

Provide a comprehensive analysis including:
1. Main purpose/functionality of these files
2. Technologies and frameworks used
3. Code quality observations
4. Key patterns or architectural decisions
5. Notable features or issues
{f"6. How this branch '{branch_context}' differs from main (if apparent)" if branch_context and branch_context not in ['main', 'master'] else ""}

Response in JSON format:
{{
    "chunk_index": {chunk_index},
    "file_count": {len(chunk)},
    "main_purpose": "",
    "technologies": [],
    "patterns": [],
    "quality_notes": "",
    "key_features": [],
    {f'"branch_context": "{branch_context}",' if branch_context else ''}
    {'"branch_differences": "",' if branch_context and branch_context not in ['main', 'master'] else ''}
    "analysis_focus": ""
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk_text in self.client.chat_stream(self.model, messages, context_name="guided_questions"):
            response += chunk_text
        
        try:
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.warning(f"      Chunk {chunk_index} JSON parse failed, using raw response")
            return {
                "chunk_index": chunk_index,
                "file_count": len(chunk),
                "raw_analysis": response[:500]
            }
    
    # ============================================================
    # STEP 4: HIERARCHICAL MERGING
    # ============================================================
    
    def _step4_merge_summaries(self, summaries: List[Dict]) -> Dict:
        """STEP 4: Hierarchically merge all summaries.
        
        This step combines chunk summaries using a merge-sort approach.
        Future enhancements could include:
        - Weighted merging based on file importance
        - Cross-reference detection between chunks
        - Dependency graph construction
        
        Args:
            summaries: List of chunk summaries
            
        Returns:
            Final merged summary
        """
        logger.info(f"  Starting hierarchical merge of {len(summaries)} summaries")
        
        def merge_recursive(summaries_to_merge: List[Dict], level: int = 1) -> Dict:
            """Recursively merge summaries."""
            
            if len(summaries_to_merge) == 1:
                return summaries_to_merge[0]
            
            # Build context from summaries
            context_parts = []
            for i, summary in enumerate(summaries_to_merge, 1):
                context_parts.append(f"=== Summary {i} ===")
                context_parts.append(json.dumps(summary, indent=2))
                context_parts.append("")
            
            context = "\n".join(context_parts)
            context_tokens = self.client.count_tokens(context)
            
            # If context is too large, recursively merge in smaller groups
            if context_tokens > self.usable_context_size:
                logger.info(f"    Level {level}: Context too large ({context_tokens} tokens), splitting")
                mid = len(summaries_to_merge) // 2
                left_summary = merge_recursive(summaries_to_merge[:mid], level)
                right_summary = merge_recursive(summaries_to_merge[mid:], level)
                return merge_recursive([left_summary, right_summary], level + 1)
            
            logger.info(f"    Level {level}: Merging {len(summaries_to_merge)} summaries ({context_tokens} tokens)")
            logger.info(f"🤖 AI: Merging {len(summaries_to_merge)} analysis summaries into unified understanding")
            
            prompt = f"""Merge these {len(summaries_to_merge)} analyses into a unified summary:

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
    "summaries_merged": {len(summaries_to_merge)},
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
            
            for chunk in self.client.chat_stream(self.model, messages, context_name="hierarchical_merge"):
                response += chunk
            
            try:
                merged = json.loads(response)
                logger.info(f"    Level {level} merge complete")
                return merged
            except json.JSONDecodeError:
                logger.warning(f"    Level {level} merge JSON parse failed")
                return {
                    "merge_level": level,
                    "summaries_merged": len(summaries_to_merge),
                    "raw_analysis": response[:500]
                }
        
        final_summary = merge_recursive(summaries)
        logger.info(f"  Hierarchical merge complete")
        return final_summary
    
    # ============================================================
    # STEP 5: FORMAT RESULTS
    # ============================================================
    
    def _step5_format_results(self, final_summary: Dict, all_files: List[Dict], 
                             chunks: List[List[Dict]], vibe_info: Dict, synthesis: Dict) -> Dict:
        """STEP 5: Format the final analysis results.
        
        This step creates the final output format.
        Future enhancements could include:
        - Confidence scores
        - Suggested improvements
        - Technical debt assessment
        - README generation
        
        Args:
            final_summary: The merged analysis
            all_files: Original file list
            chunks: The chunks that were created
            vibe_info: Vibe information gathered
            
        Returns:
            Formatted analysis results
        """
        logger.info(f"  Formatting final results")
        
        total_tokens = sum(f['tokens'] for f in all_files)
        
        result = {
            "project_type": final_summary.get("project_type", "unknown"),
            "technologies": final_summary.get("all_technologies", []),
            "state": final_summary.get("state", final_summary.get("overall_purpose", "analyzed")),
            "architecture": final_summary.get("architecture", ""),
            "quality": final_summary.get("overall_quality", ""),
            "patterns": final_summary.get("key_patterns", []),
            "vibe": vibe_info,
            "has_todo": vibe_info.get("has_todo", False),
            "synthesis": synthesis,
            "next_steps": {
                "priority": synthesis.get("next_priority", "Continue development"),
                "recommended_branch": synthesis.get("recommended_branch", "main"),
                "tasks": synthesis.get("immediate_tasks", [])
            },
            "analysis_metadata": {
                "total_files": len(all_files),
                "total_tokens": total_tokens,
                "chunks_created": len(chunks),
                "context_window": self.max_context_size,
                "model": self.model
            },
            "detailed_analysis": final_summary
        }
        
        logger.info(f"  Results formatted successfully")
        return result