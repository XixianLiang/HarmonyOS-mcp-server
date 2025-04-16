"""
    Handle with media (screen, audio)
    截屏
    播放/暂停/下一首/上一首
    增大音量/减少音量/静音
"""

import uuid
from .system import _execute_command, recv_file, shell
from mcp.server.fastmcp import Image
from PIL import Image as PILImage
from .proto import KeyCode


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


async def media_play_pause() -> str:
    """
    Play or pause media on the phone.

    Sends the media play/pause keycode to control any currently active media.
    Can be used to play music or videos that were recently playing.

    Returns:
        str: Success message if the command was sent, or an error message
             if the command failed.
    """
    Keycode = KeyCode.MEDIA_PLAY_PAUSE.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return f"Media play/pause command sent successfully"
    else:
        return f"Failed to control media: {res}"


async def media_next() -> str:
    """
    play the next media
    """
    Keycode = KeyCode.MEDIA_NEXT.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return "next media command sent successfully"
    else:
        return f"Failed to control media: {res}"


async def media_previous() -> str:
    """
    play the previous media
    """
    Keycode = KeyCode.MEDIA_PREVIOUS.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return "next previous command sent successfully"
    else:
        return f"Failed to control media: {res}"


async def volume_up() -> str:
    """
    turn up the volume
    """
    Keycode = KeyCode.VOLUME_UP.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return "Volume up command sent successfully"
    else:
        return f"Failed to control media: {res}"
    

async def volume_down() -> str:
    """
    turn down the volume
    """
    Keycode = KeyCode.VOLUME_DOWN.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return "Volume down command sent successfully"
    else:
        return f"Failed to control media: {res}"


async def volume_mute() -> str:
    """
    mute the volume
    """
    Keycode = KeyCode.VOLUME_MUTE.value
    success, res = await _execute_command(f"hdc shell uitest uiInput keyEvent {Keycode}")
    if success:
        return "Volume mute command sent successfully"
    else:
        return f"Failed to control media: {res}"