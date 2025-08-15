from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	discord_id = Column(String(255), unique=True)
	username = Column(String(255))
	joined_at = Column(DateTime, default=datetime.utcnow)
	invited_by = Column(String(255), nullable=True)
	invite_code = Column(String(255), nullable=True)