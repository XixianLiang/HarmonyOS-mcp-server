# -*- coding: utf-8 -*-
import asyncio
import tempfile
import json
import uuid
import shlex
import re
import subprocess
from typing import Union, List, Dict, Tuple, TypedDict

from .execption import HdcError, DeviceNotFoundError, DeviceAmbigiousError
from .proto import KeyCode
from .utils import FreePort
from . import logger
from logging import INFO, info

class NodeInfo(TypedDict):
    accessibilityId: str
    backgroundColor: str
    backgroundImage: str
    blur: str
    bounds: str
    checkable: str
    checked: str 
    clickable: str
    description: str
    enabled: str
    focused : str
    hitTestBehavior : str
    hostWindowId : str
    id : str
    key : str
    longClickable : str
    opacity : str
    origBounds : str
    scrollable : str
    selected : str
    text : str
    type : str
    zIndex : str

async def _execute_command(cmd: str, timeout: int = None) -> tuple[bool, str]:
    """Run a shell command and return success status and output.

    Args:
        cmd (str): Shell command to execute.
        timeout (int, optional): Command execution timeout in seconds.
                                If None, uses the default from config.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if command succeeded (exit code 0), False otherwise
            - str: Command output (stdout) if successful, error message (stderr) if failed
    """
    # Use default timeout from config if not specified
    if isinstance(cmd, (list, tuple)):
        cmd: str = ' '.join(list(map(shlex.quote, cmd)))
    
    if timeout is None:
        timeout = 10
        
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            if process.returncode == 0:
                return True, stdout.decode('utf-8')
            else:
                return False, stderr.decode('utf-8')
        except asyncio.TimeoutError:
            # Try to terminate the process if it timed out
            try:
                process.terminate()
                await process.wait()
            except:
                pass
            return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, str(e)

# def _execute_command(cmdargs: Union[str, List[str]]) -> CommandResult:
#     if isinstance(cmdargs, (list, tuple)):
#         cmdline: str = ' '.join(list(map(shlex.quote, cmdargs)))
#     elif isinstance(cmdargs, str):
#         cmdline = cmdargs

#     logger.debug(cmdline)
#     try:
#         process = subprocess.Popen(cmdline, stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE, shell=True)
#         output, error = process.communicate()
#         output = output.decode('utf-8')
#         error = error.decode('utf-8')
#         exit_code = process.returncode

#         if 'error:' in output.lower() or '[fail]' in output.lower():
#             return CommandResult("", output, -1)

#         return CommandResult(output, error, exit_code)
#     except Exception as e:
#         return CommandResult("", str(e), -1)


# def _build_hdc_prefix() -> str:
#     """
#     Construct the hdc command prefix based on environment variables.
#     """
#     host = os.getenv("HDC_SERVER_HOST")
#     port = os.getenv("HDC_SERVER_PORT")
#     if host and port:
#         logger.debug(f"HDC_SERVER_HOST: {host}, HDC_SERVER_PORT: {port}")
#         return f"hdc -s {host}:{port}"
#     return "hdc"


# async def list_devices() -> List[str]:
#     devices = []
#     hdc_prefix = _build_hdc_prefix()
#     success, result = await _execute_command(f"{hdc_prefix} list targets")
#     if success:
#         lines = result.strip().split('\n')
#         for line in lines:
#             devices.append(line.strip())
#         return devices

#     return f"[Fail] {result}"

# def send_file(self, lpath: str, rpath: str):
#     result = _execute_command(f"{self.hdc_prefix} -t {self.serial} file send {lpath} {rpath}")
#     if result.exit_code != 0:
#         raise HdcError("HDC send file error", result.error)
#     return result

async def recv_file(rpath: str, lpath: str):
    success, result = await _execute_command(f"hdc shell file recv {rpath} {lpath}")
    if success:
        return result

async def shell(cmd: str) -> str:
    # ensure the command is wrapped in double quotes
    if cmd[0] != '\"':
        cmd = "\"" + cmd
    if cmd[-1] != '\"':
        cmd += '\"'
    success, result = await _execute_command(f"hdc shell {cmd}")
    if not success:
        raise HdcError("HDC shell error", f"{cmd}\n{result}")
    return result

async def list_app() -> List[str]:
    """
    Get all installed packages on the device
    Returns:
        str: A list of all installed packages on the device as a string
    """
    success, result = await _execute_command(f"hdc shell bm dump -a")
    if success:
        raw = result.split('\n')
        return [item.strip() for item in raw if not item.startswith("ID") and item != ""]

