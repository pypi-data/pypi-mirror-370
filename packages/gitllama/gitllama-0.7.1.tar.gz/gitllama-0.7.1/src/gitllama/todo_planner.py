"""
TODO-driven Planning Module for GitLlama
Creates actionable plans based on TODO analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
from .ollama_client import OllamaClient
from .ai_query import AIQuery

logger = logging.getLogger(__name__)


class TodoPlanner:
    """Creates actionable plans from TODO analysis"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.ai = AIQuery(client, model)
    
    def create_action_plan(self, analysis: Dict) -> Dict:
        """Create detailed action plan from TODO analysis"""
        logger.info("Creating action plan from TODO analysis")
        
        # Build comprehensive context
        context = self._build_planning_context(analysis)
        
        # Step 1: Create detailed plan
        plan = self._generate_detailed_plan(context, analysis['todo_content'])
        
        # Step 2: Extract branch name from plan
        branch_name = self._extract_branch_name(plan)
        
        # Step 3: Collect files to work on
        files_to_modify = self._collect_files_interactive(plan, analysis['todo_content'])
        
        return {
            "plan": plan,
            "branch_name": branch_name,
            "files_to_modify": files_to_modify,
            "todo_excerpt": analysis['todo_content'][:500]
        }
    
    def _build_planning_context(self, analysis: Dict) -> str:
        """Build context from all analysis components"""
        parts = [
            "=== TODO CONTENTS ===",
            analysis['todo_content'][:2000],
            "",
            "=== SUMMARY OF CODE ANALYSIS ===",
            analysis['summary'],
            "",
            "=== FILE STRUCTURE ===",
            analysis['file_tree'][:1000],
            "",
            "=== KEY INSIGHTS FROM CHUNKS ==="
        ]
        
        # Add first few chunk responses
        for i, response in enumerate(analysis['chunk_responses'][:3], 1):
            parts.append(f"Chunk {i}: {response[:500]}...")
        
        return "\n".join(parts)
    
    def _generate_detailed_plan(self, context: str, todo_content: str) -> str:
        """Generate detailed implementation plan"""
        prompt = """Based on the TODO and code analysis, create a detailed action plan.

The plan should:
1. Select ONE small, bite-sized task from the TODO that can be completed in one sitting
2. List specific files that need to be created/modified/deleted
3. Describe what changes to make in each file
4. Define success criteria
5. Suggest a branch name

Be specific and actionable. Focus on making incremental progress toward the TODO goals."""
        
        result = self.ai.open(
            prompt=prompt,
            context=context,
            context_name="action_planning"
        )
        
        return result.content
    
    def _extract_branch_name(self, plan: str) -> str:
        """Extract or generate branch name from plan"""
        prompt = """Based on this plan, suggest a git branch name.

Rules:
- Use format: type/description (e.g., feat/add-auth, fix/memory-leak)
- Lowercase with hyphens
- Max 30 characters
- Be specific to the task

Respond with ONLY the branch name, no explanation."""
        
        result = self.ai.open(
            prompt=prompt,
            context=f"Plan excerpt: {plan[:1000]}",
            context_name="branch_naming"
        )
        
        branch = result.content.strip().lower().replace(' ', '-')
        
        # Validate and sanitize
        if '/' not in branch:
            branch = f"feat/{branch}"
        
        return branch[:30]  # Enforce max length
    
    def _collect_files_interactive(self, plan: str, todo_content: str) -> List[Dict]:
        """Interactively collect files to work on"""
        logger.info("Collecting files to modify through interactive process")
        
        files = []
        max_iterations = 20  # Safety limit
        
        context = f"""Action Plan:
{plan}

TODO excerpt:
{todo_content[:500]}

Files collected so far: {[f['path'] for f in files]}"""
        
        for i in range(max_iterations):
            # Ask for next file or DONE
            result = self.ai.choice(
                question=f"File #{i+1}: Name the next file to work on (with path) or say you're done",
                options=[
                    "DONE - No more files needed",
                    "src/newfile.py",
                    "docs/update.md", 
                    "config/settings.json",
                    "tests/test_feature.py"
                ],
                context=context
            )
            
            if "DONE" in result.value:
                logger.info(f"File collection complete. Total files: {len(files)}")
                break
            
            # Parse the file path
            file_path = self._parse_file_path(result.value)
            
            # Confirm the path
            confirm_result = self.ai.choice(
                question=f"Confirm this file path is correct: {file_path}",
                options=["YES - Correct", "NO - Try again"],
                context=f"Intended file from plan: {result.value}"
            )
            
            if "YES" in confirm_result.value:
                # Determine operation type
                operation = self._determine_operation(file_path, plan)
                
                files.append({
                    "path": file_path,
                    "operation": operation,
                    "reason": f"Part of plan to implement TODO task"
                })
                
                # Update context for next iteration
                context = f"""Action Plan:
{plan}

TODO excerpt:
{todo_content[:500]}

Files collected so far: {[f['path'] for f in files]}"""
                
                logger.info(f"Added file: {file_path} ({operation})")
            else:
                logger.info("Retrying file path input")
        
        return files
    
    def _parse_file_path(self, ai_response: str) -> str:
        """Parse file path from AI response"""
        # Remove common prefixes and clean up
        path = ai_response.strip()
        
        # Remove option markers if present
        for prefix in ["src/", "docs/", "config/", "tests/", "lib/"]:
            if prefix in path:
                # Extract everything after the first occurrence
                idx = path.find(prefix)
                path = path[idx:]
                break
        
        # Clean up the path
        path = path.replace(" ", "_").replace("(", "").replace(")", "")
        
        # Ensure it has an extension
        if '.' not in path.split('/')[-1]:
            # Guess extension based on directory
            if 'test' in path:
                path += '.py'
            elif 'doc' in path:
                path += '.md'
            elif 'config' in path or 'settings' in path:
                path += '.json'
            else:
                path += '.py'  # Default
        
        return path
    
    def _determine_operation(self, file_path: str, plan: str) -> str:
        """Determine if file should be created, modified, or deleted"""
        result = self.ai.choice(
            question=f"What operation for {file_path}?",
            options=["CREATE", "MODIFY", "DELETE"],
            context=f"Based on plan: {plan[:500]}"
        )
        
        return result.value