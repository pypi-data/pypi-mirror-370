# -*- coding: utf-8 -*-
# :Project:   SoL -- Tourney entity tests
# :Created:   ven 06 lug 2018 16:22:49 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2022, 2024 Lele Gaifax
#

from datetime import date, datetime
from os import fspath
from pathlib import Path
from random import randint

import pytest
from sqlalchemy.exc import NoResultFound

from sol.models import Rate, Tourney
from sol.models.bio import load_sol
from sol.models.errors import OperationAborted
from sol.models.tourney import NoMoreCombinationsError


class FakeCompetitor:
    def __init__(self, id, points, nationality='ITA'):
        self.id = id
        self.points = points
        self.nationality = nationality

    def __repr__(self):
        return f'<Competitor "{self.id}" points={self.points} nationality={self.nationality}>'


def test_base(tourney_first, tourney_simple, championship_current):
    assert tourney_first.championship is championship_current
    assert len(tourney_first.competitors) == 6
    assert len(tourney_simple.competitors) == 0


def test_owned(tourney_first, user_lele):
    assert tourney_first.owner is user_lele


def test_first_turn(tourney_second):
    assert tourney_second.matches == []
    tourney_second.updateRanking()
    tourney_second.makeNextTurn()
    assert len(tourney_second.matches) == (len(tourney_second.competitors) + 1) // 2


def test_next_turn(tourney_first):
    tourney_first.prized = False
    lastturn = tourney_first.currentturn
    tourney_first.updateRanking()
    tourney_first.makeNextTurn()
    assert tourney_first.currentturn == lastturn + 1
    assert len(tourney_first.matches) == 12
    with pytest.raises(OperationAborted):
        tourney_first.makeNextTurn()
    lastturn = tourney_first.currentturn
    for m in tourney_first.matches:
        if m.turn == lastturn:
            m.score1 = randint(1, 25)
            m.score2 = randint(1, 25)
    tourney_first.updateRanking()
    tourney_first.makeNextTurn()
    assert tourney_first.currentturn == lastturn + 1
    assert tourney_first.rankedturn == lastturn
    assert len(tourney_first.matches) == 15
    # Here we cannot generate the next turn, because there are non-scored matches
    with pytest.raises(OperationAborted):
        tourney_first.updateRanking()
    # The ranking should not fail, just ignore the not yet scored turn
    tourney_first.ranking
    assert tourney_first.currentturn == tourney_first.rankedturn + 1


def test_next_turn_few_players(session, tourney_apr24, player_lele):
    tourney_apr24.updateRanking()
    best = tourney_apr24.ranking[0]
    session.flush()
    assert best.player1 is player_lele
    assert len(tourney_apr24.matches) == 20

    lastturn = tourney_apr24.currentturn
    tourney_apr24.updateRanking()
    tourney_apr24.makeNextTurn()
    assert tourney_apr24.currentturn == lastturn + 1
    assert len(tourney_apr24.matches) == 24


def test_odd(tourney_odd):
    assert tourney_odd.matches == []
    tourney_odd.updateRanking()
    tourney_odd.makeNextTurn()
    assert len(tourney_odd.matches) == (len(tourney_odd.competitors) + 1) // 2
    assert len([m for m in tourney_odd.matches if m.competitor2 is None]) == 1
    assert [m for m in tourney_odd.matches if m.competitor2 is None][
        0
    ].score1 == tourney_odd.phantomscore
    assert tourney_odd.matches[-1].competitor2 is None
    for m in tourney_odd.matches:
        if m.turn == tourney_odd.currentturn:
            m.score1 = randint(1, 25)
            m.score2 = 0
    tourney_odd.updateRanking()
    tourney_odd.makeNextTurn()
    assert len(tourney_odd.matches) == (len(tourney_odd.competitors) + 1)
    assert len([m for m in tourney_odd.matches if m.competitor2 is None]) == 2
    with pytest.raises(OperationAborted) as e:
        tourney_odd.updateRanking()
    assert 'without result' in str(e.value)


