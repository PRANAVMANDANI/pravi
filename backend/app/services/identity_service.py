import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from app.models.member import Member
from app.models.family import Family
from app.models.identity import IdentityMatch, IdentityMergeHistory
from app.services.audit_service import create_audit_log


def find_potential_matches(db: Session, member_id: str = None, name: str = None,
                           dob: str = None, gender: str = None, district: str = None) -> List[Dict[str, Any]]:
    """Find potential duplicate members using multi-stage matching."""
    if member_id:
        target = db.query(Member).filter(Member.member_id == member_id).first()
        if not target:
            return []
        name = target.name
        dob = str(target.dob) if target.dob else None
        gender = target.gender

    if not name:
        return []

    # Get candidates — limit search scope
    candidates = db.query(Member).filter(Member.is_active == True)
    if district:
        candidates = candidates.join(Family, Family.id == Member.family_id_fk).filter(Family.district == district)
    candidates = candidates.limit(500).all()

    matches = []
    for candidate in candidates:
        if member_id and candidate.member_id == member_id:
            continue

        score, reasons = _compute_match_score(name, dob, gender, candidate)
        if score >= 70:
            matches.append({
                "member_id": candidate.member_id,
                "family_id": candidate.family_id_str,
                "name": candidate.name,
                "dob": str(candidate.dob) if candidate.dob else None,
                "gender": candidate.gender,
                "district": None,
                "confidence_score": round(score, 1),
                "match_reasons": reasons,
                "match_type": "exact" if score >= 95 else "deterministic" if score >= 85 else "fuzzy",
            })

    # Sort by confidence
    matches.sort(key=lambda x: x["confidence_score"], reverse=True)
    return matches[:20]


def _compute_match_score(name: str, dob: str, gender: str, candidate: Member) -> tuple:
    """Compute multi-factor match confidence score."""
    score = 0
    reasons = []
    weights = {"name": 40, "dob": 25, "gender": 15, "aadhaar": 20}
    total_weight = 0

    # Name similarity (fuzzy)
    if name and candidate.name:
        name_score = fuzz.token_sort_ratio(name.lower(), candidate.name.lower())
        weighted = (name_score / 100) * weights["name"]
        score += weighted
        total_weight += weights["name"]
        if name_score >= 80:
            reasons.append(f"Name similarity: {name_score}%")

    # DOB match
    if dob and candidate.dob:
        total_weight += weights["dob"]
        if str(candidate.dob) == dob:
            score += weights["dob"]
            reasons.append("DOB exact match")
        else:
            # Partial DOB match (year only)
            try:
                if str(candidate.dob)[:4] == dob[:4]:
                    score += weights["dob"] * 0.5
                    reasons.append("DOB year match")
            except (IndexError, TypeError):
                pass

    # Gender match
    if gender and candidate.gender:
        total_weight += weights["gender"]
        if gender.lower() == candidate.gender.lower():
            score += weights["gender"]
            reasons.append("Gender match")

    # Normalize score
    if total_weight > 0:
        normalized = (score / total_weight) * 100
    else:
        normalized = 0

    return normalized, reasons


def create_identity_match(db: Session, record_a: dict, record_b: dict,
                          confidence: float, reasons: list, match_type: str) -> IdentityMatch:
    count = db.query(IdentityMatch).count()
    match = IdentityMatch(
        match_id=f"MTH-{count + 1:06d}",
        record_a_type=record_a.get("type", "member"),
        record_a_id=record_a["id"],
        record_a_name=record_a.get("name"),
        record_a_source=record_a.get("source"),
        record_b_type=record_b.get("type", "member"),
        record_b_id=record_b["id"],
        record_b_name=record_b.get("name"),
        record_b_source=record_b.get("source"),
        confidence_score=confidence,
        match_reasons=json.dumps(reasons),
        match_type=match_type,
        status="pending",
    )
    db.add(match)
    db.flush()
    return match


def get_pending_matches(db: Session, limit: int = 50) -> List[IdentityMatch]:
    return db.query(IdentityMatch).filter(
        IdentityMatch.status == "pending"
    ).order_by(IdentityMatch.confidence_score.desc()).limit(limit).all()


def confirm_match(db: Session, match_id: str, officer_id: int, officer_name: str) -> Optional[IdentityMatch]:
    match = db.query(IdentityMatch).filter(IdentityMatch.match_id == match_id).first()
    if not match:
        return None
    match.status = "confirmed"
    match.reviewed_by = officer_id
    match.reviewed_at = datetime.utcnow()

    create_audit_log(db, actor_id=officer_id, actor_name=officer_name,
                     action="DUPLICATE_CONFIRMED", entity_type="identity_match", entity_id=match_id,
                     description=f"Duplicate confirmed: {match.record_a_name} ↔ {match.record_b_name}")
    db.flush()
    return match


def reject_match(db: Session, match_id: str, officer_id: int, notes: str = None) -> Optional[IdentityMatch]:
    match = db.query(IdentityMatch).filter(IdentityMatch.match_id == match_id).first()
    if not match:
        return None
    match.status = "rejected"
    match.reviewed_by = officer_id
    match.reviewed_at = datetime.utcnow()
    match.review_notes = notes

    create_audit_log(db, actor_id=officer_id, action="DUPLICATE_REJECTED",
                     entity_type="identity_match", entity_id=match_id,
                     description=f"Duplicate rejected: {match.record_a_name} ↔ {match.record_b_name}")
    db.flush()
    return match


def merge_records(db: Session, primary_id: str, secondary_id: str, entity_type: str,
                  officer_id: int, officer_name: str, reason: str = None) -> IdentityMergeHistory:
    count = db.query(IdentityMergeHistory).count()
    merge = IdentityMergeHistory(
        merge_id=f"MRG-{count + 1:06d}",
        action="merge",
        primary_id=primary_id,
        secondary_id=secondary_id,
        entity_type=entity_type,
        reason=reason,
        performed_by=officer_id,
    )
    db.add(merge)

    # If merging families, move members from secondary to primary
    if entity_type == "family":
        secondary_family = db.query(Family).filter(Family.family_id == secondary_id).first()
        if secondary_family:
            secondary_family.status = "merged"
            members = db.query(Member).filter(Member.family_id_str == secondary_id).all()
            primary_family = db.query(Family).filter(Family.family_id == primary_id).first()
            if primary_family:
                for m in members:
                    m.family_id_fk = primary_family.id
                    m.family_id_str = primary_id

    create_audit_log(db, actor_id=officer_id, actor_name=officer_name,
                     action="FAMILY_MERGED", entity_type=entity_type, entity_id=primary_id,
                     description=f"Merged {secondary_id} into {primary_id}", reason=reason)

    db.flush()
    return merge
