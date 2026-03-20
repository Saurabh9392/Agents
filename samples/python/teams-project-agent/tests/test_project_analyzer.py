# tests/test_project_analyzer.py
import pytest
import tempfile
import os
from pathlib import Path
from src.project_analyzer import ProjectAnalyzer


@pytest.fixture
def sample_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample files
        Path(tmpdir, "main.py").write_text('def main():\n    print("hello")\n')
        Path(tmpdir, "utils.py").write_text('def helper():\n    return 42\n')
        Path(tmpdir, "__init__.py").write_text("")
        os.makedirs(Path(tmpdir, "subdir"), exist_ok=True)
        Path(tmpdir, "subdir", "module.py").write_text('class MyClass:\n    pass\n')
        yield tmpdir


class TestProjectAnalyzer:
    def test_scan_directory_finds_python_files(self, sample_project):
        analyzer = ProjectAnalyzer(sample_project)
        files = analyzer.scan_directory()
        assert len(files) >= 3  # main.py, utils.py, subdir/module.py

    def test_scan_directory_excludes_venv(self, sample_project):
        os.makedirs(Path(sample_project, ".venv"), exist_ok=True)
        Path(sample_project, ".venv", "skip.py").write_text("# skip")
        analyzer = ProjectAnalyzer(sample_project)
        files = analyzer.scan_directory()
        assert not any(".venv" in f for f in files)


class TestSymbolExtraction:
    def test_extract_symbols_finds_function(self, sample_project):
        analyzer = ProjectAnalyzer(sample_project)
        symbols = analyzer.extract_symbols(Path(sample_project, "main.py"))
        assert "main" in symbols["functions"]

    def test_extract_symbols_finds_class(self, sample_project):
        analyzer = ProjectAnalyzer(sample_project)
        symbols = analyzer.extract_symbols(Path(sample_project, "subdir", "module.py"))
        assert "MyClass" in symbols["classes"]


class TestContextSelection:
    def test_get_context_for_query_finds_relevant_files(self, sample_project):
        Path(sample_project, "auth.py").write_text(
            "def login(username, password):\n    return True\n"
        )
        analyzer = ProjectAnalyzer(sample_project)
        context = analyzer.get_context_for_query("How does login work?")
        assert "auth.py" in context or "login" in context.lower()
