# :Project:   SoL -- Add an optional social site URL to tourneys
# :Created:   2020-04-13 13:46:01.403874
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '918717a067a6'
down_revision = 'd311277a4da7'


def upgrade():
    op.add_column('tourneys', sa.Column('socialurl', sa.VARCHAR(length=128), nullable=True))


def downgrade():
    op.drop_column('tourneys', 'socialurl')
