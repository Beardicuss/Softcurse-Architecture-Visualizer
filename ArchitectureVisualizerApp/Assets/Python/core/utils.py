"""
Utility functions for regex caching, profiling, and validation.
"""

import re
import sys
import cProfile
import pstats
from functools import wraps

# Try to import optional dependencies
try:
    from tqdm import tqdm  # type: ignore
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):  # type: ignore
        """Fallback when tqdm is not installed"""
        return iterable


# -------------------------------------------------------------------
# OPTIMIZED: GLOBAL COMPILED REGEX CACHE
# -------------------------------------------------------------------

COMPILED_PATTERNS = {}


def get_compiled_pattern(pattern, flags=0):
    """Cache compiled regex patterns for performance"""
    if not pattern:
        return None
    key = (pattern, flags)
    if key not in COMPILED_PATTERNS:
        COMPILED_PATTERNS[key] = re.compile(pattern, flags)
    return COMPILED_PATTERNS[key]


# -------------------------------------------------------------------
# PROFILING DECORATOR
# -------------------------------------------------------------------

def profile_function(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        print(f"\n{'='*70}")
        print(f"Performance Profile for {func.__name__}")
        print('='*70)
        stats.print_stats(20)
        
        return result
    return wrapper


# -------------------------------------------------------------------
# VALIDATION
# -------------------------------------------------------------------

def validate_environment():
    """Check if all dependencies are available"""
    issues = []
    
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    
    if issues:
        for issue in issues:
            print(f"[ERROR] {issue}")
        return False
    return True


# -------------------------------------------------------------------
# SECURITY
# -------------------------------------------------------------------

def is_safe_path(base_path, user_path):
    """
    Prevent path traversal attacks by ensuring user_path is within base_path.
    
    Args:
        base_path: The base directory (Path object)
        user_path: The user-provided path (Path object)
    
    Returns:
        bool: True if path is safe, False otherwise
    """
    from pathlib import Path
    try:
        base = Path(base_path).resolve()
        target = Path(user_path).resolve()
        return target.is_relative_to(base)
    except (ValueError, OSError):
        return False
