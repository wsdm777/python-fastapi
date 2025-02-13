"""remove is_verified, is_active

Revision ID: 004281ddd903
Revises: 8c54bf4a81fe
Create Date: 2025-02-12 20:23:17.373477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004281ddd903'
down_revision: Union[str, None] = '8c54bf4a81fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_verified')
    op.drop_column('user', 'is_active')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
