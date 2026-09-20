from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.benefit import BenefitLedger, Application


def get_family_benefits(db: Session, family_id: str) -> List[BenefitLedger]:
    return db.query(BenefitLedger).filter(BenefitLedger.family_id == family_id).order_by(BenefitLedger.created_at.desc()).all()


def get_all_benefits(db: Session, scheme_id: str = None, status: str = None,
                     limit: int = 50, offset: int = 0) -> List[BenefitLedger]:
    q = db.query(BenefitLedger)
    if scheme_id:
        q = q.filter(BenefitLedger.scheme_id == scheme_id)
    if status:
        q = q.filter(BenefitLedger.status == status)
    return q.order_by(BenefitLedger.created_at.desc()).offset(offset).limit(limit).all()


def get_family_applications(db: Session, family_id: str) -> List[Application]:
    return db.query(Application).filter(Application.family_id == family_id).all()
