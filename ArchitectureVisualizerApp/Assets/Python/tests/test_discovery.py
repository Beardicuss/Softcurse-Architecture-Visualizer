"""
Tests for file discovery functionality.
"""

import pytest
from pathlib import Path
from core.discovery import detect_language, discover_source_files_lazy, module_name_from_path


def test_detect_language_python():
    """Test Python file detection."""
    file_path = Path("test.py")
    lang, config = detect_language(file_path)
    
    assert lang == "python"
    assert config is not None
    assert ".py" in config["extensions"]


def test_detect_language_javascript():
    """Test JavaScript file detection."""
    for ext in [".js", ".jsx", ".mjs"]:
        file_path = Path(f"test{ext}")
        lang, config = detect_language(file_path)
        
        assert lang == "javascript"
        assert ext in config["extensions"]


def test_detect_language_unknown():
    """Test unknown file type."""
    file_path = Path("test.xyz")
    lang, config = detect_language(file_path)
    
    assert lang is None
    assert config is None


def test_discover_source_files_basic(sample_project_dir):
    """Test basic file discovery."""
    files = list(discover_source_files_lazy(sample_project_dir))
    
    # Should find Python and JS files
    file_paths = [str(f[0].name) for f in files]
    assert "main.py" in file_paths
    assert "index.js" in file_paths
    
    # Should not include __init__.py in results (it's empty)
    # Should not find files in node_modules
    assert not any("node_modules" in str(f[0]) for f in files)


def test_discover_excludes_trash_dirs(tmp_path):
    """Test that trash directories are excluded."""
    # Create trash directories
    (tmp_path / "venv").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "build").mkdir()
    
    # Create files in trash dirs
    (tmp_path / "venv" / "test.py").write_text("# should be excluded")
    (tmp_path / "node_modules" / "test.js").write_text("// should be excluded")
    
    # Create valid file
    (tmp_path / "main.py").write_text("def main(): pass")
    
    files = list(discover_source_files_lazy(tmp_path))
    file_paths = [str(f[0]) for f in files]
    
    # Should only find main.py
    assert len(files) == 1
    assert "main.py" in str(files[0][0])


def test_module_name_from_path():
    """Test module name generation."""
    root = Path("/project")
    
    # Regular file
    file_path = Path("/project/src/utils.py")
    name = module_name_from_path(root, file_path)
    assert name == "project.src.utils"
    
    # __init__.py
    file_path = Path("/project/src/__init__.py")
    name = module_name_from_path(root, file_path)
    assert name == "project.src"
    
    # index.js
    file_path = Path("/project/src/index.js")
    name = module_name_from_path(root, file_path)
    assert name == "project.src"


def test_module_name_outside_root():
    """Test module name for file outside root."""
    root = Path("/project")
    file_path = Path("/other/file.py")
    
    name = module_name_from_path(root, file_path)
    assert name is None
