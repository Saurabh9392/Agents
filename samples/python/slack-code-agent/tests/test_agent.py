from unittest.mock import patch, MagicMock

def test_agent_detects_code_query():
    """Test agent detects code-related queries."""
    with patch("src.agent.ProjectAnalyzer"):
        with patch("src.agent.KuzuClient"):
            with patch("src.agent.LLMHandler"):
                from src.agent import CodeAgent
                agent = CodeAgent()

                assert agent.is_code_query("What does main.py do?") == True
                assert agent.is_code_query("Find the login function") == True
                assert agent.is_document_query("What does main.py do?") == False

def test_agent_detects_document_query():
    """Test agent detects document queries."""
    with patch("src.agent.ProjectAnalyzer"):
        with patch("src.agent.KuzuClient"):
            with patch("src.agent.LLMHandler"):
                from src.agent import CodeAgent
                agent = CodeAgent()

                assert agent.is_document_query("What does the Q3 report say?") == True
                assert agent.is_document_query("Find info about revenue in PDFs") == True

def test_agent_returns_error_when_project_not_configured():
    """Test agent handles unconfigured project."""
    with patch("src.agent.ProjectAnalyzer") as mock_analyzer:
        with patch("src.agent.KuzuClient"):
            with patch("src.agent.LLMHandler"):
                from src.agent import CodeAgent
                agent = CodeAgent()
                agent.config.project_root_path = ""

                result = agent.process_message("What does this do?")

                assert "not configured" in result.text.lower()
                assert result.success == False

def test_agent_handles_parse_error():
    """Test agent returns proper error for unrecognized input."""
    with patch("src.agent.ProjectAnalyzer"):
        with patch("src.agent.KuzuClient"):
            with patch("src.agent.LLMHandler"):
                from src.agent import CodeAgent
                agent = CodeAgent()
                agent.config.project_root_path = ""

                result = agent.process_message("")

                assert result.success == False

def test_agent_combines_context_from_both_sources():
    """Test agent combines code and document context."""
    with patch("src.agent.ProjectAnalyzer") as mock_analyzer:
        mock_instance = MagicMock()
        mock_instance.get_context_for_query.return_value = "Code context: def main()"
        mock_instance.scan_directory.return_value = []
        mock_analyzer.return_value = mock_instance

        with patch("src.agent.KuzuClient") as mock_kuzu:
            mock_kuzu_instance = MagicMock()
            mock_kuzu_instance.query_documents.return_value = []
            mock_kuzu.return_value = mock_kuzu_instance

            with patch("src.agent.LLMHandler") as mock_llm:
                mock_llm_instance = MagicMock()
                mock_llm_instance.generate.return_value = MagicMock(
                    text="Test response",
                    success=True,
                    tokens_used=100
                )
                mock_llm.return_value = mock_llm_instance

                from src.agent import CodeAgent
                agent = CodeAgent()
                agent.config.project_root_path = "/test/path"

                result = agent.process_message("Explain the code")

                assert result.success == True
                mock_llm_instance.generate.assert_called_once()
