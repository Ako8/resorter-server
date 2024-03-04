"""empty message

Revision ID: 1119b73261ea
Revises: 99bc0f603bd5
Create Date: 2024-02-21 19:34:14.004260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1119b73261ea'
down_revision = '99bc0f603bd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###