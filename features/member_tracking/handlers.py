import disnake
from disnake.ext import commands
from .service import MemberTrackingService
from loader import bot
from database.database import setup as db_setup

service = MemberTrackingService(bot)

def setup(bot):
    @bot.event
    async def on_ready():
        await db_setup()
        await service.cache_invites()
        print("Invites cached and database ready")
    
    @bot.event
    async def on_member_join(member):
        # Определение инвайтера
        invite_code, inviter = await service.get_invite_usage_diff(member.guild)
        
        await service.add_member(
            member,
            inviter_id=str(inviter.id) if inviter else None,
            invite_code=invite_code
        )
        
        # Обновление кеша
        await service.update_invite_cache(member.guild)

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
                    f"**На сервере с:** <t:{stats['joined_at']}:D>"
                )
            )
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("Ваш профиль не найден в базе данных!", ephemeral=True)

    @bot.event
    async def on_message(message):
        # Игнорируем сообщения ботов и системные сообщения
        if message.author.bot or not message.guild:
            return
            
        # Счётчик сообщений
        await service.increment_messages(str(message.author.id))

        # Счётчик XP
        await service.add_xp(str(message.author.id), 1)

    @bot.event
    async def on_invite_create(invite):
        await service.update_invite_cache(invite.guild)
    
    @bot.event
    async def on_invite_delete(invite):
        if invite.guild.id in service.invite_cache:
            if invite.code in service.invite_cache[invite.guild.id]:
                del service.invite_cache[invite.guild.id][invite.code]
    
    @bot.slash_command(name="sync_members", description="Синхронизировать участников сервера с базой данных")
    @commands.has_permissions(administrator=True)
    async def sync_members(inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        await service.sync_members(inter.guild)
        await inter.edit_original_message(content="✅ Участники синхронизированы с базой данных!")