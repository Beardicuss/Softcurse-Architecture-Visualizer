import os
import sys
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

# Add Python directory to path so 'core' can be imported as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.architecture_analyzer import analyze_architecture
from core.layout_engine import compute_layout_gpu
from core.graph import build_graph

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Global state
current_project_path = None
last_analysis_result = None
is_analyzing = False

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'project': current_project_path,
        'analyzing': is_analyzing
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    global current_project_path, last_analysis_result, is_analyzing
    
    data = request.json
    project_path = data.get('path')
    use_cache = data.get('use_cache', True)
    
    if not project_path or not os.path.exists(project_path):
        return jsonify({'error': 'Invalid project path'}), 400
        
    if is_analyzing:
        return jsonify({'error': 'Analysis already in progress'}), 409
        
    current_project_path = project_path
    is_analyzing = True
    
    def run_analysis():
        global last_analysis_result, is_analyzing
        try:
            from pathlib import Path
            project_path_obj = Path(project_path).resolve()
            logger.info(f"Starting analysis for: {project_path_obj}")
            
            # Load config
            config_path = os.path.join(project_path, '.visualizer.yml')
            if not os.path.exists(config_path):
                config_path = None
                
            # Build graph
            graph_data, stats = build_graph(project_path_obj, config_path=config_path, use_cache=use_cache)
            
            # Analyze architecture
            analysis_results = analyze_architecture(graph_data)
            
            # Compute layout
            try:
                logger.info("Computing GPU layout...")
                layout_positions = compute_layout_gpu(graph_data['nodes'], graph_data['links'])
                if layout_positions:
                    for node in graph_data['nodes']:
                        if node['id'] in layout_positions:
                            pos = layout_positions[node['id']]
                            node['x'] = float(pos[0])
                            node['y'] = float(pos[1])
                    graph_data['layout_precalculated'] = True
            except Exception as e:
                logger.error(f"GPU Layout failed: {e}")
                
            # Prepare result
            result = {
                'metadata': {
                    'total_files': len(graph_data['nodes']),
                    'languages': list(set(n.get('type', 'unknown') for n in graph_data['nodes']))
                },
                'nodes': graph_data['nodes'],
                'links': graph_data['links'],
                'metrics': {
                    'total_links': len(graph_data['links'])
                },
                'analysis': analysis_results
            }
            
            last_analysis_result = result
            logger.info("Analysis complete")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
        finally:
            is_analyzing = False

    thread = threading.Thread(target=run_analysis)
    thread.start()
    
    return jsonify({'message': 'Analysis started'})

@app.route('/graph', methods=['GET'])
def get_graph():
    if not last_analysis_result:
        return jsonify({'error': 'No analysis data available'}), 404
    return jsonify(last_analysis_result)

if __name__ == '__main__':
    port = 5000
    logger.info(f"Starting API server on port {port}")
    app.run(host='127.0.0.1', port=port)