def test_dazed_odd(tourney_dazed_odd):
    assert tourney_dazed_odd.matches == []
    nboards = (len(tourney_dazed_odd.competitors) + 1) // 2
    for turn in range(1, 4):
        tourney_dazed_odd.updateRanking()
        tourney_dazed_odd.makeNextTurn()
        assert len(tourney_dazed_odd.matches) == nboards * turn
        assert (
            len([m for m in tourney_dazed_odd.matches if m.competitor2 is None]) == turn
        )
        assert [m for m in tourney_dazed_odd.matches if m.competitor2 is None][
            0
        ].score1 == tourney_dazed_odd.phantomscore
        assert tourney_dazed_odd.matches[-1].competitor2 is None
        for m in tourney_dazed_odd.matches:
            if m.turn == tourney_dazed_odd.currentturn and m.competitor2 is not None:
                m.score1 = 10
                m.score2 = 0
    tourney_dazed_odd.updateRanking()
    with pytest.raises(OperationAborted):
        tourney_dazed_odd.makeNextTurn()


def test_no_matches(tourney_odd):
    assert tourney_odd.matches == []
    # force update
    tourney_odd.rankedturn = -1
    ranking = tourney_odd.ranking
    assert len(ranking) == len(tourney_odd.competitors)


def test_dazed_iterator():
    a = FakeCompetitor('A', 10)  # 0
    b = FakeCompetitor('B', 10)  # 1
    c = FakeCompetitor('C', 10)  # 2
    d = FakeCompetitor('D', 10)  # 3
    e = FakeCompetitor('E', 10)  # 4
    f = FakeCompetitor('F', 9)  # 5
    g = FakeCompetitor('G', 8)  # 6
    h = FakeCompetitor('H', 8)  # 7

    ranking = [a, b, c, d, e, f, g, h]
    done = {(a, g), (g, a), (b, e), (e, b), (c, d), (d, c), (f, h), (h, f)}

    t = Tourney(rankedturn=1, delaycompatriotpairing=0)
    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, e, f, b, c, h]
    assert order == expected


def test_dazed_iterator_initial_even():
    a = FakeCompetitor('A', 0)  # 0
    b = FakeCompetitor('B', 0)  # 1
    c = FakeCompetitor('C', 0)  # 2
    d = FakeCompetitor('D', 0)  # 3
    e = FakeCompetitor('E', 0)  # 4
    f = FakeCompetitor('F', 0)  # 5
    g = FakeCompetitor('G', 0)  # 6
    h = FakeCompetitor('H', 0)  # 7

    ranking = [a, b, c, d, e, f, g, h]
    done = set()

    t = Tourney(rankedturn=0, delaycompatriotpairing=0)
    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [e, f, g, h, b, c, d]
    assert order == expected


def test_dazed_iterator_initial_odd():
    a = FakeCompetitor('A', 0)  # 0
    b = FakeCompetitor('B', 0)  # 1
    c = FakeCompetitor('C', 0)  # 2
    d = FakeCompetitor('D', 0)  # 3
    e = FakeCompetitor('E', 0)  # 4
    f = FakeCompetitor('F', 0)  # 5
    g = FakeCompetitor('G', 0)  # 6

    ranking = [a, b, c, d, e, f, g]
    done = set()

    t = Tourney(rankedturn=0, delaycompatriotpairing=0)
    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, e, f, g, b, c]
    assert order == expected


def test_staggered_iterator():
    ranking = [FakeCompetitor('A%d' % i, 0) for i in range(50)]
    done = set()

    t = Tourney(rankedturn=0, delaycompatriotpairing=0)
    order = list(Tourney.SwissStaggeredVisitor(t, ranking[0], ranking, done))
    assert order == ranking[25:50] + ranking[1:25]


def test_staggered_iterator_less_than_50():
    a = FakeCompetitor('A', 0)  # 0
    b = FakeCompetitor('B', 0)  # 1
    c = FakeCompetitor('C', 0)  # 2
    d = FakeCompetitor('D', 0)  # 3
    e = FakeCompetitor('E', 0)  # 4
    f = FakeCompetitor('F', 0)  # 5
    g = FakeCompetitor('G', 0)  # 6

    ranking = [a, b, c, d, e, f, g]

    t = Tourney(rankedturn=0, delaycompatriotpairing=0)
    order = list(Tourney.SwissStaggeredVisitor(t, a, ranking, set()))
    expected = list(Tourney.SwissDazedVisitor(t, a, ranking, set()))
    assert order == expected


