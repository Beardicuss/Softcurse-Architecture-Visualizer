"""
JSON Exporter for Architecture Visualizer
Exports graph data, analysis results, and metrics in JSON format.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class JSONExporter:
    """Export architecture analysis data to JSON format"""
    
    def __init__(self, version: str = "2.0.0"):
        self.version = version
    
    def export_graph(self, 
                     graph_data: Dict[str, Any], 
                     project_path: Path,
                     include_metadata: bool = True) -> Dict[str, Any]:
        """
        Export complete graph data to JSON format.
        
        Args:
            graph_data: Graph data from build_graph()
            project_path: Path to analyzed project
            include_metadata: Include metadata section
            
        Returns:
            Dictionary ready for JSON serialization
        """
        result = {}
        
        if include_metadata:
            result['metadata'] = self._generate_metadata(graph_data, project_path)
        
        # Export nodes
        result['nodes'] = self._export_nodes(graph_data.get('nodes', []))
        
        # Export links
        result['links'] = self._export_links(graph_data.get('links', []))
        
        # Export metrics
        result['metrics'] = self._calculate_metrics(graph_data)
        
        return result
    
    def export_analysis(self, 
                       analysis_results: Dict[str, Any],
                       project_path: Path) -> Dict[str, Any]:
        """
        Export analysis results (functions, classes, imports per file).
        
        Args:
            analysis_results: Results from file analysis
            project_path: Path to analyzed project
            
        Returns:
            Dictionary with detailed analysis data
        """
        return {
            'metadata': {
                'version': self.version,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'project_path': str(project_path)
            },
            'files': analysis_results
        }
    
    def export_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export metrics and statistics only.
        
        Args:
            stats: Statistics from analysis
            
        Returns:
            Dictionary with metrics
        """
        return {
            'metadata': {
                'version': self.version,
                'generated_at': datetime.utcnow().isoformat() + 'Z'
            },
            'metrics': stats
        }
    
    def export_filtered(self,
                       graph_data: Dict[str, Any],
                       project_path: Path,
                       filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Export filtered graph data.
        
        Args:
            graph_data: Complete graph data
            project_path: Path to analyzed project
            filters: Filter criteria (language, file_type, etc.)
            
        Returns:
            Filtered graph data
        """
        if not filters:
            return self.export_graph(graph_data, project_path)
        
        # Filter nodes
        filtered_nodes = self._filter_nodes(graph_data.get('nodes', []), filters)
        node_ids = {node['id'] for node in filtered_nodes}
        
        # Filter links to only include those between filtered nodes
        filtered_links = [
            link for link in graph_data.get('links', [])
            if link['source'] in node_ids and link['target'] in node_ids
        ]
        
        filtered_data = {
            'nodes': filtered_nodes,
            'links': filtered_links
        }
        
        return self.export_graph(filtered_data, project_path)
    
    def save_to_file(self, data: Dict[str, Any], output_path: Path, pretty: bool = True) -> None:
        """
        Save JSON data to file.
        
        Args:
            data: Data to save
            output_path: Output file path
            pretty: Pretty-print JSON
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
    
    def to_string(self, data: Dict[str, Any], pretty: bool = True) -> str:
        """
        Convert data to JSON string.
        
        Args:
            data: Data to convert
            pretty: Pretty-print JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    # Private helper methods
    
    def _generate_metadata(self, graph_data: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """Generate metadata section"""
        nodes = graph_data.get('nodes', [])
        
        # Count languages
        languages = {}
        for node in nodes:
            lang = node.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        return {
            'version': self.version,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'project_path': str(project_path),
            'total_files': len(nodes),
            'languages': list(languages.keys()),
            'language_distribution': languages
        }
    
    def _export_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export nodes with consistent schema"""
        exported = []
        
        for node in nodes:
            node_id = node.get('id', '')
            
            # Calculate group from module path
            # e.g., "Project.core.utils" -> "core"
            # e.g., "Project.analyzers.python" -> "analyzers"
            parts = node_id.split('.')
            if len(parts) > 1:
                group = parts[1] if len(parts) > 2 else parts[0]
            else:
                group = 'root'
            
            exported_node = {
                'id': node.get('id', ''),
                'name': node.get('name', ''),
                'path': node.get('path', ''),
                'language': node.get('language', 'unknown'),
                'type': node.get('type', 'file'),
                'group': group,  # Add group field
            }
            
            # Optional fields
            if 'size' in node:
                exported_node['size'] = node['size']
            if 'functions' in node:
                exported_node['functions'] = node['functions']
            if 'classes' in node:
                exported_node['classes'] = node['classes']
            if 'imports' in node:
                exported_node['imports'] = node['imports']
            
            exported.append(exported_node)
        
        return exported
    
    def _export_links(self, links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export links with consistent schema"""
        exported = []
        
        for link in links:
            exported_link = {
                'source': link.get('source', ''),
                'target': link.get('target', ''),
                'type': link.get('type', 'dependency'),
            }
            
            # Optional fields
            if 'strength' in link:
                exported_link['strength'] = link['strength']
            if 'count' in link:
                exported_link['count'] = link['count']
            
            exported.append(exported_link)
        
        return exported
    
    def _calculate_metrics(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics from graph data"""
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])
        
        total_nodes = len(nodes)
        total_links = len(links)
        
        # Count total functions and classes across all nodes
        total_functions = 0
        total_classes = 0
        
        for node in nodes:
            # Count functions
            if 'functions' in node:
                funcs = node['functions']
                if isinstance(funcs, list):
                    total_functions += len(funcs)
                elif isinstance(funcs, int):
                    total_functions += funcs
            
            # Count classes
            if 'classes' in node:
                classes = node['classes']
                if isinstance(classes, list):
                    total_classes += len(classes)
                elif isinstance(classes, int):
                    total_classes += classes
        
        # Calculate average dependencies
        if total_nodes > 0:
            avg_dependencies = total_links / total_nodes
        else:
            avg_dependencies = 0
        
        # Detect circular dependencies (simplified)
        circular_count = self._detect_circular_dependencies(links)
        
        # Calculate complexity score (simplified)
        complexity = (total_nodes * 0.5) + (total_links * 0.3) + (circular_count * 5)
        
        return {
            'total_nodes': total_nodes,
            'total_links': total_links,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_dependencies': round(avg_dependencies, 2),
            'circular_dependencies': circular_count,
            'complexity_score': round(complexity, 2)
        }
    
    def _detect_circular_dependencies(self, links: List[Dict[str, Any]]) -> int:
        """Detect circular dependencies (simplified check)"""
        # Build adjacency list
        graph = {}
        for link in links:
            source = link.get('source', '')
            target = link.get('target', '')
            if source not in graph:
                graph[source] = []
            graph[source].append(target)
        
        # Simple cycle detection
        visited = set()
        rec_stack = set()
        cycles = 0
        
        def has_cycle(node):
            nonlocal cycles
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        cycles += 1
                elif neighbor in rec_stack:
                    cycles += 1
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                has_cycle(node)
        
        return cycles
    
    def _filter_nodes(self, nodes: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter nodes based on criteria"""
        filtered = nodes
        
        # Filter by language
        if 'language' in filters:
            lang_filter = filters['language']
            if isinstance(lang_filter, str):
                lang_filter = [lang_filter]
            filtered = [n for n in filtered if n.get('language') in lang_filter]
        
        # Filter by file type
        if 'file_type' in filters:
            type_filter = filters['file_type']
            filtered = [n for n in filtered if n.get('type') == type_filter]
        
        # Filter by path pattern
        if 'path_pattern' in filters:
            pattern = filters['path_pattern']
            filtered = [n for n in filtered if pattern in n.get('path', '')]
        
        return filtered
