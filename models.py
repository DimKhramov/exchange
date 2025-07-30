from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Float, Boolean, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)
    api_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExchangeRateHistory(Base):
    __tablename__ = "exchange_rate_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    base_currency: Mapped[str] = mapped_column(String)
    target_currency: Mapped[str] = mapped_column(String)
    rate: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", backref="exchange_rate_history")

class APIRequest(Base):
    __tablename__ = "api_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    endpoint: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    status_code: Mapped[int] = mapped_column(Integer)
    response_time: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", backref="api_requests")
