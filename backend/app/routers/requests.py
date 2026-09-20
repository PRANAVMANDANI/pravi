from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.request_service import (
    create_change_request, get_change_requests, get_change_request_by_id,
    approve_change_request, reject_change_request, request_more_info
)

router = APIRouter(prefix="/api/v1/change-requests", tags=["Change Requests"])


class CreateChangeRequest(BaseModel):
    family_id: str
    member_id: Optional[str] = None
    request_type: str
    field_name: Optional[str] = None
    current_value: Optional[str] = None
    requested_value: Optional[str] = None
    reason: Optional[str] = None
    priority: Optional[str] = "normal"


class ReviewRequest(BaseModel):
    notes: Optional[str] = None
    reason: Optional[str] = None


@router.post("")
def create_request(data: CreateChangeRequest, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    # Citizens can only create requests for their own family
    if current_user.role == "citizen" and current_user.family_id != data.family_id:
        raise HTTPException(status_code=403, detail="You can only submit requests for your own family")

    cr = create_change_request(db, current_user.id, data.family_id, data.model_dump())
    db.commit()
    return {
        "success": True,
        "data": {
            "request_id": cr.request_id,
            "status": cr.status,
            "message": "Your request has been submitted. A verification officer will review it.",
        }
    }


@router.get("")
def list_requests(family_id: Optional[str] = None, status: Optional[str] = None,
                  request_type: Optional[str] = None, limit: int = 50, offset: int = 0,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Citizens only see their own family's requests
    if current_user.role == "citizen":
        family_id = current_user.family_id

    requests = get_change_requests(db, family_id, status, request_type, limit, offset)
    return {
        "success": True,
        "data": [{
            "request_id": r.request_id, "family_id": r.family_id, "member_id": r.member_id,
            "request_type": r.request_type, "field_name": r.field_name,
            "current_value": r.current_value, "requested_value": r.requested_value,
            "reason": r.reason, "status": r.status, "priority": r.priority,
            "review_notes": r.review_notes, "rejection_reason": r.rejection_reason,
            "created_at": str(r.created_at) if r.created_at else None,
            "reviewed_at": str(r.reviewed_at) if r.reviewed_at else None,
        } for r in requests]
    }


@router.get("/{request_id}")
def get_request(request_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    cr = get_change_request_by_id(db, request_id)
    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")
    if current_user.role == "citizen" and current_user.family_id != cr.family_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "data": {
            "request_id": cr.request_id, "family_id": cr.family_id, "member_id": cr.member_id,
            "request_type": cr.request_type, "field_name": cr.field_name,
            "current_value": cr.current_value, "requested_value": cr.requested_value,
            "reason": cr.reason, "status": cr.status, "priority": cr.priority,
            "review_notes": cr.review_notes, "rejection_reason": cr.rejection_reason,
            "before_snapshot": cr.before_snapshot, "after_snapshot": cr.after_snapshot,
            "created_at": str(cr.created_at) if cr.created_at else None,
            "reviewed_at": str(cr.reviewed_at) if cr.reviewed_at else None,
        }
    }


@router.post("/{request_id}/approve")
def approve_request(request_id: str, review: ReviewRequest = None,
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    notes = review.notes if review else None
    cr = approve_change_request(db, request_id, current_user.id, current_user.full_name, notes)
    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")
    db.commit()
    return {
        "success": True,
        "data": {
            "request_id": cr.request_id, "status": cr.status,
            "message": "Change request approved. Authoritative record updated. Eligibility re-evaluated.",
        }
    }


@router.post("/{request_id}/reject")
def reject_request_endpoint(request_id: str, review: ReviewRequest = None,
                            db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    reason = review.reason if review else None
    cr = reject_change_request(db, request_id, current_user.id, current_user.full_name, reason)
    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")
    db.commit()
    return {"success": True, "data": {"request_id": cr.request_id, "status": cr.status}}


@router.post("/{request_id}/request-information")
def request_information(request_id: str, review: ReviewRequest,
                        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    cr = request_more_info(db, request_id, current_user.id, review.notes)
    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")
    db.commit()
    return {"success": True, "data": {"request_id": cr.request_id, "status": cr.status}}
