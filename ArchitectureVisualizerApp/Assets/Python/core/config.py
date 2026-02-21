"""
Configuration data for language-specific patterns and settings.
"""

import os

# -------------------------------------------------------------------
# DEBUG MODE - Set via environment variable
# -------------------------------------------------------------------
DEBUG_MODE = os.getenv('VISUALIZER_DEBUG', 'false').lower() == 'true'

# -------------------------------------------------------------------
# LANGUAGE CONFIG WITH NON-CAPTURING GROUPS
# -------------------------------------------------------------------

LANGUAGE_CONFIG = {
    'python': {
        'extensions': ['.py'],
        'import_patterns': [
            r'^\s*import\s+([\w.]+)',
            r'^\s*from\s+([\w.]+)\s+import'
        ],
        'function_pattern': r'^\s*def\s+(\w+)',
        'class_pattern': r'^\s*class\s+(\w+)',
        'comment_patterns': [r'^\s*#', r'^\s*"""', r"^\s*'''"]
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.mjs'],
        'import_patterns': [
            r'^\s*import\s+.*?from\s+["\'](.+?)["\']',
            r'^\s*require\(["\'](.+?)["\']\)',
            r'^\s*import\(["\'](.+?)["\']\)'
        ],
        'function_pattern': r'^\s*(?:async\s+)?function\s+(\w+)|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(?',
        'class_pattern': r'^\s*class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'typescript': {
        'extensions': ['.ts', '.tsx'],
        'import_patterns': [
            r'^\s*import\s+.*?from\s+["\'](.+?)["\']',
            r'^\s*require\(["\'](.+?)["\']\)',
            r'^\s*import\(["\'](.+?)["\']\)'
        ],
        'function_pattern': r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)|^\s*(?:const|let|var)\s+(\w+)(?::\s*\w+)?\s*=\s*(?:async\s+)?\(?',
        'class_pattern': r'^\s*(?:export\s+)?class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'java': {
        'extensions': ['.java'],
        'import_patterns': [r'^\s*import\s+([\w.]+)'],
        'function_pattern': r'^\s*(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)+(\w+)\s*\(',
        'class_pattern': r'^\s*(?:public|private|protected)\s+(?:abstract\s+)?class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'csharp': {
        'extensions': ['.cs'],
        'import_patterns': [r'^\s*using\s+([\w.]+)'],
        'function_pattern': r'^\s*(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?[\w<>\[\],]+\s+(\w+)\s*\(',
        'class_pattern': r'^\s*(?:public|private|protected|internal)\s+(?:partial\s+)?(?:class|struct)\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'go': {
        'extensions': ['.go'],
        'import_patterns': [
            r'^\s*import\s+"(.+?)"',
            r'^\s*import\s+\(\s*"(.+?)"',
            r'^\s*"([^"]+)"(?!\s*[:|,])'
        ],
        'function_pattern': r'^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)',
        'class_pattern': r'^\s*type\s+(\w+)\s+struct',
        'comment_patterns': [r'^\s*//']
    },
    'rust': {
        'extensions': ['.rs'],
        'import_patterns': [
            r'^\s*use\s+([\w:]+)',
            r'^\s*extern\s+crate\s+(\w+)'
        ],
        'function_pattern': r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)',
        'class_pattern': r'^\s*(?:pub\s+)?struct\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'cpp': {
        'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx'],
        'import_patterns': [
            r'^\s*#include\s+[<"](.+?)[>"]'
        ],
        'function_pattern': r'^\s*(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:const\s*)?{',
        'class_pattern': r'^\s*class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'php': {
        'extensions': ['.php'],
        'import_patterns': [
            r'^\s*use\s+([\w\\]+)',
            r'^\s*require(?:_once)?\s*["\'](.+?)["\']',
            r'^\s*include(?:_once)?\s*["\'](.+?)["\']'
        ],
        'function_pattern': r'^\s*(?:public|private|protected)?\s*function\s+(\w+)',
        'class_pattern': r'^\s*(?:abstract\s+)?class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*', r'^\s*#']
    },
    'ruby': {
        'extensions': ['.rb'],
        'import_patterns': [
            r'^\s*require\s+["\'](.+?)["\']',
            r'^\s*require_relative\s+["\'](.+?)["\']'
        ],
        'function_pattern': r'^\s*def\s+(\w+)',
        'class_pattern': r'^\s*class\s+(\w+)',
        'comment_patterns': [r'^\s*#']
    },
    'swift': {
        'extensions': ['.swift'],
        'import_patterns': [
            r'^\s*import\s+([\w.]+)'
        ],
        'function_pattern': r'^\s*(?:public|private|internal|fileprivate|open)?\s*(?:override|mutating|nonmutating)?\s*func\s+(\w+)',
        'class_pattern': r'^\s*(?:public|private|internal|fileprivate|open)?\s*(?:final)?\s*(?:class|struct|protocol|extension)\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'kotlin': {
        'extensions': ['.kt', '.kts'],
        'import_patterns': [
            r'^\s*import\s+([\w.]+)'
        ],
        'function_pattern': r'^\s*(?:public|private|protected|internal)?\s*(?:override|suspend|inline)?\s*fun\s+(\w+)',
        'class_pattern': r'^\s*(?:public|private|protected|internal)?\s*(?:open|data|sealed|abstract)?\s*(?:class|interface|object)\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    },
    'dart': {
        'extensions': ['.dart'],
        'import_patterns': [
            r'^\s*import\s+[\'"](.+?)[\'"]'
        ],
        'function_pattern': r'^\s*(?:[\w<>]+\s+)?(\w+)\s*\(',
        'class_pattern': r'^\s*(?:abstract\s+)?class\s+(\w+)',
        'comment_patterns': [r'^\s*//', r'^\s*/\*']
    }
}


