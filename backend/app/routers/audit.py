from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.audit_service import get_audit_logs

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("")
def list_audit_logs(entity_type: Optional[str] = None, entity_id: Optional[str] = None,
                    action: Optional[str] = None, limit: int = 50, offset: int = 0,
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    logs = get_audit_logs(db, entity_type, entity_id, action, limit=limit, offset=offset)
    return {
        "success": True,
        "data": [{
            "audit_id": l.audit_id, "actor_id": l.actor_id, "actor_name": l.actor_name,
            "actor_role": l.actor_role, "department": l.department,
            "action": l.action, "entity_type": l.entity_type, "entity_id": l.entity_id,
            "description": l.description, "reason": l.reason,
            "created_at": str(l.created_at) if l.created_at else None,
        } for l in logs]
    }
