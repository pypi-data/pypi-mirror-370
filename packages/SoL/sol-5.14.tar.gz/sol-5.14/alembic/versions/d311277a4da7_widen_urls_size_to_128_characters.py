# :Project:   SoL -- Widen URLs size to 128 characters
# :Created:   2020-04-13 13:18:50.895306
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'd311277a4da7'
down_revision = None


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('clubs') as batch:
        batch.alter_column('siteurl',
                           existing_type=sa.VARCHAR(length=50),
                           type_=sa.VARCHAR(length=128))


def downgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table('clubs') as batch:
        batch.alter_column('siteurl',
                           existing_type=sa.VARCHAR(length=128),
                           type_=sa.VARCHAR(length=50))
