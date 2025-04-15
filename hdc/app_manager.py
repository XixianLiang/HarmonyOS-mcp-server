"""
    Handle with apps
"""

from typing import Union, List, Dict, Tuple
import re
from .system import _execute_command

async def list_app() -> List[str]:
    """
    Get all installed packages on the device
    Returns:
        A list of all installed packages on the device as a string
    """
    success, result = await _execute_command(f"hdc shell bm dump -a")
    if success:
        raw = result.split('\n')
        return [item.strip() for item in raw if not item.startswith("ID") and item != ""]

async def has_app(package_name: str) -> bool:
    """
    check if the given package is installed on the device
    Args:
        package_name
    """
    apps = await list_app
    return package_name in apps

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

async def launch_app(package_name: str) -> str:
    """
    launch app accrodingt to the given package name.
    Args:
        package_name: the package name of the package.
    """
    try:
        if package_name not in await list_app():
            return (
                f"[Fail] the given package {package_name} not installed."
                " Use `list_app` to checkout the available apps"
            )
        
        success, output = await _execute_command(f"hdc shell bm dump -n {package_name}")
        if not success:
            return f"[Fail] fail when dumping app info: {output}"

        json_start = output.find("{")
        if json_start == -1:
            return "[Fail] No such package"
        
        import json
        package_info = json.loads(output[json_start:])

        bundle_name = package_info["hapModuleInfos"][0]["bundleName"]
        entry_ability = package_info["hapModuleInfos"][0]["mainAbility"]
        
        success, res = await _execute_command(f"hdc shell aa start -b {bundle_name} -a {entry_ability}")
        if not success or "start ability successfully" not in res:
            return f"[Fail] {res}"
        return f"[Success] {res}"
    except BaseException as e:
        return f"[Fail] {e}"
