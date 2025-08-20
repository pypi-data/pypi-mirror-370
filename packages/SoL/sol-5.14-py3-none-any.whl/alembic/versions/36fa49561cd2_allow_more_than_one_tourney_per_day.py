# :Project:   SoL -- Allow more than one tourney per day
# :Created:   2024-03-18 19:11:49.943641
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from alembic import op


revision = '36fa49561cd2'
down_revision = 'aa0288cff765'


def upgrade():
    op.drop_index('tourneys_uk', table_name='tourneys')
    op.create_index('tourneys_uk', 'tourneys', ['date', 'description', 'idchampionship'],
                    unique=1)


def downgrade():
    op.create_index('tourneys_uk', 'tourneys', ['date', 'idchampionship'], unique=1)
