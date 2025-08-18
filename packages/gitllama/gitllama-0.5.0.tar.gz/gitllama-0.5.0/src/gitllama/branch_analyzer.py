"""
Branch Analyzer for GitLlama
Intelligent branch selection and analysis with clear decision logic
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from .ollama_client import OllamaClient
from .ai_decision_formatter import AIDecisionFormatter

logger = logging.getLogger(__name__)


class BranchAnalyzer:
    """Analyzes git branches and makes intelligent branch selection decisions"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b", report_generator=None):
        """Initialize the Branch Analyzer.
        
        Args:
            client: OllamaClient instance
            model: Model name to use for analysis
            report_generator: Optional ReportGenerator instance for report hooks
        """
        self.client = client
        self.model = model
        self.branch_analyses = {}  # Store analysis of each branch
        self.decision_formatter = AIDecisionFormatter(report_generator)
        self.report_generator = report_generator
        
        logger.info(f"BranchAnalyzer initialized with model: {model}")
    
    def analyze_and_select_branch(self, repo_path: Path, current_branch: str, 
                                 project_info: Dict, branch_summaries: Dict[str, Dict]) -> Tuple[str, str, Dict]:
        """Main entry point for branch analysis and selection.
        
        This method orchestrates the entire branch decision pipeline.
        Each step is clearly separated for easy understanding and extension.
        
        Args:
            repo_path: Path to the repository
            current_branch: Currently checked out branch
            project_info: Project analysis from ProjectAnalyzer
            branch_summaries: Dictionary of branch names to their analysis summaries
            
        Returns:
            Tuple of (selected_branch_name, decision_reason, decision_metadata)
        """
        logger.info(f"Starting intelligent branch selection process")
        logger.info("=" * 60)
        
        # Store the branch analyses
        self.branch_analyses = branch_summaries
        
        # Hook into report generator
        if self.report_generator:
            branches = list(branch_summaries.keys())
            self.report_generator.add_branch_discovery(branches)
        
        # ============================================================
        # STEP 1: ANALYZE EXISTING BRANCHES
        # Understand what each existing branch is for
        # ============================================================
        logger.info("STEP 1: ANALYZE EXISTING BRANCHES")
        branch_purposes = self._step1_analyze_branch_purposes(branch_summaries)
        
        # ============================================================
        # STEP 1.5: ANALYZE TODO.md FILES ACROSS BRANCHES
        # Compare TODO.md content between branches
        # ============================================================
        logger.info("STEP 1.5: ANALYZE TODO.md FILES ACROSS BRANCHES")
        todo_analysis = self._step1_5_analyze_todo_files(repo_path, list(branch_summaries.keys()))
        
        # ============================================================
        # STEP 2: EVALUATE REUSE POTENTIAL
        # Determine if any existing branch is suitable for our work
        # ============================================================
        logger.info("STEP 2: EVALUATE REUSE POTENTIAL")
        reuse_candidates = self._step2_evaluate_reuse_potential(
            branch_purposes, project_info, todo_analysis
        )
        
        # ============================================================
        # STEP 3: MAKE BRANCH DECISION
        # Decide whether to use existing or create new branch
        # ============================================================
        logger.info("STEP 3: MAKE BRANCH DECISION")
        decision = self._step3_make_branch_decision(
            current_branch, reuse_candidates, project_info
        )
        
        # ============================================================
        # STEP 4: GENERATE BRANCH NAME
        # Create new name if needed, or select existing
        # ============================================================
        logger.info("STEP 4: GENERATE/SELECT BRANCH NAME")
        final_branch = self._step4_finalize_branch_selection(
            decision, reuse_candidates, project_info
        )
        
        # Hook into report generator for final selection
        if self.report_generator:
            self.report_generator.set_branch_selection(
                final_branch['branch_name'],
                final_branch['reason'],
                final_branch['action']
            )
        
        logger.info("=" * 60)
        logger.info(f"Branch selection complete: {final_branch['branch_name']}")
        
        return final_branch['branch_name'], final_branch['reason'], final_branch
    
    # ============================================================
    # STEP 1: ANALYZE EXISTING BRANCHES
    # ============================================================
    
    def _step1_analyze_branch_purposes(self, branch_summaries: Dict[str, Dict]) -> Dict[str, Dict]:
        """STEP 1: Analyze the purpose of each existing branch.
        
        This step examines each branch's analysis to understand its purpose.
        Now includes git history analysis for better vibe detection.
        
        Args:
            branch_summaries: Dictionary of branch analyses
            
        Returns:
            Dictionary mapping branch names to their purposes
        """
        logger.info(f"  Analyzing purposes of {len(branch_summaries)} branches")
        
        branch_purposes = {}
        
        for branch_name, summary in branch_summaries.items():
            # Skip if no real analysis available
            if not summary or summary.get('project_type') == 'empty':
                logger.info(f"    Branch '{branch_name}': No analyzable content")
                branch_purposes[branch_name] = {
                    'purpose': 'empty',
                    'active': False,
                    'suitable_for_work': False,
                    'unique_commits': [],
                    'vibe': 'empty'
                }
                continue
            
            # Get unique commits for this branch
            unique_commits = self._get_unique_commits(branch_name)
            
            # Analyze vibe from commits and summary
            vibe = self._analyze_branch_vibe(branch_name, summary, unique_commits)
            
            # Extract key information
            purpose_info = {
                'purpose': summary.get('state', 'unknown'),
                'project_type': summary.get('project_type', 'unknown'),
                'technologies': summary.get('technologies', []),
                'quality': summary.get('quality', 'unknown'),
                'patterns': summary.get('patterns', []),
                'unique_commits': unique_commits,
                'vibe': vibe,
                'active': len(unique_commits) > 0,
                'suitable_for_work': vibe in ['wip', 'experimental', 'feature']
            }
            
            branch_purposes[branch_name] = purpose_info
            logger.info(f"    Branch '{branch_name}': {purpose_info['purpose'][:50]}... (vibe: {vibe})")
        
        return branch_purposes
    
    # ============================================================
    # STEP 1.5: ANALYZE TODO.md FILES ACROSS BRANCHES
    # ============================================================
    
    def _step1_5_analyze_todo_files(self, repo_path: Path, branches: List[str]) -> Dict[str, Dict]:
        """STEP 1.5: Analyze TODO.md files across all branches and compare them.
        
        This step checks for TODO.md files in the project root of each branch
        and uses AI to compare their content and priorities.
        
        Args:
            repo_path: Path to the repository
            branches: List of branch names to analyze
            
        Returns:
            Dictionary with TODO analysis results
        """
        logger.info(f"  Analyzing TODO.md files across {len(branches)} branches")
        
        # Store current branch to restore later
        current_branch = self._get_current_branch()
        todo_contents = {}
        
        try:
            # Collect TODO.md content from each branch
            for branch in branches:
                logger.info(f"    Checking TODO.md in branch '{branch}'")
                
                try:
                    # Switch to branch
                    subprocess.run(
                        ['git', 'checkout', branch],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    # Check for TODO.md in project root
                    todo_path = repo_path / "TODO.md"
                    if todo_path.exists():
                        with open(todo_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        todo_contents[branch] = {
                            'exists': True,
                            'content': content,
                            'length': len(content)
                        }
                        logger.info(f"      Found TODO.md ({len(content)} chars)")
                    else:
                        todo_contents[branch] = {
                            'exists': False,
                            'content': '',
                            'length': 0
                        }
                        logger.info(f"      No TODO.md found")
                        
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Could not checkout branch {branch}: {e}")
                    todo_contents[branch] = {
                        'exists': False,
                        'content': '',
                        'length': 0,
                        'error': str(e)
                    }
            
            # Generate AI comparison if we have TODO.md files
            comparison_result = self._generate_todo_comparison(todo_contents)
            branches_with_todos = [b for b, t in todo_contents.items() if t['exists']]
            
            # Hook into report generator
            if self.report_generator:
                self.report_generator.add_timeline_event(
                    "TODO.md Analysis",
                    f"Analyzed TODO.md files across {len(branches)} branches. "
                    f"Found TODO.md in {sum(1 for t in todo_contents.values() if t['exists'])} branches."
                )
                
                # Add TODO comparison to branch analysis if there are any findings
                # Show analysis even for single branch to provide visibility into TODO discovery
                if branches_with_todos or any(t['exists'] for t in todo_contents.values()):
                    self.report_generator.add_branch_todo_analysis(
                        todo_contents, comparison_result, branches_with_todos
                    )
            
            return {
                'todo_contents': todo_contents,
                'comparison': comparison_result,
                'has_todos': any(t['exists'] for t in todo_contents.values()),
                'branches_with_todos': [b for b, t in todo_contents.items() if t['exists']]
            }
            
        finally:
            # Restore original branch
            try:
                subprocess.run(
                    ['git', 'checkout', current_branch],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                logger.warning(f"Could not restore original branch {current_branch}")
    
    def _generate_todo_comparison(self, todo_contents: Dict[str, Dict]) -> str:
        """Generate AI analysis comparing TODO.md files across branches."""
        # Filter branches that have TODO.md files
        branches_with_todos = {b: t for b, t in todo_contents.items() if t['exists']}
        
        if not branches_with_todos:
            return "No TODO.md files found in any branch."
        
        if len(branches_with_todos) == 1:
            branch = list(branches_with_todos.keys())[0]
            todo_data = branches_with_todos[branch]
            
            # Generate analysis for single TODO.md file
            single_todo_prompt = f"""Analyze the TODO.md file found in the '{branch}' branch. Provide insights in this EXACT format:

**🎯 CONTENT ANALYSIS:**
[What are the main topics and priorities covered in this TODO file?]

**📊 PLANNING QUALITY:**
[How well-organized and detailed is this TODO file? Is it comprehensive?]

**📈 DEVELOPMENT STAGE:**
[What can you infer about the project's development stage from this TODO content?]

**🎯 ACTIONABILITY:**
[How actionable and current do these TODO items appear to be?]

**⚡ KEY INSIGHTS:**
[What are the most important strategic insights from this TODO analysis?]

TODO.md CONTENT TO ANALYZE:
=== BRANCH: {branch} ===
Length: {todo_data['length']} characters
Content:
{todo_data['content'][:1500] + ("..." if len(todo_data['content']) > 1500 else "")}

Provide specific insights about this project's planning and development focus:"""
            
            messages = [{"role": "user", "content": single_todo_prompt}]
            response = ""
            
            for chunk in self.client.chat_stream(self.model, messages, context_name="branch_analysis"):
                response += chunk
            
            return response.strip()
        
        # Build context for AI comparison
        context_parts = [
            f"Found TODO.md files in {len(branches_with_todos)} branches:",
            ""
        ]
        
        for branch, todo_data in branches_with_todos.items():
            context_parts.extend([
                f"=== BRANCH: {branch} ===",
                f"Length: {todo_data['length']} characters",
                f"Content:",
                todo_data['content'][:1000] + ("..." if len(todo_data['content']) > 1000 else ""),
                ""
            ])
        
        context = "\n".join(context_parts)
        
        prompt = f"""Analyze and compare the TODO.md files found across different git branches. Provide detailed insights in this EXACT format:

**🎯 PRIORITY ANALYSIS:**
[How do the priorities and focus areas differ between branches? Which branch focuses on what aspects?]

**🌿 BRANCH PURPOSE INSIGHTS:**
[What can you infer about each branch's specific purpose and development stage from its TODO content?]

**📊 COMPLETENESS COMPARISON:**
[Which branch has the most comprehensive TODO list? Compare the depth and breadth of planning.]

**📈 PROGRESS & MATURITY:**
[Are there signs of progress, task completion, or development maturity across branches?]

**🎯 SELECTION RECOMMENDATION:**
[Which branch's TODO.md is most current, actionable, and suitable for continued development? Why?]

**⚡ KEY DIFFERENCES:**
[What are the most significant strategic differences between the TODO approaches?]

BRANCH TODO.md FILES TO ANALYZE:
{context}

Provide specific, actionable insights that help with intelligent branch selection:"""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="branch_selection"):
            response += chunk
        
        return response.strip()
    
    def _get_current_branch(self) -> str:
        """Get the currently checked out branch name."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"  # fallback
    
    # ============================================================
    # STEP 2: EVALUATE REUSE POTENTIAL
    # ============================================================
    
    def _step2_evaluate_reuse_potential(self, branch_purposes: Dict[str, Dict], 
                                       project_info: Dict, todo_analysis: Dict[str, Dict]) -> List[Dict]:
        """STEP 2: Evaluate which branches could be reused.
        
        This step scores each branch for reuse potential.
        Future enhancements could include:
        - Conflict detection
        - Branch freshness scoring
        - Team ownership checking
        
        Args:
            branch_purposes: Branch purpose analysis
            project_info: Overall project analysis
            
        Returns:
            List of reuse candidates with scores
        """
        logger.info(f"  Evaluating reuse potential for existing branches")
        
        reuse_candidates = []
        project_type = project_info.get('project_type', 'unknown')
        
        for branch_name, purpose_info in branch_purposes.items():
            # Skip main/master branches
            if branch_name.lower() in ['main', 'master', 'develop', 'development']:
                logger.info(f"    Skipping protected branch: {branch_name}")
                continue
            
            # Skip empty branches
            if purpose_info['purpose'] == 'empty':
                continue
            
            # Calculate reuse score (0-100)
            score = 0
            reasons = []
            
            # Check project type compatibility
            if purpose_info['project_type'] == project_type:
                score += 30
                reasons.append("matching project type")
            
            # Check if it's a feature or development branch
            branch_lower = branch_name.lower()
            if any(prefix in branch_lower for prefix in ['feature/', 'feat/', 'enhance/', 'improve/']):
                score += 20
                reasons.append("feature branch")
            elif any(prefix in branch_lower for prefix in ['fix/', 'bugfix/', 'hotfix/']):
                score += 15
                reasons.append("fix branch")
            elif any(prefix in branch_lower for prefix in ['docs/', 'documentation/']):
                score += 10
                reasons.append("documentation branch")
            
            # Check for WIP or experimental branches (good for reuse)
            if any(indicator in branch_lower for indicator in ['wip', 'draft', 'experimental', 'test']):
                score += 25
                reasons.append("work-in-progress branch")
            
            # Bonus for branches that seem abandoned or stale (we can revive them)
            if any(indicator in branch_lower for indicator in ['old', 'stale', 'abandoned', 'temp']):
                score += 15
                reasons.append("potentially abandoned branch")
            
            # Check technology overlap
            if purpose_info.get('technologies'):
                tech_overlap = len(set(purpose_info['technologies']) & set(project_info.get('technologies', [])))
                if tech_overlap > 0:
                    score += min(tech_overlap * 5, 20)
                    reasons.append(f"{tech_overlap} matching technologies")
            
            # Check TODO.md compatibility and relevance
            if todo_analysis.get('has_todos'):
                todo_contents = todo_analysis.get('todo_contents', {})
                if branch_name in todo_contents and todo_contents[branch_name]['exists']:
                    # Branch has TODO.md - this indicates active planning
                    score += 25
                    reasons.append("has active TODO.md")
                    
                    # Check if it's the most comprehensive TODO
                    branches_with_todos = todo_analysis.get('branches_with_todos', [])
                    if len(branches_with_todos) > 1:
                        # Compare TODO length/complexity with other branches
                        this_todo_length = todo_contents[branch_name]['length']
                        avg_todo_length = sum(todo_contents[b]['length'] for b in branches_with_todos) / len(branches_with_todos)
                        
                        if this_todo_length > avg_todo_length * 1.2:
                            score += 10
                            reasons.append("comprehensive TODO.md")
                elif not any(todo_contents[b]['exists'] for b in todo_contents):
                    # No TODO.md files anywhere - neutral
                    pass
                else:
                    # Other branches have TODO.md but this one doesn't - slight penalty
                    score -= 5
                    reasons.append("missing TODO.md while others have it")
            
            if score > 0:
                reuse_candidates.append({
                    'branch_name': branch_name,
                    'score': score,
                    'reasons': reasons,
                    'purpose_info': purpose_info
                })
        
        # Sort by score
        reuse_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Hook into report generator
        if self.report_generator:
            for candidate in reuse_candidates:
                self.report_generator.add_branch_evaluation(
                    candidate['branch_name'], 
                    candidate['score'], 
                    candidate['reasons']
                )
        
        logger.info(f"  Found {len(reuse_candidates)} potential branches for reuse")
        for candidate in reuse_candidates[:3]:  # Log top 3
            logger.info(f"    {candidate['branch_name']}: score={candidate['score']}, reasons={', '.join(candidate['reasons'])}")
        
        return reuse_candidates
    
    # ============================================================
    # STEP 3: MAKE BRANCH DECISION
    # ============================================================
    
    def _step3_make_branch_decision(self, current_branch: str, 
                                   reuse_candidates: List[Dict], 
                                   project_info: Dict) -> Dict:
        """STEP 3: Decide whether to reuse or create new branch.
        
        This step makes the key decision with AI assistance.
        Future enhancements could include:
        - User preference learning
        - Risk assessment
        - Team conventions checking
        
        Args:
            current_branch: Currently checked out branch
            reuse_candidates: List of reuse candidates
            project_info: Project analysis
            
        Returns:
            Decision dictionary
        """
        logger.info(f"  Making branch selection decision")
        
        # Prepare context for AI decision
        context_parts = [
            f"Current branch: {current_branch}",
            f"Project type: {project_info.get('project_type', 'unknown')}",
            f"Number of reuse candidates: {len(reuse_candidates)}"
        ]
        
        if reuse_candidates:
            context_parts.append("\nTop reuse candidates:")
            for candidate in reuse_candidates[:3]:
                context_parts.append(f"  - {candidate['branch_name']} (score: {candidate['score']})")
                context_parts.append(f"    Reasons: {', '.join(candidate['reasons'])}")
        
        context = "\n".join(context_parts)
        
        # Strong bias towards reusing existing branches (80% probability if good candidates exist)
        reuse_threshold = 30  # Minimum score to consider reuse
        has_good_candidates = any(c['score'] >= reuse_threshold for c in reuse_candidates)
        
        # Use single-word decision system
        if has_good_candidates:
            # First decision: Should we REUSE or CREATE?
            action_decision, _ = self.decision_formatter.make_ai_decision(
                client=self.client,
                model=self.model,
                context=context,
                question="Should we reuse an existing branch or create a new one?",
                options=["REUSE", "CREATE"],
                additional_context=f"Strong preference for REUSE when candidates have score >= {reuse_threshold}"
            )
            
            if action_decision == "REUSE" and reuse_candidates:
                # Second decision: Which branch to reuse?
                branch_options = [c['branch_name'] for c in reuse_candidates[:5]]  # Top 5 candidates
                
                selected_branch, _ = self.decision_formatter.make_ai_decision(
                    client=self.client,
                    model=self.model,
                    context=f"Available branches: {', '.join(branch_options)}",
                    question="Which existing branch should we reuse?",
                    options=branch_options,
                    additional_context="Choose the most suitable branch for development"
                )
                
                decision = {
                    'decision': 'REUSE',
                    'selected_branch': selected_branch,
                    'reasoning': f"AI selected existing branch: {selected_branch}"
                }
            else:
                # Create new branch - decide type
                branch_type, _ = self.decision_formatter.make_ai_decision(
                    client=self.client,
                    model=self.model,
                    context=context,
                    question="What type of new branch should we create?",
                    options=["feature", "fix", "docs", "chore"],
                    additional_context="Choose based on the project's current needs"
                )
                
                decision = {
                    'decision': 'CREATE',
                    'new_branch_type': branch_type,
                    'reasoning': f"AI chose to create new {branch_type} branch"
                }
        else:
            # No good candidates - create new branch
            branch_type, _ = self.decision_formatter.make_ai_decision(
                client=self.client,
                model=self.model,
                context=context,
                question="What type of new branch should we create?",
                options=["feature", "fix", "docs", "chore"],
                additional_context=f"No suitable existing branches found. Creating for {project_info.get('project_type', 'project')} project."
            )
            
            decision = {
                'decision': 'CREATE',
                'new_branch_type': branch_type,
                'reasoning': f"No suitable candidates found, creating new {branch_type} branch"
            }
        
        logger.info(f"    Final Decision: {decision['decision']} - {decision.get('reasoning', 'No reason provided')}")
        return decision
    
    # ============================================================
    # STEP 4: GENERATE/SELECT BRANCH NAME
    # ============================================================
    
    def _step4_finalize_branch_selection(self, decision: Dict, 
                                        reuse_candidates: List[Dict],
                                        project_info: Dict) -> Dict:
        """STEP 4: Finalize the branch selection.
        
        This step generates a new branch name or confirms the reuse selection.
        Future enhancements could include:
        - Branch naming convention enforcement
        - Duplicate name checking
        - Team standards validation
        
        Args:
            decision: The branch decision
            reuse_candidates: Available reuse candidates
            project_info: Project analysis
            
        Returns:
            Final branch selection with metadata
        """
        logger.info(f"  Finalizing branch selection")
        
        if decision['decision'] == 'REUSE':
            selected_branch = decision.get('selected_branch')
            
            # Validate the selected branch exists in candidates
            candidate_names = [c['branch_name'] for c in reuse_candidates]
            if selected_branch not in candidate_names:
                # Fallback to best candidate
                if reuse_candidates:
                    selected_branch = reuse_candidates[0]['branch_name']
                else:
                    # Should not happen, but handle gracefully
                    logger.warning("    No reuse candidates available, creating new branch")
                    decision['decision'] = 'CREATE'
            
            if decision['decision'] == 'REUSE':
                # Find the candidate info
                candidate_info = next((c for c in reuse_candidates if c['branch_name'] == selected_branch), None)
                
                result = {
                    'branch_name': selected_branch,
                    'action': 'REUSE',
                    'reason': f"Reusing existing branch: {decision.get('reasoning', 'High compatibility score')}",
                    'score': candidate_info['score'] if candidate_info else 0,
                    'metadata': {
                        'decision': decision,
                        'candidate_info': candidate_info
                    }
                }
                
                logger.info(f"    Selected existing branch: {selected_branch}")
                return result
        
        # Create new branch
        branch_type = decision.get('new_branch_type', 'feature')
        project_type = project_info.get('project_type', 'project')
        
        # Generate branch name with AI
        logger.info(f"🤖 AI: Generating new {branch_type} branch name for {project_type} project")
        prompt = f"""Generate a branch name for a {branch_type} branch in a {project_type} project.

The branch name should:
- Start with {branch_type}/
- Be descriptive and specific
- Use lowercase and hyphens
- Be 3-5 words after the prefix
- NOT be 'main', 'master', or generic like 'feature/improvement'

Technologies in project: {', '.join(project_info.get('technologies', [])[:5])}

Respond with ONLY the branch name, no explanation."""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in self.client.chat_stream(self.model, messages, context_name="branch_selection"):
            response += chunk
        
        branch_name = response.strip().lower().replace(' ', '-')
        
        # Sanitize and validate
        if not branch_name.startswith(f"{branch_type}/"):
            branch_name = f"{branch_type}/{branch_name}"
        
        # Remove any invalid characters
        branch_name = ''.join(c if c.isalnum() or c in ['-', '/'] else '-' for c in branch_name)
        
        # Ensure it's not a protected name
        if branch_name.split('/')[-1] in ['main', 'master', 'develop']:
            branch_name = f"{branch_type}/gitllama-enhancement"
        
        result = {
            'branch_name': branch_name,
            'action': 'CREATE',
            'reason': f"Creating new {branch_type} branch: {decision.get('reasoning', 'No suitable existing branch')}",
            'score': 0,
            'metadata': {
                'decision': decision,
                'branch_type': branch_type
            }
        }
        
        logger.info(f"    Created new branch name: {branch_name}")
        return result
    
    def _get_unique_commits(self, branch_name: str, max_commits: int = 10) -> List[str]:
        """Get unique commits for a branch compared to main/master.
        
        Args:
            branch_name: Name of the branch
            max_commits: Maximum number of commits to return
            
        Returns:
            List of unique commit messages
        """
        try:
            # Find the main branch
            main_branch = 'main'
            check_main = subprocess.run(
                ['git', 'rev-parse', '--verify', 'main'],
                capture_output=True,
                text=True,
                check=False
            )
            if check_main.returncode != 0:
                main_branch = 'master'
            
            # Skip if this is the main branch
            if branch_name in ['main', 'master']:
                return []
            
            # Get unique commits
            result = subprocess.run(
                ['git', 'log', f'{main_branch}..{branch_name}', '--oneline', f'-{max_commits}'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                return [c.split(' ', 1)[1] if ' ' in c else c for c in commits if c]
            
        except Exception as e:
            logger.debug(f"Could not get unique commits for {branch_name}: {e}")
        
        return []
    
    def _analyze_branch_vibe(self, branch_name: str, summary: Dict, unique_commits: List[str]) -> str:
        """Analyze the vibe of a branch based on its name, commits, and summary.
        
        Args:
            branch_name: Name of the branch
            summary: Branch analysis summary
            unique_commits: List of unique commit messages
            
        Returns:
            Vibe string: 'wip', 'experimental', 'feature', 'fix', 'stable', etc.
        """
        branch_lower = branch_name.lower()
        
        # Check branch name patterns
        if any(x in branch_lower for x in ['wip', 'draft', 'temp', 'test']):
            return 'wip'
        if any(x in branch_lower for x in ['experiment', 'poc', 'proto']):
            return 'experimental'
        if any(x in branch_lower for x in ['feature/', 'feat/', 'enhance']):
            return 'feature'
        if any(x in branch_lower for x in ['fix/', 'bugfix/', 'hotfix']):
            return 'fix'
        if any(x in branch_lower for x in ['docs/', 'documentation']):
            return 'documentation'
        
        # Check commit messages for WIP indicators
        if unique_commits:
            commit_text = ' '.join(unique_commits).lower()
            if any(x in commit_text for x in ['wip', 'work in progress', 'todo', 'fixme']):
                return 'wip'
            if any(x in commit_text for x in ['experiment', 'test', 'trying']):
                return 'experimental'
        
        # Check if branch has TODO.md changes
        if summary and summary.get('has_todo'):
            return 'feature'
        
        # Default based on activity
        if len(unique_commits) > 5:
            return 'active'
        elif len(unique_commits) > 0:
            return 'recent'
        
        return 'stable'