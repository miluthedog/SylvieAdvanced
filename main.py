import discord
from discord.ext import commands
import asyncio
import pathlib
import os
import json
from dotenv import load_dotenv
from modules.mcp.client import MCPClient
from jsonhandler import load_json

load_dotenv()


sylvie = commands.Bot(command_prefix="Sylvie", intents=discord.Intents.all())

BASE_DIR = pathlib.Path(__file__).parent
MODULE_DIR = BASE_DIR / "modules"


async def loadModules():
    for file in MODULE_DIR.glob("*.py"):
        if file.name != "__init__.py":
            await sylvie.load_extension(f"modules.{file.name[:-3]}")

async def SylvieOS():
    APIkey = os.getenv("DISCORDTOKEN")
    if not os.path.isdir("./db"):
        os.mkdir("db")
    async with sylvie:
        await loadModules()
        await sylvie.start(APIkey)


async def MCPserver():
    client = MCPClient()
    await client.connect_to_servers(load_json(file_name="server_config.json", title="servers"))


if __name__ == "__main__":
    asyncio.run(SylvieOS())
