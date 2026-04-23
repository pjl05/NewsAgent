from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime

from src.db.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    subscriptions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSON, nullable=True)
    feedback = Column(JSON, default=dict)
