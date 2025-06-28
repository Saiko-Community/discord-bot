import disnake
from disnake.ext import commands

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix='!', intents=disnake.Intents.all())
bot = Bot()

import logging
logging.basicConfig(level=logging.WARNING)