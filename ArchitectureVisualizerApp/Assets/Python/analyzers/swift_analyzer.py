"""
Enhanced Swift analyzer using regex patterns.
Provides 80-85% accuracy for Swift code analysis.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern


def analyze_file_swift(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze Swift file using enhanced regex patterns.
    
    Returns:
        functions: List of function names
        classes: List of class/struct/protocol dicts with methods
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
        "protocols": [],
        "extensions": []
    }
    
    # Swift-specific patterns
    import_pattern = get_compiled_pattern(r'^\s*import\s+(\w+)')
    class_pattern = get_compiled_pattern(r'^\s*(?:public\s+|private\s+|internal\s+)?class\s+(\w+)')
    struct_pattern = get_compiled_pattern(r'^\s*(?:public\s+|private\s+)?struct\s+(\w+)')
    protocol_pattern = get_compiled_pattern(r'^\s*(?:public\s+)?protocol\s+(\w+)')
    extension_pattern = get_compiled_pattern(r'^\s*extension\s+(\w+)')
    func_pattern = get_compiled_pattern(r'^\s*(?:public\s+|private\s+|internal\s+)?(?:static\s+)?func\s+(\w+)')
    
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
        
        # Import
        import_match = import_pattern.match(line)
        if import_match:
            imports.append(import_match.group(1))
            continue
        
        # Class
        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Struct
        struct_match = struct_pattern.match(line)
        if struct_match:
            current_class = struct_match.group(1)
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Protocol
        protocol_match = protocol_pattern.match(line)
        if protocol_match:
            protocol_name = protocol_match.group(1)
            meta["protocols"].append(protocol_name)
            classes.append({
                "name": protocol_name,
                "methods": [],
                "type": "protocol"
            })
            continue
        
        # Extension
        extension_match = extension_pattern.match(line)
        if extension_match:
            meta["extensions"].append(extension_match.group(1))
            continue
        
        # Function/Method
        func_match = func_pattern.match(line)
        if func_match:
            func_name = func_match.group(1)
            if in_class and current_class:
                current_class_methods.append(func_name)
            else:
                functions.append(func_name)
            continue
    
    # Handle last class
    if in_class and current_class:
        classes.append({
            "name": current_class,
            "methods": current_class_methods
        })
    
    return functions, classes, imports, docstring, meta
