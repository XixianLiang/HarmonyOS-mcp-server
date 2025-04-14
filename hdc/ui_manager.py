"""
    Interact with UI
    获取组件树
    点击/滑动屏幕
    输入文本
    获取屏幕状态，唤醒/熄灭屏幕
"""
from .system import _execute_command
from .Component import ComponentNode
import re

async def tap(x: int, y: int) -> None:
    await _execute_command(f"hdc shell uitest uiInput click {x} {y}")

async def swipe(x1, y1, x2, y2, speed=1000):
    await _execute_command(f"hdc shell uitest uiInput swipe {x1} {y1} {x2} {y2} {speed}")

async def input_text(x: int, y: int, text: str):
    await _execute_command(f"hdc shell uitest uiInput inputText {x} {y} {text}")

async def screen_state() -> str:
    """
    ["INACTIVE", "SLEEP, AWAKE"]
    """
    success, data = await _execute_command("hdc shell hidumper -s PowerManagerService -a -s")
    if success:
        pattern = r"Current State:\s*(\w+)"
        match = re.search(pattern, data)

        return match.group(1) if match else None
    
async def wakeup():
    """
    wake up the phone
    """
    success, result = _execute_command("hdc shell power-shell wakeup")
    if success:
        return result

async def dump_hierarchy():
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
        node_info: ComponentNode = root["attributes"]
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