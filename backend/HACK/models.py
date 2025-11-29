# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    contact = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_given = Column(Boolean, default=False)

    points = Column(Integer, default=0)
    level = Column(String, default="Новичок")
    interests = Column(String, nullable=True)

    submissions = relationship("QuestSubmission", back_populates="user", cascade="all, delete-orphan")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    reward_points = Column(Integer, default=10)
    quest_type = Column(String, nullable=False)

    submissions = relationship("QuestSubmission", back_populates="quest")


class QuestSubmission(Base):
    __tablename__ = "quest_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    metadata_json = Column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    quest = relationship("Quest", back_populates="submissions")