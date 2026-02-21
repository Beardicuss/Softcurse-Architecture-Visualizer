"""
Configuration file loader for YAML-based settings.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file (default: .visualizer.yml)
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path('.visualizer.yml')
    
    if not config_path.exists():
        return get_default_config()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        
        # Merge with defaults
        config = get_default_config()
        config.update(user_config)
        return config
    
    except (yaml.YAMLError, IOError) as e:
        print(f"[WARN] Failed to load config from {config_path}: {e}")
        print(f"[INFO] Using default configuration")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'exclude_dirs': [
            'venv', '.venv', 'env', 'node_modules', '.git', '__pycache__',
            'build', 'dist', 'target', 'bin', 'obj', '.vs', 'packages'
        ],
        'max_depth': 10,
        'languages': None,  # None = all languages
        'performance': {
            'cache_enabled': False,
            'profiling': False
        },
        'output': {
            'html_file': 'project_architecture.html',
            'open_browser': True
        }
    }


def save_example_config(path: Path = Path('.visualizer.yml.example')) -> None:
    """
    Save an example configuration file.
    
    Args:
        path: Where to save the example file
    """
    example_config = {
        'exclude_dirs': [
            'venv',
            'node_modules',
            '.git',
            '__pycache__',
            'build',
            'dist'
        ],
        'max_depth': 10,
        'languages': [
            'python',
            'javascript',
            'typescript',
            'csharp'
        ],
        'performance': {
            'cache_enabled': True,
            'profiling': False
        },
        'output': {
            'html_file': 'project_architecture.html',
            'open_browser': True
        }
    }
    
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"[INFO] Example config saved to {path}")
