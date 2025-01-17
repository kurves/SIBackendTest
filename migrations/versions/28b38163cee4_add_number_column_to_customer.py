"""Add number column to Customer

Revision ID: 28b38163cee4
Revises: 2cb34d7da4f2
Create Date: 2024-09-26 12:11:42.445164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28b38163cee4'
down_revision = '2cb34d7da4f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('time',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('time',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###
