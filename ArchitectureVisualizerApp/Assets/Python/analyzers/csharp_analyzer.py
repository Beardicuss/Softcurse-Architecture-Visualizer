"""
C# file analyzer with advanced pattern matching and framework detection.
"""

from pathlib import Path
from core.utils import get_compiled_pattern
import re


def analyze_file_csharp_advanced(path: Path, config: dict):
    """Enhanced C# analyzer with ASP.NET and MediatR pattern detection"""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[ERROR] Analysis failed for {path}: {e}")
        return [], [], [], None, {"error": str(e)}


    lines = source.split('\n')

    # Pre-compiled patterns - Basic C# constructs
    ns_re = get_compiled_pattern(r'^\s*namespace\s+([\w\.]+)')
    using_re = get_compiled_pattern(r'^\s*using\s+([\w\.]+)\s*;')
    class_re = get_compiled_pattern(
        r'^\s*(?:public|private|protected|internal)\s+(?:partial\s+)?(?:class|struct|enum|interface|record)\s+(\w+)'
    )
    method_decl_re = get_compiled_pattern(
        r'^\s*(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?[\w<>\[\],]+\s+(\w+)\s*\('
    )
    call_re = get_compiled_pattern(r'\b([A-Za-z_]\w*)\s*\(')

    # Framework-specific patterns
    controller_re = get_compiled_pattern(r'^\s*public\s+(?:partial\s+)?class\s+(\w+Controller)\s*:\s*(?:Controller|ControllerBase)')
    mediatr_request_handler_re = get_compiled_pattern(r'IRequestHandler<([^,>]+)(?:,\s*([^>]+))?>')
    mediatr_notification_handler_re = get_compiled_pattern(r'INotificationHandler<([^>]+)>')
    http_attribute_re = get_compiled_pattern(r'^\s*\[Http(Get|Post|Put|Delete|Patch)(?:\("([^"]+)"\))?\]')
    route_attribute_re = get_compiled_pattern(r'^\s*\[Route\("([^"]+)"\)\]')
    dbcontext_re = get_compiled_pattern(r'^\s*public\s+(?:partial\s+)?class\s+(\w+)\s*:\s*DbContext')
    dbset_re = get_compiled_pattern(r'public\s+DbSet<(\w+)>\s+(\w+)')
    constructor_re = get_compiled_pattern(r'^\s*public\s+(\w+)\s*\(([^)]*)\)')

    ns = None
    functions = []
    classes = []
    imports = []
    docstring = None
    calls = set()
    
    # Framework pattern storage
    framework_patterns = {
        "controllers": [],
        "mediatr_handlers": [],
        "dependencies": set(),
        "dbcontext": None,
        "api_routes": []
    }

    # Extract namespace, usings, docstring
    for i, line in enumerate(lines[:40]):
        if ns_re:
            m = ns_re.match(line)
            if m and not ns:
                ns = m.group(1)
        if using_re:
            um = using_re.match(line)
            if um:
                imports.append(um.group(1))
        if not docstring and line.strip().startswith("//"):
            docstring = line.strip().lstrip("/ ").strip()

    # Extract classes and methods with framework patterns
    current_class = None
    current_class_type = None  # 'controller', 'handler', 'dbcontext', or None
    current_controller = None
    current_route_prefix = None
    classes_map = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue

        # Check for controller
        controller_match = controller_re.match(line) if controller_re else None
        if controller_match:
            controller_name = controller_match.group(1)
            current_class = controller_name
            current_class_type = 'controller'
            classes_map[controller_name] = []
            
            current_controller = {
                "name": controller_name,
                "base": "ControllerBase" if "ControllerBase" in line else "Controller",
                "actions": []
            }
            
            # Look for [Route] attribute on previous lines
            for j in range(max(0, i-5), i):
                route_match = route_attribute_re.match(lines[j]) if route_attribute_re else None
                if route_match:
                    current_route_prefix = route_match.group(1)
                    break
            
            framework_patterns["controllers"].append(current_controller)
            i += 1
            continue

        # Check for DbContext
        dbcontext_match = dbcontext_re.match(line) if dbcontext_re else None
        if dbcontext_match:
            dbcontext_name = dbcontext_match.group(1)
            current_class = dbcontext_name
            current_class_type = 'dbcontext'
            classes_map[dbcontext_name] = []
            
            framework_patterns["dbcontext"] = {
                "name": dbcontext_name,
                "entities": []
            }
            i += 1
            continue

        # Check for MediatR handler in class declaration line
        if 'IRequestHandler<' in line or 'INotificationHandler<' in line:
            # Extract class name first
            class_match = class_re.match(line) if class_re else None
            if class_match:
                handler_name = class_match.group(1)
                current_class = handler_name
                current_class_type = 'handler'
                classes_map[handler_name] = []
                
                # Extract request/response types
                request_match = mediatr_request_handler_re.search(line) if mediatr_request_handler_re else None
                notification_match = mediatr_notification_handler_re.search(line) if mediatr_notification_handler_re else None
                
                if request_match:
                    request_type = request_match.group(1).strip()
                    response_type = request_match.group(2).strip() if request_match.group(2) else "Unit"
                    framework_patterns["mediatr_handlers"].append({
                        "handler": handler_name,
                        "type": "request",
                        "request": request_type,
                        "response": response_type
                    })
                elif notification_match:
                    notification_type = notification_match.group(1).strip()
                    framework_patterns["mediatr_handlers"].append({
                        "handler": handler_name,
                        "type": "notification",
                        "notification": notification_type
                    })
                
                i += 1
                continue

        # Regular class detection (fallback)
        if class_re and not current_class_type:
            cm = class_re.match(line)
            if cm:
                cname = cm.group(1)
                current_class = cname
                classes_map[cname] = []
                i += 1
                continue

        # DbSet detection (for DbContext)
        if current_class_type == 'dbcontext' and dbset_re:
            dbset_match = dbset_re.search(line)
            if dbset_match:
                entity_type = dbset_match.group(1)
                if framework_patterns["dbcontext"]:
                    framework_patterns["dbcontext"]["entities"].append(entity_type)

        # Constructor detection for dependency injection
        if constructor_re:
            ctor_match = constructor_re.match(line)
            if ctor_match and current_class:
                ctor_name = ctor_match.group(1)
                params = ctor_match.group(2)
                
                # Only process if constructor name matches current class
                if ctor_name == current_class or (current_class and ctor_name in current_class):
                    # Parse parameters to extract dependency types
                    if params.strip():
                        param_list = params.split(',')
                        for param in param_list:
                            param = param.strip()
                            # Extract type (first word before parameter name)
                            parts = param.split()
                            if len(parts) >= 2:
                                dep_type = parts[0]
                                # Filter out primitive types and common keywords
                                if dep_type.startswith('I') or '<' in dep_type:
                                    framework_patterns["dependencies"].add(dep_type)

        # Action method detection (for controllers)
        if current_class_type == 'controller' and method_decl_re:
            # Look for HTTP attributes on previous lines
            http_method = None
            route_template = None
            
            for j in range(max(0, i-5), i):
                http_match = http_attribute_re.match(lines[j]) if http_attribute_re else None
                if http_match:
                    http_method = http_match.group(1).upper()
                    route_template = http_match.group(2) if http_match.group(2) else ""
                    break
            
            mm = method_decl_re.match(line)
            if mm:
                mname = mm.group(1)
                functions.append(mname)
                if current_class is not None:
                    classes_map[current_class].append(mname)
                
                # Add to controller actions if HTTP method found
                if http_method and current_controller:
                    full_route = f"{current_route_prefix}/{route_template}" if current_route_prefix else route_template
                    full_route = full_route.strip('/')
                    
                    action = {
                        "name": mname,
                        "http_method": http_method,
                        "route": full_route
                    }
                    current_controller["actions"].append(action)
                    framework_patterns["api_routes"].append({
                        "controller": current_controller["name"],
                        "action": mname,
                        "method": http_method,
                        "route": full_route
                    })
                
                i += 1
                continue

        # Regular method detection
        if method_decl_re:
            mm = method_decl_re.match(line)
            if mm:
                mname = mm.group(1)
                functions.append(mname)
                if current_class is not None:
                    classes_map[current_class].append(mname)

        i += 1

    for cname, methods in classes_map.items():
        classes.append({"name": cname, "methods": methods})

    # OPTIMIZED: Extract calls with comprehensive keyword set and exclusions
    KEYWORDS = {
        # Control flow
        "if", "for", "foreach", "while", "switch", "catch", "lock", "using",
        "return", "throw", "break", "continue", "goto", "yield",
        
        # Type keywords
        "class", "struct", "enum", "interface", "record",
        
        # Access modifiers
        "private", "public", "internal", "protected",
        
        # Modifiers
        "static", "readonly", "const", "sealed", "abstract", "partial",
        "virtual", "override", "async", "await", "volatile", "extern",
        
        # Common patterns
        "var", "new", "event", "delegate", "operator",
        "sizeof", "typeof", "nameof", "default", "stackalloc",
        
        # Common types and patterns
        "Action", "Func", "Task", "ValueTask", "Lazy",
        "EventHandler", "Attribute",
        
        # MediatR patterns
        "Request", "Notification", "Handler", "Send", "Publish",
        
        # Other keywords
        "namespace", "is", "as", "in", "out", "ref", "params",
        "this", "base", "null", "true", "false", "void",
        "get", "set", "add", "remove", "value", "where", "select",
        "from", "join", "group", "into", "orderby", "let"
    }
    
    # Build exclusion set from detected types (classes, structs, enums, interfaces, records)
    # This prevents project-defined types from being detected as function calls
    EXCLUSIONS = set()
    for cls_info in classes:
        if isinstance(cls_info, dict) and "name" in cls_info:
            EXCLUSIONS.add(cls_info["name"])
        elif isinstance(cls_info, str):
            EXCLUSIONS.add(cls_info)

    if call_re:
        for line in lines:
            s = line.strip()
            if not s or s.startswith("//") or s.startswith("/*"):
                continue
            if method_decl_re and method_decl_re.match(line):
                continue

            for m in call_re.finditer(line):
                name = m.group(1)
                # Exclude keywords and project-defined types
                if name not in KEYWORDS and name not in EXCLUSIONS:
                    calls.add(name)

    meta = {"namespace": ns} if ns else {}
    if calls:
        meta["calls"] = sorted(calls)
    
    # Add framework patterns to metadata
    if framework_patterns["controllers"]:
        meta["controllers"] = framework_patterns["controllers"]
    if framework_patterns["mediatr_handlers"]:
        meta["mediatr_handlers"] = framework_patterns["mediatr_handlers"]
    if framework_patterns["dependencies"]:
        meta["dependencies"] = sorted(framework_patterns["dependencies"])
    if framework_patterns["dbcontext"]:
        meta["dbcontext"] = framework_patterns["dbcontext"]
    if framework_patterns["api_routes"]:
        meta["api_routes"] = framework_patterns["api_routes"]

    return functions, classes, imports, docstring, meta
