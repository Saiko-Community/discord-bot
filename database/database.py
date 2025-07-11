from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = None
Session = None

async def setup():
	global engine, Session
	engine = create_engine('sqlite:///bot.db')
	Session = sessionmaker(bind=engine)
	Base.metadata.create_all(engine)
	print("База данных подключена")