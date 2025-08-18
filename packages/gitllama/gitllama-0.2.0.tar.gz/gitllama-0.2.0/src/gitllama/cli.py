"""
GitLlama CLI Module with AI Integration

AI-powered command-line interface for git automation.
"""

import argparse
import logging
import sys

from .git_operations import GitAutomator, GitOperationError
from .ai_coordinator import AICoordinator


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="GitLlama - AI-powered git automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitllama https://github.com/user/repo.git
  gitllama https://github.com/user/repo.git --model llama3.2:3b
  gitllama https://github.com/user/repo.git --branch my-feature
  gitllama https://github.com/user/repo.git --message "Custom commit message"
  gitllama https://github.com/user/repo.git --no-ai  # Disable AI
        """
    )
    
    parser.add_argument(
        "git_url",
        help="Git repository URL to clone and modify"
    )
    
    parser.add_argument(
        "--branch", "-b",
        default=None,
        help="Branch name to create (AI will decide if not specified)"
    )
    
    parser.add_argument(
        "--message", "-m",
        help="Custom commit message (AI will generate if not specified)"
    )
    
    parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="Ollama model to use for AI decisions (default: llama3.2:3b)"
    )
    
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI and use simple automation"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser


def main() -> int:
    """Main entry point for GitLlama CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )
    
    try:
        # Create AI coordinator if not disabled
        ai_coordinator = None
        if not args.no_ai:
            print(f"🤖 Initializing AI with model: {args.model}")
            ai_coordinator = AICoordinator(
                model=args.model,
                base_url=args.ollama_url
            )
            
            # Test Ollama connection
            if not ai_coordinator.client.is_available():
                print("⚠️  Warning: Ollama server not available. Falling back to simple automation.")
                print("   To use AI features, ensure Ollama is running: ollama serve")
                ai_coordinator = None
        
        # Run the workflow
        with GitAutomator(ai_coordinator=ai_coordinator) as automator:
            results = automator.run_full_workflow(
                git_url=args.git_url,
                branch_name=args.branch,
                commit_message=args.message
            )
        
        # Print results
        if results["success"]:
            print("✓ GitLlama workflow completed successfully!")
            print(f"  Repository: {results['repo_path']}")
            print(f"  Branch: {results['branch']}")
            print(f"  Modified files: {', '.join(results['modified_files'])}")
            print(f"  Commit: {results['commit_hash']}")
            
            if 'ai_analysis' in results:
                print(f"\n🤖 AI Analysis:")
                analysis = results['ai_analysis']
                print(f"  Project Type: {analysis.get('project_type', 'Unknown')}")
                print(f"  Technologies: {', '.join(analysis.get('technologies', []))}")
                print(f"  State: {analysis.get('state', 'Unknown')}")
            
            return 0
        else:
            print(f"✗ Workflow failed: {results['error']}")
            return 1
            
    except GitOperationError as e:
        print(f"✗ Git operation failed: {e}")
        return 1
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())