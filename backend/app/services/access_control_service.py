import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.department import Department, DataAccessRequest
from app.models.family import Family
from app.models.member import Member
from app.core.permissions import DEPARTMENT_FIELD_ACCESS, filter_fields_for_department
from app.services.audit_service import create_audit_log


def get_departments(db: Session):
    return db.query(Department).filter(Department.is_active == True).all()


def get_department_by_code(db: Session, code: str) -> Optional[Department]:
    return db.query(Department).filter(Department.code == code).first()


def request_family_data(db: Session, user_id: int, department_code: str,
                        family_id: str, purpose: str) -> Dict[str, Any]:
    """Process a department's data access request with field-level filtering."""
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        return {"error": "Family not found"}

    members = db.query(Member).filter(Member.family_id_str == family_id, Member.is_active == True).all()

    # Get allowed fields
    allowed_family = DEPARTMENT_FIELD_ACCESS.get(department_code, {}).get("family", [])
    allowed_member = DEPARTMENT_FIELD_ACCESS.get(department_code, {}).get("member", [])

    if not allowed_family and not allowed_member:
        # Log denied access
        count = db.query(DataAccessRequest).count()
        dar = DataAccessRequest(
            access_id=f"DAR-{count + 1:06d}",
            user_id=user_id,
            department_code=department_code,
            family_id=family_id,
            purpose=purpose,
            status="denied",
            denial_reason="Department has no configured access policy",
        )
        db.add(dar)
        db.flush()
        return {"error": "Access denied — department has no configured access policy"}

    # Build filtered response
    family_data = {}
    for field in allowed_family:
        if field == "member_count":
            family_data["member_count"] = len(members)
        elif hasattr(family, field):
            family_data[field] = getattr(family, field)

    members_data = []
    for m in members:
        md = {}
        for field in allowed_member:
            if hasattr(m, field):
                val = getattr(m, field)
                md[field] = str(val) if val is not None else None
        members_data.append(md)

    fields_returned = {"family_fields": allowed_family, "member_fields": allowed_member}

    # Log the access
    count = db.query(DataAccessRequest).count()
    dar = DataAccessRequest(
        access_id=f"DAR-{count + 1:06d}",
        user_id=user_id,
        department_code=department_code,
        family_id=family_id,
        purpose=purpose,
        fields_returned=json.dumps(fields_returned),
        status="completed",
    )
    db.add(dar)

    create_audit_log(db, actor_id=user_id, actor_role="department_officer",
                     department=department_code, action="DATA_ACCESSED",
                     entity_type="family", entity_id=family_id,
                     description=f"Department data access: {purpose}",
                     after_snapshot=fields_returned)

    db.flush()

    return {
        "family": family_data,
        "members": members_data,
        "access_id": dar.access_id,
        "department": department_code,
        "purpose": purpose,
        "fields_provided": fields_returned,
        "note": "MOCK GOVERNMENT INTEGRATION — Only permitted fields returned based on department access policy",
    }


def get_access_logs(db: Session, family_id: str = None, department_code: str = None,
                    limit: int = 50) -> list:
    q = db.query(DataAccessRequest)
    if family_id:
        q = q.filter(DataAccessRequest.family_id == family_id)
    if department_code:
        q = q.filter(DataAccessRequest.department_code == department_code)
    return q.order_by(DataAccessRequest.created_at.desc()).limit(limit).all()
