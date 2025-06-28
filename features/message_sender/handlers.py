from disnake.ext import commands
import disnake
from typing import Optional

from .service import MessageSenderService

class MessageSenderHandlers:
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.service = MessageSenderService(bot)
	
	async def initialize(self):
		"""Инициализация сообщений при запуске"""
		await self.service.initialize_messages()
	
	async def send_message(
		self, 
		inter: disnake.ApplicationCommandInteraction,
		template_name: str,
		channel: Optional[disnake.TextChannel] = None
	):
		"""Обработчик команды для отправки сообщения"""
		try:
			await self.service.send_from_template(
				template_name,
				channel or inter.channel
			)
			await inter.response.send_message(
				f"Сообщение из шаблона '{template_name}' обработано",
				ephemeral=True
			)
		except Exception as e:
			await inter.response.send_message(
				f"Ошибка: {str(e)}",
				ephemeral=True
			)

def setup(bot: commands.Bot):
	handlers = MessageSenderHandlers(bot)

	
	@bot.slash_command(name="update_messages", description="Обновить все сообщения из шаблонов")
	async def update_messages(inter: disnake.ApplicationCommandInteraction):
		"""Команда для ручного обновления всех сообщений"""
		await handlers.initialize()
		await inter.response.send_message(
			"Все сообщения из шаблонов обновлены",
			ephemeral=True
		)
	
	@bot.slash_command(name="send_message", description="Отправить сообщение из шаблона")
	async def send_message(
		inter: disnake.ApplicationCommandInteraction,
		template_name: str,
		channel: Optional[disnake.TextChannel] = None
	):
		await handlers.send_message(inter, template_name, channel)