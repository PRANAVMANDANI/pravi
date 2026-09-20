from functools import wraps
from fastapi import HTTPException, status
from typing import List

# Role constants
ROLE_CITIZEN = "citizen"
ROLE_VERIFICATION_OFFICER = "verification_officer"
ROLE_SCHEME_OFFICER = "scheme_officer"
ROLE_DEPARTMENT_OFFICER = "department_officer"
ROLE_STATE_ADMIN = "state_admin"
ROLE_ASSISTED_OPERATOR = "assisted_operator"

ALL_ROLES = [ROLE_CITIZEN, ROLE_VERIFICATION_OFFICER, ROLE_SCHEME_OFFICER,
             ROLE_DEPARTMENT_OFFICER, ROLE_STATE_ADMIN, ROLE_ASSISTED_OPERATOR]

GOVERNMENT_ROLES = [ROLE_VERIFICATION_OFFICER, ROLE_SCHEME_OFFICER,
                    ROLE_DEPARTMENT_OFFICER, ROLE_STATE_ADMIN, ROLE_ASSISTED_OPERATOR]

# Department field access policies
DEPARTMENT_FIELD_ACCESS = {
    "food_department": {
        "family": ["family_id", "status", "address", "district", "taluka", "village_city", "verification_status", "member_count"],
        "member": ["member_id", "name", "dob", "gender", "relationship", "is_active"],
    },
    "education_department": {
        "family": ["family_id", "status", "district", "taluka", "village_city", "income_band", "verification_status"],
        "member": ["member_id", "name", "dob", "gender", "occupation", "relationship", "is_active"],
    },
    "health_department": {
        "family": ["family_id", "status", "address", "district", "taluka", "village_city", "verification_status", "member_count"],
        "member": ["member_id", "name", "dob", "gender", "relationship", "is_active"],
    },
    "housing_department": {
        "family": ["family_id", "status", "address", "district", "taluka", "village_city", "income_band", "verification_status", "member_count"],
        "member": ["member_id", "name", "dob", "gender", "occupation", "income_band", "relationship", "is_active"],
    },
    "social_justice_department": {
        "family": ["family_id", "status", "address", "district", "taluka", "village_city", "income_band", "category", "verification_status", "member_count"],
        "member": ["member_id", "name", "dob", "gender", "occupation", "income_band", "category", "relationship", "is_active"],
    },
}


def require_roles(allowed_roles: List[str]):
    """Dependency that checks if the current user has one of the allowed roles."""
    def role_checker(current_user=None):
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to access this resource. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def check_role(user, allowed_roles: List[str]):
    """Inline role check."""
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )


def filter_fields_for_department(data: dict, entity_type: str, department_code: str) -> dict:
    """Filter entity fields based on department access policy."""
    allowed = DEPARTMENT_FIELD_ACCESS.get(department_code, {}).get(entity_type, [])
    if not allowed:
        return {}
    return {k: v for k, v in data.items() if k in allowed}