def test_serial_iterator():
    a = FakeCompetitor('A', 10)  # 0
    b = FakeCompetitor('B', 10)  # 1
    c = FakeCompetitor('C', 10)  # 2
    d = FakeCompetitor('D', 10)  # 3
    e = FakeCompetitor('E', 10)  # 4
    f = FakeCompetitor('F', 9)  # 5
    g = FakeCompetitor('G', 8)  # 6
    h = FakeCompetitor('H', 8)  # 7

    ranking = [a, b, c, d, e, f, g, h]
    done = {(a, f), (f, a), (b, e), (e, b), (c, d), (d, c), (g, h), (h, g)}

    t = Tourney(rankedturn=1, delaycompatriotpairing=0)
    order = Tourney.SwissSerialVisitor(t, a, ranking, done)
    order = list(order)
    expected = [b, c, d, e, g, h]
    assert order == expected


def test_serial_iterator_delay_compatriots():
    a = FakeCompetitor('A', 10, 'ITA')  # 0
    b = FakeCompetitor('B', 10, 'ITA')  # 1
    c = FakeCompetitor('C', 10, 'ITA')  # 2
    d = FakeCompetitor('D', 10, 'FRA')  # 3
    e = FakeCompetitor('E', 8, 'ITA')  # 4
    f = FakeCompetitor('F', 8, 'ITA')  # 5
    g = FakeCompetitor('G', 8, 'ITA')  # 6
    h = FakeCompetitor('H', 8, 'FRA')  # 7

    ranking = [a, b, c, d, e, f, g, h]
    done = {(a, f), (f, a), (b, e), (e, b), (c, d), (d, c), (g, h), (h, g)}

    t = Tourney(rankedturn=1, delaycompatriotpairing=1)

    order = Tourney.SwissSerialVisitor(t, a, ranking, done)
    order = list(order)
    expected = [b, c, d, e, g, h]
    assert order == expected

    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [c, d, b, e, g, h]
    assert order == expected

    t = Tourney(rankedturn=1, delaycompatriotpairing=2)

    order = Tourney.SwissSerialVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, b, c, h, e, g]
    assert order == expected

    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, c, b, h, e, g]
    assert order == expected


def test_serial_iterator_delay_compatriots_odd():
    a = FakeCompetitor('A', 10, 'ITA')  # 0
    b = FakeCompetitor('B', 10, 'ITA')  # 1
    c = FakeCompetitor('C', 10, 'ITA')  # 2
    d = FakeCompetitor('D', 10, 'FRA')  # 3
    e = FakeCompetitor('E', 10, 'ITA')  # 4
    f = FakeCompetitor('F', 9, 'ITA')  # 5
    g = FakeCompetitor('G', 8, 'ITA')  # 6
    h = FakeCompetitor('H', 8, 'FRA')  # 7
    i = FakeCompetitor('I', 8, 'ITA')  # 8

    ranking = [a, b, c, d, e, f, g, h, i, None]
    done = {(a, f), (f, a), (b, e), (e, b), (c, d), (d, c), (g, h), (h, g)}

    t = Tourney(rankedturn=1, delaycompatriotpairing=2)

    order = Tourney.SwissSerialVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, b, c, e, h, g, i, None]
    assert order == expected

    order = Tourney.SwissDazedVisitor(t, a, ranking, done)
    order = list(order)
    expected = [d, e, b, c, h, g, i, None]
    assert order == expected


def test_combine(tourney_second):
    c = [1, 2, 3, 4, 5, 6]
    d = set()
    a = []
    n = tourney_second._combine(c, d)
    while n:
        a.append(n)
        for m in n:
            c1, c2 = m
            d.add((c1, c2))
            d.add((c2, c1))
        n = tourney_second._combine(c, d)
    assert len(a) == 5


def test_asis_prizes(session, tourney_first):
    tourney_first.championship.prizes = 'asis'
    tourney_first.prized = False
    tourney_first.updateRanking()
    tourney_first.assignPrizes()
    session.flush()
    prizes = []
    for c in tourney_first.ranking:
        prizes.append(c.prize)
    assert list(range(len(prizes), 0, -1)) == prizes


