# :Project:   SoL -- Add boards table
# :Created:   2020-04-24 12:23:08.778464
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'ffec21d0a5a0'
down_revision = 'e4348b488298'


# Workaround to a reflection glitch that fails with "partial indexes": use a static snapshot of
# the matches table

matches_table = sa.Table(
    'matches', sa.MetaData(),
    sa.Column('idmatch', sa.Integer(), sa.Sequence('gen_idmatch', optional=True),
              primary_key=True, nullable=False),
    sa.Column('idtourney', sa.Integer(), sa.ForeignKey('tourneys.idtourney',
                                                       name='fk_match_tourney'),
              nullable=False),
    sa.Column('turn', sa.SmallInteger(), nullable=False),
    sa.Column('board', sa.SmallInteger(), nullable=False),
    sa.Column('final', sa.Boolean(), nullable=False, default=False),
    sa.Column('idcompetitor1', sa.Integer(), sa.ForeignKey('competitors.idcompetitor',
                                                           name='fk_match_competitor1'),
              nullable=False),
    sa.Column('idcompetitor2', sa.Integer(), sa.ForeignKey('competitors.idcompetitor',
                                                           name='fk_match_competitor2')),
    sa.Column('score1', sa.SmallInteger(), nullable=False, default=0),
    sa.Column('score2', sa.SmallInteger(), nullable=False, default=0),
    sa.Column('misses1_1', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_2', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_3', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_4', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_5', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_6', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_7', sa.SmallInteger(), nullable=True),
    sa.Column('misses1_8', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_1', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_2', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_3', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_4', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_5', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_6', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_7', sa.SmallInteger(), nullable=True),
    sa.Column('misses2_8', sa.SmallInteger(), nullable=True),
    sa.Index('matches_board', 'idtourney', 'turn', 'board', unique=True),
    sa.Index('matches_c1_vs_c2', 'idtourney', 'idcompetitor1', 'idcompetitor2', unique=True,
             sqlite_where=sa.text("final = 0"))
)


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")

    op.create_table('boards',
                    sa.Column('idboard', sa.Integer(), nullable=False),
                    sa.Column('idmatch', sa.Integer(), nullable=False),
                    sa.Column('number', sa.SmallInteger(), nullable=False),
                    sa.Column('coins1', sa.SmallInteger(), nullable=True),
                    sa.Column('coins2', sa.SmallInteger(), nullable=True),
                    sa.Column('queen', sa.CHAR(length=1), nullable=True),
                    sa.ForeignKeyConstraint(['idmatch'], ['matches.idmatch'],
                                            name='fk_board_match'),
                    sa.PrimaryKeyConstraint('idboard'))
    op.create_index('boards_number', 'boards', ['idmatch', 'number'], unique=True)

    conn = op.get_bind()
    result = conn.execute('SELECT m.idmatch,'
                          ' misses1_1,'
                          ' misses2_1,'
                          ' misses1_2,'
                          ' misses2_2,'
                          ' misses1_3,'
                          ' misses2_3,'
                          ' misses1_4,'
                          ' misses2_4,'
                          ' misses1_5,'
                          ' misses2_5,'
                          ' misses1_6,'
                          ' misses2_6,'
                          ' misses1_7,'
                          ' misses2_7,'
                          ' misses1_8,'
                          ' misses2_8'
                          ' FROM matches AS m'
                          ' WHERE m.misses1_1 IS NOT NULL'
                          '    OR m.misses2_1 IS NOT NULL')
    rows = []
    for match in result:
        row = list(match)
        idmatch = row.pop(0)
        number = 1
        while row:
            coins1 = row.pop(0)
            coins2 = row.pop(0)
            if not coins1 and not coins2:
                break
            rows.append((idmatch, number, coins1, coins2))
            number += 1
    conn.execute('INSERT INTO boards (idmatch, number, coins1, coins2)'
                 ' VALUES (?, ?, ?, ?)', rows)

    with op.batch_alter_table('matches', copy_from=matches_table) as batch:
        batch.drop_column('misses1_1')
        batch.drop_column('misses2_7')
        batch.drop_column('misses1_4')
        batch.drop_column('misses2_4')
        batch.drop_column('misses1_2')
        batch.drop_column('misses2_8')
        batch.drop_column('misses1_7')
        batch.drop_column('misses2_5')
        batch.drop_column('misses1_3')
        batch.drop_column('misses2_2')
        batch.drop_column('misses2_3')
        batch.drop_column('misses1_8')
        batch.drop_column('misses1_6')
        batch.drop_column('misses2_1')
        batch.drop_column('misses1_5')
        batch.drop_column('misses2_6')


def downgrade():
    op.execute("PRAGMA foreign_keys=OFF")

    op.add_column('matches', sa.Column('misses1_1', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_2', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_3', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_4', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_5', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_6', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_7', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses1_8', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_1', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_2', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_3', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_4', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_5', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_6', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_7', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2_8', sa.SMALLINT(), nullable=True))

    conn = op.get_bind()
    result = conn.execute('SELECT b.idmatch, b.number, b.coins1, b.coins2'
                          ' FROM boards AS b')
    bymatchid = {}
    for idmatch, number, coins1, coins2 in result:
        if idmatch in bymatchid:
            match = bymatchid[idmatch]
        else:
            match = bymatchid[idmatch] = {}
        match[f'misses1_{number}'] = coins1
        match[f'misses2_{number}'] = coins2
    for idmatch in bymatchid:
        match = bymatchid[idmatch]
        stmt = 'UPDATE matches SET ' + ','.join(f'{k}={v}' for k, v in match.items())
        op.execute(stmt + f' WHERE idmatch = {idmatch}')

    op.drop_index('boards_number', table_name='boards')
    op.drop_table('boards')
