"""
Logging configuration for the project.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = __name__, debug: bool = False) -> logging.Logger:
    """
    Configure and return a project logger.
    
    Args:
        name: Logger name (usually __name__)
        debug: Enable debug level logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Format: [LEVEL] Message
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


# Default logger for the project
default_logger = setup_logger('visualizer')
