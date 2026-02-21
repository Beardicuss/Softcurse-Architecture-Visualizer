"""
XAML file analyzer for code-behind linking.
"""

from pathlib import Path
from core.utils import get_compiled_pattern


def analyze_file_xaml(path: Path):
    """XAML analyzer for code-behind linking"""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[ERROR] Analysis failed for {path}: {e}")
        return [], [], [], None, {"error": str(e)}

    # Extract x:Class attribute
    pattern = get_compiled_pattern(r'x:Class\s*=\s*["\']([^"\']+)["\']')
    x_class = None
    
    if pattern:
        match = pattern.search(text)
        if match:
            x_class = match.group(1)

    meta = {}
    if x_class:
        meta["x_class"] = x_class

    return [], [], [], None, meta
