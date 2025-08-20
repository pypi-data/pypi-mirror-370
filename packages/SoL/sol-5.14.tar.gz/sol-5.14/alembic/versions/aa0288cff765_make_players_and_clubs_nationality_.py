# :Project:   SoL -- Make players and clubs nationality mandatory
# :Created:   2023-01-14 15:00:17.774131
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2023 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'aa0288cff765'
down_revision = '1e49ee0210d7'


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")

    op.execute("UPDATE clubs SET nationality='wrl' WHERE nationality IS NULL")
    with op.batch_alter_table('clubs') as batch:
        batch.alter_column('nationality',
                           existing_type=sa.CHAR(length=3),
                           nullable=False)

    op.execute("UPDATE players SET nationality='wrl' WHERE nationality IS NULL")
    with op.batch_alter_table('players') as batch:
        batch.alter_column('nationality',
                           existing_type=sa.CHAR(length=3),
                           nullable=False)


def downgrade():
    with op.batch_alter_table('players') as batch:
        batch.alter_column('nationality',
                           existing_type=sa.CHAR(length=3),
                           nullable=True)

    with op.batch_alter_table('clubs') as batch:
        batch.alter_column('nationality',
                           existing_type=sa.CHAR(length=3),
                           nullable=True)
