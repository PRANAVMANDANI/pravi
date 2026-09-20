from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES, ALL_ROLES
from app.models.user import User
from app.services import family_service
from app.services.audit_service import create_audit_log
import json

router = APIRouter(prefix="/api/v1/families", tags=["Families"])


def _serialize_family(f):
    return {
        "id": f.id, "family_id": f.family_id, "status": f.status,
        "head_member_id": f.head_member_id,
        "address_line": f.address_line, "district": f.district, "taluka": f.taluka,
        "village_city": f.village_city, "pincode": f.pincode, "state": f.state,
        "income_band": f.income_band, "category": f.category,
        "ration_card_type": f.ration_card_type,
        "verification_status": f.verification_status,
        "data_quality_score": f.data_quality_score,
        "source": f.source,
        "member_count": f.member_count,
        "created_at": str(f.created_at) if f.created_at else None,
        "updated_at": str(f.updated_at) if f.updated_at else None,
        "last_verified_at": str(f.last_verified_at) if f.last_verified_at else None,
    }


def _serialize_member(m):
    return {
        "id": m.id, "member_id": m.member_id, "family_id": m.family_id_str,
        "name": m.name, "name_local": m.name_local,
        "dob": str(m.dob) if m.dob else None, "age": m.age,
        "gender": m.gender, "occupation": m.occupation, "education": m.education,
        "income_band": m.income_band, "category": m.category,
        "relationship_to_head": m.relationship_to_head,
        "aadhaar_masked": m.aadhaar_masked,
        "phone": m.phone, "email": m.email,
        "is_active": m.is_active, "is_head": m.is_head,
        "verification_status": m.verification_status,
        "source": m.source,
        "created_at": str(m.created_at) if m.created_at else None,
        "updated_at": str(m.updated_at) if m.updated_at else None,
    }


@router.get("")
def list_families(
    q: Optional[str] = None, district: Optional[str] = None,
    taluka: Optional[str] = None, village: Optional[str] = None,
    status: Optional[str] = None, verification: Optional[str] = None,
    limit: int = 50, offset: int = 0,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    check_role(current_user, GOVERNMENT_ROLES)
    families = family_service.search_families(db, q, district, taluka, village, status, verification, limit, offset)
    total = family_service.count_families(db, district, status, verification)
    return {
        "success": True,
        "data": {
            "families": [_serialize_family(f) for f in families],
            "total": total, "limit": limit, "offset": offset,
        }
    }


@router.get("/{family_id}")
def get_family(family_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Citizens can only view their own family
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="You can only view your own family")

    family = family_service.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return {"success": True, "data": _serialize_family(family)}


@router.get("/{family_id}/360")
def get_family_360(family_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="You can only view your own family")

    data = family_service.get_family_360(db, family_id)
    if not data:
        raise HTTPException(status_code=404, detail="Family not found")

    result = {
        "family": _serialize_family(data["family"]),
        "members": [_serialize_member(m) for m in data["members"]],
        "benefits": [{
            "benefit_id": b.benefit_id, "scheme_id": b.scheme_id, "benefit_type": b.benefit_type,
            "amount": b.amount, "status": b.status, "description": b.description,
            "department_name": b.department_name, "period_start": str(b.period_start) if b.period_start else None,
            "period_end": str(b.period_end) if b.period_end else None,
            "created_at": str(b.created_at) if b.created_at else None,
        } for b in data["benefits"]],
        "eligibility": [{
            "scheme_id": e.scheme_id, "status": e.status, "explanation": e.explanation,
            "is_stale": e.is_stale, "evaluated_at": str(e.evaluated_at) if e.evaluated_at else None,
            "matched_rules": json.loads(e.matched_rules) if e.matched_rules else [],
            "failed_rules": json.loads(e.failed_rules) if e.failed_rules else [],
            "missing_data": json.loads(e.missing_data) if e.missing_data else [],
        } for e in data["eligibility"]],
        "change_requests": [{
            "request_id": cr.request_id, "request_type": cr.request_type,
            "status": cr.status, "current_value": cr.current_value,
            "requested_value": cr.requested_value, "reason": cr.reason,
            "created_at": str(cr.created_at) if cr.created_at else None,
        } for cr in data["change_requests"]],
        "life_events": [{
            "event_id": e.event_id, "event_type": e.event_type,
            "status": e.status, "description": e.description,
            "event_date": str(e.event_date) if e.event_date else None,
            "created_at": str(e.created_at) if e.created_at else None,
        } for e in data["life_events"]],
        "audit_logs": [{
            "audit_id": a.audit_id, "action": a.action, "actor_name": a.actor_name,
            "actor_role": a.actor_role, "description": a.description,
            "created_at": str(a.created_at) if a.created_at else None,
        } for a in data["audit_logs"]],
        "duplicate_matches": [{
            "match_id": m.match_id, "record_a_name": m.record_a_name,
            "record_b_name": m.record_b_name, "confidence_score": m.confidence_score,
            "status": m.status,
        } for m in data["duplicate_matches"]],
        "data_quality": data["data_quality"],
    }
    return {"success": True, "data": result}


@router.get("/{family_id}/members")
def get_family_members(family_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="You can only view your own family")

    members = family_service.get_family_members(db, family_id)
    return {"success": True, "data": [_serialize_member(m) for m in members]}


@router.get("/{family_id}/relationships")
def get_relationships(family_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="You can only view your own family")

    members = family_service.get_active_members(db, family_id)
    head = next((m for m in members if m.is_head), members[0] if members else None)
    relationships = []
    if head:
        for m in members:
            relationships.append({
                "member_id": m.member_id, "name": m.name,
                "relationship_to_head": m.relationship_to_head or "unknown",
                "is_head": m.is_head, "is_active": m.is_active,
            })
    return {"success": True, "data": {"head": _serialize_member(head) if head else None, "relationships": relationships}}
