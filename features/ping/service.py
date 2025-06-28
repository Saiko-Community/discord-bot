import disnake
from loader import bot

class PingService:
	@staticmethod
	async def get_ping_embed() -> disnake.Embed:
		latency = round(bot.latency * 1000)
		
		embed = disnake.Embed(
			title="🏓 Понг!",
			description=f"Задержка бота: **{latency}мс**",
		)
		embed.set_footer(text="Скорость ответа бота")
		return embed