"""add surname name ix

Revision ID: af89faaf5743
Revises: f93916497163
Create Date: 2025-01-17 22:00:23.933328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af89faaf5743'
down_revision: Union[str, None] = 'f93916497163'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_surname_name', 'user', ['surname', 'name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_surname_name', table_name='user')
    # ### end Alembic commands ###
