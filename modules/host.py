import discord
from discord.ext import commands
from jsonhandler import load_json
from modules.mcp.agent import AgentRespond


class mcpAgent(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Agent module of {self.sylvie.user} loaded!")

    @commands.Cog.listener()
    async def on_message(self, message):
        allowed_ids = load_json(file_name="client_config.json", title="user_id")
        if message.author.id not in allowed_ids:
            return

        if isinstance(message.channel, discord.DMChannel):
            chat = AgentRespond(self.sylvie.mcp_client)
            result = await chat.ai_respond(message.content)
            await message.channel.send(f"{result}")
        else:
            await self.sylvie.process_commands(message)


async def setup(sylvie):
    await sylvie.add_cog(mcpAgent(sylvie))