"""Add missing ghana_card and disability_status to student

Revision ID: 3865ce43eec6
Revises: 0e860fc9f377
Create Date: 2026-02-03 23:02:01.222226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3865ce43eec6'
down_revision: Union[str, Sequence[str], None] = '0e860fc9f377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('student')]
    
    if 'ghana_card' not in columns:
        op.add_column('student', sa.Column('ghana_card', sa.String(), nullable=True))
    if 'disability_status' not in columns:
        op.add_column('student', sa.Column('disability_status', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('student')]
    
    if 'disability_status' in columns:
        op.drop_column('student', 'disability_status')
    if 'ghana_card' in columns:
        op.drop_column('student', 'ghana_card')
