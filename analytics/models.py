from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    joined_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

class Token(Base):
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(6), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    used_at = Column(DateTime, nullable=True)