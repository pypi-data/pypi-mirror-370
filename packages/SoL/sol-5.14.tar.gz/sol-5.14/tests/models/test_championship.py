# -*- coding: utf-8 -*-
# :Project:   SoL -- Championship entity tests
# :Created:   ven 06 lug 2018 14:43:30 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2023, 2024 Lele Gaifax
#

from datetime import date


def test_previous(championship_current, championship_next):
    assert championship_next.previous is championship_current
    assert championship_current.next is championship_next


def test_owned(championship_current, user_lele):
    assert championship_current.owner is user_lele


def test_skip_worst_prize(session, championship_skip_worst, player_picol):
    dates, ranking = championship_skip_worst.ranking()
    assert len(dates) == 0

    t1 = championship_skip_worst.tourneys[0]
    t1.updateRanking()
    t1.assignPrizes()
    session.flush()

    dates, ranking = championship_skip_worst.ranking()
    assert len(dates) == 1
    assert len(ranking) == 2

    first = ranking[0]
    players, prize, prizes, nprizes, skipped = first
    assert players[0] is player_picol
    assert skipped is None

    d = date(2018, 7, 6)
    t2 = t1.replay(d)
    t2.updateRanking()
    t2.makeNextTurn()
    for m in t2.matches:
        m.score1 = 10
        m.score2 = 0
    session.flush()

    t2.updateRanking()
    t2.assignPrizes()
    session.flush()

    dates, ranking = championship_skip_worst.ranking()
    assert len(dates) == 2
    assert len(ranking) == 2

    first = ranking[0]
    players, prize, prizes, nprizes, skipped = first
    assert len(skipped) == 1


def test_tourneys_on_same_date(
    session, championship_current, tourney_second, tourney_second_replica
):
    for tourney in (tourney_second, tourney_second_replica):
        if tourney.prized:
            continue
        for turn in range(1, 4):
            tourney.updateRanking()
            tourney.makeNextTurn()
            for m in tourney.matches:
                if m.turn == tourney.currentturn and m.competitor2 is not None:
                    m.score1 = 10
                    m.score2 = 0
        tourney.updateRanking()
        tourney.assignPrizes()
    session.flush()
    try:
        dates, cship = championship_current.ranking()
        assert len(dates) == 2
        assert dates[0][0] == dates[1][0]
        assert dates[0][1] == tourney_second_replica.description
        assert dates[1][1] == tourney_second.description
        assert len(cship) == 4
        assert len(cship[2]) == 5
        assert len(cship[2][2]) == 2
    finally:
        session.rollback()
