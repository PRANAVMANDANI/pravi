import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.scheme import Scheme, SchemeRule
from app.models.family import Family
from app.models.member import Member
from app.models.eligibility import EligibilityResult


def get_all_schemes(db: Session, status: str = None) -> List[Scheme]:
    q = db.query(Scheme)
    if status:
        q = q.filter(Scheme.status == status)
    return q.all()


def get_scheme_by_id(db: Session, scheme_id: str) -> Optional[Scheme]:
    return db.query(Scheme).filter(Scheme.scheme_id == scheme_id).first()


def get_scheme_rules(db: Session, scheme_id: int) -> List[SchemeRule]:
    return db.query(SchemeRule).filter(SchemeRule.scheme_id == scheme_id, SchemeRule.is_active == True).all()


def evaluate_eligibility(db: Session, family_id: str, scheme_id: str = None) -> List[Dict[str, Any]]:
    """Evaluate eligibility for a family across one or all schemes."""
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        return []

    members = db.query(Member).filter(Member.family_id_str == family_id, Member.is_active == True).all()

    if scheme_id:
        schemes = [db.query(Scheme).filter(Scheme.scheme_id == scheme_id, Scheme.status == "active").first()]
        schemes = [s for s in schemes if s]
    else:
        schemes = db.query(Scheme).filter(Scheme.status == "active").all()

    results = []
    for scheme in schemes:
        result = _evaluate_scheme(db, family, members, scheme)
        results.append(result)
        _save_eligibility_result(db, family_id, scheme, result)

    db.commit()
    return results


def _evaluate_scheme(db: Session, family: Family, members: List[Member], scheme: Scheme) -> Dict[str, Any]:
    """Evaluate a single scheme against a family."""
    rules = get_scheme_rules(db, scheme.id)
    if not rules:
        return {
            "scheme_id": scheme.scheme_id,
            "scheme_name": scheme.name,
            "status": "eligible",
            "matched_rules": [],
            "failed_rules": [],
            "missing_data": [],
            "explanation": "No rules configured — eligible by default",
            "rule_version": 1,
        }

    matched = []
    failed = []
    missing = []

    for rule in rules:
        eval_result = _evaluate_rule(rule, family, members)
        if eval_result["status"] == "matched":
            matched.append(eval_result)
        elif eval_result["status"] == "failed":
            failed.append(eval_result)
        elif eval_result["status"] == "missing":
            missing.append(eval_result)

    if missing:
        status = "needs_verification"
        explanation = f"Missing data for {len(missing)} rule(s). Verification required."
    elif failed:
        status = "not_eligible"
        fail_reasons = "; ".join([f["description"] for f in failed])
        explanation = f"Not eligible: {fail_reasons}"
    else:
        status = "eligible"
        explanation = f"All {len(matched)} eligibility criteria met."

    return {
        "scheme_id": scheme.scheme_id,
        "scheme_name": scheme.name,
        "status": status,
        "matched_rules": matched,
        "failed_rules": failed,
        "missing_data": missing,
        "explanation": explanation,
        "rule_version": rules[0].rule_version if rules else 1,
    }


def _evaluate_rule(rule: SchemeRule, family: Family, members: List[Member]) -> Dict[str, Any]:
    """Evaluate a single rule against family/member data."""
    field = rule.field
    operator = rule.operator
    value = rule.value
    value_type = rule.value_type
    entity = rule.entity

    # Get the actual value from the entity
    if entity == "family":
        actual_value = _get_family_field(family, field, members)
    else:
        # Member-level: check if ANY active member satisfies
        actual_value = _get_best_member_field(members, field)

    if actual_value is None:
        return {
            "rule_id": rule.id,
            "field": field,
            "operator": operator,
            "expected": value,
            "actual": None,
            "status": "missing",
            "description": rule.description or f"Data missing: {field}",
        }

    # Type casting
    try:
        if value_type == "number":
            compare_value = float(value)
            actual_compare = float(actual_value)
        elif value_type == "list":
            compare_value = [v.strip() for v in value.split(",")]
            actual_compare = str(actual_value)
        else:
            compare_value = value
            actual_compare = str(actual_value)
    except (ValueError, TypeError):
        return {
            "rule_id": rule.id, "field": field, "operator": operator,
            "expected": value, "actual": str(actual_value),
            "status": "failed", "description": rule.description or f"Type mismatch for {field}",
        }

    # Evaluate
    result = False
    if operator == "=":
        result = str(actual_compare).lower() == str(compare_value).lower()
    elif operator == "!=":
        result = str(actual_compare).lower() != str(compare_value).lower()
    elif operator == ">":
        result = actual_compare > compare_value
    elif operator == ">=":
        result = actual_compare >= compare_value
    elif operator == "<":
        result = actual_compare < compare_value
    elif operator == "<=":
        result = actual_compare <= compare_value
    elif operator == "IN":
        result = str(actual_compare).lower() in [v.lower() for v in compare_value]
    elif operator == "NOT_IN":
        result = str(actual_compare).lower() not in [v.lower() for v in compare_value]
    elif operator == "EXISTS":
        result = actual_value is not None and str(actual_value).strip() != ""

    return {
        "rule_id": rule.id,
        "field": field,
        "operator": operator,
        "expected": value,
        "actual": str(actual_value),
        "status": "matched" if result else "failed",
        "description": rule.description or f"{field} {operator} {value}",
    }


