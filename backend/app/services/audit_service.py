import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


_audit_counter = 0


def _next_audit_id():
    global _audit_counter
    _audit_counter += 1
    return f"AUD-{_audit_counter:06d}"


def create_audit_log(db: Session, actor_id: int = None, actor_name: str = None, actor_role: str = None,
                     department: str = None, action: str = "", entity_type: str = None, entity_id: str = None,
                     description: str = None, reason: str = None, before_snapshot: dict = None,
                     after_snapshot: dict = None, ip_address: str = None) -> AuditLog:
    # Get next ID from DB
    max_id = db.query(AuditLog).count()
    audit_id = f"AUD-{max_id + 1:06d}"

    log = AuditLog(
        audit_id=audit_id,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        department=department,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        reason=reason,
        before_snapshot=json.dumps(before_snapshot) if before_snapshot else None,
        after_snapshot=json.dumps(after_snapshot) if after_snapshot else None,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    return log


def get_audit_logs(db: Session, entity_type: str = None, entity_id: str = None,
                   action: str = None, actor_id: int = None, limit: int = 50, offset: int = 0):
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


def get_family_audit(db: Session, family_id: str, limit: int = 50):
    return db.query(AuditLog).filter(
        AuditLog.entity_id == family_id
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()
