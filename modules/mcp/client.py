import asyncio
import os
from typing import Dict, List
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from jsonhandler import convert_mcp_tools_to_gemini


class MCPClient():
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.streams_contexts: Dict[str, any] = {}
        self.session_contexts: Dict[str, any] = {}

        self.tools_list = []
        self.tool_to_server_mapping = {}


    async def connect(self, server_config: Dict, server_id: str):
        if 'command' not in server_config:
            print(f"Invalid server configuration for {server_id}")
            return False
        command = server_config['command']
        args = server_config.get('args', [])
        env = server_config.get('env', {})
        full_env = os.environ.copy()
        full_env.update(env)

        print(f"Starting subprocess server [{server_id}]: {command} {' '.join(args)}")
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=full_env
            )

            streams_context = stdio_client(server_params)
            streams = await streams_context.__aenter__()
            session_context = ClientSession(*streams)
            session = await session_context.__aenter__()
            await session.initialize()

            self.streams_contexts[server_id] = streams_context
            self.session_contexts[server_id] = session_context
            self.sessions[server_id] = session

            response = await session.list_tools()
            tools = response.tools
            print(f"Subprocess server [{server_id}] connected with tools: {[tool.name for tool in tools]}")

            server_tools = convert_mcp_tools_to_gemini(tools)
            self.tools_list.extend(server_tools)
            for tool in tools:
                self.tool_to_server_mapping[tool.name] = server_id
            return True

        except Exception as e:
            print(f"Error connecting to subprocess server [{server_id}]: {e}")
            return False

    async def connect_to_servers(self, server_configs: List[Dict]):
        connection_tasks = []
        for config in server_configs:
            server_id = config.get('id') or config.get('name', f"server_{len(connection_tasks)}")
            task = self.connect(config, server_id)
            connection_tasks.append(task)
        
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        successful_connections = sum(1 for result in results if result is True)
        print(f"\nSuccessfully connected to {successful_connections}/{len(server_configs)} servers")
        print(f"Total available tools: {len(self.tools_list)}")
