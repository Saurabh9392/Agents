import tempfile
import os
from unittest.mock import patch, MagicMock

def test_kuzu_client_is_available_returns_false_when_no_db():
    """Test is_available returns False when DB doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from src.kuzu_client import KuzuClient
        client = KuzuClient(tmpdir + "/nonexistent.db")
        assert client.is_available() == False

def test_kuzu_client_is_available_returns_true_when_db_exists():
    """Test is_available returns True when DB exists (mock)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        # Create the file so os.path.exists returns True
        open(db_path, 'w').close()

        mock_conn = MagicMock()
        mock_kuzu_module = MagicMock()
        mock_kuzu_module.connect.return_value = mock_conn

        with patch.dict("sys.modules", {"kuzu": mock_kuzu_module}):
            from src.kuzu_client import KuzuClient
            client = KuzuClient(db_path)
            result = client.is_available()

            assert result == True
            assert client._available == True

def test_query_documents_returns_empty_when_unavailable():
    """Test query_documents returns empty list when DB is unavailable."""
    from src.kuzu_client import KuzuClient
    client = KuzuClient("/nonexistent/path.db")
    result = client.query_documents("test query")
    assert result == []

def test_query_documents_returns_documents_on_success():
    """Test query_documents returns documents when DB is available."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        open(db_path, 'w').close()

        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.get_as_dict.return_value = [
            {"id": "1", "content": "test content", "source": "file1", "metadata": {}},
            {"id": "2", "content": "another doc", "source": "file2", "metadata": {}},
        ]
        mock_conn.execute.return_value = mock_result

        mock_kuzu_module = MagicMock()
        mock_kuzu_module.connect.return_value = mock_conn

        with patch.dict("sys.modules", {"kuzu": mock_kuzu_module}):
            from src.kuzu_client import KuzuClient
            client = KuzuClient(db_path)
            # Force connection
            client._connect()
            client._available = True
            client._connection = mock_conn

            result = client.query_documents("test query")

            assert len(result) == 2
            assert result[0].id == "1"
            assert result[0].content == "test content"
            assert result[1].id == "2"

def test_search_by_keyword_returns_empty_when_unavailable():
    """Test search_by_keyword returns empty list when DB is unavailable."""
    from src.kuzu_client import KuzuClient
    client = KuzuClient("/nonexistent/path.db")
    result = client.search_by_keyword("test")
    assert result == []

def test_search_by_keyword_returns_documents_on_success():
    """Test search_by_keyword returns matching documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        open(db_path, 'w').close()

        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.get_as_dict.return_value = [
            {"id": "3", "content": "python code", "source": "file3", "metadata": {"lang": "en"}},
        ]
        mock_conn.execute.return_value = mock_result

        mock_kuzu_module = MagicMock()
        mock_kuzu_module.connect.return_value = mock_conn

        with patch.dict("sys.modules", {"kuzu": mock_kuzu_module}):
            from src.kuzu_client import KuzuClient
            client = KuzuClient(db_path)
            client._connect()
            client._available = True
            client._connection = mock_conn

            result = client.search_by_keyword("python")

            assert len(result) == 1
            assert result[0].id == "3"
            assert result[0].content == "python code"
            assert result[0].metadata == {"lang": "en"}

def test_context_manager():
    """Test KuzuClient supports context manager protocol."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        open(db_path, 'w').close()

        mock_conn = MagicMock()
        mock_kuzu_module = MagicMock()
        mock_kuzu_module.connect.return_value = mock_conn

        with patch.dict("sys.modules", {"kuzu": mock_kuzu_module}):
            from src.kuzu_client import KuzuClient
            with KuzuClient(db_path) as client:
                client._connect()
                assert client._connection is not None

            # After context exit, connection should be closed
            assert client._connection is None
            assert client._available is None

def test_row_to_document_helper():
    """Test _row_to_document static method correctly maps row to Document."""
    from src.kuzu_client import KuzuClient, Document

    row = {
        "id": "doc1",
        "content": "Hello world",
        "source": "test.txt",
        "metadata": {"author": "test"}
    }

    doc = KuzuClient._row_to_document(row)

    assert isinstance(doc, Document)
    assert doc.id == "doc1"
    assert doc.content == "Hello world"
    assert doc.source == "test.txt"
    assert doc.metadata == {"author": "test"}