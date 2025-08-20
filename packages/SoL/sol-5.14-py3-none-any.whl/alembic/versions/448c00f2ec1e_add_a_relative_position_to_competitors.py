# :Project:   SoL -- Add a relative position to competitors
# :Created:   2020-04-25 11:19:41.563058
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '448c00f2ec1e'
down_revision = 'ffec21d0a5a0'


def upgrade():
    op.add_column('competitors', sa.Column('position', sa.SmallInteger(), nullable=False,
                                           server_default=sa.text('0')))


def downgrade():
    op.drop_column('competitors', 'position')
