# :Project:   SoL -- Make delaycompatriotpairing an int instead of a boolean
# :Created:   2024-04-28 12:07:04.561032
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = '4792dcb3da70'
down_revision = 'a67281b72424'


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('tourneys') as batch:
        batch.alter_column('delaycompatriotpairing',
                           existing_type=sa.BOOLEAN(),
                           type_=sa.SmallInteger(),
                           existing_nullable=False)


def downgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('tourneys') as batch:
        batch.alter_column('delaycompatriotpairing',
                           existing_type=sa.SmallInteger(),
                           type_=sa.BOOLEAN(),
                           existing_nullable=False)
