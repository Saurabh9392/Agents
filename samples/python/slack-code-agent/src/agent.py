# src/agent.py
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

from .config import Config
from .project_analyzer import ProjectAnalyzer
from .kuzu_client import KuzuClient, Document
from .llm_handler import LLMHandler

# Keywords that indicate document queries
DOCUMENT_KEYWORDS = {
    "pdf", "document", "excel", "spreadsheet", "report", "notes",
    "meeting", "presentation", "word", "docx", "csv", "data",
    "figure", "chart", "graph", "summary", "what does the", "tell me about"
}

# Keywords that indicate code queries
CODE_KEYWORDS = {
    "file", "function", "class", "code", "method", "import",
    "def", "py", "js", "ts", "java", "codebase", "implement",
    "explain", "what does", "how does", "find"
}

@dataclass
class AgentResponse:
    text: str
    success: bool
    tokens_used: int = 0
    error: Optional[str] = None
    sources: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "success": self.success,
            "tokens_used": self.tokens_used,
            "error": self.error,
            "sources": self.sources or []
        }

class CodeAgent:
    """Main agent that coordinates code and document queries."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.project_analyzer = ProjectAnalyzer(
            self.config.project_root_path,
            max_context_tokens=self.config.max_context_tokens
        ) if self.config.is_project_configured() else None
        self.kuzu_client = KuzuClient(self.config.kuzu_db_path)
        self.llm_handler = LLMHandler()

    def is_code_query(self, query: str) -> bool:
        """Determine if query is about code."""
        query_lower = query.lower()
        for keyword in CODE_KEYWORDS:
            if keyword in query_lower:
                return True
        if any(ext in query_lower for ext in [".py", ".js", ".ts", ".java", ".go"]):
            return True
        return False

    def is_document_query(self, query: str) -> bool:
        """Determine if query is about documents."""
        query_lower = query.lower()
        for keyword in DOCUMENT_KEYWORDS:
            if keyword in query_lower:
                return True
        return False

    def get_code_context(self, query: str) -> tuple[str, List[str]]:
        """Get code context from project analyzer."""
        if not self.config.is_project_configured():
            return "", []

        # Lazy initialization if project was configured after agent creation
        if not self.project_analyzer:
            self.project_analyzer = ProjectAnalyzer(
                self.config.project_root_path,
                max_context_tokens=self.config.max_context_tokens
            )

        context = self.project_analyzer.get_context_for_query(query)
        files = self.project_analyzer.scan_directory()
        sources = [f for f in files if any(kw in f.lower() for kw in self._extract_keywords(query))]
        return context, sources

    def get_document_context(self, query: str) -> tuple[str, List[str]]:
        """Get document context from KuzuDB."""
        if not self.kuzu_client.is_available():
            return "", []

        documents = self.kuzu_client.query_documents(query, limit=10)
        if not documents:
            documents = self.kuzu_client.search_by_keyword(query)

        context_parts = []
        sources = []
        for doc in documents:
            context_parts.append(f"Document: {doc.source}\n{doc.content}")
            sources.append(doc.source)

        return "\n\n".join(context_parts), sources

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "what", "does", "how",
            "find", "explain", "tell", "me", "about", "in", "of", "for"
        }
        words = query.lower().split()
        return [w.strip("?.,!") for w in words if w not in stop_words and len(w) > 2]

    def process_message(self, message: str) -> AgentResponse:
        """Process user message and return response."""
        if not self.config.is_project_configured():
            return AgentResponse(
                text="Project not configured. Please set PROJECT_ROOT_PATH environment variable.",
                success=False,
                error="Project not configured"
            )

        is_code = self.is_code_query(message)
        is_doc = self.is_document_query(message)

        code_context = ""
        doc_context = ""
        sources = []

        if is_code or not is_doc:
            code_context, code_sources = self.get_code_context(message)
            sources.extend(code_sources)

        if is_doc or not is_code:
            doc_context, doc_sources = self.get_document_context(message)
            sources.extend(doc_sources)

        if not code_context and not doc_context:
            return AgentResponse(
                text="I couldn't find relevant information. Try asking about specific files, functions, or documents in your project.",
                success=False,
                error="No context found"
            )

        context_note = ""
        if is_doc and not doc_context and code_context:
            context_note = "\n\n(Note: Document search unavailable, answering from code only.)"
        elif is_code and not code_context and doc_context:
            context_note = "\n\n(Note: Code context unavailable, answering from documents only.)"

        full_query = message + context_note
        llm_response = self.llm_handler.generate(
            user_query=full_query,
            context=code_context,
            document_context=doc_context
        )

        if llm_response.success:
            return AgentResponse(
                text=llm_response.text,
                success=True,
                tokens_used=llm_response.tokens_used,
                sources=sources
            )
        else:
            return AgentResponse(
                text=f"AI service error: {llm_response.error or 'Unknown error'}",
                success=False,
                error=llm_response.error
            )
