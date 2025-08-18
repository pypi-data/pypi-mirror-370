# File: app/models.py (updated)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(80), nullable=False, unique=True)
    email = Column(String(254), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    
    def __repr__(self):
        return f"<User (id={self.id}, username='{self.username}')>"

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    
    def __repr__(self):
        return f"<Post (id={self.id}, title='{self.title[:50]}...')>"