import json
from pathlib import Path

def write_html(graph, output_path: Path):
    """Generate final HTML with Graph + Analysis panel + Adaptive Force Layout."""
    project_name = graph.get("project_name", "Project")
    languages = graph.get("languages", [])
    lang_badges = " ".join([f'<span class="lang-badge">{lang}</span>' for lang in languages])

    # Paths to assets
    base_dir = Path(__file__).parent
    css_path = base_dir / "static" / "css" / "style.css"
    js_path = base_dir / "static" / "js" / "visualizer.js"
    template_path = base_dir / "templates" / "index.html"

    # Read assets
    try:
        css_content = css_path.read_text(encoding="utf-8")
        js_content = js_path.read_text(encoding="utf-8")
        template_content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to read asset files: {e}")
        return

    # Prepare data
    json_data = json.dumps(graph, ensure_ascii=False, indent=2)

    # Inject into template
    html = template_content.replace("{{PROJECT_NAME}}", project_name)
    html = html.replace("{{LANG_BADGES}}", lang_badges)
    html = html.replace("{{CSS}}", css_content)
    html = html.replace("{{DATA}}", json_data)
    html = html.replace("{{JS}}", js_content)

    output_path.write_text(html, encoding="utf-8")
    print(f"[✓] Generated: {output_path}")
    print(f"[✓] Nodes: {len(graph['nodes'])} | Links: {len(graph['links'])}")
    
    # Display performance hints
    node_count = len(graph['nodes'])
    if node_count > 1000:
        print(f"[⚡] EXTREME mode activated for {node_count} nodes")
        print(f"[INFO] Graph will stabilize quickly with reduced visual quality")
    elif node_count > 500:
        print(f"[⚡] LARGE mode activated for {node_count} nodes")
        print(f"[INFO] Optimized balance between performance and quality")
    elif node_count > 200:
        print(f"[⚡] MEDIUM mode activated for {node_count} nodes")
        print(f"[INFO] Slightly optimized for better performance")
    else:
        print(f"[✨] BALANCED mode for {node_count} nodes")
        print(f"[INFO] Full quality rendering with smooth animations")
