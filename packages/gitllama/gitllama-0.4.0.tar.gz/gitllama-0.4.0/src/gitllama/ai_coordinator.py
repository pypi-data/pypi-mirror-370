"""
AI Coordinator for GitLlama
Manages AI decision-making at each step of the git workflow
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .ollama_client import OllamaClient
from .project_analyzer import ProjectAnalyzer
from .branch_analyzer import BranchAnalyzer
from .ai_decision_formatter import AIDecisionFormatter
from .file_modifier import FileModifier

logger = logging.getLogger(__name__)


class AICoordinator:
    """Coordinates AI decisions throughout the git workflow"""
    
    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.client = OllamaClient(base_url)
        self.context_window = []
        
        # Initialize the analyzers and decision formatter
        self.project_analyzer = ProjectAnalyzer(self.client, model)
        self.branch_analyzer = BranchAnalyzer(self.client, model)
        self.decision_formatter = AIDecisionFormatter()
        self.file_modifier = FileModifier(self.client, model)
        
        logger.info(f"Initialized AI Coordinator with model: {model}")
    
    def explore_repository(self, repo_path: Path, analyze_all_branches: bool = False) -> Dict:
        """Explore the repository using the dedicated ProjectAnalyzer.
        
        This delegates the complex analysis to ProjectAnalyzer which handles:
        - Data gathering
        - Chunking
        - Parallel analysis
        - Hierarchical merging
        - Result formatting
        - Multi-branch analysis (if requested)
        
        Args:
            repo_path: Path to the repository
            analyze_all_branches: Whether to analyze all branches
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"AI Coordinator delegating repository exploration to ProjectAnalyzer")
        
        if analyze_all_branches:
            # Analyze all branches and store comprehensive results
            current_branch, branch_analyses = self.project_analyzer.analyze_all_branches(repo_path)
            
            # Store branch analyses for branch selection
            self.branch_analyses = branch_analyses
            self.current_branch = current_branch
            
            # Use current branch analysis as the main result
            analysis_result = branch_analyses.get(current_branch, {})
            analysis_result['all_branches'] = list(branch_analyses.keys())
            analysis_result['current_branch'] = current_branch
        else:
            # Single branch analysis
            analysis_result = self.project_analyzer.analyze_repository(repo_path)
            self.branch_analyses = None
            self.current_branch = None
        
        # Store in context window for future reference
        self.context_window.append({
            "type": "exploration",
            "analysis": analysis_result,
            "branch_analyses": self.branch_analyses if analyze_all_branches else None
        })
        
        return analysis_result
    
    def decide_branch_name(self, repo_path: Path, project_info: Dict) -> str:
        """AI decides on an appropriate branch name using BranchAnalyzer.
        
        This now uses the intelligent BranchAnalyzer which:
        - Analyzes existing branches
        - Evaluates reuse potential
        - Makes intelligent decisions about branch creation/reuse
        - Generates appropriate branch names
        
        Args:
            repo_path: Path to the repository
            project_info: Project analysis results
            
        Returns:
            Selected or generated branch name
        """
        logger.info("AI deciding on branch name using BranchAnalyzer")
        
        # If we have branch analyses from exploration, use them
        if hasattr(self, 'branch_analyses') and self.branch_analyses and hasattr(self, 'current_branch'):
            branch_summaries = self.branch_analyses
            current_branch = self.current_branch or 'main'  # Provide fallback if None
        else:
            # Fallback: analyze branches now if not done during exploration
            logger.info("Branch analyses not available, analyzing now...")
            current_branch, branch_summaries = self.project_analyzer.analyze_all_branches(repo_path)
        
        # Use BranchAnalyzer for intelligent branch selection
        selected_branch, reason, metadata = self.branch_analyzer.analyze_and_select_branch(
            repo_path, current_branch, project_info, branch_summaries
        )
        
        # Handle metadata which could be a dict or other type
        action = metadata.get('action', 'unknown') if isinstance(metadata, dict) else 'unknown'
        
        # Store decision in context
        self.context_window.append({
            "type": "branch_decision",
            "branch": selected_branch,
            "reason": reason,
            "action": action,
            "metadata": metadata
        })
        
        logger.info(f"AI selected branch: {selected_branch} (Action: {action})")
        logger.info(f"Reason: {reason}")
        
        return selected_branch
    
    def run_file_modification_workflow(self, repo_path: Path, project_info: Dict) -> Dict:
        """Run the complete file modification workflow using the new FileModifier."""
        logger.info("Running file modification workflow with AI decisions")
        
        # Use the FileModifier to handle the complete workflow
        result = self.file_modifier.run_full_modification_workflow(repo_path, project_info)
        
        # Store in context
        self.context_window.append({
            "type": "file_modification_workflow",
            "result": result
        })
        
        return result
    
    def decide_file_operations(self, repo_path: Path, project_info: Dict) -> List[Dict[str, str]]:
        """AI decides what file operations to perform using enhanced decision system."""
        logger.info("AI deciding on file operations with enhanced decision formatter")
        
        # Use the file modifier to select files with single-word decisions
        file_operations = self.file_modifier.select_files_to_modify(repo_path, project_info)
        
        # Convert to old format for compatibility
        converted_operations = []
        for op in file_operations:
            converted_operations.append({
                "operation": op["operation"],
                "file_path": op["file_path"],
                "content": op.get("content", ""),
                "reason": op.get("reason", "AI selected")
            })
        
        return converted_operations
    
    def decide_file_operations_legacy(self, repo_path: Path, project_info: Dict) -> List[Dict[str, str]]:
        """Legacy AI file operations method (kept for reference)."""
        logger.info("AI deciding on file operations (legacy method)")
        
        # Extract detailed information from the analysis
        project_type = project_info.get("project_type", "unknown")
        technologies = project_info.get("technologies", [])
        quality = project_info.get("quality", "unknown")
        patterns = project_info.get("patterns", [])
        has_todo = project_info.get("has_todo", False)
        synthesis = project_info.get("synthesis", {}) if isinstance(project_info.get("synthesis"), dict) else {}
        next_steps = project_info.get("next_steps", {}) if isinstance(project_info.get("next_steps"), dict) else {}
        guided_questions = project_info.get("guided_questions", []) if isinstance(project_info.get("guided_questions"), list) else []
        
        # Build a comprehensive context including synthesis
        context_summary = f"""Project Analysis Summary:
- Type: {project_type}
- Technologies: {', '.join(technologies[:10]) if technologies else 'none detected'}
- Code Quality: {quality}
- Key Patterns: {', '.join(patterns[:5]) if patterns else 'none detected'}
- Total Files: {project_info.get('analysis_metadata', {}).get('total_files', 0)}
- Has TODO.md: {has_todo}

AI Synthesis & Next Steps:
- Next Priority: {synthesis.get('next_priority', 'Continue development')}
- Recommended Branch: {synthesis.get('recommended_branch', 'unknown')}
- Immediate Tasks: {', '.join(synthesis.get('immediate_tasks', []))}
- Development Direction: {synthesis.get('development_direction', 'unknown')}

Recent Guided Questions & Insights:
{self._summarize_guided_questions(guided_questions)}

Previous decisions:
{json.dumps(self.context_window[-2:], indent=2) if len(self.context_window) > 1 else 'None'}"""
        
        logger.info(f"🤖 AI: Deciding file operations based on project analysis")
        
        prompt = f"""{context_summary}

Based on this comprehensive project analysis and AI synthesis, suggest ONE meaningful file operation that aligns with the identified next priority and immediate tasks.

Prioritize operations that:
1. Address the identified next priority: {synthesis.get('next_priority', 'general improvement')}
2. Support the immediate tasks: {', '.join(synthesis.get('immediate_tasks', []))}
3. Align with the development direction: {synthesis.get('development_direction', 'unknown')}
4. Consider TODO.md guidance if available

Consider:
1. What documentation might be missing?
2. What configuration could be improved?
3. What utility or helper might be useful?
4. What test or example might add value?

Choose one operation:
- CREATE a new file (documentation, config, utility, test, example)
- MODIFY an existing file (improve code, fix issues, enhance features)
- DELETE an unnecessary file

Respond in JSON format:
{{
    "operation": "CREATE|MODIFY|DELETE",
    "file_path": "path/to/file",
    "content": "file content here (for CREATE/MODIFY)",
    "reason": "brief explanation of why this improves the project"
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
            logger.info(f"AI decided on operation: {operation['operation']} {operation['file_path']}")
            return [operation]
        except json.JSONDecodeError:
            # Fallback: create a project insights file
            fallback = {
                "operation": "CREATE",
                "file_path": "PROJECT_INSIGHTS.md",
                "content": f"""# Project Insights

