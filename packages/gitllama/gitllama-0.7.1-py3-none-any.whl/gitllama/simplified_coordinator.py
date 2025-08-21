"""
Simplified AI Coordinator for TODO-driven development
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from .ollama_client import OllamaClient
from .todo_analyzer import TodoAnalyzer
from .todo_planner import TodoPlanner
from .todo_executor import TodoExecutor

logger = logging.getLogger(__name__)


class SimplifiedCoordinator:
    """Coordinates the simplified TODO-driven workflow"""
    
    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434", git_url: Optional[str] = None):
        self.model = model
        self.client = OllamaClient(base_url)
        self.analyzer = TodoAnalyzer(self.client, model)
        self.planner = TodoPlanner(self.client, model)
        self.executor = TodoExecutor(self.client, model)
        
        # Initialize report generator if git_url provided
        self.report_generator = None
        if git_url:
            try:
                from .report_generator import ReportGenerator
                self.report_generator = ReportGenerator(git_url)
                logger.info("Report generator initialized")
            except ImportError as e:
                logger.warning(f"Report generation dependencies not available: {e}")
        
        logger.info(f"Initialized Simplified TODO-driven Coordinator with model: {model}")
    
    def run_todo_workflow(self, repo_path: Path) -> Dict:
        """Run the complete simplified workflow"""
        logger.info("=" * 60)
        logger.info("STARTING SIMPLIFIED TODO-DRIVEN WORKFLOW")
        logger.info("=" * 60)
        
        # Phase 1: Analyze repository with TODO focus
        logger.info("\n📝 PHASE 1: TODO-DRIVEN ANALYSIS")
        analysis = self.analyzer.analyze_with_todo(repo_path)
        logger.info(f"Analysis complete: {analysis['total_chunks']} chunks analyzed")
        
        # Phase 2: Create action plan
        logger.info("\n📋 PHASE 2: ACTION PLANNING")
        action_plan = self.planner.create_action_plan(analysis)
        logger.info(f"Plan created: {len(action_plan['files_to_modify'])} files to modify")
        logger.info(f"Branch: {action_plan['branch_name']}")
        
        # Phase 3: Execute plan
        logger.info("\n🚀 PHASE 3: EXECUTION")
        modified_files = self.executor.execute_plan(repo_path, action_plan)
        logger.info(f"Execution complete: {len(modified_files)} files modified")
        
        logger.info("=" * 60)
        logger.info("WORKFLOW COMPLETE")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "branch_name": action_plan['branch_name'],
            "modified_files": modified_files,
            "plan": action_plan['plan'],
            "analysis_summary": analysis['summary'],
            "todo_found": bool(analysis['todo_content'])
        }
    
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
        
        # Set executive summary for simplified workflow
        # Count decisions from AI query contexts
        from .context_manager import context_manager
        try:
            total_decisions = len([ctx for ctx in context_manager.contexts.values() 
                                 if 'open' in ctx.name or 'choice' in ctx.name])
        except (AttributeError, TypeError):
            total_decisions = 0
        
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
        # Estimate total tokens used from context manager
        try:
            estimated_tokens = sum(len(str(ctx.content)) // 4 
                                 for ctx in context_manager.contexts.values())
        except (AttributeError, TypeError):
            estimated_tokens = 0
        
        self.report_generator.set_model_info(
            model=self.model,
            context_window=context_size,
            total_tokens=estimated_tokens
        )
        
        # Add TODO-specific information to report
        if hasattr(self.report_generator, 'add_section'):
            self.report_generator.add_section(
                "TODO Analysis",
                "Simplified TODO-driven workflow was used to analyze the repository against TODO.md file."
            )
        
        # Generate and return the report
        report_path = self.report_generator.generate_report()
        logger.info(f"Report generated: {report_path}")
        return report_path