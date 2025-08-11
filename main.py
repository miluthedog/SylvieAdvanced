import discord
from discord.ext import commands
import asyncio
import config
import pathlib
import os

sylvie = commands.Bot(command_prefix="Sylvie ", intents=discord.Intents.all())

BASE_DIR = pathlib.Path(__file__).parent
MODULE_DIR = BASE_DIR / "modules"


async def loadModules():
    for file in MODULE_DIR.glob("*.py"):
        if file.name != "__init__.py":
            await sylvie.load_extension(f"modules.{file.name[:-3]}")


async def SylvieOS():
    APIkey = config.token.discord
    if not os.path.isdir("./db"):
        os.mkdir("db")
    async with sylvie:
        await loadModules()
        await sylvie.start(APIkey)

if __name__ == "__main__":
    asyncio.run(SylvieOS())
