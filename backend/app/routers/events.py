from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.event_service import (
    create_life_event, approve_life_event, reject_life_event, get_life_events
)

router = APIRouter(prefix="/api/v1/life-events", tags=["Life Events"])


class CreateLifeEvent(BaseModel):
    family_id: str
    member_id: Optional[str] = None
    event_type: str
    description: Optional[str] = None
    event_date: Optional[str] = None
    new_member_name: Optional[str] = None
    new_member_dob: Optional[str] = None
    new_member_gender: Optional[str] = None
    new_member_relationship: Optional[str] = None
    extra_data: Optional[dict] = None


class ReviewEvent(BaseModel):
    notes: Optional[str] = None


@router.post("")
def create_event(data: CreateLifeEvent, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != data.family_id:
        raise HTTPException(status_code=403, detail="You can only submit events for your own family")

    event = create_life_event(db, current_user.id, data.model_dump())
    db.commit()
    return {
        "success": True,
        "data": {
            "event_id": event.event_id, "status": event.status,
            "message": "Your life event has been submitted for verification.",
        }
    }


@router.get("")
def list_events(family_id: Optional[str] = None, status: Optional[str] = None,
                event_type: Optional[str] = None, limit: int = 50, offset: int = 0,
                db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen":
        family_id = current_user.family_id
    events = get_life_events(db, family_id, status, event_type, limit, offset)
    return {
        "success": True,
        "data": [{
            "event_id": e.event_id, "family_id": e.family_id, "member_id": e.member_id,
            "event_type": e.event_type, "description": e.description,
            "event_date": str(e.event_date) if e.event_date else None,
            "new_member_name": e.new_member_name, "new_member_gender": e.new_member_gender,
            "new_member_relationship": e.new_member_relationship,
            "status": e.status, "review_notes": e.review_notes,
            "affected_schemes": e.affected_schemes,
            "created_at": str(e.created_at) if e.created_at else None,
            "reviewed_at": str(e.reviewed_at) if e.reviewed_at else None,
        } for e in events]
    }


@router.post("/{event_id}/approve")
def approve_event(event_id: str, review: ReviewEvent = None,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    notes = review.notes if review else None
    event = approve_life_event(db, event_id, current_user.id, current_user.full_name, notes)
    if not event:
        raise HTTPException(status_code=404, detail="Life event not found")
    db.commit()
    return {
        "success": True,
        "data": {
            "event_id": event.event_id, "status": event.status,
            "affected_schemes": event.affected_schemes,
            "message": "Life event approved. Family records updated. Eligibility re-evaluated.",
        }
    }


@router.post("/{event_id}/reject")
def reject_event(event_id: str, review: ReviewEvent = None,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    notes = review.notes if review else None
    event = reject_life_event(db, event_id, current_user.id, notes)
    if not event:
        raise HTTPException(status_code=404, detail="Life event not found")
    db.commit()
    return {"success": True, "data": {"event_id": event.event_id, "status": event.status}}
