from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(20), unique=True, nullable=False, index=True)

    # Who
    actor_id = Column(Integer, nullable=True)
    actor_name = Column(String(255), nullable=True)
    actor_role = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)

    # What
    action = Column(String(50), nullable=False, index=True)  # LOGIN, FAMILY_CREATED, MEMBER_UPDATED, CHANGE_REQUEST_APPROVED, etc.
    entity_type = Column(String(50), nullable=True)  # family, member, change_request, life_event, scheme, benefit
    entity_id = Column(String(30), nullable=True, index=True)

    # Details
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    before_snapshot = Column(Text, nullable=True)  # JSON
    after_snapshot = Column(Text, nullable=True)  # JSON

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(50), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_audit_logs_actor_action", "actor_id", "action"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )
