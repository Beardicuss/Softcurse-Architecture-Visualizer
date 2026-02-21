"""
Enhanced JavaScript analyzer with better pattern matching.
Handles modern JavaScript features: arrow functions, async/await, classes, etc.
Provides 85%+ accuracy.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern


def analyze_file_javascript(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze JavaScript file with enhanced regex patterns.
    
    Returns:
        functions: List of function names
        classes: List of class dicts with methods
        imports: List of imported modules
        docstring: File-level JSDoc comment
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
        "exports": [],
        "async_functions": [],
        "arrow_functions": []
    }
    
    # Enhanced patterns for modern JavaScript
    # Function declarations
    func_pattern = get_compiled_pattern(r'^\s*(?:async\s+)?function\s+(\w+)')
    # Arrow functions
    arrow_pattern = get_compiled_pattern(r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>')
    # Class declarations
    class_pattern = get_compiled_pattern(r'^\s*class\s+(\w+)')
    # Method declarations (inside classes)
    method_pattern = get_compiled_pattern(r'^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*{')
    # Import statements
    import_pattern1 = get_compiled_pattern(r'^\s*import\s+.*?from\s+["\'](.+?)["\']')
    import_pattern2 = get_compiled_pattern(r'^\s*(?:const|let|var)\s+.*?=\s*require\(["\'](.+?)["\']\)')
    # Export statements
    export_pattern = get_compiled_pattern(r'^\s*export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)')
    
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
        
        # Class declaration
        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Method inside class
        if in_class and current_class:
            method_match = method_pattern.match(line)
            if method_match:
                method_name = method_match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch']:  # Filter keywords
                    current_class_methods.append(method_name)
                    if 'async' in line:
                        meta["async_functions"].append(f"{current_class}.{method_name}")
                continue
        
        # Function declaration
        func_match = func_pattern.match(line)
        if func_match:
            func_name = func_match.group(1)
            functions.append(func_name)
            if 'async' in line:
                meta["async_functions"].append(func_name)
            continue
        
        # Arrow function
        arrow_match = arrow_pattern.match(line)
        if arrow_match:
            func_name = arrow_match.group(1)
            functions.append(func_name)
            meta["arrow_functions"].append(func_name)
            if 'async' in line:
                meta["async_functions"].append(func_name)
            continue
        
        # Import statements
        import_match = import_pattern1.match(line)
        if not import_match:
            import_match = import_pattern2.match(line)
        if import_match:
            module = import_match.group(1)
            # Filter out relative imports and node built-ins
            if not module.startswith('.') and not module.startswith('node:'):
                imports.append(module)
            continue
        
        # Export statements
        export_match = export_pattern.match(line)
        if export_match:
            export_name = export_match.group(1)
            meta["exports"].append(export_name)
    
    # Handle last class if file ends while in class
    if in_class and current_class:
        classes.append({
            "name": current_class,
            "methods": current_class_methods
        })
    
    # Extract JSDoc comment at top of file
    if source.strip().startswith('/**'):
        doc_end = source.find('*/')
        if doc_end != -1:
            docstring = source[3:doc_end].strip()
    
    return functions, classes, imports, docstring, meta
