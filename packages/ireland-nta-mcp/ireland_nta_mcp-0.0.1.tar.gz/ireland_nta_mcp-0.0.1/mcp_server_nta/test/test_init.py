"""
Tests for the MCP Server initialization and configuration.
"""
import os
import pytest
from unittest.mock import patch
from mcp_server_nta import main


class TestMcpServerInit:
    """Test class for MCP Server initialization."""

    def test_main_raises_error_without_api_key(self):
        """Test that main() raises ValueError when no API key is provided."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('mcp_server_nta.load_dotenv', return_value=None):
                with pytest.raises(ValueError) as excinfo:
                    main()
                assert "NTA_API_KEY must be set" in str(excinfo.value)

    def test_main_runs_with_api_key(self, mock_api_key):
        """Test that main() calls asyncio.run with the API key when provided."""
        
        with patch.dict(os.environ, {"NTA_API_KEY": mock_api_key}, clear=True):
            with patch('mcp_server_nta.load_dotenv', return_value=None):
                with patch('mcp_server_nta.asyncio.run') as mock_run:
                    main()
                    mock_run.assert_called_once()
                    # Check that the serve function was called with the API key
                    args, _ = mock_run.call_args
                    assert len(args) == 1  # The serve coroutine
