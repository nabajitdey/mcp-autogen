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

# Helper to get non-blocking input from the user in async code.
# It runs the built-in input() in a threadpool so the asyncio event loop
# remains responsive while waiting for user input.
async def async_input(prompt="", *args, **kwargs) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

# Main entrypoint for the async application.
# Sets up LLM client, connects to MCP tool servers (HTTP and stdio),
# creates agent instances and runs a SelectorGroupChat with a termination
# condition, streaming the interaction to the Console UI.
async def main():

    try:
        # Load environment variables from a .env file (if present)
        dotenv.load_dotenv()

        # Read OpenAI API configuration from environment (fallback defaults provided)
        api_key = os.getenv("OPENAI_API_KEY", "")
        model_name = os.getenv("OPENAI_MODEL", "gpt-4")

        # Create the LLM client used by agents for text completions / chat.
        llm_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
        )

        ### HTTP MCP server connection
        # Example URL for an MCP server exposing tools over HTTP (SSE/streamable).
        # StreamableHttpServerParams is used when the MCP server supports streaming responses.
        mcp_url_http = "http://127.0.0.1:8000/mcp"
        server_params_http = StreamableHttpServerParams(url=mcp_url_http)

        # Query the MCP server to pull the available tools (over HTTP streamable interface).
        tools_http = await mcp_server_tools(server_params_http)

        ### STDIO-based local MCP server connection
        # Use a local MCP server launched as a subprocess (stdio communication).
        # Adjust the command/args to point to your local stdio MCP server implementation.
        server_params_stdio = StdioServerParams(command="python", args=["stdio-mcp-server/app.py"])

        # Pull all tools exposed by the stdio-based MCP server.
        tools_stdio = await mcp_server_tools(server_params_stdio)


        # Assistant agent that uses the stdio MCP tools (e.g., a calculator).
        # system_message instructs the agent about its capabilities and role.
        calculator_assistant = AssistantAgent(
            name="calculator_assistant",
            tools=tools_stdio,
            model_client=llm_client,
            system_message="You are a helpful assistant that can perform calculations using the stdio MCP server tools."
            
        )

        # Another assistant agent that uses the HTTP/SSE MCP tools (e.g., min/max finder).
        asseser_assistant = AssistantAgent(
            name="asseser_assistant",
            model_client=llm_client,
            tools=tools_http,
            system_message="You are a helpful assistant that can find maximum and minimum values using the SSE MCP server tools."
        )

        # System message / description for the user proxy agent.
        # Guides the user proxy to know when to use which assistant/toolset
        # and instructs how to summarize results back to the human user.
        system_message = (
            """You are a user interacting with an MCP-enabled assistant agent. 
You can ask the assistant to perform calculations using the calculator assistant tools \
or find maximum/minimum values using the asseser assistant tools. 
Get the information you need and respond to \
the user by summarizing the results provided by the assistant.
"""
        )

        # UserProxyAgent simulates or mediates a human user; it can prompt for input
        # using the provided async_input function so the conversation can be interactive.
        user_proxy = UserProxyAgent(
            name="user_proxy",
            description=system_message,
            input_func=async_input
        )
        
        # Termination condition: conversation stops when the special token is mentioned.
        # TextMentionTermination watches for the mention of the provided keyword.
        termination = TextMentionTermination("TERMINATION")

        # SelectorGroupChat orchestrates a multi-agent chat where agents can be selected
        # to respond or call tools. Provide the list of agents and the same LLM client used.
        team = SelectorGroupChat(
            [calculator_assistant, user_proxy, asseser_assistant], 
            model_client=llm_client,
            termination_condition=termination
        )

        # Start streaming the team chat and pipe it to the Console UI for display.
        stream = team.run_stream()
        await Console(stream)

    # Using except* to catch exception groups (Python 3.11+). Here it catches ValueError
    # instances that may be raised. Adjust as needed for broader exception handling.
    except* ValueError as e:
        print(f"ValueError occurred: {e}")


if __name__ == "__main__":
    # Run the async main function using asyncio's run helper.
    asyncio.run(main())