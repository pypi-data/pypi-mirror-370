"""
Report Generator for GitLlama
Professional HTML report system for AI decision transparency
"""

import logging
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from .context_manager import context_manager
from . import __version__

try:
    from jinja2 import Template
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    REPORT_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    REPORT_DEPENDENCIES_AVAILABLE = False
    Template = None
    highlight = None
    get_lexer_by_name = None
    guess_lexer = None
    HtmlFormatter = None
    ClassNotFound = Exception  # Fallback
    logger = logging.getLogger(__name__)
    logger.warning(f"Report generation dependencies not available: {e}. Install with: pip install jinja2 pygments")

logger = logging.getLogger(__name__)


class LogCaptureHandler(logging.Handler):
    """Custom logging handler to capture all logs during GitLlama execution."""
    
    def __init__(self, report_generator):
        super().__init__()
        self.report_generator = report_generator
        self.setLevel(logging.DEBUG)
        
    def emit(self, record):
        """Capture log record and store in report generator."""
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.thread,
                "process": record.process
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.format(record)
            
            self.report_generator.add_log_entry(log_entry)
        except Exception:
            # Don't let logging failures break the application
            pass


class ReportGenerator:
    """Generates professional HTML reports for GitLlama execution"""
    
    def __init__(self, repo_url: str, output_dir: str = "gitllama_reports"):
        """Initialize the report generator.
        
        Args:
            repo_url: URL of the repository being analyzed
            output_dir: Directory to save reports in
        """
        self.repo_url = repo_url
        self.output_dir = Path(output_dir)
        self.start_time = datetime.now()
        self.timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Data collection structures
        self.executive_summary = {}
        self.repository_analysis = {
            "phases": [],
            "timeline": []
        }
        self.ai_decisions = []
        self.guided_questions = []
        self.branch_analysis = {
            "discovered_branches": [],
            "evaluation_scores": {},
            "selection_reasoning": "",
            "final_selection": ""
        }
        self.file_operations = []
        self.metrics = {
            "processing_times": {},
            "token_usage": {},
            "ai_calls": 0,
            "model_info": {},
            "context_windows": {
                "total_count": 0,
                "total_memory_gb": 0.0,
                "contexts": {}
            }
        }
        
        # Log capture system
        self.logs = []
        self.log_handler = LogCaptureHandler(self)
        self.log_summary = ""
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup log capture after initialization
        self._setup_log_capture()
        
        logger.info(f"ReportGenerator initialized for {repo_url}")
    
    def start_phase(self, phase_name: str, description: str):
        """Start tracking a new phase of execution."""
        phase_data = {
            "name": phase_name,
            "description": description,
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None,
            "details": []
        }
        self.repository_analysis["phases"].append(phase_data)
        logger.debug(f"Started phase: {phase_name}")
    
    def end_phase(self, phase_name: str):
        """End tracking of the current phase."""
        for phase in reversed(self.repository_analysis["phases"]):
            if phase["name"] == phase_name and phase["end_time"] is None:
                phase["end_time"] = datetime.now()
                phase["duration"] = (phase["end_time"] - phase["start_time"]).total_seconds()
                self.metrics["processing_times"][phase_name] = phase["duration"]
                logger.debug(f"Ended phase: {phase_name} ({phase['duration']:.2f}s)")
                break
    
    def add_phase_detail(self, phase_name: str, detail: str):
        """Add a detail to the current phase."""
        for phase in reversed(self.repository_analysis["phases"]):
            if phase["name"] == phase_name:
                phase["details"].append({
                    "timestamp": datetime.now(),
                    "detail": detail
                })
                break
    
    def add_guided_question(self, question: str, context: str, answer: str, confidence: Optional[float] = None):
        """Add a guided question and answer to the report."""
        qa_data = {
            "timestamp": datetime.now(),
            "question": question,
            "context": context[:200] + "..." if len(context) > 200 else context,
            "answer": answer,
            "confidence": confidence,
            "type": "guided_question"
        }
        self.guided_questions.append(qa_data)
        logger.debug(f"Added guided Q&A: {question[:50]}...")
    
    
    def add_branch_discovery(self, branches: List[str]):
        """Add discovered branches to the report."""
        self.branch_analysis["discovered_branches"] = branches
        logger.debug(f"Added {len(branches)} discovered branches")
    
    def add_branch_evaluation(self, branch_name: str, score: int, reasons: List[str]):
        """Add branch evaluation scoring."""
        self.branch_analysis["evaluation_scores"][branch_name] = {
            "score": score,
            "reasons": reasons
        }
        logger.debug(f"Added branch evaluation for {branch_name}: {score}")
    
    def set_branch_selection(self, selected_branch: str, reasoning: str, action: str):
        """Set the final branch selection."""
        self.branch_analysis["final_selection"] = selected_branch
        self.branch_analysis["selection_reasoning"] = reasoning
        self.branch_analysis["action"] = action
        logger.debug(f"Set branch selection: {selected_branch} ({action})")
    
    def add_branch_todo_analysis(self, todo_contents: Dict, comparison: str, branches_with_todos: List[str]):
        """Add TODO.md analysis across branches."""
        self.branch_analysis["todo_analysis"] = {
            "todo_contents": todo_contents,
            "ai_comparison": comparison,
            "branches_with_todos": branches_with_todos,
            "total_branches_analyzed": len(todo_contents),
            "branches_with_todos_count": len(branches_with_todos)
        }
        logger.debug(f"Added TODO analysis for {len(branches_with_todos)} branches with TODO.md")
    
    def add_timeline_event(self, event_name: str, description: str):
        """Add an event to the timeline."""
        if "timeline_events" not in self.branch_analysis:
            self.branch_analysis["timeline_events"] = []
        
        self.branch_analysis["timeline_events"].append({
            "timestamp": datetime.now(),
            "event": event_name,
            "description": description
        })
        logger.debug(f"Added timeline event: {event_name}")
    
    def _setup_log_capture(self):
        """Setup log capture for the entire GitLlama session."""
        # Add handler to the gitllama root logger to capture all module logs
        gitllama_logger = logging.getLogger('gitllama')
        gitllama_logger.addHandler(self.log_handler)
        
        # Also add to src.gitllama for imports
        src_gitllama_logger = logging.getLogger('src.gitllama')
        src_gitllama_logger.addHandler(self.log_handler)
    
    def add_log_entry(self, log_entry: Dict):
        """Add a log entry to the capture list."""
        self.logs.append(log_entry)
    
    def _generate_log_summary(self):
        """Generate AI summary of all captured logs."""
        if not self.logs:
            return "No logs captured during execution."
        
        # Try to get an AI client for log analysis
        log_analysis_client = getattr(self, '_ai_client', None)
        if not log_analysis_client:
            return self._generate_basic_log_summary()
        
        # Group logs by level and module for analysis
        log_stats = self._analyze_log_statistics()
        
        # Sample representative logs for AI analysis
        sample_logs = self._sample_logs_for_analysis()
        
        prompt = f"""Analyze the GitLlama execution logs and provide a concise executive summary. Focus on:

1. **Overall Execution Health**: Were there any critical issues or warnings?
2. **Key Activities**: What major operations were performed?
3. **Performance Insights**: Any notable timing or efficiency observations?
4. **Error Analysis**: Summary of any errors or warnings and their impact
5. **Success Indicators**: Evidence of successful completion

LOG STATISTICS:
- Total logs captured: {len(self.logs)}
- Error logs: {log_stats['ERROR']}
- Warning logs: {log_stats['WARNING']}
- Info logs: {log_stats['INFO']}
- Debug logs: {log_stats['DEBUG']}
- Most active modules: {', '.join(log_stats['top_modules'][:5])}

REPRESENTATIVE LOG SAMPLES:
{sample_logs}

Provide a concise 3-4 sentence executive summary focusing on execution health and key activities:"""

        try:
            # Use the AI client to analyze logs
            messages = [{"role": "user", "content": prompt}]
            response = ""
            
            for chunk in log_analysis_client.chat_stream("gemma3:4b", messages, context_name="log_analysis"):
                response += chunk
            
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate AI log summary: {e}")
            return self._generate_basic_log_summary()
    
    def _analyze_log_statistics(self) -> Dict:
        """Analyze log statistics for summary generation."""
        stats = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0}
        module_counts = {}
        
        for log in self.logs:
            level = log.get("level", "UNKNOWN")
            module = log.get("logger", "unknown")
            
            if level in stats:
                stats[level] += 1
            
            module_counts[module] = module_counts.get(module, 0) + 1
        
        # Get top modules by activity
        top_modules = sorted(module_counts.keys(), key=lambda x: module_counts[x], reverse=True)
        stats["top_modules"] = top_modules
        
        return stats
    
    def _sample_logs_for_analysis(self, max_logs: int = 20) -> str:
        """Sample representative logs for AI analysis."""
        if len(self.logs) <= max_logs:
            sampled = self.logs
        else:
            # Sample logs: all errors/warnings + representative info/debug
            priority_logs = [log for log in self.logs if log.get("level") in ["ERROR", "WARNING"]]
            other_logs = [log for log in self.logs if log.get("level") not in ["ERROR", "WARNING"]]
            
            # Take all priority logs + sample from others
            remaining_slots = max_logs - len(priority_logs)
            if remaining_slots > 0 and other_logs:
                step = max(1, len(other_logs) // remaining_slots)
                sampled = priority_logs + other_logs[::step][:remaining_slots]
            else:
                sampled = priority_logs[:max_logs]
        
        # Format logs for analysis
        log_lines = []
        for log in sampled:
            timestamp = log["timestamp"].strftime("%H:%M:%S")
            level = log["level"]
            module = log["logger"]
            message = log["message"][:100] + ("..." if len(log["message"]) > 100 else "")
            log_lines.append(f"[{timestamp}] {level} {module}: {message}")
        
        return "\n".join(log_lines)
    
    def _generate_basic_log_summary(self) -> str:
        """Generate basic log summary without AI analysis."""
        stats = self._analyze_log_statistics()
        
        total_logs = len(self.logs)
        errors = stats['ERROR']
        warnings = stats['WARNING']
        
        if errors > 0:
            health = "❌ Issues detected"
        elif warnings > 0:
            health = "⚠️ Minor warnings"
        else:
            health = "✅ Clean execution"
        
        return f"GitLlama execution completed with {total_logs} log entries. {health}. " \
               f"Captured {errors} errors and {warnings} warnings across {len(stats['top_modules'])} modules."
    
    def add_file_operation(self, operation: str, file_path: str, reason: str, 
                          content: str = "", diff: str = "", trimmed: bool = False, 
                          trimming_details: str = ""):
        """Add a file operation to the report."""
        operation_data = {
            "timestamp": datetime.now(),
            "operation": operation,
            "file_path": file_path,
            "reason": reason,
            "content_preview": content[:2000] if content else "",
            "diff": diff,
            "highlighted_content": self._highlight_code(content, file_path) if content else "",
            "was_trimmed": trimmed,
            "trimming_details": trimming_details,
            "trimming_emoji": "✂️" if trimmed else "📄"
        }
        self.file_operations.append(operation_data)
        logger.debug(f"Added file operation: {operation} {file_path}")
    
    def add_ai_decision(self, decision_type: str, decision: str, context: str = ""):
        """Add an AI decision to the report."""
        decision_data = {
            "timestamp": datetime.now(),
            "type": decision_type,
            "decision": decision,
            "context": context
        }
        
        # Store in AI decisions list (create if doesn't exist)
        if not hasattr(self, 'ai_decisions'):
            self.ai_decisions = []
        
        self.ai_decisions.append(decision_data)
        logger.debug(f"Added AI decision: {decision_type} -> {decision}")
    
    def set_iteration_history(self, iteration_history: List[Dict], total_iterations: int, files_attempted: int):
        """Set the iteration history for the iterative workflow."""
        self.iteration_history = iteration_history
        self.total_iterations = total_iterations
        self.files_attempted = files_attempted
        logger.debug(f"Set iteration history: {total_iterations} iterations, {files_attempted} files attempted")
    
    def set_ai_client(self, client):
        """Set the AI client for log analysis."""
        self._ai_client = client
    
    def set_executive_summary(self, repo_path: str, branch: str, modified_files: List[str], 
                            commit_hash: str, success: bool, total_decisions: int):
        """Set the executive summary data."""
        total_workflow_time = (datetime.now() - self.start_time).total_seconds()
        tracked_phases_time = sum(self.metrics["processing_times"].values())
        untracked_time = max(0, total_workflow_time - tracked_phases_time)
        
        # Add untracked time to metrics
        if untracked_time > 0:
            self.metrics["processing_times"]["File Operations & Git"] = untracked_time
        
        # Generate log summary
        self.log_summary = self._generate_log_summary()
        
        self.executive_summary = {
            "repo_url": self.repo_url,
            "repo_path": repo_path,
            "branch_selected": branch,
            "files_modified": modified_files,
            "commit_hash": commit_hash,
            "success": success,
            "total_ai_decisions": total_decisions,
            "total_guided_questions": len(self.guided_questions),
            "total_file_operations": len(self.file_operations),
            "execution_time": total_workflow_time,
            "log_summary": self.log_summary,
            "total_logs_captured": len(self.logs)
        }
        logger.debug("Set executive summary data")
    
    def set_model_info(self, model: str, context_window: int, total_tokens: int):
        """Set model and token usage information."""
        self.metrics["model_info"] = {
            "model": model,
            "context_window": context_window,
            "total_tokens": total_tokens
        }
        self.metrics["token_usage"]["total"] = total_tokens
        
        # Update context window metrics from context manager
        context_summary = context_manager.get_context_summary()
        self.metrics["context_windows"] = {
            "total_count": context_summary["total_contexts"],
            "total_memory_gb": context_summary["total_memory_gb"],
            "total_api_calls": context_summary["total_api_calls"],
            "contexts": context_summary["contexts"],
            "api_call_log": context_summary["api_calls"]
        }
        
        logger.debug(f"Set model info: {model} ({total_tokens} tokens, {context_summary['total_contexts']} context windows)")
    
    def _highlight_code(self, content: str, file_path: str) -> str:
        """Apply syntax highlighting to code content."""
        try:
            if file_path:
                lexer = get_lexer_by_name(Path(file_path).suffix[1:] if Path(file_path).suffix else 'text')
            else:
                lexer = guess_lexer(content)
            
            formatter = HtmlFormatter(style='github', cssclass='highlight', noclasses=True)
            return highlight(content, lexer, formatter)
        except ClassNotFound:
            # Fallback to plain text with HTML escaping
            return f'<pre style="background: #f8f8f8; padding: 10px; border-radius: 4px;">{self._escape_html(content)}</pre>'
        except Exception as e:
            logger.debug(f"Syntax highlighting failed: {e}")
            return f'<pre style="background: #f8f8f8; padding: 10px; border-radius: 4px;">{self._escape_html(content)}</pre>'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def generate_report(self, auto_open: bool = True) -> Path:
        """Generate the final HTML report."""
        if not REPORT_DEPENDENCIES_AVAILABLE:
            logger.error("Cannot generate report: missing dependencies (jinja2, pygments)")
            logger.info("Install with: pip install jinja2 pygments")
            
            # Generate a simple fallback report
            return self._generate_fallback_report()
        
        logger.info("Generating HTML report...")
        
        # Prepare template data
        template_data = {
            "timestamp": self.timestamp,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "executive_summary": self.executive_summary,
            "repository_analysis": self.repository_analysis,
            "guided_questions": self.guided_questions,
            "ai_decisions": getattr(self, 'ai_decisions', []),
            "branch_analysis": self.branch_analysis,
            "file_operations": self.file_operations,
            "metrics": self.metrics,
            "iteration_history": getattr(self, 'iteration_history', []),
            "total_iterations": getattr(self, 'total_iterations', 0),
            "files_attempted": getattr(self, 'files_attempted', 0),
            "gitllama_version": __version__
        }
        
        # Generate HTML
        html_content = self._render_html_template(template_data)
        
        # Save HTML report
        html_filename = f"gitllama_report_{self.timestamp}.html"
        html_path = self.output_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Also save as latest.html for easy access
        latest_path = self.output_dir / "latest.html"
        self._save_as_latest(html_content, latest_path, html_filename)
        
        # Generate companion Markdown report
        md_content = self._render_markdown_template(template_data)
        md_filename = f"gitllama_report_{self.timestamp}.md"
        md_path = self.output_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Reports generated: {html_path}")
        
        # Generate detailed logs report if we have logs
        if self.logs:
            logs_path = self._generate_logs_report()
            logger.info(f"Detailed logs report: {logs_path}")
            
            # Also save logs as latest_logs.html for easy access
            latest_logs_path = self.output_dir / "latest_logs.html"
            with open(logs_path, 'r', encoding='utf-8') as f:
                logs_content = f.read()
            self._save_as_latest(logs_content, latest_logs_path, logs_path.name)
        
        # Auto-open in browser
        if auto_open:
            try:
                webbrowser.open(f'file://{html_path.absolute()}')
                logger.info("Report opened in browser")
            except Exception as e:
                logger.warning(f"Could not auto-open report: {e}")
        
        return html_path
    
    def _generate_logs_report(self) -> Path:
        """Generate detailed logs HTML report with filtering capabilities."""
        logs_html = self._get_logs_html_template()
        
        # Organize logs by level and module
        logs_by_level = {"ERROR": [], "WARNING": [], "INFO": [], "DEBUG": []}
        logs_by_module = {}
        
        for log in self.logs:
            level = log.get("level", "UNKNOWN")
            module = log.get("logger", "unknown")
            
            if level in logs_by_level:
                logs_by_level[level].append(log)
            
            if module not in logs_by_module:
                logs_by_module[module] = []
            logs_by_module[module].append(log)
        
        # Get statistics
        stats = self._analyze_log_statistics()
        
        template_data = {
            "timestamp": self.timestamp,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "repo_url": self.repo_url,
            "logs": self.logs,
            "logs_by_level": logs_by_level,
            "logs_by_module": logs_by_module,
            "stats": stats,
            "log_summary": self.log_summary
        }
        
        # Render template
        template = Template(logs_html)
        html_content = template.render(**template_data)
        
        # Save logs HTML
        logs_filename = f"gitllama_logs_{self.timestamp}.html"
        logs_path = self.output_dir / logs_filename
        
        with open(logs_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return logs_path
    
    def _save_as_latest(self, html_content: str, latest_path: Path, original_filename: str):
        """Save report as latest.html with embedded original filename for recovery."""
        # Extract the timestamp from the original filename
        timestamp_match = original_filename.replace('gitllama_report_', '').replace('.html', '')
        
        # Create metadata comment to embed in HTML
        metadata_comment = f"""<!--
GitLlama Latest Report Metadata
===============================
Original Filename: {original_filename}
Timestamp: {timestamp_match}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file is a copy of the timestamped report for easy access.
To recover the original filename, extract from this comment or use:
grep -o 'Original Filename: [^"]*' latest.html
===============================
-->"""
        
        # Insert metadata comment right after the opening <html> tag
        if '<html' in html_content:
            # Find the position after the <html> tag
            html_start = html_content.find('<html')
            html_end = html_content.find('>', html_start) + 1
            
            # Insert metadata comment
            modified_content = (
                html_content[:html_end] + 
                '\n' + metadata_comment + '\n' + 
                html_content[html_end:]
            )
        else:
            # Fallback: prepend comment to the beginning
            modified_content = metadata_comment + '\n' + html_content
        
        # Write the latest.html file
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        logger.info(f"Saved latest report: {latest_path} (original: {original_filename})")
    
    def get_original_filename_from_latest(self, latest_path: Path) -> str:
        """Extract the original filename from a latest.html file."""
        try:
            with open(latest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for the metadata comment
            if 'Original Filename:' in content:
                import re
                match = re.search(r'Original Filename: ([^\n\r]+)', content)
                if match:
                    return match.group(1).strip()
            
            # Fallback: couldn't find metadata
            return "unknown_timestamp.html"
            
        except Exception as e:
            logger.warning(f"Could not extract original filename from {latest_path}: {e}")
            return "unknown_timestamp.html"
    
    def _render_html_template(self, data: Dict[str, Any]) -> str:
        """Render the HTML template with data."""
        template = Template(self._get_html_template())
        return template.render(**data)
    
    def _render_markdown_template(self, data: Dict[str, Any]) -> str:
        """Render the Markdown template with data."""
        template = Template(self._get_markdown_template())
        return template.render(**data)
    
    def _get_html_template(self) -> str:
        """Get the HTML template string."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitLlama Report - {{ timestamp }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; color: #333; background: #f5f7fa;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        .section { 
            background: white; padding: 2rem; margin-bottom: 1.5rem; 
            border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }
        .section h2 { 
            color: #2d3748; border-bottom: 3px solid #667eea; 
            padding-bottom: 0.5rem; margin-bottom: 1.5rem; font-size: 1.8rem;
        }
        .executive-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; margin-bottom: 2rem;
        }
        .metric-card { 
            background: #f8fafc; padding: 1.5rem; border-radius: 8px; 
            border-left: 4px solid #667eea; text-align: center;
        }
        .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
        .metric-label { color: #64748b; text-transform: uppercase; font-size: 0.85rem; }
        .timeline { position: relative; padding: 1rem 0; }
        .timeline-item { 
            position: relative; padding: 1rem 0 1rem 3rem; 
            border-left: 2px solid #e2e8f0; margin-bottom: 1rem;
        }
        .timeline-item:before { 
            content: ''; position: absolute; left: -6px; top: 1.5rem;
            width: 12px; height: 12px; border-radius: 50%; background: #667eea;
        }
        .timeline-item:last-child { border-left: none; }
        .decision-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        .decision-table th, .decision-table td { 
            padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0;
        }
        .decision-table th { background: #f8fafc; font-weight: 600; }
        .decision-table tr:hover { background: #f8fafc; }
        .confidence { 
            padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem;
            font-weight: 600; text-align: center; min-width: 60px;
        }
        .confidence-high { background: #dcfce7; color: #166534; }
        .confidence-medium { background: #fef3c7; color: #92400e; }
        .confidence-low { background: #fee2e2; color: #991b1b; }
        .file-op { 
            border: 1px solid #e2e8f0; border-radius: 8px; 
            margin-bottom: 1rem; overflow: hidden;
        }
        .file-op-header { 
            background: #f8fafc; padding: 1rem; border-bottom: 1px solid #e2e8f0;
            display: flex; justify-content: space-between; align-items: center;
        }
        .file-op-content { padding: 1rem; }
        .operation-badge { 
            padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;
            font-weight: 600; text-transform: uppercase;
        }
        .op-create { background: #dcfce7; color: #166534; }
        .op-modify { background: #dbeafe; color: #1e40af; }
        .op-delete { background: #fee2e2; color: #991b1b; }
        .warning-badge { 
            background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;
            padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;
            margin-left: 0.5rem; font-weight: 600;
        }
        .trimming-badge {
            background: #f3f4f6; color: #374151; border: 1px solid #d1d5db;
            padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;
            margin-left: 0.5rem; cursor: help;
        }
        
        /* Iterative Workflow Styles */
        .workflow-stats {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem; margin-bottom: 1.5rem;
        }
        .stat-card {
            background: white; padding: 1rem; border-radius: 8px; text-align: center;
            border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value { font-size: 1.5rem; font-weight: bold; color: #1f2937; }
        .stat-label { font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem; }
        
        .iteration-timeline { display: flex; flex-direction: column; gap: 0.75rem; }
        .iteration-item {
            background: white; border-radius: 8px; padding: 1rem;
            border-left: 4px solid #d1d5db; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .iteration-item.success { border-left-color: #10b981; }
        .iteration-item.retry { border-left-color: #f59e0b; }
        
        .iteration-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 0.5rem;
        }
        .iteration-badge { display: flex; gap: 0.5rem; }
        .file-badge {
            background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem;
            border-radius: 4px; font-size: 0.75rem; font-weight: 600;
        }
        .attempt-badge {
            background: #f3f4f6; color: #374151; padding: 0.25rem 0.5rem;
            border-radius: 4px; font-size: 0.75rem; font-weight: 600;
        }
        .status-success { color: #065f46; font-weight: 600; }
        .status-retry { color: #92400e; font-weight: 600; }
        
        .iteration-details { font-size: 0.875rem; }
        .validation-reason { color: #6b7280; margin-top: 0.25rem; font-style: italic; }
        
        /* AI Decision Timeline Styles */
        .ai-decisions-summary { margin-bottom: 2rem; }
        .decision-timeline { 
            background: #f8fafc; border-radius: 8px; padding: 1rem;
            border-left: 4px solid #667eea; margin-top: 1rem;
        }
        .decision-item {
            display: flex; gap: 1rem; padding: 0.75rem 0; 
            border-bottom: 1px solid #e2e8f0;
        }
        .decision-item:last-child { border-bottom: none; }
        .decision-time {
            font-family: 'Monaco', monospace; font-size: 0.8rem; 
            color: #6b7280; min-width: 60px; text-align: right;
        }
        .decision-content { flex: 1; }
        .decision-type { 
            font-weight: 600; color: #374151; font-size: 0.875rem; 
            margin-bottom: 0.25rem;
        }
        .decision-result { 
            font-size: 0.875rem; color: #1f2937; margin-bottom: 0.25rem;
            padding: 0.25rem 0.5rem; background: white; border-radius: 4px;
            border: 1px solid #e5e7eb; display: inline-block;
        }
        .decision-context { 
            font-size: 0.8rem; color: #6b7280; font-style: italic; 
            margin-top: 0.25rem;
        }
        .file-op.has-warning { border-left: 4px solid #f59e0b; }
        .file-op.has-warning .file-op-header { background: #fffbeb; }
        .collapsible { cursor: pointer; user-select: none; }
        .collapsible:hover { background: #f8fafc; }
        .collapsible-content { display: none; padding: 1rem; background: #f8fafc; }
        .collapsible.active + .collapsible-content { display: block; }
        .qa-answer-preview { position: relative; }
        .qa-expand-btn { 
            display: inline-block; margin-left: 0.5rem; 
            padding: 0.25rem 0.5rem; border-radius: 4px;
            transition: background 0.2s;
        }
        .qa-expand-btn:hover { background: #e0e7ff; }
        .qa-full-answer { 
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            z-index: 1000; background: rgba(0,0,0,0.4);
            display: flex; align-items: center; justify-content: center;
            padding: 2rem;
        }
        .file-preview-btn {
            display: inline-block; padding: 0.5rem 1rem; border-radius: 6px;
            transition: background 0.2s; cursor: pointer; margin-top: 0.5rem;
        }
        .file-preview-btn:hover { background: #e0e7ff; }
        .file-preview-modal { 
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            z-index: 1000; background: rgba(0,0,0,0.4);
            display: flex; align-items: center; justify-content: center;
            padding: 2rem;
        }
        .file-preview-content {
            background: white; border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            width: 100%; max-width: 1200px; max-height: 90vh;
            overflow-y: auto; border: 1px solid #e2e8f0;
        }
        .decision-hover {
            position: relative; cursor: help;
            border-bottom: 1px dotted #667eea;
        }
        .decision-tooltip {
            position: absolute; top: 100%; left: 50%;
            transform: translateX(-50%);
            background: #2d3748; color: white; padding: 0.75rem 1rem;
            border-radius: 6px; font-size: 0.85rem; line-height: 1.4;
            white-space: nowrap; max-width: 300px; white-space: normal;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1001; opacity: 0; visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s;
            margin-top: 0.25rem;
        }
        .decision-tooltip::before {
            content: ''; position: absolute; bottom: 100%; left: 50%;
            transform: translateX(-50%); border: 4px solid transparent;
            border-bottom-color: #2d3748;
        }
        .decision-hover:hover .decision-tooltip {
            opacity: 1; visibility: visible;
        }
        .section-header { 
            cursor: pointer; user-select: none; 
            border-radius: 8px; transition: background 0.2s;
        }
        .section-header:hover { background: #f1f5f9; }
        .section-content { 
            display: block; overflow: hidden; 
            transition: max-height 0.3s ease-out;
        }
        .section-content.collapsed { 
            max-height: 0; 
            padding: 0 2rem; 
        }
        .collapse-indicator { 
            float: right; margin-right: 1rem; 
            transition: transform 0.3s ease;
        }
        .collapse-indicator.rotated { transform: rotate(180deg); }
        .highlight pre { margin: 0; font-size: 0.9rem; }
        .branch-flow { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; margin: 1rem 0; }
        .branch-node { 
            padding: 0.5rem 1rem; background: #f1f5f9; border-radius: 6px;
            border: 2px solid #cbd5e1; position: relative;
        }
        .branch-selected { background: #dcfce7; border-color: #22c55e; }
        .arrow { margin: 0 0.5rem; color: #64748b; }
        .footer { text-align: center; padding: 2rem; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦙 GitLlama Report</h1>
            <p>AI-Powered Repository Analysis • {{ generation_time }}</p>
            <p>Repository: {{ executive_summary.repo_url }}</p>
            <div style="margin-top: 0.5rem; opacity: 0.8; font-size: 0.9rem;">
                <span style="background: rgba(255,255,255,0.2); padding: 0.25rem 0.5rem; border-radius: 4px;">
                    Version {{ gitllama_version }}
                </span>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                📊 Executive Summary
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            <div class="executive-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.context_windows.total_count or 0 }}</div>
                    <div class="metric-label">CONTEXT WINDOWS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ executive_summary.total_ai_decisions or 0 }}</div>
                    <div class="metric-label">AI Decisions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ executive_summary.files_modified|length }}</div>
                    <div class="metric-label">Files Modified</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.1f"|format(executive_summary.execution_time or 0) }}s</div>
                    <div class="metric-label">Execution Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{% if executive_summary.success %}✅{% else %}❌{% endif %}</div>
                    <div class="metric-label">Status</div>
                </div>
            </div>
            <p><strong>Branch Selected:</strong> {{ executive_summary.branch_selected or 'N/A' }}</p>
            <p><strong>Commit:</strong> {{ executive_summary.commit_hash or 'N/A' }}</p>
            {% if executive_summary.files_modified %}
            <p><strong>Modified Files:</strong> {{ executive_summary.files_modified|join(', ') }}</p>
            {% endif %}
            
            {% if executive_summary.log_summary %}
            <div style="margin-top: 1.5rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #667eea;">
                <h4 style="margin: 0 0 0.5rem 0; color: #374151;">🤖 AI Execution Analysis</h4>
                <div style="color: #4b5563; line-height: 1.6;">{{ executive_summary.log_summary }}</div>
                {% if executive_summary.total_logs_captured %}
                <div style="margin-top: 0.75rem;">
                    <a href="latest_logs.html" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600; font-size: 0.9rem;">
                        📋 View Detailed Logs ({{ executive_summary.total_logs_captured }} entries) →
                    </a>
                </div>
                {% endif %}
            </div>
            {% endif %}
            </div>
        </div>

        <!-- Repository Analysis Timeline -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                🔍 Repository Analysis Timeline
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            <div class="timeline">
                {% for phase in repository_analysis.phases %}
                <div class="timeline-item">
                    <h3>{{ phase.name }}</h3>
                    <p>{{ phase.description }}</p>
                    {% if phase.duration %}
                    <small style="color: #64748b;">Duration: {{ "%.2f"|format(phase.duration) }}s</small>
                    {% endif %}
                    {% if phase.details %}
                    <div class="collapsible" onclick="toggleCollapsible(this)">
                        <small>📋 View Details ({{ phase.details|length }} items)</small>
                    </div>
                    <div class="collapsible-content">
                        {% for detail in phase.details %}
                        <p><small>• {{ detail.detail }}</small></p>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            </div>
        </div>

        <!-- AI Decision Log -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                🤖 AI Decision Log
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            {% if guided_questions or ai_decisions %}
            <table class="decision-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Type</th>
                        <th>Question</th>
                        <th>Answer/Decision</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {% for qa in guided_questions %}
                    <tr>
                        <td>{{ qa.timestamp.strftime('%H:%M:%S') }}</td>
                        <td>Guided Q&A</td>
                        <td>{{ qa.question }}</td>
                        <td>
                            <div class="qa-answer-preview">
                                {{ qa.answer[:100] }}{% if qa.answer|length > 100 %}...{% endif %}
                                {% if qa.answer|length > 100 %}
                                <div class="qa-expand-btn" onclick="openQAAnswer(this, '{{ loop.index }}')">
                                    <small style="color: #667eea; cursor: pointer;">📖 View Full Answer</small>
                                </div>
                                <div class="qa-full-answer" id="qa-modal-{{ loop.index }}" style="display: none;" onclick="closeAllQAAnswers()">
                                    <div class="file-preview-content" onclick="event.stopPropagation()">
                                        <div style="padding: 2rem;">
                                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e2e8f0;">
                                                <div>
                                                    <h3 style="margin: 0; color: #2d3748;">Full Answer</h3>
                                                    <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.9rem;">{{ qa.question }}</p>
                                                </div>
                                                <button onclick="closeAllQAAnswers()" style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.5rem; cursor: pointer; color: #64748b; font-size: 1.2rem; width: 2.5rem; height: 2.5rem;">×</button>
                                            </div>
                                            <div style="font-size: 1.1rem; line-height: 1.7; color: #374151; padding-right: 1rem;">
                                                {{ qa.answer|replace('\n', '<br>')|safe }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {% endif %}
                            </div>
                        </td>
                        <td>
                            {% if qa.confidence %}
                            <span class="confidence confidence-{% if qa.confidence > 0.8 %}high{% elif qa.confidence > 0.6 %}medium{% else %}low{% endif %}">
                                {{ "%.0f"|format(qa.confidence * 100) }}%
                            </span>
                            {% else %}-{% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                    {% for decision in ai_decisions %}
                    <tr>
                        <td>{{ decision.timestamp.strftime('%H:%M:%S') }}</td>
                        <td>{{ decision.type }}</td>
                        <td>{{ decision.type }}</td>
                        <td>
                            <div class="decision-hover">
                                <strong>{{ decision.decision }}</strong>
                                <div class="decision-tooltip">
                                    {% if decision.context %}
                                    <strong>Context:</strong> {{ decision.context[:200] }}{% if decision.context|length > 200 %}...{% endif %}
                                    {% endif %}
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="confidence confidence-medium">-</span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No AI decisions recorded.</p>
            {% endif %}
            </div>
        </div>

        <!-- Branch Selection Journey -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                🌿 Branch Selection Journey
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            {% if branch_analysis.discovered_branches %}
            <h3>Discovered Branches</h3>
            <div class="branch-flow">
                {% for branch in branch_analysis.discovered_branches %}
                <div class="branch-node {% if branch == branch_analysis.final_selection %}branch-selected{% endif %}">
                    {{ branch }}
                    {% if branch_analysis.evaluation_scores[branch] %}
                    <br><small>Score: {{ branch_analysis.evaluation_scores[branch].score }}</small>
                    {% endif %}
                </div>
                {% if not loop.last %}<span class="arrow">→</span>{% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            {% if branch_analysis.todo_analysis %}
            <h3>📋 TODO.md Cross-Branch Analysis</h3>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid #e2e8f0;">
                
                <!-- Summary Stats -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #3b82f6;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">{{ branch_analysis.todo_analysis.total_branches_analyzed }}</div>
                        <div style="color: #64748b; font-size: 0.875rem;">Branches Scanned</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #10b981;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">{{ branch_analysis.todo_analysis.branches_with_todos_count }}</div>
                        <div style="color: #64748b; font-size: 0.875rem;">With TODO.md</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #f59e0b;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #f59e0b;">{{ (branch_analysis.todo_analysis.branches_with_todos_count / branch_analysis.todo_analysis.total_branches_analyzed * 100)|round|int }}%</div>
                        <div style="color: #64748b; font-size: 0.875rem;">Planning Coverage</div>
                    </div>
                </div>

                <!-- Branch Details -->
                {% if branch_analysis.todo_analysis.todo_contents %}
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="margin-bottom: 1rem; color: #374151;">📁 Branch-by-Branch TODO Status</h4>
                    <div style="display: grid; gap: 0.75rem;">
                        {% for branch_name, todo_data in branch_analysis.todo_analysis.todo_contents.items() %}
                        <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                {% if todo_data.exists %}
                                    <span style="color: #10b981; font-size: 1.25rem;">📋</span>
                                    <div>
                                        <div style="font-weight: 600; color: #374151;">{{ branch_name }}</div>
                                        <div style="font-size: 0.875rem; color: #6b7280;">{{ todo_data.length }} characters • Active planning</div>
                                    </div>
                                {% else %}
                                    <span style="color: #9ca3af; font-size: 1.25rem;">📄</span>
                                    <div>
                                        <div style="font-weight: 600; color: #9ca3af;">{{ branch_name }}</div>
                                        <div style="font-size: 0.875rem; color: #9ca3af;">No TODO.md found</div>
                                    </div>
                                {% endif %}
                            </div>
                            {% if todo_data.exists %}
                                <div style="display: flex; gap: 0.5rem;">
                                    {% if todo_data.length > 500 %}
                                        <span style="background: #dcfce7; color: #166534; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">COMPREHENSIVE</span>
                                    {% elif todo_data.length > 200 %}
                                        <span style="background: #fef3c7; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">MODERATE</span>
                                    {% else %}
                                        <span style="background: #fee2e2; color: #991b1b; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">MINIMAL</span>
                                    {% endif %}
                                </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                
                <!-- AI Analysis -->
                {% if branch_analysis.todo_analysis.ai_comparison and branch_analysis.todo_analysis.ai_comparison != "No TODO.md files found in any branch." %}
                <div style="margin-top: 1.5rem;">
                    <h4 style="margin-bottom: 1rem; color: #374151;">🤖 AI Strategic Analysis</h4>
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);">
                        <div style="background: rgba(255, 255, 255, 0.1); padding: 1.25rem; border-radius: 8px; white-space: pre-line; line-height: 1.6; font-size: 0.95rem;">{{ branch_analysis.todo_analysis.ai_comparison }}</div>
                    </div>
                    
                    <div style="margin-top: 1rem; padding: 1rem; background: #fffbeb; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.25rem;">💡</span>
                            <strong style="color: #92400e;">Key Insights for Branch Selection</strong>
                        </div>
                        <div style="color: #92400e; font-size: 0.9rem;">
                            This analysis helps determine which branch has the most current and actionable TODO list, 
                            indicating active development focus and clear project direction. Branches with comprehensive 
                            TODO.md files typically represent more mature feature development and better planning.
                        </div>
                    </div>
                </div>
                {% else %}
                <div style="margin-top: 1.5rem; padding: 1.5rem; background: #f3f4f6; border-radius: 8px; text-align: center; color: #6b7280;">
                    <span style="font-size: 2rem; margin-bottom: 0.5rem; display: block;">📝</span>
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">No TODO.md Files Found</div>
                    <div style="font-size: 0.875rem;">No planning documents were discovered across any branches. This suggests either the project is very new, uses different planning methods, or tasks are tracked externally.</div>
                </div>
                {% endif %}
                
            </div>
            {% endif %}
            
            {% if branch_analysis.final_selection %}
            <h3>Final Selection</h3>
            <p><strong>Selected:</strong> {{ branch_analysis.final_selection }}</p>
            <p><strong>Action:</strong> {{ branch_analysis.action or 'Unknown' }}</p>
            <p><strong>Reasoning:</strong> {{ branch_analysis.selection_reasoning }}</p>
            {% endif %}
            </div>
        </div>

        <!-- Iterative Workflow Report -->
        {% if iteration_history %}
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                🔄 Iterative Workflow Report
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
                <div class="workflow-summary">
                    <div class="workflow-stats">
                        <div class="stat-card">
                            <div class="stat-value">{{ total_iterations or 0 }}</div>
                            <div class="stat-label">Total Iterations</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{{ files_attempted or 0 }}</div>
                            <div class="stat-label">Files Attempted</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{{ (iteration_history | selectattr('validation_success') | list | length) }}</div>
                            <div class="stat-label">Successful Validations</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{{ ((iteration_history | length) - (iteration_history | selectattr('validation_success') | list | length)) }}</div>
                            <div class="stat-label">Retries Needed</div>
                        </div>
                    </div>
                </div>
                
                <h3>🔍 Iteration Details</h3>
                <div class="iteration-timeline">
                    {% for iteration in iteration_history %}
                    <div class="iteration-item {% if iteration.validation_success %}success{% else %}retry{% endif %}">
                        <div class="iteration-header">
                            <div class="iteration-badge">
                                <span class="file-badge">File {{ iteration.file_num }}</span>
                                <span class="attempt-badge">Attempt {{ iteration.retry_num }}</span>
                            </div>
                            <div class="iteration-status">
                                {% if iteration.validation_success %}
                                    <span class="status-success">✅ VALIDATED</span>
                                {% else %}
                                    <span class="status-retry">🔄 RETRY NEEDED</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="iteration-details">
                            <div><strong>{{ iteration.operation }}:</strong> {{ iteration.file_path }}</div>
                            <div class="validation-reason">{{ iteration.validation_reason }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}

        <!-- File Operations Report -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                📝 File Operations Report
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            {% if ai_decisions %}
            <div class="ai-decisions-summary">
                <h3>🤖 AI Decision Timeline</h3>
                <div class="decision-timeline">
                    {% for decision in ai_decisions %}
                    <div class="decision-item">
                        <div class="decision-time">{{ decision.timestamp.strftime('%H:%M:%S') }}</div>
                        <div class="decision-content">
                            <div class="decision-type">{{ decision.type }}</div>
                            <div class="decision-result">{{ decision.decision }}</div>
                            {% if decision.context %}
                            <div class="decision-context">{{ decision.context }}</div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if file_operations %}
            <h3>📁 File Operations</h3>
            {% for op in file_operations %}
            <div class="file-op{% if '⚠️' in op.reason %} has-warning{% endif %}">
                <div class="file-op-header">
                    <div>
                        <span class="operation-badge op-{{ op.operation.lower() }}">{{ op.operation }}</span>
                        <strong>{{ op.file_path }}</strong>
                        {% if '⚠️' in op.reason %}
                        <span class="warning-badge">⚠️ WARNING</span>
                        {% endif %}
                        {% if op.trimming_emoji %}
                        <span class="trimming-badge" title="{{ op.trimming_details if op.trimming_details else 'No trimming applied' }}">{{ op.trimming_emoji }}</span>
                        {% endif %}
                    </div>
                    <small>{{ op.timestamp.strftime('%H:%M:%S') }}</small>
                </div>
                <div class="file-op-content">
                    <p><strong>Reason:</strong> {{ op.reason }}</p>
                    {% if op.content_preview %}
                    <div class="file-preview-btn" onclick="openFilePreview('{{ loop.index }}', '{{ op.file_path }}', '{{ op.operation }}')">
                        <strong style="color: #667eea; cursor: pointer;">📄 View File Content</strong>
                    </div>
                    <div class="file-preview-modal" id="file-modal-{{ loop.index }}" style="display: none;" onclick="closeAllFilePreviews()">
                        <div class="file-preview-content" onclick="event.stopPropagation()">
                            <div style="padding: 1.5rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e2e8f0;">
                                    <div>
                                        <h3 style="margin: 0; color: #2d3748;">File Content Preview</h3>
                                        <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.9rem;">
                                            <span class="operation-badge op-{{ op.operation.lower() }}">{{ op.operation }}</span>
                                            {{ op.file_path }}
                                        </p>
                                    </div>
                                    <button onclick="closeAllFilePreviews()" style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.5rem; cursor: pointer; color: #64748b; font-size: 1.2rem; width: 2.5rem; height: 2.5rem;">×</button>
                                </div>
                                <div style="background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; overflow: auto;">
                                    <div style="font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; font-size: 0.9rem; line-height: 1.5; padding: 1.5rem; background: #ffffff; margin: 0;">
                                        {{ op.highlighted_content|safe }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            {% else %}
            <p>No file operations recorded.</p>
            {% endif %}
            </div>
        </div>

        <!-- Metrics Dashboard -->
        <div class="section">
            <h2 class="section-header" onclick="toggleSection(this)">
                📈 Metrics Dashboard
                <span class="collapse-indicator">▼</span>
            </h2>
            <div class="section-content">
            <div class="executive-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.context_windows.total_count or 0 }}</div>
                    <div class="metric-label">Context Windows</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.6f"|format(metrics.context_windows.total_memory_gb or 0) }}</div>
                    <div class="metric-label">Memory Usage (GB)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.context_windows.total_api_calls or 0 }}</div>
                    <div class="metric-label">Total API Calls</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.token_usage.total or 0 }}</div>
                    <div class="metric-label">Total Tokens</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.model_info.model or 'N/A' }}</div>
                    <div class="metric-label">Model Used</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ metrics.model_info.context_window or 'N/A' }}</div>
                    <div class="metric-label">Model Context Size</div>
                </div>
            </div>
            
            {% if metrics.processing_times %}
            <h3>Processing Times</h3>
            <table class="decision-table">
                <thead>
                    <tr><th>Phase</th><th>Duration</th></tr>
                </thead>
                <tbody>
                    {% for phase, duration in metrics.processing_times.items() %}
                    <tr>
                        <td>{{ phase }}</td>
                        <td>{{ "%.2f"|format(duration) }}s</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            {% if metrics.context_windows.contexts %}
            <h3>🧠 Context Windows Details</h3>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid #e2e8f0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #3b82f6;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">{{ metrics.context_windows.total_count }}</div>
                        <div style="color: #64748b; font-size: 0.875rem;">Total Context Windows</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #10b981;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">{{ "%.6f"|format(metrics.context_windows.total_memory_gb) }}</div>
                        <div style="color: #64748b; font-size: 0.875rem;">Total Memory (GB)</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; border-left: 4px solid #f59e0b;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #f59e0b;">{{ metrics.context_windows.total_api_calls }}</div>
                        <div style="color: #64748b; font-size: 0.875rem;">API Calls Made</div>
                    </div>
                </div>
                
                <h4 style="margin-bottom: 1rem; color: #374151;">📋 Context Window List</h4>
                <div style="display: grid; gap: 0.75rem;">
                    {% for context_name, context_data in metrics.context_windows.contexts.items() %}
                    <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="font-weight: 600; color: #374151;">{{ context_name }}</div>
                            <div style="display: flex; gap: 0.5rem;">
                                <span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                                    Used {{ context_data.usage_count }} times
                                </span>
                                <span style="background: #dcfce7; color: #166534; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                                    {{ context_data.memory_size_bytes|filesizeformat if context_data.memory_size_bytes else "0 bytes" }}
                                </span>
                            </div>
                        </div>
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                            Created: {{ context_data.created_at[:19] if context_data.created_at else "Unknown" }} | 
                            Last used: {{ context_data.last_used[:19] if context_data.last_used else "Never" }}
                        </div>
                        <div style="font-family: 'Monaco', monospace; font-size: 0.8rem; color: #374151; background: #f9fafb; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #d1d5db;">
                            {{ context_data.content_preview }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            </div>
        </div>

        <div class="footer">
            <p>Generated by GitLlama v0.5.0 • {{ generation_time }}</p>
            <p>🦙 Transparent AI-powered git automation</p>
        </div>
    </div>

    <script>
        function toggleCollapsible(element) {
            element.classList.toggle('active');
        }
        
        function openQAAnswer(button, modalId) {
            // Close any currently open Q&A answers
            closeAllQAAnswers();
            
            // Show the selected modal
            const modal = document.getElementById('qa-modal-' + modalId);
            if (modal) {
                modal.style.display = 'block';
                // Prevent body scrolling when modal is open
                document.body.style.overflow = 'hidden';
            }
        }
        
        function closeAllQAAnswers() {
            // Hide all Q&A modals
            const modals = document.querySelectorAll('.qa-full-answer');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            
            // Restore body scrolling
            document.body.style.overflow = 'auto';
        }
        
        function openFilePreview(modalId, filePath, operation) {
            // Close any open modals first
            closeAllQAAnswers();
            closeAllFilePreviews();
            
            // Show the selected file preview modal
            const modal = document.getElementById('file-modal-' + modalId);
            if (modal) {
                modal.style.display = 'block';
                // Prevent body scrolling when modal is open
                document.body.style.overflow = 'hidden';
            }
        }
        
        function closeAllFilePreviews() {
            // Hide all file preview modals
            const modals = document.querySelectorAll('.file-preview-modal');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            
            // Restore body scrolling
            document.body.style.overflow = 'auto';
        }
        
        // Close modal when pressing Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAllQAAnswers();
                closeAllFilePreviews();
            }
        });
        
        function toggleSection(header) {
            const content = header.nextElementSibling;
            const indicator = header.querySelector('.collapse-indicator');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                content.style.maxHeight = content.scrollHeight + 'px';
                indicator.classList.remove('rotated');
                indicator.textContent = '▼';
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
                setTimeout(() => {
                    content.classList.add('collapsed');
                    content.style.maxHeight = '0px';
                }, 10);
                indicator.classList.add('rotated');
                indicator.textContent = '▲';
            }
        }
        
        // Initialize all sections as expanded by default
        document.addEventListener('DOMContentLoaded', function() {
            const contents = document.querySelectorAll('.section-content');
            contents.forEach(content => {
                content.style.maxHeight = content.scrollHeight + 'px';
            });
        });
    </script>
</body>
</html>'''
    
    def _get_markdown_template(self) -> str:
        """Get the Markdown template string."""
        return '''# 🦙 GitLlama Report - {{ timestamp }}

**Generated:** {{ generation_time }}  
**Repository:** {{ executive_summary.repo_url }}

## 📊 Executive Summary

- **AI Decisions Made:** {{ executive_summary.total_ai_decisions or 0 }}
- **Files Modified:** {{ executive_summary.files_modified|length }}
- **Execution Time:** {{ "%.1f"|format(executive_summary.execution_time or 0) }}s
- **Status:** {% if executive_summary.success %}✅ Success{% else %}❌ Failed{% endif %}
- **Branch Selected:** {{ executive_summary.branch_selected or 'N/A' }}
- **Commit:** {{ executive_summary.commit_hash or 'N/A' }}

{% if executive_summary.files_modified %}
**Modified Files:**
{% for file in executive_summary.files_modified %}
- {{ file }}
{% endfor %}
{% endif %}

## 🔍 Repository Analysis Timeline

{% for phase in repository_analysis.phases %}
### {{ phase.name }}
{{ phase.description }}
{% if phase.duration %}
**Duration:** {{ "%.2f"|format(phase.duration) }}s
{% endif %}

{% if phase.details %}
**Details:**
{% for detail in phase.details %}
- {{ detail.detail }}
{% endfor %}
{% endif %}

{% endfor %}

## 🤖 AI Decision Log

{% if guided_questions or ai_decisions %}
| Time | Type | Question | Answer/Decision | Confidence |
|------|------|----------|-----------------|------------|
{% for qa in guided_questions %}
| {{ qa.timestamp.strftime('%H:%M:%S') }} | Guided Q&A | {{ qa.question }} | {{ qa.answer[:50] }}{% if qa.answer|length > 50 %}...{% endif %} | {% if qa.confidence %}{{ "%.0f"|format(qa.confidence * 100) }}%{% else %}-{% endif %} |
{% endfor %}
{% for decision in ai_decisions %}
| {{ decision.timestamp.strftime('%H:%M:%S') }} | {{ decision.type }} | {{ decision.type }} | **{{ decision.decision }}** | - |
{% endfor %}
{% else %}
No AI decisions recorded.
{% endif %}

## 🌿 Branch Selection Journey

{% if branch_analysis.discovered_branches %}
**Discovered Branches:** {{ branch_analysis.discovered_branches|join(', ') }}

{% if branch_analysis.final_selection %}
**Final Selection:** {{ branch_analysis.final_selection }}  
**Action:** {{ branch_analysis.action or 'Unknown' }}  
**Reasoning:** {{ branch_analysis.selection_reasoning }}
{% endif %}

{% if branch_analysis.todo_analysis %}
### 📋 TODO.md Cross-Branch Analysis

#### Planning Coverage Summary
- **🔍 Branches Scanned:** {{ branch_analysis.todo_analysis.total_branches_analyzed }}
- **📋 With TODO.md:** {{ branch_analysis.todo_analysis.branches_with_todos_count }}
- **📊 Coverage Rate:** {{ (branch_analysis.todo_analysis.branches_with_todos_count / branch_analysis.todo_analysis.total_branches_analyzed * 100)|round|int }}%

#### Branch-by-Branch Status
{% if branch_analysis.todo_analysis.todo_contents %}
{% for branch_name, todo_data in branch_analysis.todo_analysis.todo_contents.items() %}
{% if todo_data.exists %}
- **{{ branch_name }}** 📋 *({{ todo_data.length }} chars)* - Active planning{% if todo_data.length > 500 %} - COMPREHENSIVE{% elif todo_data.length > 200 %} - MODERATE{% else %} - MINIMAL{% endif %}
{% else %}
- **{{ branch_name }}** 📄 - No TODO.md found
{% endif %}
{% endfor %}
{% endif %}

{% if branch_analysis.todo_analysis.ai_comparison and branch_analysis.todo_analysis.ai_comparison != "No TODO.md files found in any branch." %}
#### 🤖 AI Strategic Analysis
```
{{ branch_analysis.todo_analysis.ai_comparison }}
```

> **💡 Branch Selection Insight:** This analysis reveals which branches have the most current and actionable TODO lists, indicating active development focus and clear project direction. Comprehensive TODO.md files typically represent more mature feature development.
{% else %}
#### 📝 No Planning Documents Found
No TODO.md files were discovered across any branches. This suggests the project either uses different planning methods or tracks tasks externally.
{% endif %}
{% endif %}
{% endif %}

## 📝 File Operations Report

{% if file_operations %}
{% for op in file_operations %}
### {{ op.operation }}: {{ op.file_path }}
**Time:** {{ op.timestamp.strftime('%H:%M:%S') }}  
**Reason:** {{ op.reason }}

{% if op.content_preview %}
**Content Preview:**
```
{{ op.content_preview }}
```
{% endif %}

{% endfor %}
{% else %}
No file operations recorded.
{% endif %}

## 📈 Metrics Dashboard

- **AI API Calls:** {{ metrics.ai_calls or 0 }}
- **Total Tokens:** {{ metrics.token_usage.total or 0 }}
- **Model Used:** {{ metrics.model_info.model or 'N/A' }}
- **Context Window:** {{ metrics.model_info.context_window or 'N/A' }}

{% if metrics.processing_times %}
**Processing Times:**
{% for phase, duration in metrics.processing_times.items() %}
- {{ phase }}: {{ "%.2f"|format(duration) }}s
{% endfor %}
{% endif %}

---
*Generated by GitLlama v0.5.0 • {{ generation_time }}*  
*🦙 Transparent AI-powered git automation*
'''
    
    def _get_logs_html_template(self) -> str:
        """Get the logs HTML template with filtering capabilities."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitLlama Detailed Logs - {{ timestamp }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; color: #333; background: #f5f7fa;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1rem; }
        
        .controls { 
            background: white; padding: 1.5rem; border-radius: 12px; 
            margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }
        .filter-group { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
        .filter-section { display: flex; flex-direction: column; gap: 0.5rem; }
        .filter-section label { font-weight: 600; color: #374151; font-size: 0.9rem; }
        .filter-buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .filter-btn { 
            padding: 0.5rem 1rem; border: 2px solid #e5e7eb; background: white;
            border-radius: 6px; cursor: pointer; transition: all 0.2s;
            font-size: 0.9rem; font-weight: 600;
        }
        .filter-btn.active { background: #667eea; color: white; border-color: #667eea; }
        .filter-btn:hover { border-color: #667eea; }
        
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem; margin-bottom: 1.5rem;
        }
        .stat-card {
            background: white; padding: 1rem; border-radius: 8px; text-align: center;
            border-left: 4px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .stat-value { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #64748b; font-size: 0.875rem; }
        
        .search-box {
            width: 100%; padding: 0.75rem; border: 2px solid #e5e7eb;
            border-radius: 8px; font-size: 1rem; margin-bottom: 1rem;
        }
        .search-box:focus { outline: none; border-color: #667eea; }
        
        .logs-container {
            background: white; border-radius: 12px; overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }
        .log-entry {
            padding: 1rem; border-bottom: 1px solid #f1f5f9;
            display: flex; align-items: flex-start; gap: 1rem;
            transition: background 0.2s;
        }
        .log-entry:hover { background: #f8fafc; }
        .log-entry.hidden { display: none; }
        
        .log-time { 
            font-family: 'Monaco', monospace; font-size: 0.85rem; 
            color: #6b7280; min-width: 80px; flex-shrink: 0;
        }
        .log-level {
            padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;
            font-weight: 700; text-align: center; min-width: 70px; flex-shrink: 0;
        }
        .level-error { background: #fee2e2; color: #dc2626; }
        .level-warning { background: #fef3c7; color: #d97706; }
        .level-info { background: #dbeafe; color: #2563eb; }
        .level-debug { background: #f3f4f6; color: #6b7280; }
        
        .log-source {
            font-family: 'Monaco', monospace; font-size: 0.8rem;
            color: #9ca3af; min-width: 120px; flex-shrink: 0;
        }
        .log-message { 
            flex: 1; color: #374151; font-family: 'Monaco', monospace; 
            font-size: 0.9rem; line-height: 1.4; word-break: break-word;
        }
        
        .summary-section {
            background: white; padding: 1.5rem; border-radius: 12px;
            margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }
        .summary-section h3 { margin-bottom: 1rem; color: #374151; }
        
        .no-logs { 
            text-align: center; padding: 3rem; color: #6b7280; 
            font-style: italic; font-size: 1.1rem;
        }
        
        .back-link {
            display: inline-block; margin-bottom: 1rem; color: #667eea;
            text-decoration: none; font-weight: 600;
        }
        .back-link:hover { text-decoration: underline; }
        
        .footer { text-align: center; padding: 2rem; color: #64748b; margin-top: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 GitLlama Execution Logs</h1>
            <p>Detailed runtime analysis • {{ generation_time }}</p>
            <p>Repository: {{ repo_url }}</p>
        </div>

        <a href="latest.html" class="back-link">← Back to Main Report</a>

        {% if log_summary %}
        <div class="summary-section">
            <h3>🤖 AI Execution Summary</h3>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
                {{ log_summary }}
            </div>
        </div>
        {% endif %}

        <div class="controls">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ logs|length }}</div>
                    <div class="stat-label">Total Logs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ logs_by_level.ERROR|length }}</div>
                    <div class="stat-label">Errors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ logs_by_level.WARNING|length }}</div>
                    <div class="stat-label">Warnings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ logs_by_level.INFO|length }}</div>
                    <div class="stat-label">Info</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ logs_by_level.DEBUG|length }}</div>
                    <div class="stat-label">Debug</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ logs_by_module|length }}</div>
                    <div class="stat-label">Modules</div>
                </div>
            </div>

            <input type="text" class="search-box" id="logSearch" placeholder="🔍 Search logs by message, module, or function...">

            <div class="filter-group">
                <div class="filter-section">
                    <label>Log Level:</label>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-filter="level" data-value="all">All</button>
                        <button class="filter-btn" data-filter="level" data-value="ERROR">Error</button>
                        <button class="filter-btn" data-filter="level" data-value="WARNING">Warning</button>
                        <button class="filter-btn" data-filter="level" data-value="INFO">Info</button>
                        <button class="filter-btn" data-filter="level" data-value="DEBUG">Debug</button>
                    </div>
                </div>
                
                <div class="filter-section">
                    <label>Module:</label>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-filter="module" data-value="all">All</button>
                        {% for module in logs_by_module.keys() %}
                        <button class="filter-btn" data-filter="module" data-value="{{ module }}">{{ module.split('.')[-1] }}</button>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <div class="logs-container">
            {% if logs %}
                {% for log in logs %}
                <div class="log-entry" 
                     data-level="{{ log.level }}" 
                     data-module="{{ log.logger }}"
                     data-message="{{ log.message|lower }}"
                     data-function="{{ log.function }}"
                     data-searchtext="{{ (log.message + ' ' + log.logger + ' ' + log.function)|lower }}">
                    <div class="log-time">{{ log.timestamp.strftime('%H:%M:%S') }}</div>
                    <div class="log-level level-{{ log.level.lower() }}">{{ log.level }}</div>
                    <div class="log-source">{{ log.logger.split('.')[-1] }}:{{ log.function }}</div>
                    <div class="log-message">{{ log.message }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-logs">No logs captured during execution</div>
            {% endif %}
        </div>

        <div class="footer">
            <p>Generated by GitLlama v0.5.0 • {{ generation_time }}</p>
            <p>🦙 Transparent AI-powered git automation</p>
        </div>
    </div>

    <script>
        const logEntries = document.querySelectorAll('.log-entry');
        const searchBox = document.getElementById('logSearch');
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        let currentFilters = { level: 'all', module: 'all' };
        let searchTerm = '';

        // Filter functionality
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const filterType = btn.dataset.filter;
                const filterValue = btn.dataset.value;
                
                // Update active state
                document.querySelectorAll(`[data-filter="${filterType}"]`).forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update filters
                currentFilters[filterType] = filterValue;
                applyFilters();
            });
        });

        // Search functionality
        searchBox.addEventListener('input', (e) => {
            searchTerm = e.target.value.toLowerCase();
            applyFilters();
        });

        function applyFilters() {
            logEntries.forEach(entry => {
                const level = entry.dataset.level;
                const module = entry.dataset.module;
                const searchText = entry.dataset.searchtext;
                
                let show = true;
                
                // Level filter
                if (currentFilters.level !== 'all' && level !== currentFilters.level) {
                    show = false;
                }
                
                // Module filter
                if (currentFilters.module !== 'all' && module !== currentFilters.module) {
                    show = false;
                }
                
                // Search filter
                if (searchTerm && !searchText.includes(searchTerm)) {
                    show = false;
                }
                
                entry.classList.toggle('hidden', !show);
            });
        }

        // Initialize
        applyFilters();
    </script>
</body>
</html>'''
    
    def _generate_fallback_report(self) -> Path:
        """Generate a simple text-based fallback report when dependencies are missing."""
        logger.info("Generating fallback text report...")
        
        # Generate simple text report
        lines = [
            "GitLlama Execution Report",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Repository: {self.repo_url}",
            "",
            "Executive Summary:",
            f"  Branch: {self.executive_summary.get('branch_selected', 'Unknown')}",
            f"  Files Modified: {len(self.executive_summary.get('files_modified', []))}",
            f"  Success: {self.executive_summary.get('success', False)}",
            f"  AI Decisions: {self.executive_summary.get('total_ai_decisions', 0)}",
            "",
            "AI Decisions Made:",
        ]
        
        for i, decision in enumerate(self.ai_decisions, 1):
            lines.append(f"  {i}. {decision['question']}")
            lines.append(f"     Selected: {decision['selected']} (confidence: {decision['confidence']:.0%})")
        
        if self.guided_questions:
            lines.extend([
                "",
                "Guided Questions:",
            ])
            for i, qa in enumerate(self.guided_questions, 1):
                lines.append(f"  {i}. Q: {qa['question']}")
                lines.append(f"     A: {qa['answer'][:100]}{'...' if len(qa['answer']) > 100 else ''}")
        
        if self.file_operations:
            lines.extend([
                "",
                "File Operations:",
            ])
            for op in self.file_operations:
                lines.append(f"  {op['operation']}: {op['file_path']}")
        
        lines.extend([
            "",
            "Note: This is a simplified report. For full HTML report with styling,",
            "install dependencies: pip install jinja2 pygments",
            ""
        ])
        
        # Save to file
        txt_filename = f"gitllama_report_{self.timestamp}.txt"
        txt_path = self.output_dir / txt_filename
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Fallback report generated: {txt_path}")
        return txt_path