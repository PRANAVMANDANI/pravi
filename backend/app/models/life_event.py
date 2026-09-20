from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from datetime import datetime
from app.core.database import Base


class LifeEvent(Base):
    __tablename__ = "life_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(20), unique=True, nullable=False, index=True)  # EVT-XXXXXX
    family_id = Column(String(25), nullable=False, index=True)
    member_id = Column(String(20), nullable=True)

    event_type = Column(String(30), nullable=False, index=True)  # birth, death, marriage, divorce, address_change, income_change, member_added, member_removed, occupation_change
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=True)

    # New member details (for birth/member_added)
    new_member_name = Column(String(255), nullable=True)
    new_member_dob = Column(String(20), nullable=True)
    new_member_gender = Column(String(20), nullable=True)
    new_member_relationship = Column(String(50), nullable=True)

    # Additional data as JSON
    event_data = Column(Text, nullable=True)  # JSON with event-specific data

    # Status
    status = Column(String(30), default="submitted", index=True)  # submitted, under_review, approved, rejected
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Affected schemes (populated after processing)
    affected_schemes = Column(Text, nullable=True)  # JSON list of scheme IDs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_life_events_family_type", "family_id", "event_type"),
    )
