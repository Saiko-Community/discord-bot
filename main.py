import features
from database import database

from config import config
import loader


bot = loader.bot

async def load_features():

	await database.setup()
	print("База данных загружена")

	bot.load_extension("features.ping.handlers")					# Команда /ping
	bot.load_extension("features.message_sender.handlers")			# Отправка системных сообщений через шаблоны
	bot.load_extension("features.invite_tracking.handlers")			# Трекинг инвайтов
	bot.load_extension("features.activity_tracking.handlers")		# Трекинг активности участников
	print("Фичи загружены")
	# Добавлять новые фичи сюда

@bot.event
async def on_ready():
	print(f"Бот запущен как {bot.user}")

	await database.setup()

if __name__ == "__main__":
	bot.loop.create_task(load_features())
	bot.run(config.BOT_TOKEN)