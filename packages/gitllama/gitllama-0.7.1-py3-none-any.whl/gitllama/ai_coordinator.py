"""
AI Coordinator for GitLlama
Manages AI decision-making at each step of the git workflow
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .ollama_client import OllamaClient
from .ai_query import AIQuery  # New simple interface
from .project_analyzer import ProjectAnalyzer
from .branch_analyzer import BranchAnalyzer
from .ai_decision_formatter import AIDecisionFormatter
from .file_modifier import FileModifier
from .report_generator import ReportGenerator
from .context_manager import context_manager
from .ai_output_parser import ai_output_parser

logger = logging.getLogger(__name__)


class AICoordinator:
    """Coordinates AI decisions throughout the git workflow"""
    
    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434", repo_url: str = None):
        self.model = model
        self.client = OllamaClient(base_url)
        self.ai = AIQuery(self.client, model)  # NEW: Simple query interface
        # Remove old context_window, now using context_manager
        # self.context_window = []
        
        # Initialize report generator if repo_url is provided
        self.report_generator = None
        if repo_url:
            self.report_generator = ReportGenerator(repo_url)
        
        # Initialize the analyzers and decision formatter with report generator
        self.project_analyzer = ProjectAnalyzer(self.client, model, self.report_generator)
        self.branch_analyzer = BranchAnalyzer(self.client, model, self.report_generator)
        self.decision_formatter = AIDecisionFormatter(self.report_generator)
        self.file_modifier = FileModifier(self.client, model, self.report_generator)
        
        logger.info(f"Initialized AI Coordinator with model: {model}")
        if self.report_generator:
            logger.info("Report generation enabled")
    
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
        
        # Store in context manager for future reference
        context_content = json.dumps({
            "type": "exploration",
            "analysis": analysis_result,
            "branch_analyses": self.branch_analyses if analyze_all_branches else None
        }, indent=2)
        context_manager.get_or_create_context("repository_exploration", context_content)
        
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
        
        # Store decision in context manager
        context_content = json.dumps({
            "type": "branch_decision",
            "branch": selected_branch,
            "reason": reason,
            "action": action,
            "metadata": metadata
        }, indent=2)
        context_manager.get_or_create_context("branch_decision", context_content)
        
        logger.info(f"AI selected branch: {selected_branch} (Action: {action})")
        logger.info(f"Reason: {reason}")
        
        return selected_branch
    
    def run_file_modification_workflow(self, repo_path: Path, project_info: Dict) -> Dict:
        """Run the complete file modification workflow using the new FileModifier."""
        logger.info("Running file modification workflow with AI decisions")
        
        # Use the FileModifier to handle the complete workflow
        result = self.file_modifier.run_full_modification_workflow(repo_path, project_info)
        
        # Store in context manager
        context_content = json.dumps({
            "type": "file_modification_workflow",
            "result": result
        }, indent=2)
        context_manager.get_or_create_context("file_modification_workflow", context_content)
        
        return result
    
    def decide_file_operations(self, repo_path: Path, project_info: Dict) -> List[Dict[str, str]]:
        """AI decides what file operations to perform using simple interface."""
        logger.info("AI deciding on file operations")
        
        # Use simple choice for operation type
        operation_result = self.ai.choice(
            question="What file operation should we perform?",
            options=["CREATE a new file", "MODIFY an existing file", "DELETE an unnecessary file"],
            context=f"Project type: {project_info.get('project_type', 'unknown')}"
        )
        
        operation = operation_result.value.split()[0]  # Extract CREATE/MODIFY/DELETE
        
        # Use choice for file type
        file_type_result = self.ai.choice(
            question=f"What type of file should we {operation.lower()}?",
            options=["documentation", "configuration", "code", "test", "build script"],
            context=f"Project: {project_info.get('project_type', 'unknown')}"
        )
        
        # Map to file path
        file_paths = {
            "documentation": "docs/AI_NOTES.md",
            "configuration": "config.json", 
            "code": "src/feature.py",
            "test": "tests/test_feature.py",
            "build script": "Makefile"
        }
        
        file_path = file_paths.get(file_type_result.value, "file.txt")
        
        # Generate content if needed
        content = ""
        if operation in ["CREATE", "MODIFY"]:
            content_result = self.ai.open(
                prompt=f"Generate complete content for {file_path}. Wrap in markdown code blocks.",
                context=f"Project type: {project_info.get('project_type', 'unknown')}"
            )
            
            # Extract code from response
            from .response_parser import ResponseParser
            parser = ResponseParser()
            content = parser.extract_code(content_result.content)
        
        logger.info(f"AI decided: {operation} {file_path}")
        
        return [{
            "operation": operation,
            "file_path": file_path,
            "content": content,
            "reason": f"{operation_result.value} - {file_type_result.value}"
        }]
    
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
{context_manager.get_context_content("branch_decision") if context_manager.get_context_content("branch_decision") else 'None'}"""
        
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
    "content": "For CREATE/MODIFY: wrap complete file content in markdown code blocks with appropriate language identifier, e.g. ```python\\n# content here\\n```",
    "reason": "brief explanation of why this improves the project"
}}"""
        
        # Use context manager for this AI call
        context_manager.use_context("file_operations_decision", "Deciding file operations based on project analysis")
        
        result = self.ai.open(
            prompt=prompt,
            context="",
            context_name="file_operations_decision"
        )
        response = result.raw
        
        try:
            operation = json.loads(response)
            # Store operation in context manager
            context_content = json.dumps({
                "type": "file_operation",
                "operation": operation
            }, indent=2)
            context_manager.get_or_create_context("file_operation_result", context_content)
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
            # Store fallback operation in context manager
            fallback_content = json.dumps({
                "type": "file_operation",
                "operation": fallback
            }, indent=2)
            context_manager.get_or_create_context("file_operation_fallback", fallback_content)
            logger.info("AI fallback: creating PROJECT_INSIGHTS.md")
            return [fallback]
    
    def generate_commit_message(self, operations: List[Dict[str, str]]) -> str:
        """AI generates a commit message using simple interface."""
        logger.info("AI generating commit message")
        
        # Use choice for commit type
        type_result = self.ai.choice(
            question="What type of commit is this?",
            options=["feat", "fix", "docs", "chore", "refactor"],
            context=f"Operations: {[op['operation'] + ' ' + op['file_path'] for op in operations]}"
        )
        
        # Generate message content
        msg_result = self.ai.open(
            prompt="Generate a short commit message (max 50 chars). Just the message, no explanation.",
            context=f"Commit type: {type_result.value}, Files: {[op['file_path'] for op in operations]}"
        )
        
        message = f"{type_result.value}: {msg_result.content.strip()}"
        return message[:72]  # Ensure max length
    
    def execute_file_operations(self, repo_path: Path, operations: List[Dict[str, str]]) -> List[str]:
        """Execute the file operations decided by the AI."""
        modified_files = []
        
        for op in operations:
            file_path = repo_path / op['file_path']
            
            if op['operation'] == 'CREATE':
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Parse AI output for clean content
                raw_content = op.get('content', '')
                parse_result = ai_output_parser.parse_for_file_content(raw_content, op['file_path'])
                
                with open(file_path, 'w') as f:
                    f.write(parse_result.content)
                
                emoji = ai_output_parser.get_trimming_emoji_indicator(parse_result)
                logger.info(f"Created file: {op['file_path']} {emoji}")
                modified_files.append(op['file_path'])
                
            elif op['operation'] == 'MODIFY':
                if file_path.exists():
                    # Parse AI output for clean content
                    raw_content = op.get('content', '')
                    parse_result = ai_output_parser.parse_for_file_content(raw_content, op['file_path'])
                    
                    with open(file_path, 'w') as f:
                        f.write(parse_result.content)
                    
                    emoji = ai_output_parser.get_trimming_emoji_indicator(parse_result)
                    logger.info(f"Modified file: {op['file_path']} {emoji}")
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
    
    def generate_final_report(self, repo_path: str, branch: str, modified_files: List[str], 
                             commit_hash: str, success: bool) -> Optional[Path]:
        """Generate the final HTML report if report generator is available.
        
        Args:
            repo_path: Path to the repository
            branch: Selected branch name
            modified_files: List of modified file paths
            commit_hash: Git commit hash
            success: Whether the workflow was successful
            
        Returns:
            Path to generated report or None if no report generator
        """
        if not self.report_generator:
            return None
        
        logger.info("Generating final HTML report...")
        
        # Set executive summary
        total_decisions = sum(len(analyzer.decision_formatter.decision_history) 
                            for analyzer in [self.branch_analyzer, self.file_modifier]
                            if hasattr(analyzer, 'decision_formatter'))
        
        self.report_generator.set_executive_summary(
            repo_path=repo_path,
            branch=branch,
            modified_files=modified_files,
            commit_hash=commit_hash,
            success=success,
            total_decisions=total_decisions
        )
        
        # Set model information
        context_size = self.client.get_model_context_size(self.model)
        # Estimate total tokens used (this would be more accurate with actual tracking)
        estimated_tokens = sum(analyzer.usable_context_size for analyzer in [self.project_analyzer] 
                             if hasattr(analyzer, 'usable_context_size'))
        
        self.report_generator.set_model_info(
            model=self.model,
            context_window=context_size,
            total_tokens=estimated_tokens
        )
        
        # Generate and return the report
        report_path = self.report_generator.generate_report()
        logger.info(f"Report generated: {report_path}")
        return report_path