"""Ajout du champ image_url à Produit

Revision ID: c77300d8c2c7
Revises: 
Create Date: 2025-01-13 15:40:46.442637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c77300d8c2c7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('produit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('produit', schema=None) as batch_op:
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###
