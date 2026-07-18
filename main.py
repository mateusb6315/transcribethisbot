import discord
from discord.ext import commands
from config.vars import TOKEN
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="when_mentioned", intents=intents)


async def carregar_cogs():
    for arquivo in os.listdir("./cogs"):
        if arquivo.endswith(".py"):
            await bot.load_extension(f"cogs.{arquivo[:-3]}")


@bot.event
async def setup_hook():
    await carregar_cogs()
    await bot.tree.sync()


@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN não configurado no arquivo .env")
    bot.run(TOKEN)
