import dotenv
import os
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.tools.mcp import mcp_server_tools, SseServerParams, StreamableHttpServerParams
from autogen_ext.tools.mcp import StdioServerParams
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

async def async_input(prompt="", *args, **kwargs) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

async def main():

    try:
        # Load environment variables from .env file
        dotenv.load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY", "")
        model_name = os.getenv("OPENAI_MODEL", "gpt-4")

        llm_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
        )

        ### HTTP MCP server connection
        mcp_url_http = "http://127.0.0.1:8000/mcp"
        server_params_http = StreamableHttpServerParams(url=mcp_url_http)

        # Pull all tools from the MCP server
        tools_http = await mcp_server_tools(server_params_http)

        ### STDIO-based local MCP server connection
        server_params_stdio = StdioServerParams(command="python", args=["stdio-mcp-server/app.py"])

        # Pull all tools from the MCP server
        tools_stdio = await mcp_server_tools(server_params_stdio)


        calculator_assistant = AssistantAgent(
            name="calculator_assistant",
            tools=tools_stdio,
            model_client=llm_client,
            system_message="You are a helpful assistant that can perform calculations using the stdio MCP server tools."
            
        )

        asseser_assistant = AssistantAgent(
            name="asseser_assistant",
            model_client=llm_client,
            tools=tools_http,
            system_message="You are a helpful assistant that can find maximum and minimum values using the SSE MCP server tools."
        )

        # System message to guide the user proxy agent
        system_message = (
            """You are a user interacting with an MCP-enabled assistant agent. 
You can ask the assistant to perform calculations using the calculator assistant tools \
or find maximum/minimum values using the asseser assistant tools. 
Get the information you need and respond to \
the user by summarizing the results provided by the assistant.
"""
        )

        user_proxy = UserProxyAgent(
            name="user_proxy",
            description=system_message,
            input_func=async_input
        )
        
        termination = TextMentionTermination("TERMINATION")

        team = SelectorGroupChat(
            [calculator_assistant, user_proxy, asseser_assistant], 
            model_client=llm_client,
            termination_condition=termination
        )

        stream = team.run_stream()
        await Console(stream)

    except* ValueError as e:
        print(f"ValueError occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())