def test_fixed_prizes(session, tourney_first):
    tourney_first.championship.prizes = 'fixed'
    tourney_first.prized = False
    tourney_first.updateRanking()
    tourney_first.assignPrizes()
    session.flush()
    dates, cship = tourney_first.championship.ranking()
    assert len(dates) == len(
        [st for st in tourney_first.championship.tourneys if st.prized]
    )
    assert len(cship) == 6
    assert cship[0][1] == 18

    with pytest.raises(OperationAborted):
        tourney_first.updateRanking()

    with pytest.raises(OperationAborted) as e:
        tourney_first.makeFinalTurn()
    assert 'Cannot generate final turn after prize-giving' in str(e.value)


def test_fixed40_prizes(session, tourney_first):
    tourney_first.championship.prizes = 'fixed40'
    tourney_first.prized = False
    tourney_first.updateRanking()
    tourney_first.assignPrizes()
    session.flush()
    r = tourney_first.ranking
    assert r[0].prize == 1000
    assert r[1].prize == 900
    assert r[2].prize == 800
    assert r[3].prize == 750


def test_millesimal_prizes(session, tourney_third):
    tourney_third.championship.prizes = 'millesimal'
    tourney_third.prized = False
    tourney_third.updateRanking()
    tourney_third.assignPrizes()
    session.flush()
    dates, cship = tourney_third.championship.ranking()
    assert len(dates) == len(
        [st for st in tourney_third.championship.tourneys if st.prized]
    )
    assert len(cship) == len(tourney_third.competitors)
    r = tourney_third.ranking
    assert r[0].prize == 1000
    assert r[1].prize == 750
    assert r[2].prize == 500
    assert r[3].prize == 250


def test_centesimal_prizes(tourney_first):
    tourney_first.championship.prizes = 'centesimal'
    tourney_first.prized = False
    tourney_first.updateRanking()
    tourney_first.assignPrizes()
    assert tourney_first.ranking[0].prize == 100
    assert tourney_first.ranking[-1].prize == 1


def test_no_finals(tourney_first):
    with pytest.raises(OperationAborted) as e:
        tourney_first.makeFinalTurn()
    assert 'not considered' in str(e.value)


def test_replay(session, tourney_third):
    d = datetime(2018, 7, 16, 10, 10, 0)
    tourney_third.replay(d)
    session.flush()
    n = (
        session.query(Tourney).filter_by(
            idchampionship=tourney_third.idchampionship, date=d.date()
        )
    ).one()
    assert len(tourney_third.competitors) == len(n.competitors)


def test_replay_closed_championship(session, tourney_second):
    n = tourney_second.replay(date(2018, 7, 6))
    session.flush()
    assert n.championship.description == 'SCR 2010 (test)'


def test_replay_no_next_championship(tourney_closed):
    with pytest.raises(OperationAborted) as e:
        tourney_closed.replay(date(2018, 7, 28))
    assert 'no open championships' in str(e.value)
    with pytest.raises(OperationAborted) as e:
        tourney_closed.createKnockout(date(2018, 7, 28), 8)
    assert 'no open championships' in str(e.value)


def test_replay_double(session, tourney_double):
    n = tourney_double.replay(date(2018, 7, 7))
    session.flush()
    assert n.championship is tourney_double.championship


def test_forbidden_replay(session, tourney_rated_empty, user_lele):
    with pytest.raises(OperationAborted) as e:
        tourney_rated_empty.replay(date(2024, 4, 24), user_lele.iduser)
    assert 'You are not allowed' in str(e.value)
    assert 'rating level inaccessible by you' in str(e.value)


def test_phantom_match_last(tourney_odd):
    ncompetitors = len(tourney_odd.competitors)
    assert ncompetitors % 2 == 1
    assert tourney_odd.matches == []
    for turn in range(1, ncompetitors - 1):
        tourney_odd.updateRanking()
        tourney_odd.makeNextTurn()
        newmatches = [
            m for m in tourney_odd.matches if m.turn == tourney_odd.currentturn
        ]
        newmatches.sort(key=lambda m: m.board)
        assert newmatches[-1].competitor2 is None
        assert newmatches[-1].board == (ncompetitors + 1) / 2
        for m in newmatches:
            if m.competitor2 is not None:
                m.score1 = 10
                m.score2 = 0


def test_update_default(tourney_first):
    with pytest.raises(OperationAborted):
        result = tourney_first.update(
            dict(couplings='foo', location='bar', currentturn=1, prized=True), 'admin'
        )

    result = tourney_first.update(
        dict(couplings='dazed', location='bar', currentturn=1, prized=True), 'admin'
    )

    assert result == dict(
        couplings=('serial', 'dazed'),
        location=(None, 'bar'),
        currentturn=(3, 1),
        prized=(False, True),
    )


