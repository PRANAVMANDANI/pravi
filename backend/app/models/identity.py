from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Index
from datetime import datetime
from app.core.database import Base


class IdentityMatch(Base):
    __tablename__ = "identity_matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(20), unique=True, nullable=False, index=True)

    # Records being compared
    record_a_type = Column(String(20), nullable=False)  # family, member
    record_a_id = Column(String(30), nullable=False)
    record_a_name = Column(String(255), nullable=True)
    record_a_source = Column(String(100), nullable=True)

    record_b_type = Column(String(20), nullable=False)
    record_b_id = Column(String(30), nullable=False)
    record_b_name = Column(String(255), nullable=True)
    record_b_source = Column(String(100), nullable=True)

    # Match details
    confidence_score = Column(Float, nullable=False)  # 0-100
    match_reasons = Column(Text, nullable=True)  # JSON list of match reasons
    match_type = Column(String(30), nullable=True)  # exact, deterministic, fuzzy

    # Status
    status = Column(String(20), default="pending", index=True)  # pending, confirmed, rejected, reviewed
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdentityMergeHistory(Base):
    __tablename__ = "identity_merge_history"

    id = Column(Integer, primary_key=True, index=True)
    merge_id = Column(String(20), unique=True, nullable=False, index=True)

    action = Column(String(10), nullable=False)  # merge, split
    primary_id = Column(String(30), nullable=False)
    secondary_id = Column(String(30), nullable=False)
    entity_type = Column(String(20), nullable=False)  # family, member

    reason = Column(Text, nullable=True)
    before_snapshot = Column(Text, nullable=True)
    after_snapshot = Column(Text, nullable=True)

    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
