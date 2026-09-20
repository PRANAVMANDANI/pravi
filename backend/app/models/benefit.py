from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Index
from datetime import datetime
from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(20), unique=True, nullable=False, index=True)
    family_id = Column(String(25), nullable=False, index=True)
    member_id = Column(String(20), nullable=True)
    scheme_id = Column(String(30), nullable=False, index=True)

    status = Column(String(30), default="pending")  # pending, approved, rejected, completed
    applied_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BenefitLedger(Base):
    __tablename__ = "benefit_ledger"

    id = Column(Integer, primary_key=True, index=True)
    benefit_id = Column(String(20), unique=True, nullable=False, index=True)
    family_id = Column(String(25), nullable=False, index=True)
    member_id = Column(String(20), nullable=True)
    scheme_id = Column(String(30), nullable=False, index=True)
    application_id = Column(String(20), nullable=True)

    # Benefit info
    benefit_type = Column(String(50), nullable=True)  # cash, kind, service, subsidy
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    description = Column(Text, nullable=True)

    # Period
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    frequency = Column(String(30), nullable=True)  # one_time, monthly, quarterly, annual

    # Status
    status = Column(String(30), default="active")  # active, completed, suspended, cancelled
    department_name = Column(String(100), nullable=True)

    # Source tracking
    source = Column(String(100), default="manual")
    source_reference = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_benefit_ledger_family_scheme", "family_id", "scheme_id"),
        Index("ix_benefit_ledger_status", "status"),
    )
