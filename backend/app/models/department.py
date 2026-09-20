from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    officers = relationship("User", back_populates="department")


class DataAccessRequest(Base):
    __tablename__ = "data_access_requests"

    id = Column(Integer, primary_key=True, index=True)
    access_id = Column(String(20), unique=True, nullable=False, index=True)

    # Who
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_code = Column(String(50), nullable=True)

    # What
    family_id = Column(String(25), nullable=False, index=True)
    purpose = Column(Text, nullable=False)
    fields_requested = Column(Text, nullable=True)  # JSON
    fields_returned = Column(Text, nullable=True)  # JSON

    # Status
    status = Column(String(20), default="completed")  # completed, denied
    denial_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_data_access_family", "family_id"),
        Index("ix_data_access_dept", "department_code"),
    )
