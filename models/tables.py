from sqlalchemy.orm import Mapped , mapped_column, DeclarativeBase
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime


class Base(DeclarativeBase):
    pass


class InputEvent(Base):
    __tablename__ = "events"
    record_id : Mapped[int] = mapped_column(primary_key=True)
    event_id : Mapped[str] = mapped_column(unique=True)
    event_type : Mapped[str]
    event_data : Mapped[dict] = mapped_column(JSONB)
    event_status : Mapped[str] = mapped_column(CheckConstraint("event_status IN ('pending', 'delivered', 'failed')"))
    received_at : Mapped[datetime]
    attempt_count : Mapped[int] = mapped_column(default=0)
    next_attempt : Mapped[datetime | None] = mapped_column(default=None)
    final_status_code: Mapped[int | None ]= mapped_column(default=None)


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"
    attempt_id : Mapped[int] = mapped_column(primary_key=True)
    event_id : Mapped[str]
    attempt_number : Mapped[int]
    target : Mapped[str]
    status_code : Mapped[int | None] 
    error : Mapped[str]
    created_at : Mapped[datetime]


