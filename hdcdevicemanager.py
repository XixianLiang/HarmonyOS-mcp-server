from PIL import Image as PILImage
from hdc.hdc import NodeInfo, _execute_command, dump_hierarchy
import asyncio


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


async def launch_package(package_name: str) -> str:
    """
    launch the given package.
    Args:
        :package_name:
    """
    command = f"bm dump -n {package_name}"
    success, output = await self.device.shell(command)
    
    if success:
        json_start = output.find("{")
        if json_start == -1:
            return "[Fail] No such package"
        
        import json
        package_info = json.loads(output[json_start:])

        bundle_name = package_info["hapModuleInfos"][0]["bundleName"]
        entry_ability = package_info["hapModuleInfos"][0]["mainAbility"]
        
        success, res = _execute_command(f"hdc shell aa start -b {bundle_name} -a {entry_ability}").output
        if not success or "start ability successfully" not in res:
            return f"[Fail] {res}"
        return f"[Success] {res}"        


# async def take_screenshot(self) -> None:
#     """
#     take screenshot and save it to `screenshot.png` (high-resolution) and 
#     `compressed_screenshot.png` (low-resolution)
#     """
#     await screenshot("screenshot.png")

#     # compressing the ss to avoid "maximum call stack exceeded" error on claude desktop
#     with PILImage.open("screenshot.png") as img:
#         width, height = img.size
#         new_width = int(width * 0.3)
#         new_height = int(height * 0.3)
#         resized_img = img.resize(
#             (new_width, new_height), PILImage.Resampling.LANCZOS
#         )

#         resized_img.save(
#             "compressed_screenshot.png", "PNG", quality=85, optimize=True
#         )

async def get_uilayout() -> str:
    """
    get uilayout of current screen.

    layout example:
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
        tree = json.load(fp)
    traverseTree(root=tree)
    if not clickable_elements:
        return "No clickable elements found with text or description"

    result = "\n\n".join(clickable_elements)
    return result


async def click(self, center) -> str:
    """
    click the given coordinate
    """
    if not await self.check_device():
        return "[Fail] No available device"
    import re
    matches = re.findall(r"(\d+)\s*,\s*(\d+)", center)
    if matches:
        x, y = map(int, matches[0])
        await self.device.tap(x, y)
    else:
        return "[Fail] The input should be given like `(277, 168)` : click x=277, y=168"
    

async def input_text(self, center, text):
    """
    input text
    """
    import re
    matches = re.findall(r"(\d+)\s*,\s*(\d+)", center)
    if matches:
        x, y = map(int, matches[0])
        await input_text(x, y, text)
    else:
        return "[Fail] The input should be given like `(277, 168) hello world`"



async def main():
    # await click("(299, 2147)")
    print(await get_uilayout())

if __name__ == "__main__":
    asyncio.run(main())