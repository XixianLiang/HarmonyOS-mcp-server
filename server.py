import logging
from hdc.app_manager import list_app
from hdc.ui_manager import get_uilayout
from hdc.media import get_screenshot
from hdc.system import launch_package

from mcp.server.fastmcp import FastMCP

# Initialize MCP and device manager
# Error checking is done inside HDCDeviceManager's constructor
mcp = FastMCP("harmonyos")

mcp.tool()(list_app)
mcp.tool()(get_uilayout)
mcp.tool()(launch_package)
mcp.tool()(get_screenshot)

# logging.info("Activating server")
# if __name__ == "__main__":
#     # print(deviceManager.get_uilayout())
#     mcp.run(transport="stdio")
