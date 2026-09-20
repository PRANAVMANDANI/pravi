from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(25), unique=True, nullable=False, index=True)  # GJ-FAM-2026-XXXXXXXX
    status = Column(String(20), default="active")  # active, inactive, merged, split
    head_member_id = Column(String(20), nullable=True)

    # Address
    address_line = Column(Text, nullable=True)
    district = Column(String(100), nullable=True, index=True)
    taluka = Column(String(100), nullable=True, index=True)
    village_city = Column(String(100), nullable=True, index=True)
    pincode = Column(String(10), nullable=True)
    state = Column(String(50), default="Gujarat")

    # Household info
    income_band = Column(String(50), nullable=True)  # BPL, APL, EWS, LIG, MIG, HIG
    category = Column(String(50), nullable=True)  # General, OBC, SC, ST, etc.
    ration_card_type = Column(String(50), nullable=True)

    # Verification
    verification_status = Column(String(30), default="pending")  # pending, verified, partially_verified, rejected
    verified_by = Column(Integer, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Data quality
    data_quality_score = Column(Float, default=0.0)
    data_quality_issues = Column(Text, nullable=True)  # JSON

    # Source tracking
    source = Column(String(100), default="manual")
    source_reference = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime, nullable=True)

    # Relationships
    members = relationship("Member", back_populates="family", foreign_keys="Member.family_id_fk")

    __table_args__ = (
        Index("ix_families_district_taluka", "district", "taluka"),
        Index("ix_families_verification_status", "verification_status"),
    )

    @property
    def member_count(self):
        return len([m for m in self.members if m.is_active]) if self.members else 0
