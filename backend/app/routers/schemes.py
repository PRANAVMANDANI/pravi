from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES, ROLE_SCHEME_OFFICER, ROLE_STATE_ADMIN
from app.models.user import User
from app.models.scheme import Scheme, SchemeRule
from app.services.eligibility_service import get_all_schemes, get_scheme_by_id, evaluate_eligibility, get_family_eligibility
import json

router = APIRouter(prefix="/api/v1/schemes", tags=["Schemes"])


class CreateScheme(BaseModel):
    name: str
    description: Optional[str] = None
    department_name: Optional[str] = None
    benefit_type: Optional[str] = None
    benefit_value: Optional[str] = None
    benefit_frequency: Optional[str] = None
    target_group: Optional[str] = None


class CreateRule(BaseModel):
    field: str
    operator: str
    value: str
    value_type: Optional[str] = "string"
    entity: Optional[str] = "member"
    description: Optional[str] = None
    logical_group: Optional[str] = "AND"


def _serialize_scheme(s):
    return {
        "id": s.id, "scheme_id": s.scheme_id, "name": s.name, "description": s.description,
        "department_name": s.department_name,
        "benefit_type": s.benefit_type, "benefit_value": s.benefit_value,
        "benefit_frequency": s.benefit_frequency,
        "status": s.status, "is_demo": s.is_demo,
        "target_group": s.target_group,
        "current_beneficiaries": s.current_beneficiaries,
        "created_at": str(s.created_at) if s.created_at else None,
        "rules": [{
            "id": r.id, "field": r.field, "operator": r.operator, "value": r.value,
            "value_type": r.value_type, "entity": r.entity, "description": r.description,
            "logical_group": r.logical_group, "is_active": r.is_active,
        } for r in (s.rules or [])]
    }


@router.get("")
def list_schemes(status: Optional[str] = None, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    schemes = get_all_schemes(db, status)
    return {"success": True, "data": [_serialize_scheme(s) for s in schemes]}


@router.get("/{scheme_id}")
def get_scheme(scheme_id: str, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    scheme = get_scheme_by_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"success": True, "data": _serialize_scheme(scheme)}


@router.post("")
def create_scheme(data: CreateScheme, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    check_role(current_user, [ROLE_SCHEME_OFFICER, ROLE_STATE_ADMIN])
    count = db.query(Scheme).count()
    scheme = Scheme(
        scheme_id=f"SCH-{count + 1:04d}",
        name=data.name, description=data.description,
        department_name=data.department_name,
        benefit_type=data.benefit_type, benefit_value=data.benefit_value,
        benefit_frequency=data.benefit_frequency,
        target_group=data.target_group,
        is_demo=True,
    )
    db.add(scheme)
    db.commit()
    return {"success": True, "data": _serialize_scheme(scheme)}


@router.patch("/{scheme_id}")
def update_scheme(scheme_id: str, data: CreateScheme, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    check_role(current_user, [ROLE_SCHEME_OFFICER, ROLE_STATE_ADMIN])
    scheme = get_scheme_by_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        if hasattr(scheme, k) and v is not None:
            setattr(scheme, k, v)
    db.commit()
    return {"success": True, "data": _serialize_scheme(scheme)}


@router.post("/{scheme_id}/rules")
def add_rule(scheme_id: str, data: CreateRule, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    check_role(current_user, [ROLE_SCHEME_OFFICER, ROLE_STATE_ADMIN])
    scheme = get_scheme_by_id(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    rule = SchemeRule(
        scheme_id=scheme.id,
        field=data.field, operator=data.operator, value=data.value,
        value_type=data.value_type, entity=data.entity,
        description=data.description, logical_group=data.logical_group,
    )
    db.add(rule)
    db.commit()
    return {"success": True, "data": {"rule_id": rule.id}}


@router.post("/{scheme_id}/evaluate")
def evaluate_scheme(scheme_id: str, family_id: str = None,
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen":
        family_id = current_user.family_id
    if not family_id:
        raise HTTPException(status_code=400, detail="family_id required")

    results = evaluate_eligibility(db, family_id, scheme_id)
    return {"success": True, "data": results}
