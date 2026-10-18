import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import time
from google.genai.errors import ServerError

load_dotenv()

gemini = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def covert_mcp_tools_to_gemini(mcp_tools):
    function_declarations=[]
    for tool in mcp_tools.tools:
        function_declarations.append(types.FunctionDeclaration(name=tool.name,description=tool.description or "",parameters=tool.input_schema))
    return [types.Tool(
            function_declarations=function_declarations)
        ]
                

async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()
            mcp_tools=await session.list_tools()
            tools=covert_mcp_tools_to_gemini(mcp_tools)
            question = input("\nAsk your billing assistant: ")
            response = None

            for attempt in range(3):
                try:
                    response = gemini.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=question,
                    config=types.GenerateContentConfig(
                        tools=tools,
                        tool_config=types.ToolConfig(
                            function_calling_config=types.FunctionCallingConfig(
                                mode="AUTO"
                            )
                        )
                    )
                )
                    break

                except ServerError as e:
                    if attempt == 2:
                        print("Gemini is still unavailable. Please try again later.")
                        return

                    wait_seconds = 2 ** (attempt + 1)
                    print(f"Gemini temporarily unavailable. Retrying in {wait_seconds}s...")
                    time.sleep(wait_seconds)
            print(response)
            # Check whether Gemini requested a tool call
            function_call = None

            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call = part.function_call
                    break

            if function_call is None:
                print("Assistant:", response.text)
                return

            tool_name = function_call.name
            arguments = dict(function_call.args)

            print(f"Gemini selected tool: {tool_name}")
            print(f"Arguments: {arguments}")

            # Require approval before changing a subscription
            if tool_name == "update_subscription":
                approval = input(
                    "This changes a subscription. Proceed? (yes/no): "
                ).strip().lower()

                if approval != "yes":
                    print("Subscription update cancelled.")
                    return

            # Execute the tool selected by Gemini
            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            if result.is_error:
                print("Tool execution failed.")
                return

            tool_output = [
                item.text for item in result.content
                if hasattr(item, "text")
            ]

            # Send the actual tool result back to Gemini
            try:
                final_response = gemini.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    text=(
                                        f"User question: {question}\n"
                                        f"Tool executed: {tool_name}\n"
                                        f"Tool result: {json.dumps(tool_output)}\n"
                                        "Answer using the tool result only. "
                                        "Do not invent information."
                        )
                    )
                ]
            )
        ]
    )

                print("\nAssistant:", final_response.text)

            except ServerError as e:
                print(f"\nGemini is temporarily unavailable {e}")
                print("Raw MCP tool result:", *tool_output, sep="\n")
if __name__ == "__main__":
    asyncio.run(main())
    