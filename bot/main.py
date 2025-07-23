# File: bot/main.py
import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Adiciona a raiz do projeto ao sys.path para que 'cogs' seja encontrado
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()  # Carrega as variáveis do .env

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise Exception("DISCORD_TOKEN não definido no .env!")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Sincroniza os slash commands e exibe uma mensagem de conexão
    await bot.tree.sync()
    print(f"Bot {bot.user} está online!")

async def load_extensions():
    # Carrega todas as cogs presentes na pasta cogs/
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"Extensão {extension} carregada.")
            except Exception as e:
                print(f"Falha ao carregar a extensão {extension}: {e}")

async def main():
    # Usando o contexto assíncrono do bot para carregar as extensões e iniciar o bot
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())