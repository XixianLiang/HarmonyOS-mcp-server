"""
    Handle with media (screen, audio)
    截图/录屏
    拨打/挂断电话
    播放/暂停音乐
"""

import uuid
from .system import _execute_command, recv_file
from mcp.server.fastmcp import Image
from PIL import Image as PILImage


async def screenshot(path: str) -> str:
    """
    take screenshot
    :param path: the local path for saving the screenshot
    """
    _uuid = uuid.uuid4().hex
    _tmp_path = f"/data/local/tmp/_tmp_{_uuid}.jpeg"
    await _execute_command(f"hdc shell snapshot_display -f {_tmp_path}")
    await recv_file(_tmp_path, path)
    await _execute_command(f"hdc shell rm -rf {_tmp_path}")  # remove local path
    return path

async def get_screenshot() -> Image:
    """Takes a screenshot of the device and returns it.
    Returns:
        Image: the screenshot
    """
    path = await screenshot("screenshot.png")
    # compressing the ss to avoid "maximum call stack exceeded" error on claude desktop
    with PILImage.open(path) as img:
        width, height = img.size
        new_width = int(width * 0.3)
        new_height = int(height * 0.3)
        resized_img = img.resize(
            (new_width, new_height), PILImage.Resampling.LANCZOS
        )
        resized_img.save(
            "compressed_screenshot.png", "PNG", quality=85, optimize=True
        )
    return Image("compressed_screenshot.png")

async def call_number(number: str) -> str:
    pass

async def end_call(number: str) -> str:
    pass

async def play_media() -> str:
    """
    Play or pause media on the phone.

    Sends the media play/pause keycode to control any currently active media.
    Can be used to play music or videos that were recently playing.

    Returns:
        str: Success message if the command was sent, or an error message
             if the command failed.
    """
    pass
