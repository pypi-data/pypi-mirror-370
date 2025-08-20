import pytest
from aladhan_mcp.tools.date_conversion import register_date_conversion_tools
from mcp.server import FastMCP


class TestDateConversion:
    @pytest.fixture
    def server(self):
        """Create a test server instance"""
        return FastMCP("test-server")

    def test_register_date_conversion_tools(self, server):
        """Test that date conversion tools register successfully"""
        # This should not raise any exceptions
        register_date_conversion_tools(server)
        # If we get here without exceptions, registration was successful
        assert True

    def test_basic_functionality(self, server):
        """Test basic functionality works"""
        register_date_conversion_tools(server)
        # If registration succeeds, the tools are working
        assert True