Generated by GitLlama AI Analysis

## Project Type
{project_type}

## Technologies Detected
{chr(10).join('- ' + tech for tech in technologies[:10]) if technologies else '- None detected'}

## Code Quality Assessment
{quality if quality else 'Not assessed'}

## Key Patterns
{chr(10).join('- ' + pattern for pattern in patterns[:5]) if patterns else '- None detected'}

## Potential Improvements
- [ ] Add comprehensive documentation
- [ ] Improve test coverage
- [ ] Optimize performance bottlenecks
- [ ] Enhance error handling
- [ ] Update dependencies

---
*This file was automatically generated based on AI analysis of the repository.*
""",
                "reason": "Document AI insights and improvement suggestions"
            }
            self.context_window.append({
                "type": "file_operation",
                "operation": fallback
            })
            logger.info("AI fallback: creating PROJECT_INSIGHTS.md")
            return [fallback]
    
    def generate_commit_message(self, operations: List[Dict[str, str]]) -> str:
        """AI generates a commit message based on the operations performed and synthesis."""
        logger.info("AI generating commit message")
        
        # Get project context from exploration
        project_context = None
        for ctx in self.context_window:
            if ctx.get('type') == 'exploration':
                project_context = ctx.get('analysis', {})
                break
        
        project_type = project_context.get('project_type', 'project') if project_context else 'project'
        synthesis = project_context.get('synthesis', {}) if project_context else {}
        next_priority = synthesis.get('next_priority', '')
        
        logger.info(f"🤖 AI: Generating commit message for {len(operations)} operations")
        
        prompt = f"""Generate a concise, professional git commit message for these operations:
{json.dumps(operations, indent=2)}

