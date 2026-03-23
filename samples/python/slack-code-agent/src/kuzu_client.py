# src/kuzu_client.py
from typing import List, Optional, Any
from dataclasses import dataclass
import logging
import os

logger = logging.getLogger(__name__)

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

    def _connect(self) -> bool:
        """Establish connection to KuzuDB. Returns True on success."""
        if self._connection is not None:
            return True

        if not self.db_path:
            return False

        if not os.path.exists(self.db_path):
            return False

        try:
            import kuzu
            self._connection = kuzu.connect(self.db_path)
            return True
        except Exception as e:
            logger.warning("Failed to connect to KuzuDB: %s", e)
            return False

    def is_available(self) -> bool:
        """Check if KuzuDB is available and accessible."""
        if self._available is not None:
            return self._available

        self._available = self._connect()
        return self._available

    @staticmethod
    def _row_to_document(row: dict) -> Document:
        """Convert a database row to a Document instance."""
        return Document(
            id=row.get("id", ""),
            content=row.get("content", ""),
            source=row.get("source", ""),
            metadata=row.get("metadata", {})
        )

    def query_documents(self, query: str, limit: int = 10) -> List[Document]:
        """Query documents semantically from KuzuDB."""
        if not self.is_available():
            return []

        try:
            # Placeholder - actual implementation depends on schema
            result = self._connection.execute("SELECT * FROM documents LIMIT $1", [limit])
            documents = []
            for row in result.get_as_dict():
                documents.append(self._row_to_document(row))
            return documents
        except Exception as e:
            logger.error("Error querying documents: %s", e)
            return []

    def search_by_keyword(self, keyword: str) -> List[Document]:
        """Search documents by keyword."""
        if not self.is_available():
            return []

        try:
            result = self._connection.execute(
                "SELECT * FROM documents WHERE content CONTAINS $1 LIMIT 50",
                [keyword]
            )
            documents = []
            for row in result.get_as_dict():
                documents.append(self._row_to_document(row))
            return documents
        except Exception as e:
            logger.error("Error searching by keyword: %s", e)
            return []

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._available = None

    def __enter__(self) -> "KuzuClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()