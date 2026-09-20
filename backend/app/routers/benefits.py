from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.benefit_service import get_family_benefits, get_all_benefits

router = APIRouter(prefix="/api/v1/benefits", tags=["Benefits"])


@router.get("")
def list_benefits(family_id: Optional[str] = None, scheme_id: Optional[str] = None,
                  status: Optional[str] = None, limit: int = 50, offset: int = 0,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen":
        family_id = current_user.family_id

    if family_id:
        benefits = get_family_benefits(db, family_id)
    else:
        check_role(current_user, GOVERNMENT_ROLES)
        benefits = get_all_benefits(db, scheme_id, status, limit, offset)

    return {
        "success": True,
        "data": [{
            "benefit_id": b.benefit_id, "family_id": b.family_id, "member_id": b.member_id,
            "scheme_id": b.scheme_id, "benefit_type": b.benefit_type,
            "amount": b.amount, "currency": b.currency, "description": b.description,
            "period_start": str(b.period_start) if b.period_start else None,
            "period_end": str(b.period_end) if b.period_end else None,
            "frequency": b.frequency, "status": b.status,
            "department_name": b.department_name, "source": b.source,
            "created_at": str(b.created_at) if b.created_at else None,
        } for b in benefits]
    }
