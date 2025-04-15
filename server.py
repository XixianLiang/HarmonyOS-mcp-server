from hdc.app_manager import list_app, launch_app
from hdc.window_manager import get_uilayout, click, input_text
from hdc.media import get_screenshot
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("harmonyos")

mcp.tool()(list_app)
mcp.tool()(get_uilayout)
mcp.tool()(launch_app)
mcp.tool()(get_screenshot)
mcp.tool()(click)
mcp.tool()(input_text)

if __name__ == "__main__":
    mcp.run(transport="stdio")

