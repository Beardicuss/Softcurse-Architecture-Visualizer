"""
Tests for Python analyzer.
"""

import pytest
from pathlib import Path
from analyzers.python_analyzer import analyze_file_python
def test_python_analyzer_imports(tmp_path):
    """Test Python import detection."""
    content = '''import os
import sys
from pathlib import Path
from typing import List, Dict
'''
    file_path = tmp_path / "imports.py"
    file_path.write_text(content)
    
    functions, classes, imports, docstring, meta = analyze_file_python(file_path)
    
    # Standard library imports should be filtered
    assert "os" not in imports
    assert "sys" not in imports
    assert "pathlib" not in imports


def test_python_analyzer_decorators(tmp_path):
    """Test decorator detection."""
    content = '''
@property
def my_property(self):
    return self._value

@staticmethod
def static_method():
    pass

@classmethod
def class_method(cls):
    pass
'''
    file_path = tmp_path / "decorators.py"
    file_path.write_text(content)
    
    functions, classes, imports, docstring, meta = analyze_file_python(file_path)
    
    assert "decorators" in meta
    assert "property" in meta["decorators"]
    assert "staticmethod" in meta["decorators"]
    assert "classmethod" in meta["decorators"]


def test_python_analyzer_error_handling(tmp_path):
    """Test error handling for invalid Python files."""
    content = "this is not valid python code {"
    file_path = tmp_path / "invalid.py"
    file_path.write_text(content)
    
    # Should not crash, should return empty results
    functions, classes, imports, docstring, meta = analyze_file_python(file_path)
    
    assert isinstance(functions, list)
    assert isinstance(classes, list)
    assert isinstance(imports, list)
