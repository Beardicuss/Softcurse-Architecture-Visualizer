"""
Architecture analysis module for detecting cycles, god modules, and calculating health metrics.
Language-agnostic - works on any dependency graph.
"""

from typing import Dict, List, Set, Tuple, Any


def find_cycles_tarjan(graph: Dict[str, Any]) -> List[List[str]]:
    """
    Find all cycles in the dependency graph using Tarjan's algorithm.
    Returns list of strongly connected components (cycles).
    """
    nodes = {node["id"]: node for node in graph["nodes"]}
    adjacency = {}
    
    # Build adjacency list
    for node_id in nodes:
        adjacency[node_id] = []
    
    for link in graph["links"]:
        source = link["source"] if isinstance(link["source"], str) else link["source"]["id"]
        target = link["target"] if isinstance(link["target"], str) else link["target"]["id"]
        if source in adjacency:
            adjacency[source].append(target)
    
    # Tarjan's algorithm
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    cycles = []
    
    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        on_stack[node] = True
        stack.append(node)
        
        # Explore neighbors
        for neighbor in adjacency.get(node, []):
            if neighbor not in nodes:
                continue
            if neighbor not in index:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif on_stack.get(neighbor, False):
                lowlinks[node] = min(lowlinks[node], index[neighbor])
        
        # If node is a root node, pop the stack and collect SCC
        if lowlinks[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == node:
                    break
            # Only consider SCCs with more than 1 node (actual cycles)
            if len(scc) > 1:
                cycles.append(scc)
    
    # Run algorithm on all unvisited nodes
    for node_id in nodes:
        if node_id not in index:
            strongconnect(node_id)
    
    return cycles


def detect_god_modules(graph: Dict[str, Any], threshold: int = 15) -> List[Dict[str, Any]]:
    """
    Detect god modules (nodes with too many connections).
    Threshold defaults to 15 total connections (in + out).
    """
    nodes = {node["id"]: node for node in graph["nodes"]}
    in_degree = {node_id: 0 for node_id in nodes}
    out_degree = {node_id: 0 for node_id in nodes}
    
    # Calculate degrees
    for link in graph["links"]:
        source = link["source"] if isinstance(link["source"], str) else link["source"]["id"]
        target = link["target"] if isinstance(link["target"], str) else link["target"]["id"]
        
        if source in out_degree:
            out_degree[source] += 1
        if target in in_degree:
            in_degree[target] += 1
    
    god_modules = []
    for node_id, node in nodes.items():
        total_connections = in_degree[node_id] + out_degree[node_id]
        if total_connections > threshold:
            god_modules.append({
                "id": node_id,
                "in_degree": in_degree[node_id],
                "out_degree": out_degree[node_id],
                "total": total_connections
            })
    
    # Sort by total connections (worst first)
    god_modules.sort(key=lambda x: x["total"], reverse=True)
    return god_modules


def detect_cross_language_edges(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect edges that cross between different languages.
    """
    nodes = {node["id"]: node for node in graph["nodes"]}
    cross_language_edges = []
    
    for link in graph["links"]:
        source_id = link["source"] if isinstance(link["source"], str) else link["source"]["id"]
        target_id = link["target"] if isinstance(link["target"], str) else link["target"]["id"]
        
        if source_id not in nodes or target_id not in nodes:
            continue
        
        source_lang = nodes[source_id].get("language", "unknown")
        target_lang = nodes[target_id].get("language", "unknown")
        
        if source_lang != target_lang:
            cross_language_edges.append({
                "source": source_id,
                "target": target_id,
                "source_language": source_lang,
                "target_language": target_lang
            })
    
    return cross_language_edges


def calculate_language_metrics(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate per-language metrics.
    """
    language_stats = {}
    
    for node in graph["nodes"]:
        lang = node.get("language", "unknown")
        if lang not in language_stats:
            language_stats[lang] = {
                "modules": 0,
                "total_connections": 0,
                "avg_connections": 0
            }
        language_stats[lang]["modules"] += 1
    
    # Calculate connections per language
    for link in graph["links"]:
        source_id = link["source"] if isinstance(link["source"], str) else link["source"]["id"]
        source_node = next((n for n in graph["nodes"] if n["id"] == source_id), None)
        if source_node:
            lang = source_node.get("language", "unknown")
            if lang in language_stats:
                language_stats[lang]["total_connections"] += 1
    
    # Calculate averages
    for lang, stats in language_stats.items():
        if stats["modules"] > 0:
            stats["avg_connections"] = round(stats["total_connections"] / stats["modules"], 2)
    
    return language_stats


def calculate_health_score(cycles_count: int, god_modules_count: int, orphan_count: int, total_modules: int) -> int:
    """
    Calculate architecture health score (0-100).
    100 = perfect, 0 = disaster
    """
    score = 100
    
    # Penalize cycles (very bad)
    if cycles_count > 0:
        score -= min(40, cycles_count * 10)  # -10 per cycle, max -40
    
    # Penalize god modules (bad)
    if god_modules_count > 0:
        god_ratio = god_modules_count / max(total_modules, 1)
        score -= min(30, int(god_ratio * 100))  # Up to -30 based on ratio
    
    # Penalize orphans (mildly bad)
    if orphan_count > 0:
        orphan_ratio = orphan_count / max(total_modules, 1)
        score -= min(15, int(orphan_ratio * 50))  # Up to -15 based on ratio
    
    return max(0, score)


def analyze_architecture(graph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main architecture analysis function.
    Runs all analysis and returns comprehensive metrics.
    """
    # Find cycles
    cycles = find_cycles_tarjan(graph)
    cycles_flat = [node for cycle in cycles for node in cycle]  # Flatten for marking
    
    # Detect god modules
    god_modules = detect_god_modules(graph)
    
    # Count orphans (already marked as disconnected in graph building)
    orphan_count = sum(1 for node in graph["nodes"] if node.get("disconnected", False))
    
    # Cross-language analysis
    cross_language_edges = detect_cross_language_edges(graph)
    language_metrics = calculate_language_metrics(graph)
    
    # Calculate health score
    total_modules = len(graph["nodes"])
    health_score = calculate_health_score(len(cycles), len(god_modules), orphan_count, total_modules)
    
    # Mark nodes with metadata
    for node in graph["nodes"]:
        node["in_cycle"] = node["id"] in cycles_flat
        node["is_god_module"] = node["id"] in [gm["id"] for gm in god_modules]
    
    # Calculate average connections
    total_connections = len(graph["links"])
    avg_connections = round(total_connections / max(total_modules, 1), 2)
    
    # Find module with most connections
    most_complex = god_modules[0] if god_modules else None
    
    return {
        "health_score": health_score,
        "cycles": {
            "count": len(cycles),
            "cycles": cycles
        },
        "god_modules": {
            "count": len(god_modules),
            "modules": god_modules
        },
        "orphans": {
            "count": orphan_count
        },
        "total_modules": total_modules,
        "total_connections": total_connections,
        "avg_connections": avg_connections,
        "most_complex": most_complex,
        "cross_language": {
            "count": len(cross_language_edges),
            "edges": cross_language_edges
        },
        "language_metrics": language_metrics
    }
