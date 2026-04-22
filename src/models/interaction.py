from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Interaction(Base):
    """用户交互记录"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    content_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    read_time = Column(Integer, default=0)
    weight = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
