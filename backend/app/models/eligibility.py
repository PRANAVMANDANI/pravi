from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Index
from datetime import datetime
from app.core.database import Base


class EligibilityResult(Base):
    __tablename__ = "eligibility_results"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(25), nullable=False, index=True)
    member_id = Column(String(20), nullable=True)
    scheme_id = Column(String(30), nullable=False, index=True)

    # Result
    status = Column(String(20), nullable=False)  # eligible, not_eligible, needs_verification
    confidence = Column(Float, default=1.0)

    # Explanation
    matched_rules = Column(Text, nullable=True)  # JSON
    failed_rules = Column(Text, nullable=True)  # JSON
    missing_data = Column(Text, nullable=True)  # JSON
    explanation = Column(Text, nullable=True)
    rule_version = Column(Integer, default=1)

    # Staleness
    is_stale = Column(Boolean, default=False)
    stale_reason = Column(String(255), nullable=True)

    evaluated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_eligibility_family_scheme", "family_id", "scheme_id"),
    )
