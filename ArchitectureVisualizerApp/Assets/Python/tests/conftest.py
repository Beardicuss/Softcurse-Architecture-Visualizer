"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    content = '''"""
Sample module for testing.
"""

def hello_world():
    """Say hello."""
    return "Hello, World!"

class SampleClass:
    """Sample class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Greet by name."""
        return f"Hello, {self.name}!"
'''
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_js_file(tmp_path):
    """Create a sample JavaScript file for testing."""
    content = '''/**
 * Sample JavaScript module
 */

function helloWorld() {
    return "Hello, World!";
}

class SampleClass {
    constructor(name) {
        this.name = name;
    }
    
    greet() {
        return `Hello, ${this.name}!`;
    }
}

module.exports = { helloWorld, SampleClass };
'''
    file_path = tmp_path / "sample.js"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_project_dir(tmp_path):
    """Create a sample project directory structure."""
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "node_modules").mkdir()  # Should be excluded
    
    # Create Python files
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "main.py").write_text("def main(): pass")
    
    # Create JS files
    (tmp_path / "src" / "index.js").write_text("console.log('test');")
    
    return tmp_path
