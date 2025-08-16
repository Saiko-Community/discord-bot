import disnake
from disnake.ext import commands
from .service import ActivityTrackingService
from loader import bot

service = ActivityTrackingService(bot)

def setup(bot):

    @bot.slash_command(name="profile", description="Показать ваш профиль")
    async def profile(inter: disnake.ApplicationCommandInteraction):
        stats = await service.get_user_stats(str(inter.author.id))
        if stats:
            embed = disnake.Embed(
                title=f"Профиль {inter.author.display_name}",
                description=(
                    f"**Уровень:** {stats['level']}\n"
                    f"**XP:** {stats['xp']}\n"
                    f"**Сообщений:** {stats['messages']}\n"
                    f"**На сервере с:** <t:{stats['joined_at']}:R>"
                )
            )
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("Ваш профиль не найден в базе данных!", ephemeral=True)

    @bot.event
    async def on_message(message):
        # Игнор ботов
        if message.author.bot or not message.guild:
            return
            
        # Счётчик сообщений
        await service.increment_messages(str(message.author.id))

        # Счётчик XP
        await service.add_xp(str(message.author.id), 1)