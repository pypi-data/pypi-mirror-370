"""
AI Output Parser for GitLlama
Extracts clean code content from AI responses with markdown blocks and thinking tags
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Result of parsing AI output for file content"""
    content: str
    was_trimmed: bool
    trimming_details: Dict[str, Any]
    original_length: int
    final_length: int


class AIOutputParser:
    """Parses AI output to extract clean code content for file writing"""
    
    def __init__(self):
        # Regex patterns for different content blocks
        self.thinking_pattern = re.compile(r'<thinking>.*?</thinking>', re.DOTALL | re.IGNORECASE)
        self.code_block_pattern = re.compile(r'```(?:\w+)?\s*\n(.*?)\n```', re.DOTALL)
        self.single_line_code_pattern = re.compile(r'`([^`]+)`')
        
        # Common language extensions and their identifiers
        self.language_mapping = {
            'python': ['.py'],
            'javascript': ['.js', '.mjs'], 
            'typescript': ['.ts'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cxx', '.cc'],
            'c': ['.c'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt'],
            'scala': ['.scala'],
            'html': ['.html', '.htm'],
            'css': ['.css'],
            'scss': ['.scss'],
            'sass': ['.sass'],
            'xml': ['.xml'],
            'json': ['.json'],
            'yaml': ['.yaml', '.yml'],
            'toml': ['.toml'],
            'markdown': ['.md'],
            'dockerfile': ['Dockerfile'],
            'shell': ['.sh', '.bash'],
            'sql': ['.sql'],
            'r': ['.r', '.R']
        }
    
    def parse_for_file_content(self, ai_output: str, target_file_path: str = "") -> ParseResult:
        """
        Parse AI output to extract clean file content.
        
        Args:
            ai_output: Raw AI response text
            target_file_path: Path of the target file to help with language detection
            
        Returns:
            ParseResult with cleaned content and trimming information
        """
        original_length = len(ai_output)
        trimming_details = {
            'removed_thinking_blocks': False,
            'removed_extra_chatter': False,
            'extracted_from_code_block': False,
            'code_blocks_found': 0,
            'thinking_blocks_found': 0
        }
        
        logger.info(f"🔍 Parsing AI output for file content ({original_length} chars)")
        
        # Step 1: Remove thinking blocks
        thinking_matches = self.thinking_pattern.findall(ai_output)
        if thinking_matches:
            trimming_details['thinking_blocks_found'] = len(thinking_matches)
            trimming_details['removed_thinking_blocks'] = True
            ai_output = self.thinking_pattern.sub('', ai_output)
            logger.info(f"🧠 Removed {len(thinking_matches)} thinking blocks")
        
        # Step 2: Look for code blocks
        code_blocks = self.code_block_pattern.findall(ai_output)
        trimming_details['code_blocks_found'] = len(code_blocks)
        
        if code_blocks:
            # Choose the best code block based on file extension
            selected_content = self._select_best_code_block(code_blocks, ai_output, target_file_path)
            trimming_details['extracted_from_code_block'] = True
            logger.info(f"📝 Extracted content from code block ({len(code_blocks)} found)")
        else:
            # No code blocks found, check if this looks like raw code
            selected_content = self._extract_raw_code_content(ai_output)
            if selected_content != ai_output.strip():
                trimming_details['removed_extra_chatter'] = True
                logger.info("✂️ Trimmed extra chatter from raw content")
        
        # Step 3: Final cleanup
        final_content = self._final_cleanup(selected_content)
        final_length = len(final_content)
        
        was_trimmed = any([
            trimming_details['removed_thinking_blocks'],
            trimming_details['removed_extra_chatter'], 
            trimming_details['extracted_from_code_block']
        ])
        
        if was_trimmed:
            logger.info(f"✅ Content parsed: {original_length} → {final_length} chars (trimmed: {was_trimmed})")
        else:
            logger.info(f"✅ Content parsed: {final_length} chars (no trimming needed)")
        
        return ParseResult(
            content=final_content,
            was_trimmed=was_trimmed,
            trimming_details=trimming_details,
            original_length=original_length,
            final_length=final_length
        )
    
    def _select_best_code_block(self, code_blocks: list, full_text: str, target_file_path: str) -> str:
        """Select the most appropriate code block based on context"""
        if len(code_blocks) == 1:
            return code_blocks[0].strip()
        
        # Get file extension
        file_ext = self._get_file_extension(target_file_path)
        
        # Find language-specific code blocks
        full_matches = list(self.code_block_pattern.finditer(full_text))
        
        for i, match in enumerate(full_matches):
            # Extract the language identifier from the match itself
            match_text = full_text[match.start():match.end()]
            lang_match = re.search(r'```(\w+)', match_text)
            
            if lang_match:
                lang = lang_match.group(1).lower()
                if self._language_matches_extension(lang, file_ext):
                    logger.info(f"📋 Selected code block with language '{lang}' matching '{file_ext}'")
                    return code_blocks[i].strip()
        
        # Default to the largest code block
        largest_block = max(code_blocks, key=len)
        logger.info(f"📋 Selected largest code block ({len(largest_block)} chars)")
        return largest_block.strip()
    
    def _extract_raw_code_content(self, text: str) -> str:
        """Extract code-like content when no markdown blocks are present"""
        lines = text.split('\n')
        
        # Look for common patterns that indicate code vs explanation
        code_lines = []
        in_code_section = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if in_code_section:
                    code_lines.append(line)
                continue
            
            # Detect if this line looks like code
            looks_like_code = self._line_looks_like_code(stripped)
            
            # Detect if this line is explanatory text
            looks_like_explanation = self._line_looks_like_explanation(stripped)
            
            if looks_like_code and not looks_like_explanation:
                in_code_section = True
                code_lines.append(line)
            elif in_code_section and not looks_like_explanation:
                # Continue adding lines if we're in a code section
                code_lines.append(line)
            elif looks_like_explanation and in_code_section:
                # Stop if we hit explanatory text after code
                break
        
        if code_lines:
            result = '\n'.join(code_lines).strip()
            logger.info(f"🔍 Extracted raw code content ({len(code_lines)} lines)")
            return result
        
        # Fallback: return trimmed original
        return text.strip()
    
    def _line_looks_like_code(self, line: str) -> bool:
        """Heuristic to determine if a line looks like code"""
        # Common code indicators
        code_indicators = [
            line.startswith(('def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'try:', 'except:')),  # Python
            line.startswith(('function ', 'const ', 'let ', 'var ', 'if (', 'for (', 'while (')),  # JavaScript
            line.startswith(('public ', 'private ', 'protected ', 'static ', 'final ')),  # Java/C#
            line.startswith(('<?php', '<?=')),  # PHP
            line.startswith('#include'),  # C/C++
            re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=:]\s*', line),  # Variable assignment
            re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\)\s*[{:]?\s*$', line),  # Function calls
            '{' in line or '}' in line,  # Braces
            line.count('"') >= 2 or line.count("'") >= 2,  # String literals
            re.search(r'[;{}()\[\]]', line),  # Common code punctuation
        ]
        
        return any(code_indicators)
    
    def _line_looks_like_explanation(self, line: str) -> bool:
        """Heuristic to determine if a line is explanatory text"""
        explanation_indicators = [
            line.startswith(('Here', 'This', 'The ', 'To ', 'You ', 'I ', 'We ', 'Now ', 'First', 'Next', 'Finally')),
            line.endswith(('.', '!', '?', ':')),
            'will' in line or 'should' in line or 'can' in line,
            len(line.split()) > 8,  # Long sentences are usually explanations
            not re.search(r'[;{}()\[\]=]', line),  # Lacks code punctuation
        ]
        
        return any(explanation_indicators)
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension from path"""
        if not file_path:
            return ""
        
        if '.' in file_path:
            return '.' + file_path.split('.')[-1].lower()
        
        # Handle special cases like Dockerfile
        filename = file_path.split('/')[-1]
        if filename.lower() in ['dockerfile', 'makefile']:
            return filename.lower()
        
        return ""
    
    def _language_matches_extension(self, language: str, extension: str) -> bool:
        """Check if a language identifier matches a file extension"""
        if not extension:
            return False
        
        language = language.lower()
        extension = extension.lower()
        
        # Direct match
        if language in self.language_mapping:
            return extension in self.language_mapping[language]
        
        # Fuzzy matching for common cases
        fuzzy_matches = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'sh': 'shell',
            'bash': 'shell',
            'yml': 'yaml',
        }
        
        for pattern, lang in fuzzy_matches.items():
            if pattern in language and extension in self.language_mapping.get(lang, []):
                return True
        
        return False
    
    def _final_cleanup(self, content: str) -> str:
        """Final cleanup of the extracted content"""
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Remove any remaining markdown artifacts
        content = re.sub(r'^```\w*\s*\n?', '', content)
        content = re.sub(r'\n?```\s*$', '', content)
        
        # Remove excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def get_trimming_emoji_indicator(self, parse_result: ParseResult) -> str:
        """Get emoji indicator for whether content was trimmed"""
        if parse_result.was_trimmed:
            return "✂️"  # Scissors emoji for "yes, trimmed"
        else:
            return "📄"  # Document emoji for "no, not trimmed"
    
    def get_detailed_trimming_info(self, parse_result: ParseResult) -> str:
        """Get detailed information about what was trimmed"""
        details = []
        
        if parse_result.trimming_details['removed_thinking_blocks']:
            count = parse_result.trimming_details['thinking_blocks_found']
            details.append(f"Removed {count} thinking block(s)")
        
        if parse_result.trimming_details['extracted_from_code_block']:
            count = parse_result.trimming_details['code_blocks_found']
            details.append(f"Extracted from {count} code block(s)")
        
        if parse_result.trimming_details['removed_extra_chatter']:
            details.append("Removed extra explanatory text")
        
        if not details:
            return "No trimming needed"
        
        size_reduction = parse_result.original_length - parse_result.final_length
        details.append(f"Size: {parse_result.original_length} → {parse_result.final_length} chars (-{size_reduction})")
        
        return "; ".join(details)


# Global instance
ai_output_parser = AIOutputParser()