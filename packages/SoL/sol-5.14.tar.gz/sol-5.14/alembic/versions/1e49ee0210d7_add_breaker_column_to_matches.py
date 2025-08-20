# :Project:   SoL -- Add breaker column to matches
# :Created:   2020-05-01 12:51:36.491964
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '1e49ee0210d7'
down_revision = '448c00f2ec1e'


def upgrade():
    op.add_column('matches', sa.Column('breaker', sa.CHAR(length=1), nullable=True))


def downgrade():
    op.drop_column('matches', 'breaker')
