"""Quick fix for visualizer.js - change data.stats to data.metrics"""
import re

file_path = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\Assets\Python\ui\static\js\visualizer.js"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace data.stats with data.metrics in initStats function
content = content.replace('data.stats.total_files', 'data.metadata.total_files')
content = content.replace('data.stats.total_functions', 'data.metrics.total_functions')
content = content.replace('data.stats.total_classes', 'data.metrics.total_classes')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed visualizer.js - changed data.stats to data.metrics")