async def has_app(package_name: str) -> bool:
    success, data = await _execute_command("hdc shell bm dump -a")
    if success:
        return True if package_name in data else False

async def start_app(package_name: str, ability_name: str):
    success, result = await _execute_command(f"hdc shell aa start -a {ability_name} -b {package_name}")
    if success:
        return "Success" in result
    
async def stop_app(package_name: str):
    success, result = _execute_command(f"hdc shell aa force-stop {package_name}")
    if success:
        return result

async def current_app() -> Tuple[str, str]:
    """
    Get the current foreground application information.

    Returns:
        Tuple[str, str]: A tuple contain the package_name andpage_name of the foreground application.
                            If no foreground application is found, returns (None, None).
    """

    def __extract_info(output: str):
        results = []

        mission_blocks = re.findall(r'Mission ID #[\s\S]*?isKeepAlive: false\s*}', output)
        if not mission_blocks:
            return results

        for block in mission_blocks:
            if 'state #FOREGROUND' in block:
                bundle_name_match = re.search(r'bundle name \[(.*?)\]', block)
                main_name_match = re.search(r'main name \[(.*?)\]', block)
                if bundle_name_match and main_name_match:
                    package_name = bundle_name_match.group(1)
                    page_name = main_name_match.group(1)
                    results.append((package_name, page_name))

        return results

    success, output = await _execute_command("hdc shell aa dump -l")
    if success:
        results = __extract_info(output)
        return results[0] if results else (None, None)

async def wakeup():
    """
    wake up the phone
    """
    success, result = _execute_command("hdc shell power-shell wakeup")
    if success:
        return result

async def screen_state() -> str:
    """
    ["INACTIVE", "SLEEP, AWAKE"]
    """
    success, data = await _execute_command("hdc shell hidumper -s PowerManagerService -a -s")
    if success:
        pattern = r"Current State:\s*(\w+)"
        match = re.search(pattern, data)

        return match.group(1) if match else None

async def tap(x: int, y: int) -> None:
    await _execute_command(f"hdc shell uitest uiInput click {x} {y}")

async def swipe(x1, y1, x2, y2, speed=1000):
    await _execute_command(f"hdc shell uitest uiInput swipe {x1} {y1} {x2} {y2} {speed}")

async def input_text(x: int, y: int, text: str):
    await _execute_command(f"hdc shell uitest uiInput inputText {x} {y} {text}")

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



async def dump_hierarchy() -> Dict:
    """
    """
    _tmp_path = f"/data/local/tmp/hierarchy_tmp.json"
    await _execute_command(f"hdc shell uitest dumpLayout -p {_tmp_path}")
    await _execute_command(f"hdc file recv {_tmp_path} ./tmp.json")
    
        
async def get_uilayout() -> str:
    """
    Retrieves information about clickable elements in the current UI.
    Returns a formatted string containing details about each clickable element,
    including its text, content description, bounds, and center coordinates.

    Returns:
        str: A formatted list of clickable elements with their properties
    """
    await dump_hierarchy()

    import re

    def calculate_center(bounds_str):
        matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
        if len(matches) == 2:
            x1, y1 = map(int, matches[0])
            x2, y2 = map(int, matches[1])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            return center_x, center_y
        return None

    clickable_elements = []

    def traverseTree(root):
        """
        traverse the tree to extract all layouts
        """
        node_info: NodeInfo = root["attributes"]
        text = node_info["text"]
        desc = node_info["description"]
        bounds = node_info["bounds"]

        if text or desc:
            center = calculate_center(bounds)
            element_info = "Clickable element:"
            if text:
                element_info += f"\n  Text: {text}"
            if desc:
                element_info += f"\n  Description: {desc}"
            element_info += f"\n  Bounds: {bounds}"
            if center:
                element_info += f"\n  Center: ({center[0]}, {center[1]})"
            clickable_elements.append(element_info)

        for child in root["children"]:
            traverseTree(child)

    import json
    with open("tmp.json", "r") as fp:
        res = fp.read()
        start = res.find("{")
        root = json.loads(res[start:])
    traverseTree(root)
    if not clickable_elements:
        return "No clickable elements found with text or description"

    result = "\n\n".join(clickable_elements)
    return result

