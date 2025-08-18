"""
GitLlama Configuration Module

Simple logging setup and basic utilities.
"""

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Setup basic logging for GitLlama."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s"
    )
    
    # Set specific logger levels
    logging.getLogger("gitllama").setLevel(level)