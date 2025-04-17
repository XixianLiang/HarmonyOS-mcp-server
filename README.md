# HarmonyOS MCP Server

This is a MCP server for manipulating harmonyOS Device.

See our example.

### Quick Start

```bash
uv python install 3.13
uv sync
```

You can use [Claude Desktop](https://modelcontextprotocol.io/quickstart/user) to try our tool.



You can also use [openai-agents SDK](https://openai.github.io/openai-agents-python/mcp/) to try the mcp server.

Here's an example

```python
import asyncio
import os

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStdio, MCPServer

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to manipulate the HarmonyOS device and finish the task.",
        mcp_servers=[mcp_server],
    )

    message = "Launch the app `settings` on the phone"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():

    # Use async context manager to initialize the server
    async with MCPServerStdio(
        params={
            "command": "<...>/Python.framework/Versions/3.11/bin/uv",
            "args": [
                "--directory",
                "<...>/harmonyos-mcp-server",
                "run",
                "server.py"
            ]
        }
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP HarmonyOS", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())
```