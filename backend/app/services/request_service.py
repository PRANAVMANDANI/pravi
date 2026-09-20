import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.change_request import ChangeRequest
from app.models.family import Family
from app.models.member import Member
from app.models.notification import Notification
from app.services.audit_service import create_audit_log
from app.services.eligibility_service import invalidate_eligibility, evaluate_eligibility


def create_change_request(db: Session, user_id: int, family_id: str, request_data: dict) -> ChangeRequest:
    count = db.query(ChangeRequest).count()
    request_id = f"REQ-{count + 1:06d}"

    cr = ChangeRequest(
        request_id=request_id,
        family_id=family_id,
        member_id=request_data.get("member_id"),
        requested_by=user_id,
        request_type=request_data["request_type"],
        field_name=request_data.get("field_name"),
        current_value=request_data.get("current_value"),
        requested_value=request_data.get("requested_value"),
        reason=request_data.get("reason"),
        status="submitted",
        priority=request_data.get("priority", "normal"),
    )
    db.add(cr)
    db.flush()

    create_audit_log(db, actor_id=user_id, action="CHANGE_REQUEST_CREATED",
                     entity_type="change_request", entity_id=request_id,
                     description=f"Change request submitted: {cr.request_type}")

    return cr


def get_change_requests(db: Session, family_id: str = None, status: str = None,
                        request_type: str = None, limit: int = 50, offset: int = 0) -> List[ChangeRequest]:
    q = db.query(ChangeRequest)
    if family_id:
        q = q.filter(ChangeRequest.family_id == family_id)
    if status:
        q = q.filter(ChangeRequest.status == status)
    if request_type:
        q = q.filter(ChangeRequest.request_type == request_type)
    return q.order_by(ChangeRequest.created_at.desc()).offset(offset).limit(limit).all()


def get_change_request_by_id(db: Session, request_id: str) -> Optional[ChangeRequest]:
    return db.query(ChangeRequest).filter(ChangeRequest.request_id == request_id).first()


def approve_change_request(db: Session, request_id: str, officer_id: int, officer_name: str,
                           review_notes: str = None) -> ChangeRequest:
    cr = get_change_request_by_id(db, request_id)
    if not cr:
        return None

    # Snapshot before state
    before = _capture_snapshot(db, cr)

    # Apply the change
    _apply_change(db, cr)

    # Snapshot after state
    after = _capture_snapshot(db, cr)

    cr.status = "approved"
    cr.reviewed_by = officer_id
    cr.reviewed_at = datetime.utcnow()
    cr.review_notes = review_notes
    cr.before_snapshot = json.dumps(before)
    cr.after_snapshot = json.dumps(after)
    cr.updated_at = datetime.utcnow()

    # Audit
    create_audit_log(db, actor_id=officer_id, actor_name=officer_name, actor_role="verification_officer",
                     action="CHANGE_REQUEST_APPROVED", entity_type="change_request", entity_id=request_id,
                     description=f"Approved: {cr.request_type}", reason=review_notes,
                     before_snapshot=before, after_snapshot=after)

    # Invalidate & re-evaluate eligibility
    invalidate_eligibility(db, cr.family_id, reason=f"change_request_{request_id}_approved")
    evaluate_eligibility(db, cr.family_id)

    # Notify citizen
    _notify_citizen(db, cr, "approved")

    db.flush()
    return cr


def reject_change_request(db: Session, request_id: str, officer_id: int, officer_name: str,
                          rejection_reason: str = None) -> ChangeRequest:
    cr = get_change_request_by_id(db, request_id)
    if not cr:
        return None

    cr.status = "rejected"
    cr.reviewed_by = officer_id
    cr.reviewed_at = datetime.utcnow()
    cr.rejection_reason = rejection_reason
    cr.updated_at = datetime.utcnow()

    create_audit_log(db, actor_id=officer_id, actor_name=officer_name, actor_role="verification_officer",
                     action="CHANGE_REQUEST_REJECTED", entity_type="change_request", entity_id=request_id,
                     description=f"Rejected: {cr.request_type}", reason=rejection_reason)

    _notify_citizen(db, cr, "rejected")
    db.flush()
    return cr


def request_more_info(db: Session, request_id: str, officer_id: int, notes: str) -> ChangeRequest:
    cr = get_change_request_by_id(db, request_id)
    if not cr:
        return None

    cr.status = "more_info_required"
    cr.reviewed_by = officer_id
    cr.review_notes = notes
    cr.updated_at = datetime.utcnow()
    _notify_citizen(db, cr, "more_info_required")
    db.flush()
    return cr


def _apply_change(db: Session, cr: ChangeRequest):
    """Apply the approved change to the authoritative record."""
    if cr.request_type in ("name", "dob", "gender", "occupation", "income") and cr.member_id:
        member = db.query(Member).filter(Member.member_id == cr.member_id).first()
        if member and cr.field_name:
            field_map = {
                "name": "name", "dob": "dob", "gender": "gender",
                "occupation": "occupation", "income": "income_band",
            }
            actual_field = field_map.get(cr.request_type, cr.field_name)
            if hasattr(member, actual_field):
                setattr(member, actual_field, cr.requested_value)
                member.updated_at = datetime.utcnow()

    elif cr.request_type == "address":
        family = db.query(Family).filter(Family.family_id == cr.family_id).first()
        if family:
            family.address_line = cr.requested_value
            family.updated_at = datetime.utcnow()

    elif cr.request_type == "income":
        family = db.query(Family).filter(Family.family_id == cr.family_id).first()
        if family:
            family.income_band = cr.requested_value
            family.updated_at = datetime.utcnow()


def _capture_snapshot(db: Session, cr: ChangeRequest) -> dict:
    """Capture state of the affected entity."""
    if cr.member_id:
        member = db.query(Member).filter(Member.member_id == cr.member_id).first()
        if member:
            return {"member_id": member.member_id, "name": member.name,
                    "dob": str(member.dob) if member.dob else None,
                    "gender": member.gender, "occupation": member.occupation}
    family = db.query(Family).filter(Family.family_id == cr.family_id).first()
    if family:
        return {"family_id": family.family_id, "address": family.address_line,
                "district": family.district, "income_band": family.income_band}
    return {}


def _notify_citizen(db: Session, cr: ChangeRequest, outcome: str):
    """Create notification for the citizen."""
    count = db.query(Notification).count()
    titles = {
        "approved": f"Your {cr.request_type} change request has been approved",
        "rejected": f"Your {cr.request_type} change request has been rejected",
        "more_info_required": f"More information required for your {cr.request_type} request",
    }
    messages = {
        "approved": f"Request {cr.request_id}: Your change from '{cr.current_value}' to '{cr.requested_value}' has been approved and the authoritative record updated.",
        "rejected": f"Request {cr.request_id}: Your change request was rejected. Reason: {cr.rejection_reason or 'See details.'}",
        "more_info_required": f"Request {cr.request_id}: Additional information is needed. Notes: {cr.review_notes or 'Please check the request.'}",
    }
    notif = Notification(
        notification_id=f"NTF-{count + 1:06d}",
        user_id=cr.requested_by,
        title=titles.get(outcome, "Request update"),
        message=messages.get(outcome, ""),
        notification_type="request_update",
        entity_type="change_request",
        entity_id=cr.request_id,
    )
    db.add(notif)
