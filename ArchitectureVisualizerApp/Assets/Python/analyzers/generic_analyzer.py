"""
Generic file analyzer using regex patterns for multiple languages.
"""

from pathlib import Path
from core.utils import get_compiled_pattern
from .python_analyzer import analyze_file_python


# Language-specific keyword sets to exclude from function call detection
from core.config import STDLIB_EXCLUSIONS

# Language-specific keyword sets to exclude from function call detection
LANGUAGE_KEYWORDS = {
    'javascript': {
        # Control flow
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'throw', 'try', 'catch', 'finally',
        # Type keywords
        'class', 'function', 'const', 'let', 'var', 'new', 'this', 'super',
        'extends', 'implements', 'interface', 'type', 'enum',
        # Async/await
        'async', 'await', 'Promise',
        # Common patterns
        'import', 'export', 'default', 'from', 'as',
        'typeof', 'instanceof', 'delete', 'void', 'yield',
        # Values
        'null', 'undefined', 'true', 'false', 'NaN', 'Infinity',
        # Common types
        'Array', 'Object', 'String', 'Number', 'Boolean', 'Symbol', 'BigInt',
        'Map', 'Set', 'WeakMap', 'WeakSet', 'Date', 'RegExp', 'Error',
        'Proxy', 'Reflect', 'JSON', 'Math', 'console',
    },
    'typescript': {
        # All JavaScript keywords
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'throw', 'try', 'catch', 'finally',
        'class', 'function', 'const', 'let', 'var', 'new', 'this', 'super',
        'extends', 'implements', 'interface', 'type', 'enum',
        'async', 'await', 'Promise',
        'import', 'export', 'default', 'from', 'as',
        'typeof', 'instanceof', 'delete', 'void', 'yield',
        'null', 'undefined', 'true', 'false', 'NaN', 'Infinity',
        'Array', 'Object', 'String', 'Number', 'Boolean', 'Symbol', 'BigInt',
        'Map', 'Set', 'WeakMap', 'WeakSet', 'Date', 'RegExp', 'Error',
        'Proxy', 'Reflect', 'JSON', 'Math', 'console',
        # TypeScript-specific
        'namespace', 'module', 'declare', 'abstract', 'readonly',
        'public', 'private', 'protected', 'static', 'override',
        'keyof', 'infer', 'is', 'asserts', 'any', 'unknown', 'never',
    },
    'java': {
        # Control flow
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'throw', 'try', 'catch', 'finally',
        # Type keywords
        'class', 'interface', 'enum', 'record', 'extends', 'implements',
        # Modifiers
        'public', 'private', 'protected', 'static', 'final', 'abstract',
        'synchronized', 'volatile', 'transient', 'native', 'strictfp',
        # Common patterns
        'new', 'this', 'super', 'instanceof', 'package', 'import',
        'void', 'var', 'assert',
        # Values
        'null', 'true', 'false',
        # Common types
        'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean',
        'Character', 'Byte', 'Short', 'Object', 'List', 'Map', 'Set',
        'ArrayList', 'HashMap', 'HashSet', 'Optional', 'Stream',
    },
    'go': {
        # Control flow
        'if', 'else', 'for', 'switch', 'case', 'break', 'continue',
        'return', 'goto', 'fallthrough', 'defer', 'panic', 'recover',
        # Type keywords
        'type', 'struct', 'interface', 'func', 'var', 'const',
        'package', 'import', 'map', 'chan', 'range', 'go', 'select',
        # Values
        'nil', 'true', 'false', 'iota',
        # Common types
        'string', 'int', 'int8', 'int16', 'int32', 'int64',
        'uint', 'uint8', 'uint16', 'uint32', 'uint64',
        'float32', 'float64', 'complex64', 'complex128',
        'bool', 'byte', 'rune', 'error',
    },
    'rust': {
        # Control flow
        'if', 'else', 'for', 'while', 'loop', 'match', 'break', 'continue',
        'return', 'yield',
        # Type keywords
        'fn', 'struct', 'enum', 'trait', 'impl', 'type', 'mod',
        'let', 'mut', 'const', 'static', 'use', 'pub', 'crate',
        # Ownership
        'ref', 'move', 'as', 'where', 'self', 'Self', 'super',
        'unsafe', 'extern', 'dyn', 'async', 'await',
        # Values
        'true', 'false', 'None', 'Some', 'Ok', 'Err',
        # Common types
        'String', 'Vec', 'Option', 'Result', 'Box', 'Rc', 'Arc',
        'HashMap', 'HashSet', 'BTreeMap', 'BTreeSet', 'new'
    },
    'cpp': {
        # Control flow
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'throw', 'try', 'catch', 'goto',
        # Type keywords
        'class', 'struct', 'union', 'enum', 'namespace', 'typedef',
        'typename', 'template', 'using',
        # Modifiers
        'public', 'private', 'protected', 'static', 'const', 'constexpr',
        'virtual', 'override', 'final', 'abstract', 'inline', 'extern',
        'mutable', 'volatile', 'explicit', 'friend',
        # Memory
        'new', 'delete', 'this', 'nullptr', 'sizeof', 'alignof',
        # Values
        'true', 'false', 'NULL',
        # Common types
        'void', 'bool', 'char', 'int', 'short', 'long', 'float', 'double',
        'auto', 'decltype', 'signed', 'unsigned',
        'string', 'vector', 'map', 'set', 'list', 'deque', 'array',
        'unique_ptr', 'shared_ptr', 'weak_ptr',
    },
    'php': {
        # Control flow
        'if', 'else', 'elseif', 'for', 'foreach', 'while', 'do', 'switch',
        'case', 'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally',
        # Type keywords
        'class', 'interface', 'trait', 'enum', 'extends', 'implements',
        'function', 'fn', 'namespace', 'use', 'as',
        # Modifiers
        'public', 'private', 'protected', 'static', 'final', 'abstract',
        'readonly', 'const', 'var',
        # Common patterns
        'new', 'clone', 'instanceof', 'yield', 'from',
        'echo', 'print', 'die', 'exit', 'eval', 'include', 'require',
        'include_once', 'require_once',
        # Values
        'null', 'true', 'false', 'self', 'parent', 'static',
        # Common types
        'array', 'string', 'int', 'float', 'bool', 'object', 'callable',
        'iterable', 'mixed', 'void', 'never',
    },
    'ruby': {
        # Control flow
        'if', 'elsif', 'else', 'unless', 'case', 'when', 'for', 'while',
        'until', 'break', 'next', 'redo', 'retry', 'return', 'yield',
        'raise', 'rescue', 'ensure', 'begin', 'end',
        # Type keywords
        'class', 'module', 'def', 'undef', 'alias', 'super', 'self',
        # Common patterns
        'do', 'then', 'and', 'or', 'not', 'in',
        'require', 'require_relative', 'include', 'extend', 'prepend',
        'attr_reader', 'attr_writer', 'attr_accessor',
        # Values
        'nil', 'true', 'false',
        # Common types
        'String', 'Integer', 'Float', 'Array', 'Hash', 'Symbol',
        'Range', 'Regexp', 'Proc', 'Lambda', 'Class', 'Module', 'new'
    },
    'swift': {
        'class', 'deinit', 'enum', 'extension', 'func', 'import', 'init',
        'internal', 'let', 'operator', 'private', 'protocol', 'public',
        'static', 'struct', 'subscript', 'typealias', 'var', 'break', 'case',
        'continue', 'default', 'do', 'else', 'fallthrough', 'for', 'if', 'in',
        'return', 'switch', 'where', 'while', 'as', 'Any', 'catch', 'false',
        'is', 'nil', 'rethrows', 'super', 'self', 'Self', 'throw', 'throws',
        'true', 'try', 'associativity', 'convenience', 'dynamic', 'didSet',
        'final', 'get', 'infix', 'inout', 'lazy', 'left', 'mutating', 'none',
        'nonmutating', 'optional', 'override', 'postfix', 'precedence',
        'prefix', 'Protocol', 'required', 'right', 'set', 'Type', 'unowned',
        'weak', 'willSet', 'String', 'Int', 'Double', 'Bool', 'Array', 'Dictionary',
        'Set', 'Optional', 'Result', 'Error'
    },
    'kotlin': {
        'as', 'as?', 'break', 'class', 'continue', 'do', 'else', 'false',
        'for', 'fun', 'if', 'in', '!in', 'interface', 'is', '!is', 'null',
        'object', 'package', 'return', 'super', 'this', 'throw', 'true',
        'try', 'typealias', 'typeof', 'val', 'var', 'when', 'while', 'by',
        'catch', 'constructor', 'delegate', 'dynamic', 'field', 'file',
        'finally', 'get', 'import', 'init', 'param', 'property', 'receiver',
        'set', 'setparam', 'where', 'actual', 'abstract', 'annotation',
        'companion', 'const', 'crossinline', 'data', 'enum', 'expect',
        'external', 'final', 'infix', 'inline', 'inner', 'internal',
        'lateinit', 'noinline', 'open', 'operator', 'out', 'override',
        'private', 'protected', 'public', 'reified', 'sealed', 'suspend',
        'tailrec', 'vararg', 'String', 'Int', 'Long', 'Double', 'Float',
        'Boolean', 'List', 'Map', 'Set', 'Array', 'Any', 'Unit', 'Nothing'
    },
    'dart': {
        'abstract', 'as', 'assert', 'async', 'await', 'break', 'case',
        'catch', 'class', 'const', 'continue', 'covariant', 'default',
        'deferred', 'do', 'dynamic', 'else', 'enum', 'export', 'extends',
        'extension', 'external', 'factory', 'false', 'final', 'finally',
        'for', 'Function', 'get', 'hide', 'if', 'implements', 'import', 'in',
        'interface', 'is', 'late', 'library', 'mixin', 'new', 'null', 'on',
        'operator', 'part', 'required', 'rethrow', 'return', 'set', 'show',
        'static', 'super', 'switch', 'sync', 'this', 'throw', 'true', 'try',
        'typedef', 'var', 'void', 'while', 'with', 'yield', 'String', 'int',
        'double', 'bool', 'List', 'Map', 'Set', 'Future', 'Stream', 'Object'
    }
}


