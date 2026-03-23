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