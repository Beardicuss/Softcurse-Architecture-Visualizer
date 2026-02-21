import ast
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set
from core.config import STDLIB_EXCLUSIONS

def analyze_file_python(path: Path) -> Tuple[List[str], List[Dict[str, Any]], List[str], str, Dict[str, Any]]:
    """
    Analyze a Python file using the AST module for 100% accuracy.
    
    Returns:
        functions: List of function names
        classes: List of class dicts (name, methods)
        imports: List of imported module names
        docstring: Module-level docstring
        meta: Dictionary with extra details (calls, variables, decorators)
    """
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except Exception as e:
        print(f"[ERROR] Analysis failed for {path}: {e}")
        return [], [], [], None, {"error": str(e)}

    functions = []
    classes = []
    imports = []
    docstring = ast.get_docstring(tree)
    
    # Meta data
    meta = {
        "calls": set(),
        "variables": [],
        "decorators": set(),
        "async_functions": []
    }

    class Visitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                imports.append(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module:
                # e.g. from os import path -> 'os'
                # from myproject.models import User -> 'myproject.models'
                imports.append(node.module)
            elif node.level > 0:
                # Relative import, e.g. from . import utils or from .. import parent
                # We'll represent this as a relative path indicator
                prefix = "." * node.level
                # If there's a module after the dots, append it
                if node.module:
                    imports.append(prefix + node.module)
                else:
                    # Just dots, e.g. from . import something
                    # The imported names are in node.names, but for dependency graph we care about the base module
                    # We'll just record the relative indicator
                    imports.append(prefix)
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({"name": node.name, "methods": methods})
            
            # Collect decorators
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    meta["decorators"].add(dec.id)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    meta["decorators"].add(dec.func.id)
            
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            functions.append(node.name)
            # Collect decorators
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    meta["decorators"].add(dec.id)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    meta["decorators"].add(dec.func.id)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            functions.append(node.name)
            meta["async_functions"].append(node.name)
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    meta["decorators"].add(dec.id)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    meta["decorators"].add(dec.func.id)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                meta["calls"].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                meta["calls"].add(node.func.attr)
            self.generic_visit(node)
            
        def visit_Assign(self, node):
            # Global variables (only if at module level, but visitor visits all)
            # We can filter later or just collect interesting assignments
            if isinstance(node.targets[0], ast.Name):
                meta["variables"].append(node.targets[0].id)
            self.generic_visit(node)

    visitor = Visitor()
    visitor.visit(tree)

    # Filter out standard library imports
    stdlib_py = STDLIB_EXCLUSIONS.get('python', set())
    filtered_imports = []
    for imp in imports:
        # Check if it's a standard library import
        is_stdlib = False
        
        # Direct match or prefix match
        if imp in stdlib_py:
            is_stdlib = True
        else:
            # Check if it starts with a stdlib module (e.g., os.path starts with os)
            base_module = imp.split('.')[0] if '.' in imp else imp
            if base_module in stdlib_py:
                is_stdlib = True
        
        if not is_stdlib:
            filtered_imports.append(imp)
    
    imports = filtered_imports

    # Convert sets to lists for JSON serialization
    meta["calls"] = list(meta["calls"])
    meta["decorators"] = list(meta["decorators"])

    return functions, classes, imports, docstring, meta
