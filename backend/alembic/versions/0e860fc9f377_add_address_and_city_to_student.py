"""add address and city to student

Revision ID: 0e860fc9f377
Revises: 4e0d1f191eac
Create Date: 2026-01-29 14:18:41.070467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e860fc9f377'
down_revision: Union[str, Sequence[str], None] = '4e0d1f191eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    guardian_cols = [c['name'] for c in inspector.get_columns('guardian')]
    if 'secondary_phone' not in guardian_cols:
        op.add_column('guardian', sa.Column('secondary_phone', sa.String(), nullable=True))
    if 'occupation' not in guardian_cols:
        op.add_column('guardian', sa.Column('occupation', sa.String(), nullable=True))
        
    student_cols = [c['name'] for c in inspector.get_columns('student')]
    if 'address' not in student_cols:
        op.add_column('student', sa.Column('address', sa.Text(), nullable=True))
    if 'city' not in student_cols:
        op.add_column('student', sa.Column('city', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    student_cols = [c['name'] for c in inspector.get_columns('student')]
    if 'city' in student_cols:
        op.drop_column('student', 'city')
    if 'address' in student_cols:
        op.drop_column('student', 'address')
        
    guardian_cols = [c['name'] for c in inspector.get_columns('guardian')]
    if 'occupation' in guardian_cols:
        op.drop_column('guardian', 'occupation')
    if 'secondary_phone' in guardian_cols:
        op.drop_column('guardian', 'secondary_phone')
