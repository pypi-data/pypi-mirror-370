from mcp.server import FastMCP

from .tools.date_conversion import register_date_conversion_tools
from .tools.prayer_times import register_prayer_times_tools
from .tools.qibla import register_qibla_tools
from .tools.calendars import register_calendar_tools

server = FastMCP("aladhan-mcp")


def register_all_tools():
    """Register all tools with the server"""
    register_date_conversion_tools(server)
    register_prayer_times_tools(server)
    register_qibla_tools(server)
    register_calendar_tools(server)


def main():
    # Register all tools
    register_all_tools()
    
    # Start the server with stdio transport
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
