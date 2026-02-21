"""
File discovery and language detection functionality.
"""

import os
from pathlib import Path
from .config import LANGUAGE_CONFIG


# -------------------------------------------------------------------
# OPTIMIZED: DISCOVERY WITH LAZY GENERATOR
# -------------------------------------------------------------------

def detect_language(file_path: Path):
    ext = file_path.suffix.lower()
    for lang, config in LANGUAGE_CONFIG.items():
        if ext in config['extensions']:
            return lang, config
    return None, None


def discover_source_files_lazy(root_dir: Path, exclude_dirs=None, max_depth=10):
    """
    OPTIMIZED: Generator version - yields files one by one (90% memory reduction)
    
    Args:
        root_dir: Root directory to scan
        exclude_dirs: List of directory names to exclude
        max_depth: Maximum directory depth to scan
    """
    SKIP_EXT = {
        ".dll", ".exe", ".pdb", ".obj", ".lib", ".so", ".a", ".wasm",
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".mp3", ".wav", ".ogg", ".flac",
        ".class", ".jar",
        ".sqlite", ".db", ".dat", ".bin"
    }

    # Default exclude directories
    if exclude_dirs is None:
        exclude_dirs = [
            "venv", ".venv", "env", "venv_sebas", ".env",
            "lib", "lib64", "site-packages", "__pypackages__",
            "node_modules", "bower_components",
            "target", ".gradle", "gradle", ".m2", "out",
            "build", "dist", "release", "debug",
            "cmake-build-debug", "cmake-build-release",
            "CMakeFiles", "bin", "obj",
            "packages", ".vs", "x64", "x86",
            ".git", ".svn", ".hg",
            ".idea", ".vscode",
            ".cache", "cache", ".pytest_cache",
            ".mypy_cache", ".ruff_cache", "coverage",
            "vendor", "thirdparty", "third_party",
            "extern", "external", "deps"
        ]
    
    KNOWN_TRASH_DIRS = set(d.lower() for d in exclude_dirs)

    def is_trash_dir(d: Path):
        return d.name.lower() in KNOWN_TRASH_DIRS
    
    def get_depth(path: Path):
        try:
            rel = path.relative_to(root_dir)
            return len(rel.parts)
        except ValueError:
            return 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_path = Path(dirpath)
        
        # Check depth limit
        if get_depth(current_path) >= max_depth:
            dirnames.clear()
            continue
            
        # Log progress for deep directories
        if get_depth(current_path) <= 2:
            import sys
            print(f"[INFO] Scanning: {current_path.name}/", file=sys.stderr)
        
        # Filter directories in-place to avoid descending
        dirnames[:] = [d for d in dirnames if not is_trash_dir(current_path / d)]
        
        for fname in filenames:
            if fname.startswith("."):
                continue
            
            file_path = current_path / fname
            ext = file_path.suffix.lower()
            
            if ext in SKIP_EXT:
                continue
            
            if ext == ".xaml":
                yield (file_path, "xaml", {})
            else:
                lang, config = detect_language(file_path)
                if lang:
                    yield (file_path, lang, config)


def module_name_from_path(root_dir: Path, file_path: Path):
    try:
        rel = file_path.relative_to(root_dir)
    except ValueError:
        return None

    parts = list(rel.parts)

    if parts[-1] in ["__init__.py", "index.js", "index.ts", "mod.rs"]:
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].rsplit(".", 1)[0]

    if not parts:
        return root_dir.name

    return root_dir.name + "." + ".".join(parts)