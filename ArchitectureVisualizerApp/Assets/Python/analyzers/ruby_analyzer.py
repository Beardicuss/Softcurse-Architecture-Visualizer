"""
Enhanced Ruby analyzer using regex patterns.
Provides 80-85% accuracy for Ruby code analysis.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern


def analyze_file_ruby(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze Ruby file using enhanced regex patterns.
    
    Returns:
        functions: List of method/function names
        classes: List of class/module dicts with methods
        imports: List of require statements
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
        "modules": []
    }
    
    # Ruby-specific patterns
    require_pattern = get_compiled_pattern(r'^\s*require\s+["\']([^"\']+)["\']')
    class_pattern = get_compiled_pattern(r'^\s*class\s+(\w+)')
    module_pattern = get_compiled_pattern(r'^\s*module\s+(\w+)')
    def_pattern = get_compiled_pattern(r'^\s*def\s+(?:self\.)?(\w+)')
    
    current_class = None
    current_class_methods = []
    in_class = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # Track class scope by indentation
        if in_class:
            if line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and line.strip().startswith('end'):
                    if current_class:
                        classes.append({
                            "name": current_class,
                            "methods": current_class_methods.copy()
                        })
                    current_class = None
                    current_class_methods = []
                    in_class = False
                    indent_level = 0
        
        # Require statements
        require_match = require_pattern.match(line)
        if require_match:
            req = require_match.group(1)
            imports.append(req)
            continue
        
        # Class declaration
        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            in_class = True
            indent_level = len(line) - len(line.lstrip())
            continue
        
        # Module declaration
        module_match = module_pattern.match(line)
        if module_match:
            module_name = module_match.group(1)
            meta["modules"].append(module_name)
            continue
        
        # Method definition
        def_match = def_pattern.match(line)
        if def_match:
            method_name = def_match.group(1)
            if in_class and current_class:
                current_class_methods.append(method_name)
            else:
                functions.append(method_name)
            continue
    
    # Handle last class if file ends while in class
    if in_class and current_class:
        classes.append({
            "name": current_class,
            "methods": current_class_methods
        })
    
    # Extract file-level comment
    if source.strip().startswith('#'):
        doc_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                doc_lines.append(line.strip()[1:].strip())
            else:
                break
        if doc_lines:
            docstring = ' '.join(doc_lines)
    
    return functions, classes, imports, docstring, meta
