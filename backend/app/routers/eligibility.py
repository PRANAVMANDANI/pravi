from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.services.eligibility_service import evaluate_eligibility, get_family_eligibility

router = APIRouter(prefix="/api/v1/eligibility", tags=["Eligibility"])


@router.get("/{family_id}")
def get_eligibility(family_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="Access denied")

    results = get_family_eligibility(db, family_id)
    if not results:
        # Evaluate on-the-fly
        results_data = evaluate_eligibility(db, family_id)
        return {"success": True, "data": results_data}

    import json
    return {
        "success": True,
        "data": [{
            "scheme_id": r.scheme_id, "status": r.status,
            "explanation": r.explanation, "is_stale": r.is_stale,
            "matched_rules": json.loads(r.matched_rules) if r.matched_rules else [],
            "failed_rules": json.loads(r.failed_rules) if r.failed_rules else [],
            "missing_data": json.loads(r.missing_data) if r.missing_data else [],
            "evaluated_at": str(r.evaluated_at) if r.evaluated_at else None,
        } for r in results]
    }


@router.post("/{family_id}/evaluate")
def evaluate(family_id: str, scheme_id: Optional[str] = None,
             db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "citizen" and current_user.family_id != family_id:
        raise HTTPException(status_code=403, detail="Access denied")

    results = evaluate_eligibility(db, family_id, scheme_id)
    return {"success": True, "data": results}