Project type: {project_type}
Next Priority: {next_priority}

Follow conventional commit format (feat:, fix:, docs:, chore:, etc.)
Keep it under 72 characters.
Be specific about what was done.
{f'Consider that this aligns with: {next_priority}' if next_priority else ''}

Respond with ONLY the commit message, no explanation."""
        
        messages = [{"role": "user", "content": prompt}]
        response = ""
        for chunk in self.client.chat_stream(self.model, messages):
            response += chunk
        
        commit_message = response.strip()
        
        # Validate and fallback if necessary
        if not commit_message or len(commit_message) > 72:
            if operations and operations[0].get('operation') == 'CREATE':
                file_name = Path(operations[0]['file_path']).name
                commit_message = f"feat: add {file_name}"
            elif operations and operations[0].get('operation') == 'MODIFY':
                file_name = Path(operations[0]['file_path']).name
                commit_message = f"fix: update {file_name}"
            else:
                commit_message = "chore: automated improvements by GitLlama"
        
        self.context_window.append({
            "type": "commit_message",
            "message": commit_message
        })
        
        logger.info(f"AI generated commit message: {commit_message}")
        return commit_message
    
    def execute_file_operations(self, repo_path: Path, operations: List[Dict[str, str]]) -> List[str]:
        """Execute the file operations decided by the AI."""
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
    
    def _summarize_guided_questions(self, guided_questions: List[Dict]) -> str:
        """Summarize the guided questions and answers for context.
        
        Args:
            guided_questions: List of guided question dictionaries
            
        Returns:
            Formatted summary string
        """
        if not guided_questions:
            return "No guided questions available"
        
        summary_lines = []
        for i, qa in enumerate(guided_questions[-3:], 1):  # Last 3 questions
            question = qa.get('question', 'Unknown question')
            answer = qa.get('answer', 'No answer')[:100]  # Truncate long answers
            if len(qa.get('answer', '')) > 100:
                answer += '...'
            summary_lines.append(f"{i}. Q: {question}\n   A: {answer}")
        
        return "\n".join(summary_lines)