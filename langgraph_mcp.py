from langchain_ollama import ChatOllama
from typing import List
from typing_extensions import TypedDict
from typing import Annotated
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from langchain_core.runnables import RunnableConfig
server_params = StdioServerParameters(
    command="/home/chad/.local/bin/uv",
    args=["--directory",
          ".",
          "run",
          "server.py"],
    
)



async def create_graph(session):
    llm = ChatOllama(model="qwen2.5:7b", temperature=0)
    
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
    graph_builder = StateGraph(State)
    graph_builder.add_node("chat_node", chat_node)
    graph_builder.add_node("tool_node", ToolNode(tools=tools))
    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
    graph_builder.add_edge("tool_node", "chat_node")
    graph = graph_builder.compile(checkpointer=MemorySaver())
    return graph





async def main():
    # config = {"configurable": {"thread_id": 1234}}
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            #1.session初始化
            await session.initialize()

            # Check available tools
            tools = await load_mcp_tools(session)
            print("Available tools:", [tool.name for tool in tools])
            # List available tools
            # response = await session.list_tools()
            # print("\n/////////////////tools//////////////////")
            # for tool in response.tools:
            #     print(f'{tool}\n\n')
            prompts = await load_mcp_prompt(session, "system_prompt")
            print("Available prompts:", [prompt.content for prompt in prompts])
            # # 如何测试工具
            # result = await session.call_tool("add", arguments={"a": 2, "b": 2})
            # print("\n/////////////////result//////////////////")
            # print(result.content[0].text)
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
