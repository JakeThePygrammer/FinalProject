from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine("sqlite:///polls.db")
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

Base.metadata.create_all(bind=engine)