def test_update_missing(tourney_first):
    with pytest.raises(OperationAborted):
        tourney_first.update(
            dict(couplings='foo', location='bar', currentturn=1, prized=True),
            'admin',
            missing_only=True,
        )

    result = tourney_first.update(
        dict(couplings='dazed', location='bar', currentturn=1, prized=True),
        'admin',
        missing_only=True,
    )

    assert result == dict(location=(None, 'bar'), prized=(False, True))


def test_all_against_all(session):
    # SoL2 was able to generate only three rounds

    testdir = Path(__file__).parent.parent
    fullname = testdir / 'scr' / 'Campionato_SCR_2015_2016-2016-04-24+3.sol.gz'
    tourneys, skipped = load_sol(session, fspath(fullname))

    t = tourneys[0]

    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    t.resetPrizes()
    session.flush()

    # switch to all-against-all mode, to generate remaining three rounds
    # with only two boards

    t.couplings = 'all'

    t.makeNextTurn()

    nboards = 0
    lastturn = t.currentturn
    for m in t.matches:
        if m.turn == lastturn:
            m.score1 = randint(1, 25)
            m.score2 = randint(1, 25)
            nboards += 1

    assert nboards == 2

    t.updateRanking()
    t.makeNextTurn()

    nboards = 0
    lastturn = t.currentturn
    for m in t.matches:
        if m.turn == lastturn:
            m.score1 = randint(1, 25)
            m.score2 = randint(1, 25)
            nboards += 1

    assert nboards == 2

    t.updateRanking()
    t.makeNextTurn()

    nboards = 0
    lastturn = t.currentturn
    for m in t.matches:
        if m.turn == lastturn:
            m.score1 = randint(1, 25)
            m.score2 = randint(1, 25)
            nboards += 1

    with pytest.raises(OperationAborted):
        t.makeNextTurn()


def test_ranking(tourney_first, player_blond):
    tourney_first.updateRanking()
    ranking = tourney_first.ranking
    assert len(ranking) == 6
    first = ranking[0]
    assert first.player1 is player_blond
    assert first.points == 5
    assert first.bucholz == 7


def test_compute_ranking(tourney_first, player_blond):
    c, r = tourney_first.computeRanking(1)[0]
    assert c.player1 is player_blond
    assert r.points == 2
    assert r.bucholz == 0
    assert r.netscore == 20

    c, r = tourney_first.computeRanking(2)[0]
    assert c.player1 is player_blond
    assert r.points == 4
    assert r.bucholz == 1
    assert r.netscore == 22

    c, r = tourney_first.computeRanking(3)[0]
    firstr = tourney_first.ranking[0]
    assert c.player1 is firstr.player1
    assert c.points == firstr.points
    assert c.bucholz == firstr.bucholz
    assert c.netscore == firstr.netscore


def test_reset_prizes(session, tourney_first):
    modified = tourney_first.modified
    tourney_first.updateRanking()
    tourney_first.assignPrizes()
    session.flush()
    r = tourney_first.ranking
    assert r[0].prize == 18
    assert r[-1].prize == 11
    tourney_first.resetPrizes()
    session.flush()
    assert tourney_first.prized is False
    r = tourney_first.ranking
    assert r[0].prize == 0
    assert r[-1].prize == 0
    assert tourney_first.modified > modified


def test_reset_rated_tourney_prizes(session, tourney_rated):
    oneplayerid = tourney_rated.competitors[0].idplayer1
    tourney_rated.updateRanking()
    tourney_rated.assignPrizes()
    session.flush()
    tourney_rated.resetPrizes()
    session.flush()
    with pytest.raises(NoResultFound):
        session.query(Rate).filter_by(
            idplayer=oneplayerid, date=tourney_rated.date
        ).one()


