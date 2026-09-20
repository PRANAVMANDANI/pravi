from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from datetime import datetime
from app.core.database import Base


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(20), unique=True, nullable=False, index=True)  # REQ-XXXXXX
    family_id = Column(String(25), nullable=False, index=True)
    member_id = Column(String(20), nullable=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Request details
    request_type = Column(String(50), nullable=False)  # name, dob, gender, address, occupation, income, member_addition, member_removal, relationship, marriage, birth, death, other
    field_name = Column(String(100), nullable=True)
    current_value = Column(Text, nullable=True)
    requested_value = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)

    # Status workflow
    status = Column(String(30), default="submitted", index=True)  # submitted, under_review, more_info_required, approved, rejected, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, urgent

    # Officer review
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Before/after snapshots for audit
    before_snapshot = Column(Text, nullable=True)  # JSON
    after_snapshot = Column(Text, nullable=True)  # JSON

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_change_requests_status_type", "status", "request_type"),
        Index("ix_change_requests_family", "family_id", "status"),
    )


class ChangeRequestDocument(Base):
    __tablename__ = "change_request_documents"

    id = Column(Integer, primary_key=True, index=True)
    change_request_id = Column(Integer, ForeignKey("change_requests.id"), nullable=False)
    document_type = Column(String(50), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
