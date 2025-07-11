from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	discord_id = Column(String(255), unique=True)
	username = Column(String(255))