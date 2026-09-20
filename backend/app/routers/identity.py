from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.identity_service import (
    find_potential_matches, get_pending_matches,
    confirm_match, reject_match, merge_records
)

router = APIRouter(prefix="/api/v1/identity", tags=["Identity Resolution"])


class MatchRequest(BaseModel):
    member_id: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    district: Optional[str] = None


class MergeRequest(BaseModel):
    primary_id: str
    secondary_id: str
    entity_type: str = "family"
    reason: Optional[str] = None


class ReviewMatch(BaseModel):
    notes: Optional[str] = None


@router.post("/match")
def find_matches(data: MatchRequest, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    matches = find_potential_matches(db, data.member_id, data.name, data.dob, data.gender, data.district)
    return {"success": True, "data": matches}


@router.get("/matches")
def list_pending_matches(limit: int = 50, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    matches = get_pending_matches(db, limit)
    return {
        "success": True,
        "data": [{
            "match_id": m.match_id,
            "record_a_type": m.record_a_type, "record_a_id": m.record_a_id,
            "record_a_name": m.record_a_name, "record_a_source": m.record_a_source,
            "record_b_type": m.record_b_type, "record_b_id": m.record_b_id,
            "record_b_name": m.record_b_name, "record_b_source": m.record_b_source,
            "confidence_score": m.confidence_score,
            "match_reasons": m.match_reasons, "match_type": m.match_type,
            "status": m.status,
            "created_at": str(m.created_at) if m.created_at else None,
        } for m in matches]
    }


@router.post("/matches/{match_id}/confirm")
def confirm(match_id: str, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    m = confirm_match(db, match_id, current_user.id, current_user.full_name)
    if not m:
        raise HTTPException(status_code=404, detail="Match not found")
    db.commit()
    return {"success": True, "data": {"match_id": m.match_id, "status": m.status}}


@router.post("/matches/{match_id}/reject")
def reject(match_id: str, review: ReviewMatch = None, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    notes = review.notes if review else None
    m = reject_match(db, match_id, current_user.id, notes)
    if not m:
        raise HTTPException(status_code=404, detail="Match not found")
    db.commit()
    return {"success": True, "data": {"match_id": m.match_id, "status": m.status}}


@router.post("/merge")
def merge(data: MergeRequest, db: Session = Depends(get_db),
          current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    result = merge_records(db, data.primary_id, data.secondary_id, data.entity_type,
                           current_user.id, current_user.full_name, data.reason)
    db.commit()
    return {"success": True, "data": {"merge_id": result.merge_id, "action": result.action}}
