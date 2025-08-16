import disnake
from disnake.ext import commands
from .service import InviteTrackingService
from loader import bot

service = InviteTrackingService(bot)

def setup(bot):
    @bot.event
    async def on_ready():
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