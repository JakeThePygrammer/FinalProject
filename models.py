from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# моделот/табелата којашто ја чуваме во база
class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    city_query = Column(String(120), nullable=False)
    city_full_name = Column(String(255), nullable=True)
    category = Column(String(40), nullable=False)
    price_level = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    ai_description = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
