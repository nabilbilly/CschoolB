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
    
    # Use autocommit block for ALTER TYPE
    with op.get_context().autocommit_block():
        # 1. Academics
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Active' AND enumtypid = 'yearstatus'::regtype) THEN
                    ALTER TYPE yearstatus ADD VALUE 'Active';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Draft' AND enumtypid = 'yearstatus'::regtype) THEN
                    ALTER TYPE yearstatus ADD VALUE 'Draft';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Archived' AND enumtypid = 'yearstatus'::regtype) THEN
                    ALTER TYPE yearstatus ADD VALUE 'Archived';
                END IF;
            END$$;
        """)

        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Active' AND enumtypid = 'termstatus'::regtype) THEN
                    ALTER TYPE termstatus ADD VALUE 'Active';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Draft' AND enumtypid = 'termstatus'::regtype) THEN
                    ALTER TYPE termstatus ADD VALUE 'Draft';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Closed' AND enumtypid = 'termstatus'::regtype) THEN
                    ALTER TYPE termstatus ADD VALUE 'Closed';
                END IF;
            END$$;
        """)

        # 2. Admissions
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Pending' AND enumtypid = 'admissionstatus'::regtype) THEN
                    ALTER TYPE admissionstatus ADD VALUE 'Pending';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Approved' AND enumtypid = 'admissionstatus'::regtype) THEN
                    ALTER TYPE admissionstatus ADD VALUE 'Approved';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Rejected' AND enumtypid = 'admissionstatus'::regtype) THEN
                    ALTER TYPE admissionstatus ADD VALUE 'Rejected';
                END IF;
            END$$;
        """)

        # 3. Students
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Male' AND enumtypid = 'gender'::regtype) THEN
                    ALTER TYPE gender ADD VALUE 'Male';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Female' AND enumtypid = 'gender'::regtype) THEN
                    ALTER TYPE gender ADD VALUE 'Female';
                END IF;
            END$$;
        """)

        # 4. EVoucher
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Unused' AND enumtypid = 'voucherstatus'::regtype) THEN
                    ALTER TYPE voucherstatus ADD VALUE 'Unused';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Reserved' AND enumtypid = 'voucherstatus'::regtype) THEN
                    ALTER TYPE voucherstatus ADD VALUE 'Reserved';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Used' AND enumtypid = 'voucherstatus'::regtype) THEN
                    ALTER TYPE voucherstatus ADD VALUE 'Used';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Expired' AND enumtypid = 'voucherstatus'::regtype) THEN
                    ALTER TYPE voucherstatus ADD VALUE 'Expired';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Revoked' AND enumtypid = 'voucherstatus'::regtype) THEN
                    ALTER TYPE voucherstatus ADD VALUE 'Revoked';
                END IF;
            END$$;
        """)

        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Valid' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Valid';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Invalid Pin' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Invalid Pin';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Not Found' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Not Found';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Expired' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Expired';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Used' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Used';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'Reserved' AND enumtypid = 'voucherattemptresult'::regtype) THEN
                    ALTER TYPE voucherattemptresult ADD VALUE 'Reserved';
                END IF;
            END$$;
        """)

    # Data updates can be in a transaction (default) or not. 
    # Since we left the autocommit block, we are back to default mode (transactional).
    
    # 1. Academics
    op.execute("UPDATE academicyear SET status = 'Active' WHERE status::text = 'ACTIVE'")
    op.execute("UPDATE academicyear SET status = 'Draft' WHERE status::text = 'DRAFT'")
    op.execute("UPDATE academicyear SET status = 'Archived' WHERE status::text = 'ARCHIVED'")

    op.execute("UPDATE term SET status = 'Active' WHERE status::text = 'ACTIVE'")
    op.execute("UPDATE term SET status = 'Draft' WHERE status::text = 'DRAFT'")
    op.execute("UPDATE term SET status = 'Closed' WHERE status::text = 'CLOSED'")

    # 2. Admissions
    op.execute("UPDATE admission SET status = 'Pending' WHERE status::text = 'PENDING'")
    op.execute("UPDATE admission SET status = 'Approved' WHERE status::text = 'APPROVED'")
    op.execute("UPDATE admission SET status = 'Rejected' WHERE status::text = 'REJECTED'")

    # 3. Students
    op.execute("UPDATE student SET gender = 'Male' WHERE gender::text = 'MALE'")
    op.execute("UPDATE student SET gender = 'Female' WHERE gender::text = 'FEMALE'")

    # 4. EVoucher
    op.execute("UPDATE evoucher SET status = 'Unused' WHERE status::text = 'UNUSED'")
    op.execute("UPDATE evoucher SET status = 'Reserved' WHERE status::text = 'RESERVED'")
    op.execute("UPDATE evoucher SET status = 'Used' WHERE status::text = 'USED'")
    op.execute("UPDATE evoucher SET status = 'Expired' WHERE status::text = 'EXPIRED'")
    op.execute("UPDATE evoucher SET status = 'Revoked' WHERE status::text = 'REVOKED'")

    op.execute("UPDATE voucherattemptlog SET result = 'Valid' WHERE result::text = 'VALID'")
    op.execute("UPDATE voucherattemptlog SET result = 'Invalid Pin' WHERE result::text = 'INVALID_PIN'")
    op.execute("UPDATE voucherattemptlog SET result = 'Not Found' WHERE result::text = 'NOT_FOUND'")
    op.execute("UPDATE voucherattemptlog SET result = 'Expired' WHERE result::text = 'EXPIRED'")
    op.execute("UPDATE voucherattemptlog SET result = 'Used' WHERE result::text = 'USED'")
    op.execute("UPDATE voucherattemptlog SET result = 'Reserved' WHERE result::text = 'RESERVED'")


def downgrade():
    # Removing values from an enum is not directly supported in Postgres
    pass
