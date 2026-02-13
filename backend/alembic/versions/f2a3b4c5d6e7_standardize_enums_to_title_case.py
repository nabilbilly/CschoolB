"""Standardize enums to Title Case

Revision ID: f2a3b4c5d6e7
Revises: 3865ce43eec6
Create Date: 2026-02-13 11:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2a3b4c5d6e7'
down_revision = '3865ce43eec6'
branch_labels = None
depends_on = None


def upgrade():
    # We need to run ALTER TYPE ... ADD VALUE outside of a transaction in Postgres
    # if the version is old, but Alembic handles it in some cases.
    # To be safest, we'll try to execute them. 
    # Note: 'IF NOT EXISTS' is available in PG 9.1+.
    
    # 1. Academics
    op.execute("ALTER TYPE yearstatus ADD VALUE IF NOT EXISTS 'Active'")
    op.execute("ALTER TYPE yearstatus ADD VALUE IF NOT EXISTS 'Draft'")
    op.execute("ALTER TYPE yearstatus ADD VALUE IF NOT EXISTS 'Archived'")
    op.execute("UPDATE academicyear SET status = 'Active' WHERE status = 'ACTIVE'")
    op.execute("UPDATE academicyear SET status = 'Draft' WHERE status = 'DRAFT'")
    op.execute("UPDATE academicyear SET status = 'Archived' WHERE status = 'ARCHIVED'")

    op.execute("ALTER TYPE termstatus ADD VALUE IF NOT EXISTS 'Active'")
    op.execute("ALTER TYPE termstatus ADD VALUE IF NOT EXISTS 'Draft'")
    op.execute("ALTER TYPE termstatus ADD VALUE IF NOT EXISTS 'Closed'")
    op.execute("UPDATE term SET status = 'Active' WHERE status = 'ACTIVE'")
    op.execute("UPDATE term SET status = 'Draft' WHERE status = 'DRAFT'")
    op.execute("UPDATE term SET status = 'Closed' WHERE status = 'CLOSED'")

    # 2. Admissions
    op.execute("ALTER TYPE admissionstatus ADD VALUE IF NOT EXISTS 'Pending'")
    op.execute("ALTER TYPE admissionstatus ADD VALUE IF NOT EXISTS 'Approved'")
    op.execute("ALTER TYPE admissionstatus ADD VALUE IF NOT EXISTS 'Rejected'")
    op.execute("UPDATE admission SET status = 'Pending' WHERE status = 'PENDING'")
    op.execute("UPDATE admission SET status = 'Approved' WHERE status = 'APPROVED'")
    op.execute("UPDATE admission SET status = 'Rejected' WHERE status = 'REJECTED'")

    # 3. Students
    op.execute("ALTER TYPE gender ADD VALUE IF NOT EXISTS 'Male'")
    op.execute("ALTER TYPE gender ADD VALUE IF NOT EXISTS 'Female'")
    op.execute("UPDATE student SET gender = 'Male' WHERE gender = 'MALE'")
    op.execute("UPDATE student SET gender = 'Female' WHERE gender = 'FEMALE'")

    # 4. EVoucher
    op.execute("ALTER TYPE voucherstatus ADD VALUE IF NOT EXISTS 'Unused'")
    op.execute("ALTER TYPE voucherstatus ADD VALUE IF NOT EXISTS 'Reserved'")
    op.execute("ALTER TYPE voucherstatus ADD VALUE IF NOT EXISTS 'Used'")
    op.execute("ALTER TYPE voucherstatus ADD VALUE IF NOT EXISTS 'Expired'")
    op.execute("ALTER TYPE voucherstatus ADD VALUE IF NOT EXISTS 'Revoked'")
    op.execute("UPDATE evoucher SET status = 'Unused' WHERE status = 'UNUSED'")
    op.execute("UPDATE evoucher SET status = 'Reserved' WHERE status = 'RESERVED'")
    op.execute("UPDATE evoucher SET status = 'Used' WHERE status = 'USED'")
    op.execute("UPDATE evoucher SET status = 'Expired' WHERE status = 'EXPIRED'")
    op.execute("UPDATE evoucher SET status = 'Revoked' WHERE status = 'REVOKED'")

    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Valid'")
    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Invalid Pin'")
    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Not Found'")
    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Expired'")
    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Used'")
    op.execute("ALTER TYPE voucherattemptresult ADD VALUE IF NOT EXISTS 'Reserved'")
    op.execute("UPDATE voucherattemptlog SET result = 'Valid' WHERE result = 'VALID'")
    op.execute("UPDATE voucherattemptlog SET result = 'Invalid Pin' WHERE result = 'INVALID_PIN'")
    op.execute("UPDATE voucherattemptlog SET result = 'Not Found' WHERE result = 'NOT_FOUND'")
    op.execute("UPDATE voucherattemptlog SET result = 'Expired' WHERE result = 'EXPIRED'")
    op.execute("UPDATE voucherattemptlog SET result = 'Used' WHERE result = 'USED'")
    op.execute("UPDATE voucherattemptlog SET result = 'Reserved' WHERE result = 'RESERVED'")


def downgrade():
    # Removing values from an enum is not directly supported in Postgres
    pass