def analyze_file_generic(path: Path, lang: str, config: dict):
    """Optimized generic analyzer with cached regex patterns and exclusions"""
    if lang == 'python':
        return analyze_file_python(path)

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[ERROR] Analysis failed for {path}: {e}")
        return [], [], [], None, {"error": str(e)}

    lines = source.split('\n')
    functions = []
    classes = []
    imports = []
    docstring = None
    meta = {}

    # Pre-compile patterns once
    import_patterns = [get_compiled_pattern(p) for p in config.get('import_patterns', [])]
    func_pattern = get_compiled_pattern(config.get('function_pattern'))
    class_pattern = get_compiled_pattern(config.get('class_pattern'))
    comment_patterns = [get_compiled_pattern(p) for p in config.get('comment_patterns', [])]
    
    # Pattern for detecting function calls
    call_pattern = get_compiled_pattern(r'\b([A-Za-z_]\w*)\s*\(')

    # Extract docstring
    for line in lines[:20]:
        for cp in comment_patterns:
            if cp and cp.match(line):
                docstring = line.strip().lstrip('#/"\' ')
                break
        if docstring:
            break

    # Get standard library exclusions for this language
    stdlib_exclusions = STDLIB_EXCLUSIONS.get(lang, set())

    # Extract imports
    for line in lines:
        for pattern in import_patterns:
            if pattern:
                match = pattern.search(line)
                if match:
                    import_name = match.group(1)
                    if import_name:
                        # Check if it's a standard library import
                        is_stdlib = False
                        
                        # Direct match or prefix match (e.g. java.util.List matches java.util)
                        if import_name in stdlib_exclusions:
                            is_stdlib = True
                        else:
                            for exclusion in stdlib_exclusions:
                                if (import_name.startswith(exclusion + ".") or 
                                    import_name.startswith(exclusion + ":") or 
                                    import_name.startswith(exclusion + "/")):
                                    is_stdlib = True
                                    break
                        
                        if not is_stdlib:
                            imports.append(import_name.strip())

    # Get language-specific keywords
    KEYWORDS = LANGUAGE_KEYWORDS.get(lang, {'if', 'for', 'while', 'switch', 'return'})

    # Extract functions
    if func_pattern:
        for line in lines:
            match = func_pattern.search(line)
            if match:
                func_name = next((g for g in match.groups() if g), None)
                if func_name and func_name not in KEYWORDS:
                    functions.append(func_name)

    # Extract classes with methods
    if class_pattern:
        for i, line in enumerate(lines):
            match = class_pattern.search(line)
            if match:
                class_name = match.group(1)
                methods = []

                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, min(i + 200, len(lines))):
                    next_line = lines[j]
                    if not next_line.strip():
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level:
                        break
                    if func_pattern:
                        method_match = func_pattern.search(next_line)
                        if method_match:
                            method_name = next((g for g in method_match.groups() if g), None)
                            if method_name:
                                methods.append(method_name)

                classes.append({"name": class_name, "methods": methods})

    # Build exclusion set from detected types
    EXCLUSIONS = set()
    for cls_info in classes:
        if isinstance(cls_info, dict) and "name" in cls_info:
            EXCLUSIONS.add(cls_info["name"])
        elif isinstance(cls_info, str):
            EXCLUSIONS.add(cls_info)

    # Extract function calls with keyword and type exclusions
    calls = set()
    if call_pattern:
        for line in lines:
            s = line.strip()
            # Skip comments and empty lines
            if not s:
                continue
            skip_line = False
            for cp in comment_patterns:
                if cp and cp.match(line):
                    skip_line = True
                    break
            if skip_line:
                continue
            # Skip function/method declarations
            if func_pattern and func_pattern.match(line):
                continue

            for m in call_pattern.finditer(line):
                name = m.group(1)
                # Exclude keywords and project-defined types
                if name not in KEYWORDS and name not in EXCLUSIONS:
                    calls.add(name)

    if calls:
        meta["calls"] = sorted(calls)

    # Language-specific extras
    if lang in ("csharp", "java"):
        ns_pattern = get_compiled_pattern(r'^\s*namespace\s+([\w\.]+)')
        for line in lines:
            if ns_pattern:
                m = ns_pattern.match(line)
                if m:
                    meta["namespace"] = m.group(1)
                    break

    if lang in ("javascript", "typescript"):
        exports = set()
        export_default = get_compiled_pattern(r'^\s*export\s+default\s+')
        export_func = get_compiled_pattern(r'^\s*export\s+(?:async\s+)?function\s+(\w+)')
        export_class = get_compiled_pattern(r'^\s*export\s+class\s+(\w+)')
        
        for line in lines:
            if export_default and export_default.search(line):
                exports.add("default")
            if export_func:
                m = export_func.search(line)
                if m:
                    exports.add(m.group(1))
            if export_class:
                m = export_class.search(line)
                if m:
                    exports.add(m.group(1))
        if exports:
            meta["exports"] = sorted(exports)

    return functions, classes, imports, docstring, meta
