from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    notification_type = Column(String(50), nullable=True)  # request_update, eligibility_change, benefit_update, system, data_quality
    
    # Related entity
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(30), nullable=True)

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )
