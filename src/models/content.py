from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from datetime import datetime

from src.db.database import Base


class Content(Base):
    """内容模型"""
    __tablename__ = "contents"

    content_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    source = Column(String)
    url = Column(String)
    published_at = Column(DateTime)
    summary = Column(Text)
    tags = Column(JSON, default=list)
    embedding = Column(JSON, nullable=True)
    audio_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
