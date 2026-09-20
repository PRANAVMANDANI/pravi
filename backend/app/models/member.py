from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String(20), unique=True, nullable=False, index=True)  # GJ-MEM-XXXXXXXX
    family_id_fk = Column(Integer, ForeignKey("families.id"), nullable=False)
    family_id_str = Column(String(25), nullable=False, index=True)  # GJ-FAM-2026-XXXXXXXX

    # Personal info
    name = Column(String(255), nullable=False)
    name_local = Column(String(255), nullable=True)  # Gujarati name
    dob = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other
    occupation = Column(String(100), nullable=True)
    education = Column(String(100), nullable=True)
    income_band = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)

    # Relationship to head
    relationship_to_head = Column(String(50), nullable=True)  # self, spouse, son, daughter, father, mother, etc.

    # Identity references (NO raw Aadhaar)
    aadhaar_reference_hash = Column(String(64), nullable=True, index=True)
    aadhaar_masked = Column(String(12), nullable=True)  # XXXX-XXXX-1234

    # Contact
    phone = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_head = Column(Boolean, default=False)
    verification_status = Column(String(30), default="pending")  # pending, verified, rejected

    # Source
    source = Column(String(100), default="manual")
    source_reference = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = relationship("Family", back_populates="members", foreign_keys=[family_id_fk])

    __table_args__ = (
        Index("ix_members_name", "name"),
        Index("ix_members_dob", "dob"),
        Index("ix_members_family_active", "family_id_fk", "is_active"),
    )

    @property
    def age(self):
        if self.dob:
            from datetime import date
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
