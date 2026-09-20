from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.user import User
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    data: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    family_id: str | None = None
    member_id: str | None = None
    department_id: int | None = None


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    user.last_login = datetime.utcnow()

    create_audit_log(db, actor_id=user.id, actor_name=user.full_name, actor_role=user.role,
                     action="LOGIN", description=f"User login: {user.username}")
    db.commit()

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "family_id": user.family_id,
                "member_id": user.member_id,
                "department_id": user.department_id,
            }
        }
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    dept_name = None
    if current_user.department:
        dept_name = current_user.department.name
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "family_id": current_user.family_id,
            "member_id": current_user.member_id,
            "department_id": current_user.department_id,
            "department_name": dept_name,
        }
    }
