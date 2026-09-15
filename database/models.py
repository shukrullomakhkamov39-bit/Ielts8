from sqlalchemy import BigInteger, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    target_band: Mapped[float] = mapped_column(Float, default=7.5)
    current_level: Mapped[str] = mapped_column(String(50), default="B1")
    daily_hours: Mapped[float] = mapped_column(Float, default=4.5)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    streak: Mapped[int] = mapped_column(Integer, default=1)

    errors = relationship("UserError", back_populates="user", cascade="all, delete-orphan")

class UserError(Base):
    __tablename__ = 'user_errors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'))
    skill: Mapped[str] = mapped_column(String(50))
    question: Mapped[str] = mapped_column(Text)
    user_answer: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    is_mastered: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="errors")
