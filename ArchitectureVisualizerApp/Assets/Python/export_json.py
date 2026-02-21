"""
JSON Export Wrapper
Provides simple interface for exporting graph data to JSON
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.graph import build_graph
from core.json_exporter import JSONExporter


def export_project_json(project_path, output_file=None, use_cache=False, config_path=None):
    """
    Export project architecture to JSON format.
    
    Args:
        project_path: Path to project directory
        output_file: Output JSON file (None = stdout)
        use_cache: Use incremental caching
        config_path: Path to .visualizer.yml config file (optional)
        
    Returns:
        JSON data dictionary
    """
    project_path = Path(project_path).resolve()
    
    # Build graph with config support
    print(f"[INFO] Analyzing project: {project_path}", file=sys.stderr)
    graph_data, stats = build_graph(project_path, use_cache=use_cache, config_path=config_path)
    
    # Run architecture analysis
    print(f"[INFO] Running architecture analysis...", file=sys.stderr)
    from core.architecture_analyzer import analyze_architecture
    analysis_results = analyze_architecture(graph_data)
    
    # Add analysis results to graph data
    graph_data['analysis'] = analysis_results
    
    # GPU Layout Calculation
    try:
        from core.gpu_utils import detect_gpu
        from core.layout_engine import compute_layout_gpu
        
        gpu_info = detect_gpu()
        if gpu_info['available']:
            print(f"[INFO] GPU detected: {gpu_info['name']}", file=sys.stderr)
            layout = compute_layout_gpu(graph_data["nodes"], graph_data["links"])
            
            if layout:
                # Apply positions to nodes
                for node in graph_data["nodes"]:
                    if node["id"] in layout:
                        x, y = layout[node["id"]]
                        node["x"] = x
                        node["y"] = y
                        # Also set fixed positions to prevent initial jitter
                        node["fx"] = x
                        node["fy"] = y
                
                # Mark as pre-calculated
                graph_data["layout_precalculated"] = True
                print("[INFO] GPU layout applied successfully", file=sys.stderr)
    except Exception as e:
        print(f"[WARNING] GPU layout failed: {e}", file=sys.stderr)
    
    # Export to JSON
    exporter = JSONExporter()
    json_data = exporter.export_graph(graph_data, project_path)
    
    # Add analysis results to JSON output
    json_data['analysis'] = analysis_results
    
    # Output
    if output_file:
        output_path = Path(output_file)
        # Manually save to file to ensure all fields (including x, y) are preserved
        # The exporter might filter fields, so we dump the modified graph_data directly if needed
        # But exporter.export_graph creates a new dict. Let's merge our modifications.
        
        # Actually, exporter.export_graph returns a clean structure. 
        # We need to make sure the x,y coordinates we added to graph_data['nodes'] 
        # are present in json_data['nodes'].
        
        # Re-map positions from graph_data to json_data
        if graph_data.get("layout_precalculated"):
            node_map = {n["id"]: n for n in graph_data["nodes"]}
            for node in json_data["nodes"]:
                if node["id"] in node_map:
                    src = node_map[node["id"]]
                    if "x" in src:
                        node["x"] = src["x"]
                        node["y"] = src["y"]
                        node["fx"] = src["fx"]
                        node["fy"] = src["fy"]
            json_data["layout_precalculated"] = True

        exporter.save_to_file(json_data, output_path)
        print(f"[✓] Exported to: {output_path.absolute()}", file=sys.stderr)
        print(f"[✓] Nodes: {len(json_data['nodes'])} | Links: {len(json_data['links'])}", file=sys.stderr)
        print(f"[✓] Health Score: {analysis_results['health_score']}/100", file=sys.stderr)
        print(f"[✓] Cycles: {analysis_results['cycles']['count']} | God Modules: {analysis_results['god_modules']['count']}", file=sys.stderr)
    else:
        # Print to stdout
        print(exporter.to_string(json_data, pretty=True))
    
    return json_data


if __name__ == "__main__":
    import argparse
    import cProfile
    import pstats
    
    parser = argparse.ArgumentParser(description="Export project architecture to JSON")
    parser.add_argument('project_dir', help='Project directory to analyze')
    parser.add_argument('-o', '--output', help='Output JSON file (default: stdout)')
    parser.add_argument('--cache', action='store_true', help='Use incremental caching')
    parser.add_argument('--config', help='Path to .visualizer.yml config file')
    parser.add_argument('--profile', action='store_true', help='Profile the architecture analysis')
    
    args = parser.parse_args()
    
    if args.profile:
        print("[INFO] Profiling enabled", file=sys.stderr)
        profiler = cProfile.Profile()
        profiler.enable()
        
        export_project_json(args.project_dir, args.output, args.cache, args.config)
        
        profiler.disable()
        import io
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
        
        print("[INFO] ⏱️ --- Performance Profile ---", file=sys.stderr)
        for line in s.getvalue().split('\n'):
            if line.strip():
                print(f"[INFO] ⏱️ {line}", file=sys.stderr)
    else:
        export_project_json(args.project_dir, args.output, args.cache, args.config)
