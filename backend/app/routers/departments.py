from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES, ROLE_DEPARTMENT_OFFICER
from app.models.user import User
from app.services.access_control_service import get_departments, request_family_data, get_access_logs

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])


class DataAccessRequestBody(BaseModel):
    family_id: str
    purpose: str


@router.get("")
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    depts = get_departments(db)
    return {
        "success": True,
        "data": [{
            "id": d.id, "code": d.code, "name": d.name,
            "description": d.description, "is_active": d.is_active,
        } for d in depts]
    }


@router.post("/data-access")
def access_data(data: DataAccessRequestBody, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    dept_code = None
    if current_user.department:
        dept_code = current_user.department.code
    elif current_user.department_id:
        from app.models.department import Department
        dept = db.query(Department).filter(Department.id == current_user.department_id).first()
        dept_code = dept.code if dept else "food_department"
    else:
        dept_code = "food_department"  # Default for demo

    result = request_family_data(db, current_user.id, dept_code, data.family_id, data.purpose)
    db.commit()
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return {"success": True, "data": result}


@router.get("/data-access/logs")
def list_access_logs(family_id: Optional[str] = None, department_code: Optional[str] = None,
                     limit: int = 50, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)
    logs = get_access_logs(db, family_id, department_code, limit)
    return {
        "success": True,
        "data": [{
            "access_id": l.access_id, "department_code": l.department_code,
            "family_id": l.family_id, "purpose": l.purpose,
            "status": l.status, "fields_returned": l.fields_returned,
            "created_at": str(l.created_at) if l.created_at else None,
        } for l in logs]
    }
