"""
AI Decision Formatter for GitLlama
Special formatting for AI responses with single-word decision parsing
"""

import logging
import re
from typing import List, Tuple, Dict, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class AIDecisionFormatter:
    """Formats AI prompts and parses single-word responses with fuzzy matching"""
    
    def __init__(self, report_generator=None):
        self.decision_history: List[Dict[str, Any]] = []
        self.report_generator = report_generator
    
    def format_decision_prompt(self, context: str, question: str, options: List[str], 
                             additional_context: str = "") -> str:
        """Format a special decision prompt that forces single-word responses.
        
        Args:
            context: The context for the decision
            question: The specific question being asked
            options: List of valid single-word options
            additional_context: Any extra context to include
            
        Returns:
            Formatted prompt string
        """
        options_str = " | ".join(options)
        
        prompt = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                              🤖 AI DECISION REQUIRED                              ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ CONTEXT:                                                                         ║
║ {context[:70]}{'...' if len(context) > 70 else ''}                                                        ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ QUESTION:                                                                        ║
║ {question[:70]}{'...' if len(question) > 70 else ''}                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ VALID OPTIONS: {options_str:<58} ║
╚══════════════════════════════════════════════════════════════════════════════════╝

{additional_context}

CRITICAL INSTRUCTIONS:
- You MUST respond with EXACTLY ONE WORD from the options above
- Do NOT provide explanations, reasoning, or additional text
- Do NOT use punctuation or formatting
- The response must be one of: {options_str}

Your single-word decision:"""
        
        return prompt
    
    def parse_single_word_response(self, response: str, valid_options: List[str], 
                                 min_similarity: float = 0.6) -> Tuple[str, float]:
        """Parse AI response and find best matching option using fuzzy matching.
        
        Args:
            response: The AI's response text
            valid_options: List of valid options to match against
            min_similarity: Minimum similarity score to consider a match
            
        Returns:
            Tuple of (matched_option, confidence_score)
        """
        # Clean the response - extract the first word-like token
        cleaned_response = re.sub(r'[^\w\s]', '', response.strip().lower())
        first_word = cleaned_response.split()[0] if cleaned_response.split() else ""
        
        if not first_word:
            logger.warning(f"No word found in response: '{response}'")
            return valid_options[0], 0.0
        
        # Find best match using fuzzy matching
        best_match = ""
        best_score = 0.0
        
        for option in valid_options:
            # Calculate similarity
            similarity = SequenceMatcher(None, first_word, option.lower()).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = option
        
        # Check if we have a good enough match
        if best_score < min_similarity:
            logger.warning(f"Low confidence match: '{first_word}' -> '{best_match}' (score: {best_score:.2f})")
        
        logger.info(f"AI Response: '{first_word}' -> Matched: '{best_match}' (confidence: {best_score:.2f})")
        
        return best_match, best_score
    
    def make_ai_decision(self, client, model: str, context: str, question: str, 
                        options: List[str], additional_context: str = "") -> Tuple[str, float]:
        """Make a single AI decision with special formatting and parsing.
        
        Args:
            client: The AI client to use
            model: Model name
            context: Context for the decision
            question: Question to ask
            options: Valid response options
            additional_context: Additional context
            
        Returns:
            Tuple of (selected_option, confidence_score)
        """
        # Format the special prompt
        prompt = self.format_decision_prompt(context, question, options, additional_context)
        
        # Log the formatted prompt
        logger.info("╔" + "═" * 80 + "╗")
        logger.info("║" + " AI DECISION PROMPT ".center(80) + "║")
        logger.info("╚" + "═" * 80 + "╝")
        
        # Make the AI call
        messages = [{"role": "user", "content": prompt}]
        response = ""
        
        for chunk in client.chat_stream(model, messages, context_name="decision_formatting"):
            response += chunk
        
        # Parse the response
        selected_option, confidence = self.parse_single_word_response(response, options)
        
        # Store in history
        decision_record = {
            "context": context,
            "question": question,
            "options": options,
            "raw_response": response.strip(),
            "selected_option": selected_option,
            "confidence": confidence
        }
        self.decision_history.append(decision_record)
        
        # Hook into report generator
        if self.report_generator:
            self.report_generator.add_ai_decision(
                context=response.strip(),  # Store raw response in context for tooltip
                question=question,
                options=options,
                selected=selected_option,
                confidence=confidence,
                reasoning=f"Based on provided options with {confidence:.0%} confidence"
            )
        
        # Log the result with special formatting
        logger.info("╔" + "═" * 80 + "╗")
        logger.info("║" + f" AI DECISION RESULT ".center(80) + "║")
        logger.info("║" + f" Selected: {selected_option} (Confidence: {confidence:.2f}) ".center(80) + "║")
        logger.info("╚" + "═" * 80 + "╝")
        
        return selected_option, confidence
    
    def make_multiple_decisions(self, client, model: str, decisions: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """Make multiple AI decisions in sequence.
        
        Args:
            client: The AI client
            model: Model name
            decisions: List of decision dictionaries with keys:
                      - context, question, options, additional_context (optional)
        
        Returns:
            List of (selected_option, confidence) tuples
        """
        results = []
        
        for i, decision in enumerate(decisions, 1):
            logger.info(f"Making AI decision {i}/{len(decisions)}")
            
            result = self.make_ai_decision(
                client=client,
                model=model,
                context=decision['context'],
                question=decision['question'],
                options=decision['options'],
                additional_context=decision.get('additional_context', '')
            )
            
            results.append(result)
        
        return results
    
    def get_decision_summary(self) -> str:
        """Get a summary of all decisions made.
        
        Returns:
            Formatted summary string
        """
        if not self.decision_history:
            return "No decisions made yet."
        
        summary_lines = ["AI Decision Summary:", "=" * 50]
        
        for i, decision in enumerate(self.decision_history, 1):
            summary_lines.append(f"{i}. {decision['question']}")
            summary_lines.append(f"   Options: {', '.join(decision['options'])}")
            summary_lines.append(f"   Selected: {decision['selected_option']} (confidence: {decision['confidence']:.2f})")
            summary_lines.append("")
        
        return "\n".join(summary_lines)