def test_knockout(tourney_knockout):
    assert tourney_knockout.matches == []
    totmatches = 0
    for turn in range(1, 7):
        tourney_knockout.updateRanking()
        tourney_knockout.makeNextTurn()
        totmatches += 2 ** (6 - turn)
        assert tourney_knockout.currentturn == turn
        assert len(tourney_knockout.matches) == totmatches
        matches = [m for m in tourney_knockout.matches if m.turn == turn]
        assert len(matches) == 2 ** (6 - turn)

        if turn == 1:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [
                (1, 64),
                (32, 33),
                (17, 48),
                (16, 49),
                (9, 56),
                (24, 41),
                (25, 40),
                (8, 57),
                (5, 60),
                (28, 37),
                (21, 44),
                (12, 53),
                (13, 52),
                (20, 45),
                (29, 36),
                (4, 61),
                (3, 62),
                (30, 35),
                (19, 46),
                (14, 51),
                (11, 54),
                (22, 43),
                (27, 38),
                (6, 59),
                (7, 58),
                (26, 39),
                (23, 42),
                (10, 55),
                (15, 50),
                (18, 47),
                (31, 34),
                (2, 63),
            ]
        elif turn == 2:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [
                (1, 32),
                (16, 17),
                (9, 24),
                (8, 25),
                (5, 28),
                (12, 21),
                (13, 20),
                (4, 29),
                (3, 30),
                (14, 19),
                (11, 22),
                (6, 27),
                (7, 26),
                (10, 23),
                (15, 18),
                (2, 31),
            ]
        elif turn == 3:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [(1, 16), (8, 9), (5, 12), (4, 13), (3, 14), (6, 11), (7, 10), (2, 15)]
        elif turn == 4:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [(1, 8), (4, 5), (3, 6), (2, 7)]
        elif turn == 5:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [(1, 4), (2, 3)]
        elif turn == 6:
            assert [
                (m.competitor1.position, m.competitor2.position) for m in matches
            ] == [(1, 2)]

        for m in matches:
            m.score1 = 10
            m.score2 = 5

    tourney_knockout.updateRanking()
    with pytest.raises(OperationAborted):
        tourney_knockout.makeNextTurn()


def test_best_of_3_knockout(session, tourney_knockout_bot):
    try:
        tourney_knockout_bot.matches = []
        for turn in range(1, 4):
            tourney_knockout_bot.updateRanking()
            tourney_knockout_bot.makeNextTurn()
            session.flush()
            assert tourney_knockout_bot.currentturn == turn
            matches = [m for m in tourney_knockout_bot.matches if m.turn == turn]
            assert len(matches) == 2 ** (3 - turn)

            if turn == 2:
                assert [
                    (m.competitor1.position, m.competitor2.position) for m in matches
                ] == [(1, 4), (2, 3)]
            elif turn == 3:
                assert [
                    (m.competitor1.position, m.competitor2.position) for m in matches
                ] == [(1, 2)]

            for match in matches:
                match.score1 = 10
                match.score2 = 5
                match.score1_2 = 10
                match.score2_2 = 5

        tourney_knockout_bot.updateRanking()
        with pytest.raises(OperationAborted):
            tourney_knockout_bot.makeNextTurn()
    finally:
        session.rollback()


def test_knockout_odd(tourney_knockout_odd):
    assert tourney_knockout_odd.matches == []
    totmatches = 0
    totmatches = 0
    for turn in range(1, 4):
        tourney_knockout_odd.updateRanking()
        tourney_knockout_odd.makeNextTurn()
        totmatches += 2 ** (3 - turn)
        assert tourney_knockout_odd.currentturn == turn
        assert len(tourney_knockout_odd.matches) == totmatches
        matches = [m for m in tourney_knockout_odd.matches if m.turn == turn]
        assert len(matches) == 2 ** (3 - turn)

        if turn == 1:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, None), (1550, 1505), (1600, 1400), (1700, 1300)]
        elif turn == 2:
            assert [(m.competitor1.rate, m.competitor2.rate) for m in matches] == [
                (1900, 1550),
                (1700, 1600),
            ]
        elif turn == 3:
            assert [(m.competitor1.rate, m.competitor2.rate) for m in matches] == [
                (1900, 1700)
            ]

        for m in matches:
            m.score1 = 10
            m.score2 = 5

    tourney_knockout_odd.updateRanking()
    with pytest.raises(OperationAborted):
        tourney_knockout_odd.makeNextTurn()


