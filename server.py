from hdc.app_manager import list_app, launch_app, stop_app, current_app
from hdc.window_manager import get_uilayout, click, long_click, swipe, input_text
from hdc.media import get_screenshot, media_play_pause, volume_up, volume_down, volume_mute, media_next, media_previous
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("harmonyos")

mcp.tool()(list_app)
mcp.tool()(launch_app)
mcp.tool()(stop_app)        # 跑不了
mcp.tool()(current_app)

mcp.tool()(media_play_pause)
mcp.tool()(media_next)
mcp.tool()(media_previous)
mcp.tool()(volume_up)
mcp.tool()(volume_down)
mcp.tool()(volume_mute)

mcp.tool()(get_uilayout)
mcp.tool()(get_screenshot)
mcp.tool()(click)
mcp.tool()(long_click)
mcp.tool()(swipe)
mcp.tool()(input_text)

if __name__ == "__main__":
    mcp.run(transport="stdio")

