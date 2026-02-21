"""
Tests for cache functionality.
"""

import pytest
from pathlib import Path
from core.cache import IncrementalAnalyzer


def test_cache_initialization(tmp_path):
    """Test cache initialization."""
    cache_file = tmp_path / "test_cache.json"
    analyzer = IncrementalAnalyzer(cache_file)
    
    assert analyzer.cache_file == cache_file
    assert analyzer.hits == 0
    assert analyzer.misses == 0
    assert isinstance(analyzer.cache, dict)


def test_cache_file_hash(tmp_path):
    """Test file hashing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")
    
    cache_file = tmp_path / "cache.json"
    analyzer = IncrementalAnalyzer(cache_file)
    
    hash1 = analyzer._file_hash(test_file)
    assert hash1 is not None
    
    # Same content should give same hash
    hash2 = analyzer._file_hash(test_file)
    assert hash1 == hash2
    
    # Different content should give different hash
    test_file.write_text("Different content")
    hash3 = analyzer._file_hash(test_file)
    assert hash1 != hash3


def test_cache_hit_and_miss(tmp_path):
    """Test cache hit and miss counting."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    cache_file = tmp_path / "cache.json"
    analyzer = IncrementalAnalyzer(cache_file)
    
    def mock_analyze(path, lang, config):
        return (["test"], [], [], None, {})
    
    # First call should be a miss
    result1 = analyzer.analyze_with_cache(test_file, "python", {}, mock_analyze)
    assert analyzer.misses == 1
    assert analyzer.hits == 0
    
    # Second call with same file should be a hit
    result2 = analyzer.analyze_with_cache(test_file, "python", {}, mock_analyze)
    assert analyzer.hits == 1
    assert analyzer.misses == 1
    
    # Results should be the same
    assert result1 == result2


def test_cache_persistence(tmp_path):
    """Test cache saving and loading."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    cache_file = tmp_path / "cache.json"
    
    def mock_analyze(path, lang, config):
        return (["test"], [], [], None, {})
    
    # Create analyzer and cache a result
    analyzer1 = IncrementalAnalyzer(cache_file)
    analyzer1.analyze_with_cache(test_file, "python", {}, mock_analyze)
    analyzer1.save()
    
    # Create new analyzer - should load cached data
    analyzer2 = IncrementalAnalyzer(cache_file)
    result = analyzer2.analyze_with_cache(test_file, "python", {}, mock_analyze)
    
    # Should be a cache hit
    assert analyzer2.hits == 1
    assert analyzer2.misses == 0


def test_cache_invalidation_on_change(tmp_path):
    """Test cache invalidation when file changes."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    cache_file = tmp_path / "cache.json"
    analyzer = IncrementalAnalyzer(cache_file)
    
    call_count = 0
    def mock_analyze(path, lang, config):
        nonlocal call_count
        call_count += 1
        return ([f"test{call_count}"], [], [], None, {})
    
    # First call
    result1 = analyzer.analyze_with_cache(test_file, "python", {}, mock_analyze)
    assert call_count == 1
    
    # Modify file
    test_file.write_text("def test(): return 42")
    
    # Should re-analyze
    result2 = analyzer.analyze_with_cache(test_file, "python", {}, mock_analyze)
    assert call_count == 2
    assert result1 != result2
