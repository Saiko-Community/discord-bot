from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Computed
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	discord_id = Column(String(255), unique=True)
	joined_at = Column(BigInteger)  # Unix timestamp
	invited_by = Column(String(255), nullable=True)
	invite_code = Column(String(255), nullable=True)
	messages = Column(Integer, default=0)
	xp = Column(Integer, default=0)
	level = Column(Integer, Computed("ROUND(xp / 25)"))