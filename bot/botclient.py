# File: bot/botclient.py
import discord
from discord.ext import commands

class BotClient(commands.Bot):
    def __init__(self, command_prefix, intents, **kwargs):
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)

    async def setup_hook(self):
        # Aqui podem ser inseridas inicializações adicionais
        pass