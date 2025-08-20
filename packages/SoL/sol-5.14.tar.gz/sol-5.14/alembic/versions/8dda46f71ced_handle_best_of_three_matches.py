# :Project:   SoL -- Handle best-of-three matches
# :Created:   2024-03-26 10:26:53.404928
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '8dda46f71ced'
down_revision = '36fa49561cd2'


def upgrade():
    op.add_column('matches', sa.Column('score1_2', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('score2_2', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('score1_3', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('score2_3', sa.SmallInteger(), nullable=True))
    op.add_column('tourneys', sa.Column('matcheskind', sa.VARCHAR(length=10),
                                        nullable=False, server_default='simple'))


def downgrade():
    op.drop_column('tourneys', 'matcheskind')
    op.drop_column('matches', 'score2_3')
    op.drop_column('matches', 'score1_3')
    op.drop_column('matches', 'score2_2')
    op.drop_column('matches', 'score1_2')
