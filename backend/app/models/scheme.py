from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_name = Column(String(100), nullable=True)

    # Benefit details
    benefit_type = Column(String(50), nullable=True)  # cash, kind, service, subsidy
    benefit_value = Column(String(100), nullable=True)  # e.g., "₹5,000 per year"
    benefit_frequency = Column(String(50), nullable=True)  # one_time, monthly, quarterly, annual

    # Status
    status = Column(String(20), default="active")  # active, inactive, draft
    is_demo = Column(Boolean, default=True)

    # Metadata
    target_group = Column(String(255), nullable=True)
    max_beneficiaries = Column(Integer, nullable=True)
    current_beneficiaries = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rules = relationship("SchemeRule", back_populates="scheme", cascade="all, delete-orphan")


class SchemeRule(Base):
    __tablename__ = "scheme_rules"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False, index=True)
    rule_version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    # Rule definition (JSON)
    # Format: {"field": "member_age", "operator": ">=", "value": 60, "entity": "member", "description": "Age >= 60"}
    field = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)  # =, !=, >, >=, <, <=, IN, NOT_IN, EXISTS
    value = Column(String(255), nullable=False)
    value_type = Column(String(20), default="string")  # string, number, boolean, list
    entity = Column(String(20), default="member")  # family, member
    description = Column(Text, nullable=True)
    logical_group = Column(String(10), default="AND")  # AND, OR

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scheme = relationship("Scheme", back_populates="rules")

    __table_args__ = (
        Index("ix_scheme_rules_scheme_active", "scheme_id", "is_active"),
    )
