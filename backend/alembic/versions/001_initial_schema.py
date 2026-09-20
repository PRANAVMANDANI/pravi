"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-09-20
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Departments
    op.create_table('departments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('ix_departments_code', 'departments', ['code'])

    # Users
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('family_id', sa.String(25), nullable=True),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_role', 'users', ['role'])

    # Families
    op.create_table('families',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('family_id', sa.String(25), unique=True, nullable=False),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('head_member_id', sa.String(20), nullable=True),
        sa.Column('address_line', sa.Text(), nullable=True),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('taluka', sa.String(100), nullable=True),
        sa.Column('village_city', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('state', sa.String(50), default='Gujarat'),
        sa.Column('income_band', sa.String(50), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('ration_card_type', sa.String(50), nullable=True),
        sa.Column('verification_status', sa.String(30), default='pending'),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), default=0.0),
        sa.Column('data_quality_issues', sa.Text(), nullable=True),
        sa.Column('source', sa.String(100), default='manual'),
        sa.Column('source_reference', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_families_family_id', 'families', ['family_id'])
    op.create_index('ix_families_district', 'families', ['district'])
    op.create_index('ix_families_taluka', 'families', ['taluka'])
    op.create_index('ix_families_village_city', 'families', ['village_city'])
    op.create_index('ix_families_verification_status', 'families', ['verification_status'])
    op.create_index('ix_families_district_taluka', 'families', ['district', 'taluka'])

    # Members
    op.create_table('members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('member_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id_fk', sa.Integer(), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('family_id_str', sa.String(25), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_local', sa.String(255), nullable=True),
        sa.Column('dob', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('occupation', sa.String(100), nullable=True),
        sa.Column('education', sa.String(100), nullable=True),
        sa.Column('income_band', sa.String(50), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('relationship_to_head', sa.String(50), nullable=True),
        sa.Column('aadhaar_reference_hash', sa.String(64), nullable=True),
        sa.Column('aadhaar_masked', sa.String(12), nullable=True),
        sa.Column('phone', sa.String(15), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_head', sa.Boolean(), default=False),
        sa.Column('verification_status', sa.String(30), default='pending'),
        sa.Column('source', sa.String(100), default='manual'),
        sa.Column('source_reference', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_members_member_id', 'members', ['member_id'])
    op.create_index('ix_members_family_id_str', 'members', ['family_id_str'])
    op.create_index('ix_members_name', 'members', ['name'])
    op.create_index('ix_members_dob', 'members', ['dob'])
    op.create_index('ix_members_aadhaar_ref', 'members', ['aadhaar_reference_hash'])
    op.create_index('ix_members_family_active', 'members', ['family_id_fk', 'is_active'])

    # Schemes
    op.create_table('schemes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('scheme_id', sa.String(30), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('department_name', sa.String(100), nullable=True),
        sa.Column('benefit_type', sa.String(50), nullable=True),
        sa.Column('benefit_value', sa.String(100), nullable=True),
        sa.Column('benefit_frequency', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('is_demo', sa.Boolean(), default=True),
        sa.Column('target_group', sa.String(255), nullable=True),
        sa.Column('max_beneficiaries', sa.Integer(), nullable=True),
        sa.Column('current_beneficiaries', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_schemes_scheme_id', 'schemes', ['scheme_id'])

    # Scheme Rules
    op.create_table('scheme_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('scheme_id', sa.Integer(), sa.ForeignKey('schemes.id'), nullable=False),
        sa.Column('rule_version', sa.Integer(), default=1),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('field', sa.String(100), nullable=False),
        sa.Column('operator', sa.String(20), nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('value_type', sa.String(20), default='string'),
        sa.Column('entity', sa.String(20), default='member'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logical_group', sa.String(10), default='AND'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_scheme_rules_scheme_active', 'scheme_rules', ['scheme_id', 'is_active'])

    # Eligibility Results
    op.create_table('eligibility_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('scheme_id', sa.String(30), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float(), default=1.0),
        sa.Column('matched_rules', sa.Text(), nullable=True),
        sa.Column('failed_rules', sa.Text(), nullable=True),
        sa.Column('missing_data', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('rule_version', sa.Integer(), default=1),
        sa.Column('is_stale', sa.Boolean(), default=False),
        sa.Column('stale_reason', sa.String(255), nullable=True),
        sa.Column('evaluated_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_eligibility_family_scheme', 'eligibility_results', ['family_id', 'scheme_id'])

    # Change Requests
    op.create_table('change_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('requested_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=True),
        sa.Column('current_value', sa.Text(), nullable=True),
        sa.Column('requested_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), default='submitted'),
        sa.Column('priority', sa.String(20), default='normal'),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('before_snapshot', sa.Text(), nullable=True),
        sa.Column('after_snapshot', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_change_requests_request_id', 'change_requests', ['request_id'])
    op.create_index('ix_change_requests_family', 'change_requests', ['family_id', 'status'])
    op.create_index('ix_change_requests_status_type', 'change_requests', ['status', 'request_type'])

    # Change Request Documents
    op.create_table('change_request_documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('change_request_id', sa.Integer(), sa.ForeignKey('change_requests.id'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('uploaded_at', sa.DateTime()),
    )

    # Life Events
    op.create_table('life_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('event_type', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_date', sa.DateTime(), nullable=True),
        sa.Column('new_member_name', sa.String(255), nullable=True),
        sa.Column('new_member_dob', sa.String(20), nullable=True),
        sa.Column('new_member_gender', sa.String(20), nullable=True),
        sa.Column('new_member_relationship', sa.String(50), nullable=True),
        sa.Column('event_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), default='submitted'),
        sa.Column('requested_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('affected_schemes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_life_events_event_id', 'life_events', ['event_id'])
    op.create_index('ix_life_events_family_type', 'life_events', ['family_id', 'event_type'])
    op.create_index('ix_life_events_status', 'life_events', ['status'])

    # Applications
    op.create_table('applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('scheme_id', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), default='pending'),
        sa.Column('applied_at', sa.DateTime()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_applications_family', 'applications', ['family_id'])
    op.create_index('ix_applications_scheme', 'applications', ['scheme_id'])

    # Benefit Ledger
    op.create_table('benefit_ledger',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('benefit_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('scheme_id', sa.String(30), nullable=False),
        sa.Column('application_id', sa.String(20), nullable=True),
        sa.Column('benefit_type', sa.String(50), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(10), default='INR'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.Column('frequency', sa.String(30), nullable=True),
        sa.Column('status', sa.String(30), default='active'),
        sa.Column('department_name', sa.String(100), nullable=True),
        sa.Column('source', sa.String(100), default='manual'),
        sa.Column('source_reference', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_benefit_ledger_family_scheme', 'benefit_ledger', ['family_id', 'scheme_id'])
    op.create_index('ix_benefit_ledger_status', 'benefit_ledger', ['status'])

    # Documents
    op.create_table('documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.String(20), unique=True, nullable=False),
        sa.Column('family_id', sa.String(25), nullable=True),
        sa.Column('member_id', sa.String(20), nullable=True),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('verified_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime()),
    )

    # Identity Matches
    op.create_table('identity_matches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('match_id', sa.String(20), unique=True, nullable=False),
        sa.Column('record_a_type', sa.String(20), nullable=False),
        sa.Column('record_a_id', sa.String(30), nullable=False),
        sa.Column('record_a_name', sa.String(255), nullable=True),
        sa.Column('record_a_source', sa.String(100), nullable=True),
        sa.Column('record_b_type', sa.String(20), nullable=False),
        sa.Column('record_b_id', sa.String(30), nullable=False),
        sa.Column('record_b_name', sa.String(255), nullable=True),
        sa.Column('record_b_source', sa.String(100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('match_reasons', sa.Text(), nullable=True),
        sa.Column('match_type', sa.String(30), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_identity_matches_status', 'identity_matches', ['status'])

    # Identity Merge History
    op.create_table('identity_merge_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('merge_id', sa.String(20), unique=True, nullable=False),
        sa.Column('action', sa.String(10), nullable=False),
        sa.Column('primary_id', sa.String(30), nullable=False),
        sa.Column('secondary_id', sa.String(30), nullable=False),
        sa.Column('entity_type', sa.String(20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('before_snapshot', sa.Text(), nullable=True),
        sa.Column('after_snapshot', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime()),
    )

    # Data Access Requests
    op.create_table('data_access_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('access_id', sa.String(20), unique=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('department_code', sa.String(50), nullable=True),
        sa.Column('family_id', sa.String(25), nullable=False),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('fields_requested', sa.Text(), nullable=True),
        sa.Column('fields_returned', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('ix_data_access_family', 'data_access_requests', ['family_id'])
    op.create_index('ix_data_access_dept', 'data_access_requests', ['department_code'])

    # Notifications
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('notification_id', sa.String(20), unique=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('notification_type', sa.String(50), nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(30), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('ix_notifications_user_read', 'notifications', ['user_id', 'is_read'])

    # Audit Logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('audit_id', sa.String(20), unique=True, nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_name', sa.String(255), nullable=True),
        sa.Column('actor_role', sa.String(50), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(30), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('before_snapshot', sa.Text(), nullable=True),
        sa.Column('after_snapshot', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('request_id', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('ix_audit_logs_audit_id', 'audit_logs', ['audit_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_actor_action', 'audit_logs', ['actor_id', 'action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('notifications')
    op.drop_table('data_access_requests')
    op.drop_table('identity_merge_history')
    op.drop_table('identity_matches')
    op.drop_table('documents')
    op.drop_table('benefit_ledger')
    op.drop_table('applications')
    op.drop_table('life_events')
    op.drop_table('change_request_documents')
    op.drop_table('change_requests')
    op.drop_table('eligibility_results')
    op.drop_table('scheme_rules')
    op.drop_table('schemes')
    op.drop_table('members')
    op.drop_table('families')
    op.drop_table('users')
    op.drop_table('departments')
