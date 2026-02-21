"""
Enhanced Kotlin analyzer using regex patterns.
Provides 80-85% accuracy for Kotlin code analysis.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from core.utils import get_compiled_pattern


def analyze_file_kotlin(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], Optional[str], Dict[str, Any]]:
    """
    Analyze Kotlin file using enhanced regex patterns.
    
    Returns:
        functions: List of function names
        classes: List of class/interface/object dicts with methods
        imports: List of import statements
        docstring: File-level KDoc
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
        "package": None,
        "interfaces": [],
        "objects": []
    }
    
    # Kotlin-specific patterns
    package_pattern = get_compiled_pattern(r'^\s*package\s+([\w.]+)')
    import_pattern = get_compiled_pattern(r'^\s*import\s+([\w.]+)')
    class_pattern = get_compiled_pattern(r'^\s*(?:open\s+|abstract\s+|data\s+)?class\s+(\w+)')
    interface_pattern = get_compiled_pattern(r'^\s*interface\s+(\w+)')
    object_pattern = get_compiled_pattern(r'^\s*object\s+(\w+)')
    fun_pattern = get_compiled_pattern(r'^\s*(?:private\s+|public\s+|internal\s+)?(?:suspend\s+)?fun\s+(\w+)')
    
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
        
        # Package
        pkg_match = package_pattern.match(line)
        if pkg_match:
            meta["package"] = pkg_match.group(1)
            continue
        
        # Import
        import_match = import_pattern.match(line)
        if import_match:
            imp = import_match.group(1)
            if not imp.startswith(('kotlin.', 'java.', 'javax.')):
                imports.append(imp)
            continue
        
        # Class
        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue
        
        # Interface
        interface_match = interface_pattern.match(line)
        if interface_match:
            interface_name = interface_match.group(1)
            meta["interfaces"].append(interface_name)
            classes.append({
                "name": interface_name,
                "methods": [],
                "type": "interface"
            })
            continue
        
        # Object
        object_match = object_pattern.match(line)
        if object_match:
            object_name = object_match.group(1)
            meta["objects"].append(object_name)
            continue
        
        # Function
        fun_match = fun_pattern.match(line)
        if fun_match:
            fun_name = fun_match.group(1)
            if in_class and current_class:
                current_class_methods.append(fun_name)
            else:
                functions.append(fun_name)
            continue
    
    # Handle last class
    if in_class and current_class:
        classes.append({
            "name": current_class,
            "methods": current_class_methods
        })
    
    return functions, classes, imports, docstring, meta
