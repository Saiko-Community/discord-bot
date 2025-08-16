import disnake
import time
from database.database import Session
from database.models import User

class ActivityTrackingService:
    def __init__(self, bot):
        self.bot = bot
    
    async def add_xp(self, user_id: str, xp_amount: int):
        """Добавляет XP пользователю (уровень обновится автоматически)"""
        session = Session()
        try:
            user = session.query(User).filter_by(discord_id=user_id).first()
            if user:
                user.xp += xp_amount
                session.commit()
        finally:
            session.close()
    
    async def increment_messages(self, user_id: str):
        """Увеличивает счётчик сообщений пользователя"""
        session = Session()
        try:
            user = session.query(User).filter_by(discord_id=user_id).first()
            if user:
                user.messages += 1
                session.commit()
        finally:
            session.close()
    
    async def get_user_stats(self, user_id: str):
        """Получает статистику пользователя"""
        session = Session()
        try:
            user = session.query(User).filter_by(discord_id=user_id).first()
            if user:
                return {
                    'messages': user.messages,
                    'xp': user.xp,
                    'level': user.level,
                    'joined_at': user.joined_at
                }
            return None
        finally:
            session.close()