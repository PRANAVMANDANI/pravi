import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.family import Family
from app.models.member import Member
from app.models.change_request import ChangeRequest
from app.models.life_event import LifeEvent
from app.models.benefit import BenefitLedger
from app.models.eligibility import EligibilityResult
from app.models.audit import AuditLog
from app.models.identity import IdentityMatch


def get_family_by_id(db: Session, family_id: str) -> Optional[Family]:
    return db.query(Family).filter(Family.family_id == family_id).first()


def get_family_by_pk(db: Session, pk: int) -> Optional[Family]:
    return db.query(Family).filter(Family.id == pk).first()


def search_families(db: Session, query: str = None, district: str = None, taluka: str = None,
                    village: str = None, status: str = None, verification: str = None,
                    limit: int = 50, offset: int = 0) -> List[Family]:
    q = db.query(Family)
    if query:
        q = q.outerjoin(Member, Member.family_id_fk == Family.id)
        q = q.filter(or_(
            Family.family_id.ilike(f"%{query}%"),
            Member.member_id.ilike(f"%{query}%"),
            Member.name.ilike(f"%{query}%"),
        )).distinct()
    if district:
        q = q.filter(Family.district == district)
    if taluka:
        q = q.filter(Family.taluka == taluka)
    if village:
        q = q.filter(Family.village_city == village)
    if status:
        q = q.filter(Family.status == status)
    if verification:
        q = q.filter(Family.verification_status == verification)
    return q.order_by(Family.created_at.desc()).offset(offset).limit(limit).all()


def count_families(db: Session, district: str = None, status: str = None, verification: str = None) -> int:
    q = db.query(Family)
    if district:
        q = q.filter(Family.district == district)
    if status:
        q = q.filter(Family.status == status)
    if verification:
        q = q.filter(Family.verification_status == verification)
    return q.count()


def get_family_members(db: Session, family_id: str) -> List[Member]:
    return db.query(Member).filter(Member.family_id_str == family_id).all()


def get_active_members(db: Session, family_id: str) -> List[Member]:
    return db.query(Member).filter(Member.family_id_str == family_id, Member.is_active == True).all()


def get_member_by_id(db: Session, member_id: str) -> Optional[Member]:
    return db.query(Member).filter(Member.member_id == member_id).first()


def get_family_360(db: Session, family_id: str) -> Dict[str, Any]:
    """Get complete family 360 view including members, schemes, benefits, events, requests, audit."""
    family = get_family_by_id(db, family_id)
    if not family:
        return None

    members = get_family_members(db, family_id)
    benefits = db.query(BenefitLedger).filter(BenefitLedger.family_id == family_id).all()
    eligibility = db.query(EligibilityResult).filter(EligibilityResult.family_id == family_id).all()
    change_requests = db.query(ChangeRequest).filter(ChangeRequest.family_id == family_id).order_by(ChangeRequest.created_at.desc()).limit(20).all()
    life_events = db.query(LifeEvent).filter(LifeEvent.family_id == family_id).order_by(LifeEvent.created_at.desc()).limit(20).all()
    audit = db.query(AuditLog).filter(AuditLog.entity_id == family_id).order_by(AuditLog.created_at.desc()).limit(30).all()
    matches = db.query(IdentityMatch).filter(
        or_(IdentityMatch.record_a_id == family_id, IdentityMatch.record_b_id == family_id),
        IdentityMatch.status == "pending"
    ).all()

    # Data quality issues
    quality_issues = compute_data_quality(family, members)

    return {
        "family": family,
        "members": members,
        "benefits": benefits,
        "eligibility": eligibility,
        "change_requests": change_requests,
        "life_events": life_events,
        "audit_logs": audit,
        "duplicate_matches": matches,
        "data_quality": quality_issues,
    }


def compute_data_quality(family: Family, members: List[Member]) -> Dict[str, Any]:
    """Compute data quality score and issues for a family."""
    issues = []
    total_checks = 0
    passed_checks = 0

    # Family-level checks
    total_checks += 5
    if family.address_line:
        passed_checks += 1
    else:
        issues.append({"field": "address", "issue": "Missing address", "severity": "high"})

    if family.district:
        passed_checks += 1
    else:
        issues.append({"field": "district", "issue": "Missing district", "severity": "high"})

    if family.income_band:
        passed_checks += 1
    else:
        issues.append({"field": "income_band", "issue": "Missing income band", "severity": "medium"})

    if family.verification_status == "verified":
        passed_checks += 1
    else:
        issues.append({"field": "verification", "issue": "Family not verified", "severity": "medium"})

    if any(m.is_head for m in members):
        passed_checks += 1
    else:
        issues.append({"field": "head", "issue": "No head of household designated", "severity": "high"})

    # Member-level checks
    active_members = [m for m in members if m.is_active]
    for m in active_members:
        total_checks += 3
        if m.dob:
            passed_checks += 1
        else:
            issues.append({"field": f"member_{m.member_id}_dob", "issue": f"Missing DOB for {m.name}", "severity": "medium"})
        if m.gender:
            passed_checks += 1
        else:
            issues.append({"field": f"member_{m.member_id}_gender", "issue": f"Missing gender for {m.name}", "severity": "low"})
        if m.relationship_to_head:
            passed_checks += 1
        else:
            issues.append({"field": f"member_{m.member_id}_relationship", "issue": f"Missing relationship for {m.name}", "severity": "medium"})

    score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    return {
        "score": round(score, 1),
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "issues": issues,
        "issue_count": len(issues),
    }


def create_family(db: Session, family_data: dict) -> Family:
    count = db.query(Family).count()
    family_id = f"GJ-FAM-2026-{count + 1:08d}"
    family = Family(family_id=family_id, **family_data)
    db.add(family)
    db.flush()
    return family


def create_member(db: Session, family: Family, member_data: dict) -> Member:
    count = db.query(Member).count()
    member_id = f"GJ-MEM-{count + 1:08d}"
    member = Member(
        member_id=member_id,
        family_id_fk=family.id,
        family_id_str=family.family_id,
        **member_data
    )
    db.add(member)
    db.flush()
    return member


def update_family(db: Session, family: Family, updates: dict) -> Family:
    for key, value in updates.items():
        if hasattr(family, key):
            setattr(family, key, value)
    family.updated_at = datetime.utcnow()
    db.flush()
    return family


def update_member(db: Session, member: Member, updates: dict) -> Member:
    for key, value in updates.items():
        if hasattr(member, key):
            setattr(member, key, value)
    member.updated_at = datetime.utcnow()
    db.flush()
    return member
