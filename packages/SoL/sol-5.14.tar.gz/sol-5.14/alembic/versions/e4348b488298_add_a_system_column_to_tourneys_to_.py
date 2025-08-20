# :Project:   SoL -- Add a system column to tourneys, to implement the knockout type
# :Created:   2020-04-16 16:05:52.098030
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'e4348b488298'
down_revision = 'ddd5d82c8e56'


def upgrade():
    op.add_column('tourneys', sa.Column('system', sa.VARCHAR(length=10), nullable=False,
                                        server_default='swiss'))


def downgrade():
    op.drop_column('tourneys', 'system')
