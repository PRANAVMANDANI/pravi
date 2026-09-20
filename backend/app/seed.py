"""
Pravi ID — Seed Script
Generates synthetic demo data: 100+ families, 300+ members, schemes, benefits, requests, etc.
All data is SYNTHETIC and clearly labeled as DEMO.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
import random
import json
import hashlib
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.family import Family
from app.models.member import Member
from app.models.department import Department
from app.models.scheme import Scheme, SchemeRule
from app.models.benefit import BenefitLedger, Application
from app.models.change_request import ChangeRequest
from app.models.life_event import LifeEvent
from app.models.identity import IdentityMatch
from app.models.eligibility import EligibilityResult
from app.models.audit import AuditLog
from app.models.notification import Notification

# Synthetic data pools
DISTRICTS = ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"]
TALUKAS = {
    "Ahmedabad": ["Daskroi", "Dholka", "Sanand", "Bavla", "Dhandhuka"],
    "Surat": ["Chorasi", "Kamrej", "Palsana", "Olpad", "Mandvi"],
    "Vadodara": ["Padra", "Karjan", "Savli", "Waghodia", "Dabhoi"],
    "Rajkot": ["Lodhika", "Jasdan", "Gondal", "Dhoraji", "Jetpur"],
    "Gandhinagar": ["Kalol", "Mansa", "Dehgam", "Gandhinagar", "Kadi"],
}
VILLAGES = ["Rampur", "Laxminagar", "Shantinagar", "Vijaynagar", "Anandnagar",
            "Surajpur", "Chandrapur", "Ganeshpura", "Navsari", "Devnagar",
            "Krishnanagar", "Mohanpura", "Rajnagar", "Lakshmipur", "Sitapur"]
FIRST_NAMES_M = ["Rajesh", "Amit", "Suresh", "Mahesh", "Ramesh", "Vijay", "Arun", "Sanjay",
                  "Prakash", "Kiran", "Nitin", "Ajay", "Deepak", "Manish", "Rohit", "Anand",
                  "Hari", "Mohan", "Govind", "Bharat", "Dinesh", "Kamal", "Pankaj", "Naresh"]
FIRST_NAMES_F = ["Meena", "Sunita", "Kavita", "Priya", "Anita", "Geeta", "Sita", "Radha",
                  "Laxmi", "Pushpa", "Neha", "Asha", "Rekha", "Savita", "Kanta", "Ritu",
                  "Sneha", "Pooja", "Divya", "Jaya", "Nirmala", "Shanti", "Usha", "Kamala"]
FIRST_NAMES_CHILD_M = ["Aarav", "Vihaan", "Arjun", "Reyan", "Vivaan", "Aditya", "Rudra", "Krishna",
                        "Dev", "Ishaan", "Aryan", "Kabir", "Dhruv", "Shaurya", "Yash", "Om"]
FIRST_NAMES_CHILD_F = ["Kavya", "Ananya", "Diya", "Saanvi", "Aadhya", "Prisha", "Myra", "Anika",
                        "Riya", "Nisha", "Isha", "Tanvi", "Kiara", "Avni", "Navya", "Mira"]
LAST_NAMES = ["Patel", "Shah", "Modi", "Desai", "Mehta", "Joshi", "Trivedi", "Pandya",
              "Bhatt", "Parikh", "Chauhan", "Solanki", "Rathod", "Thakor", "Makwana",
              "Vaghela", "Raval", "Nayak", "Gajjar", "Darji", "Suthar", "Mistry"]
OCCUPATIONS = ["Farming", "Business", "Government Service", "Private Service", "Daily Wages",
               "Teaching", "Healthcare", "Self-employed", "Retired", "Student", "Homemaker"]
INCOME_BANDS = ["BPL", "BPL", "BPL", "EWS", "EWS", "LIG", "LIG", "MIG", "APL", "APL"]
CATEGORIES = ["General", "OBC", "SC", "ST", "General", "OBC", "General"]
RATION_TYPES = ["AAY", "BPL", "APL", "Antyodaya"]


def generate_aadhaar_hash():
    num = "".join([str(random.randint(0, 9)) for _ in range(12)])
    return hashlib.sha256(num.encode()).hexdigest()[:64], f"XXXX-XXXX-{num[-4:]}"


def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("🌱 Seeding Pravi ID database...")

        # 1. Departments
        departments = [
            Department(code="food_department", name="Food & Civil Supplies Department", description="Ration cards, food security, PDS"),
            Department(code="education_department", name="Education Department", description="Schools, scholarships, education schemes"),
            Department(code="health_department", name="Health & Family Welfare Department", description="Healthcare schemes, insurance"),
            Department(code="housing_department", name="Housing & Urban Development Department", description="Housing assistance, PMAY"),
            Department(code="social_justice_department", name="Social Justice & Empowerment Department", description="Pensions, social welfare"),
        ]
        db.add_all(departments)
        db.flush()
        print(f"  ✓ {len(departments)} departments created")

        # 2. Users (demo accounts)
        demo_password = get_password_hash("demo123")
        users = [
            User(username="citizen", email="citizen@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Rajesh Kumar Patel", role="citizen", family_id="GJ-FAM-2026-00000001", member_id="GJ-MEM-00000001"),
            User(username="citizen2", email="citizen2@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Amit Shah", role="citizen", family_id="GJ-FAM-2026-00000002", member_id="GJ-MEM-00000005"),
            User(username="verifier", email="verifier@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Verification Officer Demo", role="verification_officer"),
            User(username="scheme_officer", email="scheme@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Scheme Officer Demo", role="scheme_officer"),
            User(username="dept_officer", email="dept@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Department Officer Demo", role="department_officer", department_id=departments[1].id),
            User(username="admin", email="admin@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="State Administrator Demo", role="state_admin"),
            User(username="operator", email="operator@demo.praviid.gj.gov.in", password_hash=demo_password,
                 full_name="Assisted Service Operator Demo", role="assisted_operator"),
        ]
        db.add_all(users)
        db.flush()
        print(f"  ✓ {len(users)} demo users created")

        # 3. Families & Members
        all_families = []
        all_members = []
        member_counter = 0

        for i in range(1, 121):  # 120 families
            district = random.choice(DISTRICTS)
            taluka = random.choice(TALUKAS[district])
            village = random.choice(VILLAGES)
            last_name = random.choice(LAST_NAMES)
            income = random.choice(INCOME_BANDS)
            cat = random.choice(CATEGORIES)
            verification = random.choice(["verified", "verified", "verified", "pending", "partially_verified"])

            family = Family(
                family_id=f"GJ-FAM-2026-{i:08d}",
                status="active",
                address_line=f"{random.randint(1,500)}, {village} Road, {taluka}",
                district=district, taluka=taluka, village_city=village,
                pincode=f"{random.randint(360001, 396999)}",
                income_band=income, category=cat,
                ration_card_type=random.choice(RATION_TYPES) if income in ("BPL", "EWS") else "APL",
                verification_status=verification,
                data_quality_score=round(random.uniform(65, 100), 1),
                source=random.choice(["manual", "ration_import", "census_import", "department_sync"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                last_verified_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)) if verification == "verified" else None,
            )
            all_families.append(family)

            # Generate members (2-6 per family)
            num_members = random.choice([2, 3, 3, 4, 4, 4, 5, 5, 6])
            father_name = random.choice(FIRST_NAMES_M)
            mother_name = random.choice(FIRST_NAMES_F)
            father_dob = random_date(1960, 1985)
            mother_dob = random_date(1962, 1988)

            # Father (head)
            member_counter += 1
            aah, aam = generate_aadhaar_hash()
            father = Member(
                member_id=f"GJ-MEM-{member_counter:08d}",
                family_id_str=family.family_id,
                name=f"{father_name} {last_name}",
                dob=father_dob, gender="male",
                occupation=random.choice(OCCUPATIONS[:8]),
                education=random.choice(["10th Pass", "12th Pass", "Graduate", "Post-Graduate", "Below 10th"]),
                income_band=income, category=cat,
                relationship_to_head="self",
                aadhaar_reference_hash=aah, aadhaar_masked=aam,
                phone=f"9{random.randint(100000000, 999999999)}",
                is_active=True, is_head=True,
                verification_status=verification,
                source=family.source,
            )
            all_members.append(father)

            # Mother
            member_counter += 1
            aah, aam = generate_aadhaar_hash()
            mother = Member(
                member_id=f"GJ-MEM-{member_counter:08d}",
                family_id_str=family.family_id,
                name=f"{mother_name} {father_name} {last_name}",
                dob=mother_dob, gender="female",
                occupation=random.choice(["Homemaker", "Teaching", "Self-employed", "Farming"]),
                education=random.choice(["10th Pass", "12th Pass", "Graduate", "Below 10th"]),
                income_band=income, category=cat,
                relationship_to_head="spouse",
                aadhaar_reference_hash=aah, aadhaar_masked=aam,
                is_active=True, is_head=False,
                verification_status=verification,
                source=family.source,
            )
            all_members.append(mother)

            # Children
            for c in range(num_members - 2):
                member_counter += 1
                is_male = random.choice([True, False])
                child_name = random.choice(FIRST_NAMES_CHILD_M if is_male else FIRST_NAMES_CHILD_F)
                child_dob = random_date(2000, 2022)
                aah, aam = generate_aadhaar_hash()
                child = Member(
                    member_id=f"GJ-MEM-{member_counter:08d}",
                    family_id_str=family.family_id,
                    name=f"{child_name} {father_name} {last_name}",
                    dob=child_dob, gender="male" if is_male else "female",
                    occupation="Student" if child_dob.year > 2004 else random.choice(OCCUPATIONS),
                    education="Studying" if child_dob.year > 2004 else random.choice(["10th Pass", "12th Pass", "Graduate"]),
                    income_band=None, category=cat,
                    relationship_to_head="son" if is_male else "daughter",
                    aadhaar_reference_hash=aah, aadhaar_masked=aam,
                    is_active=True, is_head=False,
                    verification_status=verification,
                    source=family.source,
                )
                all_members.append(child)

            family.head_member_id = father.member_id

        db.add_all(all_families)
        db.flush()

        # Link members to families
        for m in all_members:
            family = next(f for f in all_families if f.family_id == m.family_id_str)
            m.family_id_fk = family.id

        db.add_all(all_members)
        db.flush()
        print(f"  ✓ {len(all_families)} families, {len(all_members)} members created")

        # 4. Schemes
        schemes = [
            Scheme(scheme_id="SCH-0001", name="DEMO — Education Assistance Scheme",
                   description="Financial assistance for school/college students from economically weaker families. DEMO SCHEME — SYNTHETIC RULES.",
                   department_id=departments[1].id, department_name="Education Department",
                   benefit_type="cash", benefit_value="₹5,000 per year", benefit_frequency="annual",
                   target_group="Students aged 6-25 from BPL/EWS families", is_demo=True),
            Scheme(scheme_id="SCH-0002", name="DEMO — Food Assistance Scheme",
                   description="Subsidized food grains for below poverty line families. DEMO SCHEME — SYNTHETIC RULES.",
                   department_id=departments[0].id, department_name="Food & Civil Supplies Department",
                   benefit_type="kind", benefit_value="35kg grain per month", benefit_frequency="monthly",
                   target_group="BPL/AAY families", is_demo=True),
            Scheme(scheme_id="SCH-0003", name="DEMO — Housing Assistance Scheme",
                   description="Financial assistance for construction of dwelling unit. DEMO SCHEME — SYNTHETIC RULES.",
                   department_id=departments[3].id, department_name="Housing & Urban Development Department",
                   benefit_type="cash", benefit_value="₹1,20,000 one-time", benefit_frequency="one_time",
                   target_group="Homeless BPL/EWS families", is_demo=True),
            Scheme(scheme_id="SCH-0004", name="DEMO — Senior Citizen Assistance Scheme",
                   description="Monthly pension for senior citizens from economically weaker families. DEMO SCHEME — SYNTHETIC RULES.",
                   department_id=departments[4].id, department_name="Social Justice & Empowerment Department",
                   benefit_type="cash", benefit_value="₹1,000 per month", benefit_frequency="monthly",
                   target_group="Senior citizens aged 60+ from BPL/EWS families", is_demo=True),
            Scheme(scheme_id="SCH-0005", name="DEMO — Family Health Assistance Scheme",
                   description="Health insurance coverage for families below poverty line. DEMO SCHEME — SYNTHETIC RULES.",
                   department_id=departments[2].id, department_name="Health & Family Welfare Department",
                   benefit_type="service", benefit_value="₹5,00,000 coverage", benefit_frequency="annual",
                   target_group="BPL/EWS families", is_demo=True),
        ]
        db.add_all(schemes)
        db.flush()

        # Scheme Rules
        rules = [
            # Education
            SchemeRule(scheme_id=schemes[0].id, field="has_student", operator="=", value="yes", value_type="string", entity="member", description="Family must have student member (age 6-25)"),
            SchemeRule(scheme_id=schemes[0].id, field="income_band", operator="IN", value="BPL,EWS,LIG", value_type="list", entity="family", description="Family income band must be BPL, EWS, or LIG"),
            SchemeRule(scheme_id=schemes[0].id, field="verification_status", operator="=", value="verified", value_type="string", entity="family", description="Family must be verified"),
            # Food
            SchemeRule(scheme_id=schemes[1].id, field="income_band", operator="IN", value="BPL,EWS,AAY", value_type="list", entity="family", description="Family income must be BPL/EWS/AAY"),
            SchemeRule(scheme_id=schemes[1].id, field="member_count", operator=">=", value="2", value_type="number", entity="family", description="Must have at least 2 family members"),
            # Housing
            SchemeRule(scheme_id=schemes[2].id, field="income_band", operator="IN", value="BPL,EWS", value_type="list", entity="family", description="Family income must be BPL or EWS"),
            SchemeRule(scheme_id=schemes[2].id, field="verification_status", operator="=", value="verified", value_type="string", entity="family", description="Family must be verified"),
            # Senior
            SchemeRule(scheme_id=schemes[3].id, field="has_senior", operator="=", value="yes", value_type="string", entity="member", description="Family must have member aged 60+"),
            SchemeRule(scheme_id=schemes[3].id, field="income_band", operator="IN", value="BPL,EWS,LIG", value_type="list", entity="family", description="Family income band must be BPL/EWS/LIG"),
            # Health
            SchemeRule(scheme_id=schemes[4].id, field="income_band", operator="IN", value="BPL,EWS,LIG", value_type="list", entity="family", description="Family income must be BPL/EWS/LIG"),
            SchemeRule(scheme_id=schemes[4].id, field="verification_status", operator="=", value="verified", value_type="string", entity="family", description="Family must be verified"),
        ]
        db.add_all(rules)
        db.flush()
        print(f"  ✓ {len(schemes)} schemes, {len(rules)} rules created")

        # 5. Benefits
        benefits = []
        benefit_counter = 0
        for fam in all_families[:60]:  # 60 families with benefits
            num_benefits = random.randint(1, 3)
            for _ in range(num_benefits):
                benefit_counter += 1
                scheme = random.choice(schemes)
                benefits.append(BenefitLedger(
                    benefit_id=f"BEN-{benefit_counter:06d}",
                    family_id=fam.family_id,
                    member_id=None,
                    scheme_id=scheme.scheme_id,
                    benefit_type=scheme.benefit_type,
                    amount=random.choice([1000, 2000, 5000, 10000, 120000]) if scheme.benefit_type == "cash" else None,
                    description=f"Benefit under {scheme.name}",
                    period_start=datetime.utcnow() - timedelta(days=random.randint(30, 300)),
                    period_end=datetime.utcnow() + timedelta(days=random.randint(30, 365)),
                    frequency=scheme.benefit_frequency,
                    status=random.choice(["active", "active", "active", "completed", "suspended"]),
                    department_name=scheme.department_name,
                    source="demo_seed",
                ))
        db.add_all(benefits)
        db.flush()
        print(f"  ✓ {len(benefits)} benefits created")

        # 6. Change Requests
        change_requests = []
        cr_types = ["name", "address", "dob", "income", "occupation", "gender", "member_addition", "relationship"]
        for j in range(1, 26):
            fam = random.choice(all_families[:20])
            members = [m for m in all_members if m.family_id_str == fam.family_id]
            member = random.choice(members) if members else None
            cr_type = random.choice(cr_types)

            cr_status = random.choice(["submitted", "submitted", "under_review", "approved", "rejected", "more_info_required"])
            cr = ChangeRequest(
                request_id=f"REQ-{j:06d}",
                family_id=fam.family_id,
                member_id=member.member_id if member and cr_type != "address" else None,
                requested_by=users[0].id,
                request_type=cr_type,
                field_name=cr_type,
                current_value="Current Value" if cr_type not in ("member_addition",) else None,
                requested_value="Requested Value" if cr_type not in ("member_addition",) else "New member details",
                reason=random.choice([
                    "Incorrect information in records", "Recently changed",
                    "Spelling mistake", "Updated after relocation",
                    "Correction needed", "As per latest document",
                ]),
                status=cr_status,
                priority=random.choice(["normal", "normal", "high", "low"]),
                reviewed_by=users[2].id if cr_status in ("approved", "rejected") else None,
                reviewed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if cr_status in ("approved", "rejected") else None,
                rejection_reason="Insufficient documentation" if cr_status == "rejected" else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            )
            change_requests.append(cr)
        db.add_all(change_requests)
        db.flush()
        print(f"  ✓ {len(change_requests)} change requests created")

        # 7. Life Events
        life_events = []
        event_types = ["birth", "death", "marriage", "address_change", "income_change", "member_added"]
        for k in range(1, 16):
            fam = random.choice(all_families[:20])
            etype = random.choice(event_types)
            evt_status = random.choice(["submitted", "approved", "approved", "rejected"])
            evt = LifeEvent(
                event_id=f"EVT-{k:06d}",
                family_id=fam.family_id,
                event_type=etype,
                description=f"Demo {etype.replace('_', ' ')} event",
                event_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                new_member_name=f"{random.choice(FIRST_NAMES_CHILD_M)} Patel" if etype in ("birth", "member_added") else None,
                new_member_gender="male" if etype in ("birth", "member_added") else None,
                new_member_relationship="son" if etype == "birth" else None,
                status=evt_status,
                requested_by=users[0].id,
                reviewed_by=users[2].id if evt_status != "submitted" else None,
                reviewed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if evt_status != "submitted" else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            )
            life_events.append(evt)
        db.add_all(life_events)
        db.flush()
        print(f"  ✓ {len(life_events)} life events created")

        # 8. Identity Matches (duplicates)
        identity_matches = []
        for n in range(1, 13):
            m1 = random.choice(all_members[:50])
            # Create slight name variation
            name_parts = m1.name.split()
            varied_name = f"{name_parts[0]} {name_parts[-1]}" if len(name_parts) > 2 else m1.name
            m2 = random.choice(all_members[50:100])

            match = IdentityMatch(
                match_id=f"MTH-{n:06d}",
                record_a_type="member", record_a_id=m1.member_id,
                record_a_name=m1.name, record_a_source="ration_import",
                record_b_type="member", record_b_id=m2.member_id,
                record_b_name=varied_name, record_b_source="pension_import",
                confidence_score=round(random.uniform(72, 98), 1),
                match_reasons=json.dumps(["Name similarity", "DOB match", "District match"]),
                match_type=random.choice(["deterministic", "fuzzy"]),
                status=random.choice(["pending", "pending", "confirmed", "rejected"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            )
            identity_matches.append(match)
        db.add_all(identity_matches)
        db.flush()
        print(f"  ✓ {len(identity_matches)} identity matches created")

        # 9. Audit Logs
        audit_logs = []
        actions = ["LOGIN", "FAMILY_CREATED", "MEMBER_UPDATED", "CHANGE_REQUEST_CREATED",
                    "CHANGE_REQUEST_APPROVED", "CHANGE_REQUEST_REJECTED", "LIFE_EVENT_CREATED",
                    "LIFE_EVENT_APPROVED", "DATA_ACCESSED", "ELIGIBILITY_EVALUATED",
                    "DUPLICATE_DETECTED", "SCHEME_CREATED"]
        for a in range(1, 101):
            audit_logs.append(AuditLog(
                audit_id=f"AUD-{a:06d}",
                actor_id=random.choice([u.id for u in users]),
                actor_name=random.choice([u.full_name for u in users]),
                actor_role=random.choice(["citizen", "verification_officer", "state_admin", "scheme_officer"]),
                action=random.choice(actions),
                entity_type=random.choice(["family", "member", "change_request", "life_event", "scheme"]),
                entity_id=random.choice(all_families[:20]).family_id,
                description=f"Demo audit log entry #{a}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23)),
            ))
        db.add_all(audit_logs)
        db.flush()
        print(f"  ✓ {len(audit_logs)} audit logs created")

        # 10. Notifications
        notifications = []
        for nid in range(1, 11):
            notifications.append(Notification(
                notification_id=f"NTF-{nid:06d}",
                user_id=users[0].id,
                title=random.choice([
                    "Your address change request has been approved",
                    "New scheme available — Education Assistance",
                    "Family verification complete",
                    "More information required for your request",
                    "Benefit status updated",
                ]),
                message="This is a demo notification for the Pravi ID system.",
                notification_type=random.choice(["request_update", "eligibility_change", "system"]),
                is_read=random.choice([True, False]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            ))
        db.add_all(notifications)
        db.flush()
        print(f"  ✓ {len(notifications)} notifications created")

        # 11. Eligibility Results for first 20 families
        elig_results = []
        for fam in all_families[:20]:
            members = [m for m in all_members if m.family_id_str == fam.family_id and m.is_active]
            for scheme in schemes:
                has_student = any(m.age and 6 <= m.age <= 25 for m in members if m.age)
                has_senior = any(m.age and m.age >= 60 for m in members if m.age)
                is_bpl = fam.income_band in ("BPL", "EWS", "LIG")
                is_verified = fam.verification_status == "verified"

                if scheme.scheme_id == "SCH-0001":
                    elig_status = "eligible" if (has_student and is_bpl and is_verified) else ("needs_verification" if not is_verified else "not_eligible")
                elif scheme.scheme_id == "SCH-0002":
                    elig_status = "eligible" if (fam.income_band in ("BPL", "EWS") and len(members) >= 2) else "not_eligible"
                elif scheme.scheme_id == "SCH-0003":
                    elig_status = "eligible" if (fam.income_band in ("BPL", "EWS") and is_verified) else ("needs_verification" if not is_verified else "not_eligible")
                elif scheme.scheme_id == "SCH-0004":
                    elig_status = "eligible" if (has_senior and is_bpl) else "not_eligible"
                else:
                    elig_status = "eligible" if (is_bpl and is_verified) else ("needs_verification" if not is_verified else "not_eligible")

                explanation = f"{'Eligible' if elig_status == 'eligible' else 'Not eligible' if elig_status == 'not_eligible' else 'Verification required'} for {scheme.name}"
                elig_results.append(EligibilityResult(
                    family_id=fam.family_id, scheme_id=scheme.scheme_id,
                    status=elig_status, explanation=explanation,
                    matched_rules=json.dumps([]), failed_rules=json.dumps([]), missing_data=json.dumps([]),
                    evaluated_at=datetime.utcnow(),
                ))
        db.add_all(elig_results)
        db.flush()
        print(f"  ✓ {len(elig_results)} eligibility results created")

        db.commit()
        print("\n✅ Seed complete! Database populated with synthetic demo data.")
        print(f"   Families: {len(all_families)}")
        print(f"   Members: {len(all_members)}")
        print(f"   Schemes: {len(schemes)}")
        print(f"   Benefits: {len(benefits)}")
        print(f"   Change Requests: {len(change_requests)}")
        print(f"   Life Events: {len(life_events)}")
        print(f"   Identity Matches: {len(identity_matches)}")
        print(f"   Audit Logs: {len(audit_logs)}")
        print(f"\n   Demo Credentials (all passwords: demo123):")
        print(f"   citizen / citizen2 / verifier / scheme_officer / dept_officer / admin / operator")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
