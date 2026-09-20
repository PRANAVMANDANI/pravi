from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(20), unique=True, nullable=False, index=True)
    family_id = Column(String(25), nullable=True, index=True)
    member_id = Column(String(20), nullable=True)

    document_type = Column(String(50), nullable=False)  # address_proof, identity_proof, income_proof, birth_certificate, death_certificate, marriage_certificate, other
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # Verification
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