def test_best_of_3_knockout_retired_competitor(session, tourney_knockout_bot):
    try:
        tourney_knockout_bot.matches = []
        tourney_knockout_bot.updateRanking()
        tourney_knockout_bot.makeNextTurn()
        session.flush()
        matches = [m for m in tourney_knockout_bot.matches if m.turn == 1]
        for match in matches:
            match.score1 = 10
            match.score2 = 5
            match.score1_2 = 10
            match.score2_2 = 5
        session.flush()
        tourney_knockout_bot.updateRanking()
        retiredcomp = tourney_knockout_bot.competitors[0].idcompetitor
        tourney_knockout_bot.competitors[0].retired = True
        tourney_knockout_bot.makeNextTurn()
        session.flush()
        matches = [m for m in tourney_knockout_bot.matches if m.turn == 2]
        retmatch = [m for m in matches if m.idcompetitor1 == retiredcomp][0]
        assert retmatch.score1 == 0
        assert retmatch.score2 == 25
        assert retmatch.score1_2 == 0
        assert retmatch.score2_2 == 25
        for match in matches:
            if match is retmatch:
                continue
            match.score1 = 10
            match.score2 = 5
            match.score1_2 = 10
            match.score2_2 = 5
        session.flush()
        tourney_knockout_bot.updateRanking()
        retiredcomp2 = tourney_knockout_bot.competitors[3].idcompetitor
        tourney_knockout_bot.competitors[3].retired = True
        tourney_knockout_bot.makeNextTurn()
        session.flush()
        matches = [m for m in tourney_knockout_bot.matches if m.turn == 3]
        retmatch2 = [m for m in matches if m.idcompetitor2 == retiredcomp2][0]
        assert retmatch2.score1 == 25
        assert retmatch2.score2 == 0
        assert retmatch2.score1_2 == 25
        assert retmatch2.score2_2 == 0
    finally:
        session.rollback()


def test_corona_all_against_all(tourney_corona_all_against_all):
    from math import factorial as f

    assert tourney_corona_all_against_all.matches == []
    assert tourney_corona_all_against_all.rankedturn == 0
    assert tourney_corona_all_against_all.currentturn == 0

    tourney_corona_all_against_all.updateRanking()
    assert tourney_corona_all_against_all.rankedturn == 0
    assert tourney_corona_all_against_all.currentturn == 0

    tourney_corona_all_against_all.makeNextTurn()
    n = len(tourney_corona_all_against_all.competitors)
    k = 2
    assert len(tourney_corona_all_against_all.matches) == f(n) / (f(k) * f(n - k))

    assert tourney_corona_all_against_all.rankedturn == 0
    nturns = max(m.turn for m in tourney_corona_all_against_all.matches)
    for cturn in range(1, nturns):
        assert cturn == tourney_corona_all_against_all.currentturn
        for m in tourney_corona_all_against_all.matches:
            if m.turn > cturn:
                break
            elif m.turn == cturn:
                m.score1 = 1
                m.score2 = 2

        tourney_corona_all_against_all.updateRanking()
        assert tourney_corona_all_against_all.rankedturn == cturn

    for m in tourney_corona_all_against_all.matches:
        if m.turn == nturns:
            m.score1 = 2
            m.score2 = 1

    tourney_corona_all_against_all.updateRanking()
    assert tourney_corona_all_against_all.rankedturn == nturns
    assert tourney_corona_all_against_all.currentturn == nturns


def test_corona_all_against_all_odd(tourney_corona_all_against_all_odd):
    from math import factorial as f

    tourney_corona_all_against_all_odd.makeNextTurn()
    n = len(tourney_corona_all_against_all_odd.competitors)
    assert n % 2
    n += 1
    k = 2
    assert len(tourney_corona_all_against_all_odd.matches) == f(n) / (f(k) * f(n - k))


