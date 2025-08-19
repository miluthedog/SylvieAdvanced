import asyncio
import os
from typing import List
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
from jsonhandler import add_role
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINIAPIKEY")
model = "gemini-2.0-flash-001"
max_turns = 5

class ChatClient():
    def __init__(self, mcp_client):
        self.ai_client = genai.Client(api_key=api_key)
        
        self.tools_list = mcp_client.tools_list
        self.tool_to_server_mapping = mcp_client.tool_to_server_mapping
        self.sessions = mcp_client.sessions

    async def execute_function_calls(self, function_call_parts: List) -> List:
        function_response_parts = []
        for function_call_part in function_call_parts:
            tool_name = function_call_part.function_call.name
            tool_args = function_call_part.function_call.args

            server_id = self.tool_to_server_mapping.get(tool_name)
            if not server_id:
                function_response = {"error": f"Tool '{tool_name}' not found in any connected server"}
                print(f"ERROR: Tool '{tool_name}' not found in any server")
            else:
                print(f"Calling tool: {tool_name} (from server {server_id}) with args {tool_args}")

                try:
                    session = self.sessions[server_id]
                    result = await session.call_tool(tool_name, tool_args)
                    function_response = {"result": result.content}
                    print(f"Tool {tool_name} completed successfully")
                except Exception as e:
                    function_response = {"Error": str(e)}

            function_response_part = types.Part.from_function_response(
                name=tool_name,
                response=function_response
            )
            function_response_parts.append(function_response_part)

        return function_response_parts

    async def ai_process(self, user_prompt: str) -> str:
        system_prompt = """
        You are an AI agent that can call tools to assist the user. You will receive a user prompt and may respond with text or call tools to perform actions.

        You have 5 turns to complete the task, you can respond and keep memery of all turns. Think step by step and use tools as needed.
        All initial turns will only be saved in memory, the final response will be returned to the user.
        The last response must be a text response, report what tool used.

        If you call a tool, you must provide the tool name and arguments in the function call format.
        You can run multiple tools in a single response, or run tools continous.
        You can only call tools that are available on the connected servers.
        If no tools are available, you must complete the task using only text responses.
        If you cannot complete the task, respond with an appropriate message.
        """
        user_prompt_content = add_role('user', user_prompt)
        conversation_history = [user_prompt_content]

        turn = 0
        while turn < max_turns:
            turn += 1
            response = self.ai_client.models.generate_content(
                model=model,
                contents=conversation_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=self.tools_list
                )
            )

            ai_response_parts = response.candidates[0].content.parts
            ai_response_content = add_role('assistant', ai_response_parts)
            conversation_history.append(ai_response_content)

            function_call_parts = [part for part in ai_response_parts if hasattr(part, 'function_call') and part.function_call]

            if function_call_parts:
                print(f"Agent requested {len(function_call_parts)} tool call(s)")
                function_response_parts = await self.execute_function_calls(function_call_parts)
                function_response_content = add_role('tool', function_response_parts)
                conversation_history.append(function_response_content)
                continue
            else:
                final_text = response.text if response.text else "Task completed."
                return final_text

        return response.text

    async def ai_respond(self, user_prompt=None) -> str:
        while True:
            if user_prompt.lower() in ['ok', 'tks']:
                break

            response = await self.ai_process(user_prompt)
            return response