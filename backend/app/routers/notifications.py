from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(is_read: Optional[bool] = None, limit: int = 50,
                       db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if is_read is not None:
        q = q.filter(Notification.is_read == is_read)
    notifications = q.order_by(Notification.created_at.desc()).limit(limit).all()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).count()

    return {
        "success": True,
        "data": {
            "notifications": [{
                "notification_id": n.notification_id, "title": n.title, "message": n.message,
                "notification_type": n.notification_type,
                "entity_type": n.entity_type, "entity_id": n.entity_id,
                "is_read": n.is_read,
                "created_at": str(n.created_at) if n.created_at else None,
            } for n in notifications],
            "unread_count": unread_count,
        }
    }


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if n:
        n.is_read = True
        n.read_at = datetime.utcnow()
        db.commit()
    return {"success": True}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"success": True}
