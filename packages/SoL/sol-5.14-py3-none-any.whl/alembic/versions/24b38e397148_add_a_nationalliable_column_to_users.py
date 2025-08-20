# :Project:   SoL -- Add a nationalliable column to users
# :Created:   2024-05-22 19:52:53.905497
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '24b38e397148'
down_revision = '4792dcb3da70'


def upgrade():
    op.add_column('users', sa.Column('nationalliable', sa.CHAR(length=3), nullable=True))


def downgrade():
    op.drop_column('users', 'nationalliable')
