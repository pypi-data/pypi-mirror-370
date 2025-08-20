# :Project:   SoL -- Store per-board misses values, not just the total
# :Created:   2020-04-13 14:22:30.026293
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020 Lele Gaifax
#

from alembic import op
import sqlalchemy as sa


revision = 'ddd5d82c8e56'
down_revision = '918717a067a6'


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
    sa.Column('misses1', sa.SmallInteger(), nullable=True),
    sa.Column('misses2', sa.SmallInteger(), nullable=True),
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
    op.add_column('matches', sa.Column('misses1_1', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_2', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_3', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_4', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_5', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_6', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_7', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses1_8', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_1', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_2', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_3', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_4', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_5', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_6', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_7', sa.SmallInteger(), nullable=True))
    op.add_column('matches', sa.Column('misses2_8', sa.SmallInteger(), nullable=True))

    conn = op.get_bind()
    result = conn.execute('SELECT c.trainingboards, m.idmatch, m.misses1, m.misses2'
                          ' FROM championships AS c'
                          ' JOIN tourneys AS t ON t.idchampionship = c.idchampionship'
                          ' JOIN matches AS m ON m.idtourney = t.idtourney'
                          ' WHERE m.misses1 IS NOT NULL'
                          '    OR m.misses2 IS NOT NULL')
    for trainingboards, idmatch, misses1, misses2 in result:
        stmt = 'UPDATE matches SET '
        first_field = True
        if misses1:
            avg = misses1 // trainingboards
            for i in range(1, trainingboards):
                if first_field:
                    first_field = False
                else:
                    stmt += ', '
                stmt += f'misses1_{i} = {avg}'
                misses1 -= avg
            if first_field:
                first_field = False
            else:
                stmt += ', '
            stmt += f'misses1_{trainingboards} = {misses1}'
        if misses2:
            avg = misses2 // trainingboards
            for i in range(1, trainingboards):
                if first_field:
                    first_field = False
                else:
                    stmt += ', '
                stmt += f'misses2_{i} = {avg}'
                misses2 -= avg
            if first_field:
                first_field = False
            else:
                stmt += ', '
            stmt += f'misses2_{trainingboards} = {misses2}'
        stmt += f' WHERE idmatch = {idmatch}'
        op.execute(stmt)

    with op.batch_alter_table('matches', copy_from=matches_table) as batch:
        batch.drop_column('misses1')
        batch.drop_column('misses2')


def downgrade():
    op.add_column('matches', sa.Column('misses1', sa.SMALLINT(), nullable=True))
    op.add_column('matches', sa.Column('misses2', sa.SMALLINT(), nullable=True))

    conn = op.get_bind()
    result = conn.execute('SELECT c.trainingboards, m.idmatch,'
                          '       m.misses1_1, m.misses1_2, m.misses1_3, m.misses1_4,'
                          '       m.misses1_5, m.misses1_6, m.misses1_7, m.misses1_8,'
                          '       m.misses2_1, m.misses2_2, m.misses2_3, m.misses2_4,'
                          '       m.misses2_5, m.misses2_6, m.misses2_7, m.misses2_8'
                          ' FROM championships AS c'
                          ' JOIN tourneys AS t ON t.idchampionship = c.idchampionship'
                          ' JOIN matches AS m ON m.idtourney = t.idtourney'
                          ' WHERE m.misses1_1 IS NOT NULL'
                          '    OR m.misses2_1 IS NOT NULL')
    for (trainingboards, idmatch,
         misses1_1, misses1_2, misses1_3, misses1_4,
         misses1_5, misses1_6, misses1_7, misses1_8,
         misses2_1, misses2_2, misses2_3, misses2_4,
         misses2_5, misses2_6, misses2_7, misses2_8) in result:
        misses1 = ((misses1_1 or 0) +
                   (misses1_2 or 0) +
                   (misses1_3 or 0) +
                   (misses1_4 or 0) +
                   (misses1_5 or 0) +
                   (misses1_6 or 0) +
                   (misses1_7 or 0) +
                   (misses1_8 or 0))
        misses2 = ((misses2_1 or 0) +
                   (misses2_2 or 0) +
                   (misses2_3 or 0) +
                   (misses2_4 or 0) +
                   (misses2_5 or 0) +
                   (misses2_6 or 0) +
                   (misses2_7 or 0) +
                   (misses2_8 or 0))
        stmt = (f'UPDATE matches SET misses1 = {misses1}, misses2 = {misses2}'
                ' WHERE idmatch = {idmatch}')
        op.execute(stmt)

    with op.batch_alter_table('matches', copy_from=matches_table) as batch:
        batch.drop_column('misses2_8')
        batch.drop_column('misses2_7')
        batch.drop_column('misses2_6')
        batch.drop_column('misses2_5')
        batch.drop_column('misses2_4')
        batch.drop_column('misses2_3')
        batch.drop_column('misses2_2')
        batch.drop_column('misses2_1')
        batch.drop_column('misses1_8')
        batch.drop_column('misses1_7')
        batch.drop_column('misses1_6')
        batch.drop_column('misses1_5')
        batch.drop_column('misses1_4')
        batch.drop_column('misses1_3')
        batch.drop_column('misses1_2')
        batch.drop_column('misses1_1')
