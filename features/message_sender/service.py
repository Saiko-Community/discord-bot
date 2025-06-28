import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import disnake
from disnake import TextChannel, Thread, ButtonStyle, File

class MessageSenderService:
	TEMPLATES_DIR = Path(__file__).parent / "templates"

	def __init__(self, bot):
		self.bot = bot
		self.logger = logging.getLogger('message_sender')

	async def _load_local_image(self, filename: str) -> Optional[File]:
		"""Загружает локальный файл изображения"""
		image_path = self.TEMPLATES_DIR / filename
		if not image_path.exists():
			self.logger.warning(f"Image file not found: {filename}")
			return None
		return File(image_path, filename=filename)

	async def send_from_data(self, data: Dict[str, Any]) -> Optional[disnake.Message]:
		"""Отправляет/обновляет сообщение из данных JSON с поддержкой локальных изображений"""
		target_channel = self.bot.get_channel(data.get("channel_id"))
		if not target_channel:
			self.logger.warning("No channel specified in template")
			return None

		# Обработка локальных изображений
		files = []
		if "image" in data:
			if image_file := await self._load_local_image(data["image"]):
				files.append(image_file)
				data["embeds"][0].set_image(url=f"attachment://{data['image']}")

	async def initialize_messages(self):
		"""Обновляет все сообщения при запуске бота"""
		self.logger.info("Starting message initialization...")
		
		for template_file in self.TEMPLATES_DIR.glob("*.json"):
			try:
				template_name = template_file.stem
				self.logger.info(f"Processing template: {template_name}")
				await self.send_from_template(template_name)
			except Exception as e:
				self.logger.error(f"Error processing {template_file.name}: {str(e)}")

	async def cleanup_channel(self, channel: TextChannel):
		"""Очищает канал от старых сообщений и веток"""
		# Удаляем все сообщения
		try:
			await channel.purge(limit=100)
		except Exception as e:
			self.logger.error(f"Failed to purge channel: {str(e)}")

		# Архивируем все старые ветки
		for thread in channel.threads:
			try:
				await thread.edit(archived=True)
			except Exception as e:
				self.logger.error(f"Failed to archive thread {thread.name}: {str(e)}")

	async def create_threads(self, channel: TextChannel, threads_data: List[Dict]) -> Dict[str, Thread]:
		"""Создаёт ветки и возвращает их ID"""
		created_threads = {}
		for thread_data in threads_data:
			try:
				name = thread_data.get("name")
				if not name:
					continue

				if "initial_message" in thread_data:
					message = await channel.send(thread_data["initial_message"])
					thread = await message.create_thread(
						name=name,
						auto_archive_duration=thread_data.get("auto_archive", 1440),
						reason="Автоматическое создание ветки из шаблона"
				    )
				else:
					thread = await channel.create_thread(
						name=name,
						auto_archive_duration=thread_data.get("auto_archive", 1440),
						reason="Автоматическое создание ветки из шаблона",
						type=disnake.ChannelType.public_thread
					)

				created_threads[name] = thread
			except Exception as e:
				self.logger.error(f"Failed to create thread {name}: {str(e)}")

		return created_threads

	async def send_from_template(self, template_name: str) -> Optional[disnake.Message]:
		"""Отправляет/обновляет сообщение из шаблона"""
		template = self.load_template(template_name)
		return await self.send_from_data(template)

	def load_template(self, template_name: str) -> Dict[str, Any]:
		"""Загружает JSON шаблон из файла"""
		template_path = self.TEMPLATES_DIR / f"{template_name}.json"
		
		if not template_path.exists():
			raise FileNotFoundError(f"Template {template_name} not found")
		
		with open(template_path, 'r', encoding='utf-8') as f:
			return json.load(f)
	
	async def send_from_data(self, data: Dict[str, Any]) -> Optional[disnake.Message]:
		"""Отправляет/обновляет сообщение из данных JSON"""
		target_channel = self.bot.get_channel(data.get("channel_id"))
		if not target_channel:
			self.logger.warning("No channel specified in template")
			return None

		# Очистка канала если требуется
		if data.get("clear_channel", False):
			await self.cleanup_channel(target_channel)

		# Создание веток
		threads = {}
		if "threads" in data:
			threads = await self.create_threads(target_channel, data["threads"])

		# Обработка локальных изображений
		files = []
		embeds = []
		for embed_data in data.get("embeds", []):
			embed = disnake.Embed.from_dict(embed_data)

			# Если есть изображение в эмбеде
			if "image" in embed_data:
				image_name = embed_data["image"]["url"].replace("attachment://", "")
				if image_file := await self._load_local_image(image_name):
					files.append(image_file)

			embeds.append(embed)

		# Создание кнопок
		components = []
		if "buttons" in data or "threads" in data:
			action_row = disnake.ui.ActionRow()
			
			# Кнопки из шаблона
			for btn_data in data.get("buttons", []):
				btn = disnake.ui.Button(
					style=ButtonStyle[btn_data.get("style", "primary")],
					label=btn_data.get("label"),
					url=btn_data.get("url"),
					emoji=btn_data.get("emoji"),
					disabled=btn_data.get("disabled", False)
				)
				action_row.append_item(btn)
			
			# Кнопки для веток
			for thread_name, thread in threads.items():
				btn = disnake.ui.Button(
					style=ButtonStyle.blurple,
					label=thread_name,
					url=thread.jump_url,
					emoji=data.get("threads_emoji", "🧵")
				)
				action_row.append_item(btn)
			
			if action_row.children:
				components.append(action_row)

		# Попытка обновить существующ1ее сообщение
		message_id = data.get("message_id")
		if message_id:
			try:
				message = await target_channel.fetch_message(message_id)
				await message.edit(
					content=data.get("content"),
					embeds=[disnake.Embed.from_dict(e) for e in data.get("embeds", [])],
					components=components
				)
				self.logger.info(f"Message updated in {target_channel.id}")
				return message
			except disnake.NotFound:
				self.logger.info("Message not found, sending new one")
			except Exception as e:
				self.logger.error(f"Failed to edit message: {str(e)}")

		# Отправка нового сообщения
		try:
			return await target_channel.send(
				content=data.get("content"),
				embeds=[disnake.Embed.from_dict(e) for e in data.get("embeds", [])],
				files=files if files else None,
				components=components
			)
		except Exception as e:
			self.logger.error(f"Failed to send message: {str(e)}")
			return None
