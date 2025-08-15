import disnake
from database.database import Session
from database.models import User
from datetime import datetime

class MemberTrackingService:
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}
        
    async def cache_invites(self):
        """Кэширует текущие инвайты сервера"""
        for guild in self.bot.guilds:
            try:
                self.invite_cache[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
            except disnake.Forbidden:
                pass
    
    async def get_invite_usage_diff(self, guild):
        """Находит инвайт с изменившимся количеством использований"""
        new_invites = await guild.invites()
        new_cache = {invite.code: invite.uses for invite in new_invites}
        old_cache = self.invite_cache.get(guild.id, {})
        
        for code, uses in new_cache.items():
            old_uses = old_cache.get(code, 0)
            if uses > old_uses:
                return code, next(inv for inv in new_invites if inv.code == code).inviter
        
        return None, None
    
    async def update_invite_cache(self, guild):
        """Обновляет кэш инвайтов для сервера"""
        self.invite_cache[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
    
    async def add_member(self, member, inviter_id=None, invite_code=None):
        """Добавляет участника в базу данных"""
        session = Session()
        try:
            if not session.query(User).filter_by(discord_id=str(member.id)).first():
                new_user = User(
                    discord_id=str(member.id),
                    username=member.name,
                    joined_at=member.joined_at or datetime.utcnow(),
                    invited_by=inviter_id,
                    invite_code=invite_code
                )
                session.add(new_user)
                session.commit()
        finally:
            session.close()
    
    async def sync_members(self, guild):
        """Синхронизирует участников сервера с базой данных"""
        session = Session()
        try:
            db_members = {user.discord_id for user in session.query(User).all()}
            
            for member in guild.members:
                if str(member.id) not in db_members:
                    new_user = User(
                        discord_id=str(member.id),
                        username=member.name,
                        joined_at=member.joined_at or datetime.utcnow()
                    )
                    session.add(new_user)
            
            session.commit()
        finally:
            session.close()