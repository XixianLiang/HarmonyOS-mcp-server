import asyncio
from hdc.ui_manager import tap, input_text

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
        await tap(x, y)
    else:
        return "[Fail] The input should be given like `(277, 168)` : click x=277, y=168"
    

async def input(self, center, text):
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