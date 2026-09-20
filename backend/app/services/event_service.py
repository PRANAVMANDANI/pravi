import json
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.life_event import LifeEvent
from app.models.family import Family
from app.models.member import Member
from app.models.notification import Notification
from app.services.audit_service import create_audit_log
from app.services.eligibility_service import invalidate_eligibility, evaluate_eligibility


def create_life_event(db: Session, user_id: int, event_data: dict) -> LifeEvent:
    count = db.query(LifeEvent).count()
    event_id = f"EVT-{count + 1:06d}"

    event = LifeEvent(
        event_id=event_id,
        family_id=event_data["family_id"],
        member_id=event_data.get("member_id"),
        event_type=event_data["event_type"],
        description=event_data.get("description"),
        event_date=event_data.get("event_date"),
        new_member_name=event_data.get("new_member_name"),
        new_member_dob=event_data.get("new_member_dob"),
        new_member_gender=event_data.get("new_member_gender"),
        new_member_relationship=event_data.get("new_member_relationship"),
        event_data=json.dumps(event_data.get("extra_data")) if event_data.get("extra_data") else None,
        status="submitted",
        requested_by=user_id,
    )
    db.add(event)
    db.flush()

    create_audit_log(db, actor_id=user_id, action="LIFE_EVENT_CREATED",
                     entity_type="life_event", entity_id=event_id,
                     description=f"Life event submitted: {event.event_type}")

    return event


def approve_life_event(db: Session, event_id: str, officer_id: int, officer_name: str,
                       review_notes: str = None) -> Optional[LifeEvent]:
    event = db.query(LifeEvent).filter(LifeEvent.event_id == event_id).first()
    if not event:
        return None

    # Process the event
    affected_schemes = _process_life_event(db, event)

    event.status = "approved"
    event.reviewed_by = officer_id
    event.reviewed_at = datetime.utcnow()
    event.review_notes = review_notes
    event.affected_schemes = json.dumps(affected_schemes)
    event.updated_at = datetime.utcnow()

    create_audit_log(db, actor_id=officer_id, actor_name=officer_name, actor_role="verification_officer",
                     action="LIFE_EVENT_APPROVED", entity_type="life_event", entity_id=event_id,
                     description=f"Life event approved: {event.event_type}")

    # Re-evaluate eligibility
    invalidate_eligibility(db, event.family_id, reason=f"life_event_{event_id}")
    evaluate_eligibility(db, event.family_id)

    db.flush()
    return event


def reject_life_event(db: Session, event_id: str, officer_id: int, review_notes: str = None) -> Optional[LifeEvent]:
    event = db.query(LifeEvent).filter(LifeEvent.event_id == event_id).first()
    if not event:
        return None

    event.status = "rejected"
    event.reviewed_by = officer_id
    event.reviewed_at = datetime.utcnow()
    event.review_notes = review_notes
    event.updated_at = datetime.utcnow()

    create_audit_log(db, actor_id=officer_id, action="LIFE_EVENT_REJECTED",
                     entity_type="life_event", entity_id=event_id,
                     description=f"Life event rejected: {event.event_type}")
    db.flush()
    return event


def get_life_events(db: Session, family_id: str = None, status: str = None,
                    event_type: str = None, limit: int = 50, offset: int = 0) -> List[LifeEvent]:
    q = db.query(LifeEvent)
    if family_id:
        q = q.filter(LifeEvent.family_id == family_id)
    if status:
        q = q.filter(LifeEvent.status == status)
    if event_type:
        q = q.filter(LifeEvent.event_type == event_type)
    return q.order_by(LifeEvent.created_at.desc()).offset(offset).limit(limit).all()


def _process_life_event(db: Session, event: LifeEvent) -> list:
    """Process an approved life event and update family/member records."""
    affected = []

    if event.event_type == "birth" or event.event_type == "member_added":
        # Add new member to the family
        family = db.query(Family).filter(Family.family_id == event.family_id).first()
        if family and event.new_member_name:
            member_count = db.query(Member).count()
            new_member = Member(
                member_id=f"GJ-MEM-{member_count + 1:08d}",
                family_id_fk=family.id,
                family_id_str=family.family_id,
                name=event.new_member_name,
                gender=event.new_member_gender,
                relationship_to_head=event.new_member_relationship or "child",
                is_active=True,
                verification_status="pending",
                source="life_event",
            )
            if event.new_member_dob:
                try:
                    new_member.dob = date.fromisoformat(event.new_member_dob)
                except (ValueError, TypeError):
                    pass
            db.add(new_member)
            affected = ["education_assistance", "food_assistance", "family_health"]

    elif event.event_type == "death":
        # Deactivate member
        if event.member_id:
            member = db.query(Member).filter(Member.member_id == event.member_id).first()
            if member:
                member.is_active = False
                member.updated_at = datetime.utcnow()
                affected = ["senior_assistance", "food_assistance", "family_health"]

    elif event.event_type == "address_change":
        family = db.query(Family).filter(Family.family_id == event.family_id).first()
        if family and event.description:
            family.address_line = event.description
            family.updated_at = datetime.utcnow()
            affected = ["housing_assistance", "food_assistance"]

    elif event.event_type == "income_change":
        family = db.query(Family).filter(Family.family_id == event.family_id).first()
        if family:
            extra = json.loads(event.event_data) if event.event_data else {}
            if extra.get("new_income_band"):
                family.income_band = extra["new_income_band"]
                family.updated_at = datetime.utcnow()
            affected = ["education_assistance", "housing_assistance", "food_assistance"]

    elif event.event_type == "marriage":
        affected = ["housing_assistance", "family_health"]

    elif event.event_type == "member_removed":
        if event.member_id:
            member = db.query(Member).filter(Member.member_id == event.member_id).first()
            if member:
                member.is_active = False
                member.updated_at = datetime.utcnow()
                affected = ["food_assistance", "family_health"]

    return affected
