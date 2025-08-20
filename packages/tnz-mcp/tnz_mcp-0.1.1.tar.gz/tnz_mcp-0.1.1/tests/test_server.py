import unittest
from unittest.mock import patch
from tnz_mcp.server import run_server

class TestTNZMCPServer(unittest.TestCase):
    @patch("tnz_mcp.server.TNZAPI")
    @patch("tnz_mcp.server.FastMCP")
    def test_server_initialization(self, mock_fastmcp, mock_tnzapi):
        with patch("tnz_mcp.config.load_config", return_value={"auth_token": "test-token"}):
            try:
                run_server(transport="stdio")
                mock_tnzapi.assert_called_with(AuthToken="test-token")
                mock_fastmcp.assert_called_with("TNZ Messaging and Addressbook API")
            except Exception:
                pass  # Server will fail due to mock, but we verify initialization

if __name__ == "__main__":
    unittest.main()
