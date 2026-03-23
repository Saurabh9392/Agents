import tempfile
import os
from pathlib import Path

def test_scan_directory_finds_python_files():
    """Test that scan_directory finds .py files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "main.py").write_text("def main(): pass")
        Path(tmpdir, "utils.py").write_text("def helper(): pass")
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "nested.py").write_text("class Foo: pass")

        from src.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer(tmpdir)
        files = analyzer.scan_directory()

        assert "main.py" in files
        assert "utils.py" in files
        assert any("nested.py" in f for f in files)

def test_scan_directory_excludes_venv():
    """Test that venv and __pycache__ are excluded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "main.py").write_text("def main(): pass")
        Path(tmpdir, "venv").mkdir()
        Path(tmpdir, "venv", "script.py").write_text("import py")
        Path(tmpdir, "__pycache__").mkdir()
        Path(tmpdir, "__pycache__", "cached.pyc").write_text("")

        from src.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer(tmpdir)
        files = analyzer.scan_directory()

        assert "main.py" in files
        assert not any("venv" in f for f in files)
        assert not any("__pycache__" in f for f in files)

def test_extract_symbols_extracts_classes_and_functions():
    """Test AST parsing extracts classes and functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "sample.py").write_text('''
class MyClass:
    def method(self): pass

def standalone_function(): pass
''')
        from src.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer(tmpdir)
        symbols = analyzer.extract_symbols(Path(tmpdir, "sample.py"))

        assert "MyClass" in symbols["classes"]
        assert "MyClass.method" in symbols["functions"]
        assert "standalone_function" in symbols["functions"]

def test_get_context_for_query_finds_relevant_files():
    """Test context building finds relevant files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "auth.py").write_text("def login(): pass")
        Path(tmpdir, "main.py").write_text("def main(): pass")

        from src.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer(tmpdir)
        context = analyzer.get_context_for_query("login authentication")

        assert "auth.py" in context
        assert "login" in context