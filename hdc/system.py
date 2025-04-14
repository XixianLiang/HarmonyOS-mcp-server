"""
    Interact with system
    shell 执行命令
    发送/接收文件
    启动给定的 package / 获取所有的 packages
"""

import shlex
import subprocess
import asyncio
from .execption import HdcError

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
    
# def send_file(self, lpath: str, rpath: str):
#     result = _execute_command(f"{self.hdc_prefix} -t {self.serial} file send {lpath} {rpath}")
#     if result.exit_code != 0:
#         raise HdcError("HDC send file error", result.error)
#     return result

async def recv_file(rpath: str, lpath: str):
    success, result = await _execute_command(f"hdc file recv {rpath} {lpath}")
    if success:
        return result


async def launch_package(package_name: str) -> str:
    """
    launch the given package.
    Args:
        :package_name:
    """
    success, output = await _execute_command(f"hdc shell bm dump -n {package_name}")
    if not success:
        return f"[Fail] fail when dumping: {output}"

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

async def check_hdc_installed() -> bool:
    """
    Check if HDC is installed on the system.
    """
    success, _ = await _execute_command("hdc version")
    return success

# async def get_packages() -> str:
#     """
#     get all the installed packages
#     raw command: `hdc shell bm dump -a`
#     """
#     command = "bm dump -a"
#     res = await self.device.shell(command)

#     result = [
#         package.strip() for package in res if not package.startswith("ID")
#     ]
#     output = "\n".join(result)
#     return output