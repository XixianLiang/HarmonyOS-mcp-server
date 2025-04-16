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
    

async def click(center) -> bool:
    """
    click the given coordinate
    Args:
        center: a string like "(x, y)", sample: "(227, 168)"
    """
    import re
    matches = re.findall(r"(\d+)\s*,\s*(\d+)", center)
    if not matches:
        return "[Fail] The input should be given like `(277, 168)` : click x=277, y=168"
    
    x, y = map(int, matches[0])
    success, _ = await _execute_command(f"hdc shell uitest uiInput click {x} {y}")

    return success

async def long_click(center) -> bool:
    """
    long click the given coordinate
    Args:
        center: a string like "(x, y)", sample: "(227, 168)"
    """
    import re
    matches = re.findall(r"(\d+)\s*,\s*(\d+)", center)
    if not matches:
        return "[Fail] The input should be given like `(277, 168)` : click x=277, y=168"
    
    x, y = map(int, matches[0])
    success, _ = await _execute_command(f"hdc shell uitest uiInput longClick {x} {y}")
    return success

async def swipe(x1, y1, x2, y2, speed=1000):
    await _execute_command(f"hdc shell uitest uiInput swipe {x1} {y1} {x2} {y2} {speed}")

async def input_text(center, text) -> bool:
    """
    input text to the given coordinate
    Args:
        center: a string like "(x, y)", sample: "(227, 168)"
        text: the text to input
    """
    import re
    matches = re.findall(r"(\d+)\s*,\s*(\d+)", center)
    if not matches:
        return "[Fail] The input should be given like `(277, 168) hello world`"
    
    x, y = map(int, matches[0])
    success, _ = await _execute_command(f"hdc shell uitest uiInput inputText {x} {y} {text}")
    
    return success

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
    dump the hierachy and save it to `tmp.json` in the local working dir
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
        text = node_info["text"].strip()
        desc = node_info["description"].strip()
        bounds = node_info["bounds"].strip()
        clickable = node_info["clickable"].strip()
        id = node_info["id"].strip()

        if clickable == "true" or text or desc:
            if clickable == "true":
                element_info = "Clickable element:"
            else:
                element_info = "Text element"
            center = calculate_center(bounds)
            if id:
                element_info += f"\n Id: {id}"
            if text:
                element_info += f"\n  Text: {text}"
            if desc:
                element_info += f"\n  Description: {desc}"
            if center:
                element_info += f"\n  Center: ({center[0]}, {center[1]})"
            element_info += f"\n  Bounds: {bounds}"
            clickable_elements.append(element_info)

        # if text or desc:
        #     center = calculate_center(bounds)
        #     element_info = "Clickable element:"
        #     if text:
        #         element_info += f"\n  Text: {text}"
        #     if desc:
        #         element_info += f"\n  Description: {desc}"
        #     element_info += f"\n  Bounds: {bounds}"
        #     if center:
        #         element_info += f"\n  Center: ({center[0]}, {center[1]})"
        #     clickable_elements.append(element_info)

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