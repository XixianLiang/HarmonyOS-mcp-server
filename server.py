import logging
# from hdc.hdc import list_app, get_uilayout
from hdc.hdc import *
from mcp.server.fastmcp import FastMCP, Image

# Initialize MCP and device manager
# Error checking is done inside HDCDeviceManager's constructor
mcp = FastMCP("harmonyos")

mcp.tool()(list_app)
mcp.tool()(get_uilayout)
mcp.tool()(get_screenshot)
# mcp.tool()(open_app)
# mcp.tool()(call_number)
# mcp.tool()(end_call)
# @mcp.tool(launch_package)

# @mcp.tool()
# async def click(center: str):
#     """
#     click the center
#     Args:
#         center (str): The coordinate. e.g. (577, 244)
#     """
#     await HDCDeviceManager().click(center)

# @mcp.tool()
# async def input_text(center: str, text: str):
#     """
#     input text to the center
#     Args:
#         center (str): The coordinate. e.g. (577, 244)
#         text: the text to input.
#     """
#     await HDCDeviceManager().input_text(center, text)


# logging.info("Activating server")
# if __name__ == "__main__":
#     # print(deviceManager.get_uilayout())
#     mcp.run(transport="stdio")
