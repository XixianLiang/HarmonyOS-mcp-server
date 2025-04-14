"""
    Handle with apps
"""

from typing import Union, List, Dict, Tuple, TypedDict
import re
from .system import _execute_command

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