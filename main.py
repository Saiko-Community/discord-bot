import features
from database import database

from config import config
import loader


bot = loader.bot

async def load_features():
	bot.load_extension("features.ping.handlers")
	bot.load_extension("features.message_sender.handlers")
	# Добавлять новые фичи сюда

@bot.event
async def on_ready():
	print(f"Бот запущен как {bot.user}")

	await database.setup()

if __name__ == "__main__":
	bot.loop.create_task(load_features())
	bot.run(config.BOT_TOKEN)