import disnake
from disnake.ext import commands
from .service import PingService


def setup(bot):
    @commands.slash_command(
        name="пинг",
        description="Проверить скорость ответа бота"
    )
    async def ping_command(self, inter: disnake.CommandInteraction):
        embed = await PingService.get_ping_embed()
        await inter.response.send_message(embed=embed)