"""empty message

Revision ID: 373dc7870694
Revises: 
Create Date: 2024-02-09 20:42:14.074063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '373dc7870694'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('discounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rise_or_disc', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('discounts', schema=None) as batch_op:
        batch_op.drop_column('rise_or_disc')

    # ### end Alembic commands ###
