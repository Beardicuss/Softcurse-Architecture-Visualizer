"""
Tests for multi-language support.
"""

import pytest
from pathlib import Path
from core.discovery import detect_language


def test_all_languages_configured():
    '''Test that all 13 languages are configured.'''
    from core.config import LANGUAGE_CONFIG
    
    expected = ['python', 'javascript', 'typescript', 'java', 'csharp',
                'go', 'rust', 'cpp', 'php', 'ruby', 'swift', 'kotlin', 'dart']
    
    for lang in expected:
        assert lang in LANGUAGE_CONFIG
        assert 'extensions' in LANGUAGE_CONFIG[lang]


def test_javascript_detection():
    for ext in ['.js', '.jsx', '.mjs']:
        lang, _ = detect_language(Path(f"test{ext}"))
        assert lang == "javascript"


def test_typescript_detection():
    for ext in ['.ts', '.tsx']:
        lang, _ = detect_language(Path(f"test{ext}"))
        assert lang == "typescript"


def test_csharp_detection():
    lang, _ = detect_language(Path("test.cs"))
    assert lang == "csharp"


def test_java_detection():
    lang, _ = detect_language(Path("test.java"))
    assert lang == "java"


def test_go_detection():
    lang, _ = detect_language(Path("test.go"))
    assert lang == "go"


def test_rust_detection():
    lang, _ = detect_language(Path("test.rs"))
    assert lang == "rust"


def test_cpp_detection():
    for ext in ['.cpp', '.hpp']:
        lang, _ = detect_language(Path(f"test{ext}"))
        assert lang == "cpp"


def test_php_detection():
    lang, _ = detect_language(Path("test.php"))
    assert lang == "php"


def test_ruby_detection():
    lang, _ = detect_language(Path("test.rb"))
    assert lang == "ruby"


def test_swift_detection():
    lang, _ = detect_language(Path("test.swift"))
    assert lang == "swift"


def test_kotlin_detection():
    for ext in ['.kt', '.kts']:
        lang, _ = detect_language(Path(f"test{ext}"))
        assert lang == "kotlin"


def test_dart_detection():
    lang, _ = detect_language(Path("test.dart"))
    assert lang == "dart"
