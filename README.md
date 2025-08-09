<div align="center">
<h1>HarmonyOS MCP Server</h1>

 <a href='LICENSE'><img src='https://img.shields.io/badge/License-MIT-orange'></a> &nbsp;&nbsp;&nbsp;
 <a><img src='https://img.shields.io/badge/python-3.13-blue'></a>
</div>

<div align="center">
    <img style="max-width: 500px; width: 60%;" width="1111" alt="image" src="https://github.com/user-attachments/assets/7c2e6879-f583-48d7-b467-c4c6d99c5fab" />
</div>

## Intro

This is a MCP server for manipulating harmonyOS Device.


https://github.com/user-attachments/assets/7af7f5af-e8c6-4845-8d92-cd0ab30bfe17


## Quick Start

### Installation

1. Clone this repo
   
```bash
git clone https://github.com/XixianLiang/HarmonyOS-mcp-server.git
cd HarmonyOS-mcp-server
```

2. Setup the envirnment.

```bash
uv python install 3.13
uv sync
```

### Usage


#### Claude Desktop

You can use [Claude Desktop](https://modelcontextprotocol.io/quickstart/user) to try our tool.

#### Openai SDK
You can also use [openai-agents SDK](https://openai.github.io/openai-agents-python/mcp/) to try the mcp server. Here's an example

```python
"""
Example: Use Openai-agents SDK to call HarmonyOS-mcp-server
"""
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
            "command": "<...>/bin/uv",
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

#### Langchain
You can use [LangGraph](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/), a flexible LLM agent framework to design your workflows. Here's an example

```python
"""
langgraph_mcp.py
"""

server_params = StdioServerParameters(
    command="/home/chad/.local/bin/uv",
    args=["--directory",
          ".",
          "run",
          "server.py"],
    
)


#This fucntion would use langgraph to build your own agent workflow
async def create_graph(session):
    llm = ChatOllama(model="qwen2.5:7b", temperature=0)
    #!!!load_mcp_tools is a langchain package function that integrates the mcp into langchain.
    #!!!bind_tools fuction enable your llm to access your mcp tools
    tools = await load_mcp_tools(session)
    llm_with_tool = llm.bind_tools(tools)

    
    system_prompt = await load_mcp_prompt(session, "system_prompt")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt[0].content),
        MessagesPlaceholder("messages")
    ])
    chat_llm = prompt_template | llm_with_tool

    # State Management
    class State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]

    # Nodes
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Building the graph
    # graph is like a workflow of your agent.
    #If you want to know more langgraph basic,reference this link (https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/#3-add-a-node)
    graph_builder = StateGraph(State)
    graph_builder.add_node("chat_node", chat_node)
    graph_builder.add_node("tool_node", ToolNode(tools=tools))
    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
    graph_builder.add_edge("tool_node", "chat_node")
    graph = graph_builder.compile(checkpointer=MemorySaver())
    return graph





async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            config = RunnableConfig(thread_id=1234,recursion_limit=15)
            # Use the MCP Server in the graph
            agent = await create_graph(session)

            while True:
                message = input("User: ")
                try:
                    response = await agent.ainvoke({"messages": message}, config=config)
                    print("AI: "+response["messages"][-1].content)
                except RecursionError:
                    result = None
                    logging.error("Graph recursion limit reached.")


if __name__ == "__main__":
    asyncio.run(main())
```

Write the system prompt in `server.py`

```python
"""
server.py
"""
@mcp.prompt()
def system_prompt() -> str:
    """System prompt description"""
    return """
    You are an AI assistant use the tools if needed.
    """
```
Use `load_mcp_prompt` function to get your prompt from mcp server.
```python
"""
langgraph_mcp.py
"""
prompts = await load_mcp_prompt(session, "system_prompt")
```
