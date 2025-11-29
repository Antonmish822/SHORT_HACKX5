# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # email или @username — одно поле (как в ТЗ: "email / Telegram")
    contact = Column(String, unique=True, index=True, nullable=False)  # напр. "ivan@example.com" или "@ivan_tg"
    hashed_password = Column(String, nullable=True)  # может быть NULL, если вход по Telegram без пароля
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_given = Column(Boolean, default=False)  # согласие на обработку данных

    # игровые данные
    points = Column(Integer, default=0)
    level = Column(String, default="Новичок")  # "Новичок", "Эксперт", "Гуру"
    interests = Column(String, nullable=True)  # JSON-строка или CSV: "Data Science,Python"

    # связи
    submissions = relationship("QuestSubmission", back_populates="user", cascade="all, delete-orphan")


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    reward_points = Column(Integer, default=10)
    quest_type = Column(String, nullable=False)  # "quiz", "photo", "qr_hunt", "roleplay", "tech_qa"

    submissions = relationship("QuestSubmission", back_populates="quest")


class QuestSubmission(Base):
    __tablename__ = "quest_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")  # "completed", "pending", "rejected"
    metadata_json = Column(Text, nullable=True)  # доп. данные: фото URL, ответы и т.п.

    user = relationship("User", back_populates="submissions")
    quest = relationship("Quest", back_populates="submissions")