def _get_family_field(family: Family, field: str, members: List[Member]):
    """Extract a field value from family context."""
    mapping = {
        "family_income_band": family.income_band,
        "income_band": family.income_band,
        "district": family.district,
        "category": family.category,
        "verification_status": family.verification_status,
        "member_count": len([m for m in members if m.is_active]),
        "family_status": family.status,
        "ration_card_type": family.ration_card_type,
    }
    return mapping.get(field, getattr(family, field, None))


def _get_best_member_field(members: List[Member], field: str):
    """For member-level rules, get the best matching value across active members."""
    active = [m for m in members if m.is_active]
    if not active:
        return None

    if field in ("member_age", "age"):
        ages = [m.age for m in active if m.age is not None]
        return min(ages) if ages else None  # Return youngest for student schemes or oldest for senior
    elif field == "max_age":
        ages = [m.age for m in active if m.age is not None]
        return max(ages) if ages else None
    elif field == "min_age":
        ages = [m.age for m in active if m.age is not None]
        return min(ages) if ages else None
    elif field == "has_senior":
        return "yes" if any(m.age and m.age >= 60 for m in active) else "no"
    elif field == "has_child":
        return "yes" if any(m.age and m.age < 18 for m in active) else "no"
    elif field == "has_student":
        return "yes" if any(m.age and 6 <= m.age <= 25 for m in active) else "no"
    elif field == "gender":
        genders = set(m.gender for m in active if m.gender)
        return ",".join(genders)
    elif field == "member_occupation":
        occs = [m.occupation for m in active if m.occupation]
        return occs[0] if occs else None
    elif field == "member_status":
        return "active" if active else "inactive"

    # Generic fallback
    for m in active:
        val = getattr(m, field, None)
        if val is not None:
            return val
    return None


def _save_eligibility_result(db: Session, family_id: str, scheme: Scheme, result: Dict):
    """Save or update eligibility result in DB."""
    existing = db.query(EligibilityResult).filter(
        EligibilityResult.family_id == family_id,
        EligibilityResult.scheme_id == scheme.scheme_id
    ).first()

    data = {
        "status": result["status"],
        "matched_rules": json.dumps(result["matched_rules"]),
        "failed_rules": json.dumps(result["failed_rules"]),
        "missing_data": json.dumps(result["missing_data"]),
        "explanation": result["explanation"],
        "rule_version": result["rule_version"],
        "is_stale": False,
        "stale_reason": None,
        "evaluated_at": datetime.utcnow(),
    }

    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
    else:
        existing = EligibilityResult(
            family_id=family_id,
            scheme_id=scheme.scheme_id,
            **data
        )
        db.add(existing)
    db.flush()


def invalidate_eligibility(db: Session, family_id: str, reason: str = "data_changed"):
    """Mark all eligibility results for a family as stale."""
    results = db.query(EligibilityResult).filter(EligibilityResult.family_id == family_id).all()
    for r in results:
        r.is_stale = True
        r.stale_reason = reason
    db.flush()


def get_family_eligibility(db: Session, family_id: str) -> List[EligibilityResult]:
    return db.query(EligibilityResult).filter(EligibilityResult.family_id == family_id).all()
