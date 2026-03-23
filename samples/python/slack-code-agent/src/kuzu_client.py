# src/kuzu_client.py
from typing import List, Optional, Any
from dataclasses import dataclass
import os

@dataclass
class Document:
    """Represents a document from KuzuDB."""
    id: str
    content: str
    source: str
    metadata: dict

class KuzuClient:
    """Client for querying KuzuDB graph database."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._connection = None
        self._available = None

    def is_available(self) -> bool:
        """Check if KuzuDB is available and accessible."""
        if self._available is not None:
            return self._available

        if not self.db_path:
            self._available = False
            return False

        if not os.path.exists(self.db_path):
            self._available = False
            return False

        try:
            import kuzu
            self._connection = kuzu.connect(self.db_path)
            self._available = True
            return True
        except Exception:
            self._available = False
            return False

    def query_documents(self, query: str, limit: int = 10) -> List[Document]:
        """Query documents semantically from KuzuDB."""
        if not self.is_available():
            return []

        try:
            # Placeholder - actual implementation depends on schema
            result = self._connection.execute("SELECT * FROM documents LIMIT ?", [limit])
            documents = []
            for row in result.get_as_dict():
                documents.append(Document(
                    id=row.get("id", ""),
                    content=row.get("content", ""),
                    source=row.get("source", ""),
                    metadata=row.get("metadata", {})
                ))
            return documents
        except Exception:
            return []

    def search_by_keyword(self, keyword: str) -> List[Document]:
        """Search documents by keyword."""
        if not self.is_available():
            return []

        try:
            result = self._connection.execute(
                "SELECT * FROM documents WHERE content CONTAINS ? LIMIT 50",
                [keyword]
            )
            documents = []
            for row in result.get_as_dict():
                documents.append(Document(
                    id=row.get("id", ""),
                    content=row.get("content", ""),
                    source=row.get("source", ""),
                    metadata=row.get("metadata", {})
                ))
            return documents
        except Exception:
            return []

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._available = None