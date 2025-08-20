# :Project:   SoL -- Add max rating level to users
# :Created:   2024-04-20 19:43:13.213471
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'a67281b72424'
down_revision = '8dda46f71ced'


def upgrade():
    op.add_column('users', sa.Column('maxratinglevel', sa.CHAR(length=1), nullable=False,
                                     server_default='2'))


def downgrade():
    op.drop_column('users', 'maxratinglevel')
