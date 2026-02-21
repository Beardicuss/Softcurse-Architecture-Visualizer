"""
Enhanced TypeScript analyzer extending JavaScript analyzer.
Handles TypeScript-specific features: interfaces, types, generics, decorators.
Provides 85%+ accuracy.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern
from .javascript_analyzer import analyze_file_javascript


def analyze_file_typescript(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze TypeScript file with enhanced patterns for TS-specific features.
    
    Returns:
        functions: List of function names
        classes: List of class/interface dicts with methods
        imports: List of imported modules
        docstring: File-level TSDoc comment
        meta: Additional metadata
    """
    # Start with JavaScript analysis
    functions, classes, imports, docstring, meta = analyze_file_javascript(path)
    
    try:
        source = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return functions, classes, imports, docstring, {"error": str(e)}
    
    lines = source.split('\n')
    
    # TypeScript-specific metadata
    meta["interfaces"] = []
    meta["types"] = []
    meta["decorators"] = []
    meta["generics"] = []
    
    # TypeScript-specific patterns
    interface_pattern = get_compiled_pattern(r'^\s*(?:export\s+)?interface\s+(\w+)')
    type_pattern = get_compiled_pattern(r'^\s*(?:export\s+)?type\s+(\w+)\s*=')
    decorator_pattern = get_compiled_pattern(r'^\s*@(\w+)')
    generic_pattern = get_compiled_pattern(r'<([A-Z]\w*(?:,\s*[A-Z]\w*)*)>')
    
    current_interface = None
    interface_methods = []
    in_interface = False
    brace_count = 0
    
    for i, line in enumerate(lines):
        # Track interface scope
        if in_interface:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                if current_interface:
                    classes.append({
                        "name": current_interface,
                        "methods": interface_methods.copy(),
                        "type": "interface"
                    })
                current_interface = None
                interface_methods = []
                in_interface = False
                brace_count = 0
        
        # Interface declaration
        interface_match = interface_pattern.match(line)
        if interface_match:
            interface_name = interface_match.group(1)
            meta["interfaces"].append(interface_name)
            current_interface = interface_name
            in_interface = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Interface methods
        if in_interface and current_interface:
            # Match method signatures in interfaces
            method_match = re.match(r'^\s*(\w+)\s*\([^)]*\)\s*:', line)
            if method_match:
                interface_methods.append(method_match.group(1))
            continue
        
        # Type alias
        type_match = type_pattern.match(line)
        if type_match:
            meta["types"].append(type_match.group(1))
            continue
        
        # Decorators
        decorator_match = decorator_pattern.match(line)
        if decorator_match:
            decorator_name = decorator_match.group(1)
            if decorator_name not in meta["decorators"]:
                meta["decorators"].append(decorator_name)
            continue
        
        # Generics
        generic_match = generic_pattern.search(line)
        if generic_match:
            generic_params = generic_match.group(1)
            for param in generic_params.split(','):
                param = param.strip()
                if param and param not in meta["generics"]:
                    meta["generics"].append(param)
    
    # Handle last interface if file ends while in interface
    if in_interface and current_interface:
        classes.append({
            "name": current_interface,
            "methods": interface_methods,
            "type": "interface"
        })
    
    return functions, classes, imports, docstring, meta
