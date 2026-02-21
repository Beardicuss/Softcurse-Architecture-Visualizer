"""
Analysis dispatcher that routes files to appropriate analyzers.
"""

from pathlib import Path
from typing import Optional
from core.config import LANGUAGE_CONFIG
from .python_analyzer import analyze_file_python
from .csharp_analyzer import analyze_file_csharp_advanced
from .xaml_analyzer import analyze_file_xaml
from .java_analyzer import analyze_file_java
from .javascript_analyzer import analyze_file_javascript
from .typescript_analyzer import analyze_file_typescript
from .php_analyzer import analyze_file_php
from .go_analyzer import analyze_file_go
from .rust_analyzer import analyze_file_rust
from .ruby_analyzer import analyze_file_ruby
from .swift_analyzer import analyze_file_swift
from .kotlin_analyzer import analyze_file_kotlin
from .dart_analyzer import analyze_file_dart
from .cpp_analyzer import analyze_file_cpp
from .generic_analyzer import analyze_file_generic


def analyze_file_dispatch(path: Path, lang: str, config: Optional[dict] = None):
    """Unified file analysis dispatcher with error handling"""
    if config is None:
        config = LANGUAGE_CONFIG.get(lang, {})
    
    try:
        if lang == "python":
            return analyze_file_python(path)
        elif lang == "csharp":
            return analyze_file_csharp_advanced(path, config)
        elif lang == "xaml":
            return analyze_file_xaml(path)
        elif lang == "java":
            return analyze_file_java(path)
        elif lang == "javascript":
            return analyze_file_javascript(path)
        elif lang == "typescript":
            return analyze_file_typescript(path)
        elif lang == "php":
            return analyze_file_php(path)
        elif lang == "go":
            return analyze_file_go(path)
        elif lang == "rust":
            return analyze_file_rust(path)
        elif lang == "ruby":
            return analyze_file_ruby(path)
        elif lang == "swift":
            return analyze_file_swift(path)
        elif lang == "kotlin":
            return analyze_file_kotlin(path)
        elif lang == "dart":
            return analyze_file_dart(path)
        elif lang == "cpp":
            return analyze_file_cpp(path)
        else:
            return analyze_file_generic(path, lang, config)
    except Exception as e:
        print(f"[ERROR] Analysis failed for {path}: {e}")
        return [], [], [], None, {"error": str(e)}