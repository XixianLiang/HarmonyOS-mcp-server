# -*- coding: utf-8 -*-
import asyncio
import re
from .system import launch_package
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



if __name__ == "__main__":
    asyncio.run(launch_package("com.huawei.hmos.browser"))
