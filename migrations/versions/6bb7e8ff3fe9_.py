"""empty message

Revision ID: 6bb7e8ff3fe9
Revises: aeebec85caaa
Create Date: 2024-01-26 22:35:40.506656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bb7e8ff3fe9'
down_revision = 'aeebec85caaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('regions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('images', sa.Text(), nullable=True))
        batch_op.drop_column('image')
        batch_op.drop_column('photos')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('regions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photos', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('image', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('images')

    # ### end Alembic commands ###
