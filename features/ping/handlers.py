import disnake
from disnake.ext import commands

from .service import PingService
from loader import bot

def setup(bot):
	@bot.slash_command(name="пинг", description="Проверить скорость ответа бота")
	async def ping(inter: disnake.CommandInteraction):
		embed = await PingService.get_ping_embed()
		await inter.response.send_message(embed=embed)