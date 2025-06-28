import disnake
from loader import bot

class PingService:
	@staticmethod
	async def get_ping_embed() -> disnake.Embed:
		latency = round(bot.latency * 1000)
		color = 0x2ECC71 if latency < 100 else 0xF1C40F
		
		embed = disnake.Embed(
			title="🏓 Понг!",
			description=f"Задержка бота: **{latency}мс**",
			color=color
		)
		embed.set_footer(text="Скорость ответа бота")
		return embed