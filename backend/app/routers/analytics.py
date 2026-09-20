from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import check_role, GOVERNMENT_ROLES
from app.models.user import User
from app.models.family import Family
from app.models.member import Member
from app.models.change_request import ChangeRequest
from app.models.life_event import LifeEvent
from app.models.benefit import BenefitLedger
from app.models.identity import IdentityMatch
from app.models.scheme import Scheme
from app.models.eligibility import EligibilityResult
from app.models.notification import Notification

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("")
def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_role(current_user, GOVERNMENT_ROLES)

    total_families = db.query(Family).count()
    verified_families = db.query(Family).filter(Family.verification_status == "verified").count()
    pending_verification = db.query(Family).filter(Family.verification_status == "pending").count()
    total_members = db.query(Member).filter(Member.is_active == True).count()

    total_requests = db.query(ChangeRequest).count()
    pending_requests = db.query(ChangeRequest).filter(ChangeRequest.status.in_(["submitted", "under_review"])).count()
    approved_requests = db.query(ChangeRequest).filter(ChangeRequest.status == "approved").count()
    rejected_requests = db.query(ChangeRequest).filter(ChangeRequest.status == "rejected").count()

    duplicate_matches = db.query(IdentityMatch).filter(IdentityMatch.status == "pending").count()
    active_benefits = db.query(BenefitLedger).filter(BenefitLedger.status == "active").count()
    total_life_events = db.query(LifeEvent).count()
    pending_events = db.query(LifeEvent).filter(LifeEvent.status == "submitted").count()

    total_schemes = db.query(Scheme).filter(Scheme.status == "active").count()

    # District distribution
    district_data = db.query(Family.district, func.count(Family.id)).group_by(Family.district).all()
    districts = [{"district": d[0] or "Unknown", "count": d[1]} for d in district_data]

    # Verification distribution
    verification_data = db.query(Family.verification_status, func.count(Family.id)).group_by(Family.verification_status).all()
    verification_dist = [{"status": v[0], "count": v[1]} for v in verification_data]

    # Request type distribution
    request_type_data = db.query(ChangeRequest.request_type, func.count(ChangeRequest.id)).group_by(ChangeRequest.request_type).all()
    request_types = [{"type": r[0], "count": r[1]} for r in request_type_data]

    # Income band distribution
    income_data = db.query(Family.income_band, func.count(Family.id)).group_by(Family.income_band).all()
    income_dist = [{"band": i[0] or "Unknown", "count": i[1]} for i in income_data]

    # Benefits by scheme
    benefit_scheme_data = db.query(BenefitLedger.scheme_id, func.count(BenefitLedger.id)).group_by(BenefitLedger.scheme_id).all()
    benefits_by_scheme = [{"scheme_id": b[0], "count": b[1]} for b in benefit_scheme_data]

    # Data quality issues
    low_quality = db.query(Family).filter(Family.data_quality_score < 70).count()

    return {
        "success": True,
        "data": {
            "overview": {
                "total_families": total_families,
                "verified_families": verified_families,
                "pending_verification": pending_verification,
                "total_members": total_members,
                "total_schemes": total_schemes,
                "active_benefits": active_benefits,
                "total_life_events": total_life_events,
                "pending_events": pending_events,
                "duplicate_matches": duplicate_matches,
                "data_quality_issues": low_quality,
            },
            "requests": {
                "total": total_requests,
                "pending": pending_requests,
                "approved": approved_requests,
                "rejected": rejected_requests,
            },
            "charts": {
                "families_by_district": districts,
                "verification_distribution": verification_dist,
                "request_types": request_types,
                "income_distribution": income_dist,
                "benefits_by_scheme": benefits_by_scheme,
            }
        }
    }
