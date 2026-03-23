# src/project_analyzer.py
import ast
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


class ProjectAnalyzer:
    """Scans a Python project to extract code context for LLM queries."""

    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".env",
        ".pytest_cache",
        ".idea",
        ".vscode",
        "build",
        "dist",
        "*.egg-info",
    }

    # Maximum file size to process (in KB)
    MAX_FILE_SIZE_KB: int = 1000

    def __init__(self, project_root: str, max_context_tokens: int = 8000):
        """Initialize the ProjectAnalyzer.

        Args:
            project_root: Path to the root directory of the project to analyze.
            max_context_tokens: Maximum number of tokens to include in context.
        """
        self.project_root = Path(project_root).resolve()
        self.max_context_tokens = max_context_tokens
        self._file_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl: int = 900  # 15 minutes TTL

    def scan_directory(self) -> List[str]:
        """Scan the project directory for Python files.

        Returns:
            List of relative paths to Python files, excluding common directories.
        """
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS and not d.endswith(".egg-info")]

            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    relative_path = str(full_path.relative_to(self.project_root))
                    python_files.append(relative_path)

        return sorted(python_files)

    def extract_symbols(self, file_path: Path) -> Dict[str, List[str]]:
        """Extract code symbols (classes, functions, imports, docstrings) from a Python file.

        Args:
            file_path: Path to the Python file (can be relative or absolute).

        Returns:
            Dictionary with keys: 'classes', 'functions', 'imports', 'docstrings'
        """
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        result = {
            "classes": [],
            "functions": [],
            "imports": [],
            "docstrings": [],
        }

        if not file_path.exists():
            return result

        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            # Get module docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                result["docstrings"].append(("module", module_docstring))

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    result["classes"].append(node.name)
                    class_docstring = ast.get_docstring(node)
                    if class_docstring:
                        result["docstrings"].append((node.name, class_docstring))
                    # Get methods within class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            result["functions"].append(f"{node.name}.{item.name}")
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    result["functions"].append(node.name)
                    func_docstring = ast.get_docstring(node)
                    if func_docstring:
                        result["docstrings"].append((node.name, func_docstring))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        result["imports"].append(f"{module}.{alias.name}" if module else alias.name)

        except (SyntaxError, UnicodeDecodeError) as e:
            # Return empty result for files that can't be parsed
            pass

        return result

    def get_context_for_query(self, query: str, max_tokens: Optional[int] = None) -> str:
        """Build relevant context string based on query keywords.

        Args:
            query: The user's query to match against files/symbols.
            max_tokens: Optional override for max context tokens.

        Returns:
            A context string with file paths and relevant code.
        """
        if max_tokens is None:
            max_tokens = self.max_context_tokens

        # Extract keywords from query
        keywords = self._extract_keywords(query)

        # Check cache
        cache_key = f"{query}_{max_tokens}"
        if self._is_cache_valid() and cache_key in self._file_cache:
            return self._file_cache[cache_key].get("context", "")

        # Find relevant files
        relevant_files = self._find_relevant_files(keywords)

        # Build context string
        context_parts = []
        estimated_tokens = 0

        for file_path in relevant_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue

            # Skip files larger than MAX_FILE_SIZE_KB
            file_size_kb = full_path.stat().st_size // 1024
            if file_size_kb > self.MAX_FILE_SIZE_KB:
                continue

            try:
                content = full_path.read_text(encoding="utf-8")
                file_context = f"\n# File: {file_path}\n{content}\n"

                # Rough token estimation (4 chars per token on average)
                estimated_file_tokens = len(file_context) // 4

                if estimated_tokens + estimated_file_tokens > max_tokens:
                    # Include partial content if we have space
                    remaining_tokens = max_tokens - estimated_tokens
                    if remaining_tokens > 100:  # Only include if meaningful
                        remaining_chars = remaining_tokens * 4
                        partial_content = content[:remaining_chars]
                        context_parts.append(f"\n# File: {file_path} (truncated)\n{partial_content}\n")
                    break

                context_parts.append(file_context)
                estimated_tokens += estimated_file_tokens

            except (UnicodeDecodeError, OSError):
                continue

        context = "".join(context_parts)

        # Update cache
        self._file_cache[cache_key] = {"context": context, "timestamp": time.time()}
        self._cache_timestamp = time.time()

        return context

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from a query.

        Args:
            query: The user's query.

        Returns:
            List of lowercase keywords.
        """
        # Common stop words to exclude
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "how", "what", "where",
            "when", "why", "who", "which", "that", "this", "these", "those",
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
            "us", "them", "my", "your", "his", "its", "our", "their", "and",
            "or", "but", "if", "then", "else", "so", "for", "with", "about",
            "to", "of", "in", "on", "at", "by", "from", "into", "through",
            "during", "before", "after", "above", "below", "between", "under",
            "again", "further", "once", "here", "there", "all", "each", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "than", "too", "very", "just", "work", "works",
            "does", "do", "tell", "give", "show", "get", "let", "put",
        }

        # Split query into words and filter
        words = query.lower().split()
        keywords = []

        for word in words:
            # Clean word of punctuation
            cleaned = "".join(c for c in word if c.isalnum())
            if cleaned and cleaned not in stop_words and len(cleaned) > 1:
                keywords.append(cleaned)

        return keywords

    def _find_relevant_files(self, keywords: List[str]) -> List[str]:
        """Find files that match the given keywords.

        Args:
            keywords: List of keywords to match.

        Returns:
            List of file paths sorted by relevance.
        """
        scored_files = []

        for file_path in self.scan_directory():
            score = 0
            file_path_lower = file_path.lower()

            # Score based on filename match
            filename = Path(file_path).stem.lower()
            for keyword in keywords:
                if keyword in filename:
                    score += 10
                if keyword in file_path_lower:
                    score += 5

            # Score based on symbol names
            symbols = self.extract_symbols(Path(file_path))
            for func in symbols.get("functions", []):
                func_lower = func.lower()
                for keyword in keywords:
                    if keyword in func_lower:
                        score += 3

            for cls in symbols.get("classes", []):
                cls_lower = cls.lower()
                for keyword in keywords:
                    if keyword in cls_lower:
                        score += 3

            if score > 0:
                scored_files.append((file_path, score))

        # Sort by score (descending) and return paths
        scored_files.sort(key=lambda x: x[1], reverse=True)
        return [f[0] for f in scored_files]

    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid based on TTL.

        Returns:
            True if cache is valid, False otherwise.
        """
        if self._cache_timestamp == 0:
            return False
        return (time.time() - self._cache_timestamp) < self._cache_ttl

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._file_cache.clear()
        self._cache_timestamp = 0