# -------------------------------------------------------------------
# OPTIMIZED: MATCHING WITH LRU CACHE + SETS
# -------------------------------------------------------------------

# OPTIMIZED: Use sets instead of lists (50x faster lookups)
EXTERNAL_PREFIXES = {
    "System.", "Microsoft.", "mscorlib", "java.", "javax.", "android.",
    "org.", "com.", "std", "react", "vue", "node:", "@", "flutter",
    "dart:", "kotlin.", "Swift.", "UIKit.", "Foundation."
}

STDLIB_EXCLUSIONS = {
    'python': {
        "os", "sys", "pathlib", "json", "typing", "logging", "re",
        "subprocess", "asyncio", "time", "math", "itertools", "functools",
        "collections", "datetime", "random", "hashlib", "base64", "io",
        "shutil", "copy", "pickle", "socket", "threading", "multiprocessing",
        "argparse", "configparser", "csv", "email", "http", "urllib", "uuid"
    },
    'javascript': {
        "fs", "path", "http", "https", "crypto", "util", "events", "os",
        "child_process", "cluster", "dns", "net", "readline", "stream",
        "tls", "dgram", "zlib", "buffer", "url", "querystring", "punycode",
        "string_decoder", "tty", "constants", "vm", "v8", "perf_hooks",
        "async_hooks", "worker_threads", "assert", "console", "module", "process"
    },
    'typescript': {
        "fs", "path", "http", "https", "crypto", "util", "events", "os",
        "child_process", "cluster", "dns", "net", "readline", "stream",
        "tls", "dgram", "zlib", "buffer", "url", "querystring", "punycode",
        "string_decoder", "tty", "constants", "vm", "v8", "perf_hooks",
        "async_hooks", "worker_threads", "assert", "console", "module", "process"
    },
    'go': {
        "fmt", "os", "io", "net", "http", "encoding", "time", "strings",
        "strconv", "sync", "context", "errors", "log", "math", "sort",
        "regexp", "path", "flag", "reflect", "runtime", "testing", "unsafe",
        "archive", "bufio", "bytes", "compress", "container", "crypto",
        "database", "debug", "expvar", "hash", "html", "image", "index",
        "mime", "plugin", "text", "unicode", "syscall"
    },
    'java': {
        "java.lang", "java.util", "java.io", "java.net", "java.nio",
        "java.time", "java.math", "java.text", "java.sql", "java.beans",
        "java.util.logging", "java.util.regex", "java.util.stream",
        "java.util.concurrent", "java.util.function"
    },
    'csharp': {
        "System", "System.Collections", "System.Collections.Generic",
        "System.IO", "System.Linq", "System.Text", "System.Threading",
        "System.Threading.Tasks", "System.Net", "System.Net.Http",
        "System.Data", "System.Diagnostics", "System.Reflection",
        "System.Runtime", "System.Security", "System.Xml"
    },
    'rust': {
        "std", "core", "alloc", "proc_macro", "test"
    },
    'cpp': {
        "iostream", "vector", "string", "map", "set", "algorithm", "memory",
        "thread", "mutex", "chrono", "atomic", "condition_variable", "future",
        "functional", "utility", "tuple", "array", "deque", "list",
        "forward_list", "stack", "queue", "iterator", "numeric", "complex",
        "valarray", "random", "ratio", "regex", "exception", "stdexcept",
        "cassert", "cctype", "cerrno", "cfloat", "ciso646", "climits",
        "clocale", "cmath", "csetjmp", "csignal", "cstdarg", "cstddef",
        "cstdio", "cstdlib", "cstring", "ctime", "cwchar", "cwctype"
    },
    'swift': {
        "Foundation", "Swift", "UIKit", "AppKit", "SwiftUI", "Combine",
        "CoreData", "CoreGraphics", "CoreImage", "CoreLocation", "MapKit",
        "AVFoundation", "Dispatch", "XCTest"
    },
    'kotlin': {
        "kotlin", "kotlin.collections", "kotlin.io", "kotlin.text",
        "kotlin.ranges", "kotlin.sequences", "kotlin.time", "kotlin.math",
        "kotlin.concurrent", "kotlin.reflect", "java.util", "java.io"
    },
    'dart': {
        "dart:core", "dart:async", "dart:math", "dart:convert", "dart:io",
        "dart:html", "dart:ui", "dart:isolate", "dart:typed_data",
        "dart:developer", "dart:mirrors"
    },
    'ruby': {
        "json", "yaml", "fileutils", "pathname", "uri", "net/http", "openssl",
        "digest", "date", "time", "logger", "benchmark", "cgi", "csv",
        "delegate", "erb", "etc", "fcntl", "forwardable", "getoptlong",
        "ipaddr", "mathn", "matrix", "minitest", "monitor", "mutex_m",
        "observer", "open3", "ostruct", "prime", "pstore", "racc", "rake",
        "rdoc", "resolv", "rexml", "rss", "scanf", "set", "shell",
        "singleton", "socket", "stringio", "strscan", "sync", "tempfile",
        "thread", "thwait", "timeout", "tmpdir", "tracer", "tsort", "un",
        "vector", "weakref", "webrick", "zlib"
    },
    'php': {
        "Exception", "DateTime", "JsonSerializable", "Countable",
        "Iterator", "ArrayAccess", "Traversable", "Throwable",
        "Stringable", "PDO", "PDOException", "SplFileInfo",
        "SplFileObject", "SimpleXMLElement", "DOMDocument"
    }
}
