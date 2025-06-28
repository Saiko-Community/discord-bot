import disnake
from disnake.ext import commands
from .service import PingService

class PingHandlers(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command(
		name="ping",
		description="Проверить скорость ответа бота"
	)
	async def ping_command(self, inter: disnake.CommandInteraction):
		embed = await PingService.get_ping_embed()
		await inter.response.send_message(embed=embed)

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"Ког Ping загружен! Бот: {self.bot.user}")

def setup(bot):
	cog = PingHandlers(bot)
	bot.add_cog(cog)
	
	# Можно регистрировать дополнительные события здесь
	@bot.event
	async def on_guild_join(guild):
		print(f"Бот добавлен на сервер: {guild.name}")