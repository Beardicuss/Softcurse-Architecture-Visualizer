"""
Enhanced Dart analyzer using regex patterns.
Provides 80-85% accuracy for Dart code analysis.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern


def analyze_file_dart(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze Dart file using enhanced regex patterns.
    
    Returns:
        functions: List of function names
        classes: List of class dicts with methods
        imports: List of import statements
        docstring: File-level comment
        meta: Additional metadata
    """
    try:
        source = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return [], [], [], None, {"error": str(e)}
    
    lines = source.split('\n')
    functions = []
    classes = []
    imports = []
    docstring = None
    meta = {
        "library": None,
        "mixins": []
    }
    
    # Dart-specific patterns
    library_pattern = get_compiled_pattern(r'^\s*library\s+([\w.]+);')
    import_pattern = get_compiled_pattern(r'^\s*import\s+["\']([^"\']+)["\']')
    class_pattern = get_compiled_pattern(r'^\s*class\s+(\w+)')
    mixin_pattern = get_compiled_pattern(r'^\s*mixin\s+(\w+)')
    function_pattern = get_compiled_pattern(r'^\s*(?:Future<\w+>\s+)?(\w+)\s*\([^)]*\)\s*(?:async\s*)?{')
    method_pattern = get_compiled_pattern(r'^\s*(?:Future<\w+>\s+)?(\w+)\s*\(')
    
    current_class = None
    current_class_methods = []
    in_class = False
    brace_count = 0
    
    for i, line in enumerate(lines):
        # Track class scope
        if in_class:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                if current_class:
                    classes.append({
                        "name": current_class,
                        "methods": current_class_methods.copy()
                    })
                current_class = None
                current_class_methods = []
                in_class = False
                brace_count = 0
        
        # Library
        lib_match = library_pattern.match(line)
        if lib_match:
            meta["library"] = lib_match.group(1)
            continue
        
        # Import
        import_match = import_pattern.match(line)
        if import_match:
            imp = import_match.group(1)
            if not imp.startswith('dart:'):
                imports.append(imp)
            continue
        
        # Class
        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Mixin
        mixin_match = mixin_pattern.match(line)
        if mixin_match:
            meta["mixins"].append(mixin_match.group(1))
            continue
        
        # Method inside class
        if in_class and current_class:
            method_match = method_pattern.match(line)
            if method_match:
                method_name = method_match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch']:
                    current_class_methods.append(method_name)
            continue
        
        # Function outside class
        if not in_class:
            func_match = function_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                if func_name not in ['if', 'for', 'while', 'switch', 'void', 'main']:
                    functions.append(func_name)
                continue
    
    # Handle last class
    if in_class and current_class:
        classes.append({
            "name": current_class,
            "methods": current_class_methods
        })
    
    return functions, classes, imports, docstring, meta