def test_roundrobin_all(session, tourney_rated_no_turns_odd):
    t = tourney_rated_no_turns_odd
    t.system = 'roundrobin'
    t.couplings = 'all'
    assert not t.matches
    assert len(t.competitors) == 7
    for turn in range(1, 8):
        t.updateRanking()
        t.makeNextTurn()
        matches = [m for m in t.matches if m.turn == turn]
        matches.sort(key=lambda m: -m.competitor1.rate)
        if turn == 1:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1300), (1800, 1700), (1600, None), (1505, 1400)]
        elif turn == 2:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1400), (1700, None), (1600, 1800), (1505, 1300)]
        elif turn == 3:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1505), (1800, None), (1600, 1700), (1400, 1300)]
        elif turn == 4:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, None), (1800, 1505), (1700, 1400), (1600, 1300)]
        elif turn == 5:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1600), (1800, 1400), (1700, 1505), (1300, None)]
        elif turn == 6:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1700), (1800, 1300), (1600, 1505), (1400, None)]
        elif turn == 7:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1800), (1700, 1300), (1600, 1400), (1505, None)]

        for m in matches:
            m.score1 = 10
            m.score2 = 5

    with pytest.raises(OperationAborted):
        t.updateRanking()
        t.makeNextTurn()

    session.rollback()


def test_roundrobin_circle(session, tourney_rated_no_turns_odd):
    t = tourney_rated_no_turns_odd
    t.system = 'roundrobin'
    t.couplings = 'circle'
    assert not t.matches
    assert len(t.competitors) == 7
    for turn in range(1, 8):
        t.updateRanking()
        t.makeNextTurn()
        matches = [m for m in t.matches if m.turn == turn]
        matches.sort(key=lambda m: -m.competitor1.rate)
        if turn == 1:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, None), (1800, 1300), (1700, 1400), (1600, 1505)]
        elif turn == 2:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1300), (1800, 1505), (1700, 1600), (1400, None)]
        elif turn == 3:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1400), (1800, 1700), (1600, None), (1505, 1300)]
        elif turn == 4:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1505), (1800, None), (1700, 1300), (1600, 1400)]
        elif turn == 5:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1600), (1800, 1400), (1700, 1505), (1300, None)]
        elif turn == 6:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1700), (1800, 1600), (1505, None), (1400, 1300)]
        elif turn == 7:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1800), (1700, None), (1600, 1300), (1505, 1400)]

        for m in matches:
            m.score1 = 10
            m.score2 = 5

    with pytest.raises(OperationAborted):
        t.updateRanking()
        t.makeNextTurn()

    session.rollback()


def test_roundrobin_seeds(session, tourney_rated_no_turns_odd):
    t = tourney_rated_no_turns_odd
    t.system = 'roundrobin'
    t.couplings = 'seeds'
    assert not t.matches
    assert len(t.competitors) == 7
    for turn in range(1, 8):
        t.updateRanking()
        t.makeNextTurn()
        matches = [m for m in t.matches if m.turn == turn]
        matches.sort(key=lambda m: -m.competitor1.rate)
        if turn == 1:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, None), (1800, 1300), (1700, 1400), (1600, 1505)]
        elif turn == 2:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1300), (1800, None), (1700, 1505), (1600, 1400)]
        elif turn == 3:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1400), (1800, 1505), (1700, None), (1600, 1300)]
        elif turn == 4:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1505), (1800, 1400), (1700, 1300), (1600, None)]
        elif turn == 5:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1600), (1800, 1700), (1505, None), (1400, 1300)]
        elif turn == 6:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1700), (1800, 1600), (1505, 1300), (1400, None)]
        elif turn == 7:
            assert [
                (m.competitor1.rate, m.competitor2.rate if m.competitor2 else None)
                for m in matches
            ] == [(1900, 1800), (1700, 1600), (1505, 1400), (1300, None)]

        for m in matches:
            m.score1 = 10
            m.score2 = 5

    with pytest.raises(OperationAborted):
        t.updateRanking()
        t.makeNextTurn()

    session.rollback()


def test_rates_ambiguities(session, tourney_rated_no_turns_odd):
    t = tourney_rated_no_turns_odd
    t.system = 'roundrobin'
    t.couplings = 'seeds'
    t.competitors[0]._rate = 42
    t.competitors[1]._rate = 42
    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    t.competitors[0]._rate = 41
    t.competitors[1]._rate = 42

    for seed, c in enumerate(t.competitors, 1):
        c.position = 0
    t.competitors[1].position = 42
    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    for c in t.competitors:
        c.position = 42
    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    t.idrating = None
    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    for seed, c in enumerate(t.competitors, 1):
        c.position = 0
    with pytest.raises(OperationAborted):
        t.makeNextTurn()

    for seed, c in enumerate(t.competitors, 1):
        c.position = seed
    t.competitors[2].position = 1
    with pytest.raises(OperationAborted):
        t.makeNextTurn()
