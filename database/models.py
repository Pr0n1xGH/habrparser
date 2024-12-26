from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PostRecord(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    published_at = Column(DateTime)
    hubs = Column(String, nullable=True)

class BotStats(Base):
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    posts_processed = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    last_check_time = Column(DateTime, nullable=True) 