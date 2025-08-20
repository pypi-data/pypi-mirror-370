# -*- coding: utf-8 -*-
# :Project:   SoL -- Tourney's finals behaviours tests
# :Created:   ven 06 lug 2018 21:04:52 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2022, 2023 Lele Gaifax
#

import pytest

from sol.models.errors import OperationAborted


def test_no_finals(tourney_first):
    with pytest.raises(OperationAborted):
        tourney_first.makeFinalTurn()


def test_apr24_finals_same_winners(session, tourney_apr24):
    assert tourney_apr24.firstFinalTurn is None

    tourney_apr24.updateRanking()
    c1, c2, c3, c4 = tourney_apr24.ranking[:4]

    tourney_apr24.makeFinalTurn()
    session.flush()
    assert tourney_apr24.firstFinalTurn == tourney_apr24.currentturn

    finals = [m for m in tourney_apr24.matches if m.final]
    assert len(finals) == 2
    assert finals[0].turn == tourney_apr24.currentturn
    assert tourney_apr24.finalturns is True
    assert tourney_apr24.prized is False
    finals[0].score1 = 10
    finals[1].score2 = 10

    tourney_apr24.updateRanking()
    tourney_apr24.makeNextTurn()
    finals = [m for m in tourney_apr24.matches if m.final]
    assert len(finals) == 4
    finals[2].score1 = 10
    finals[3].score2 = 10

    tourney_apr24.updateRanking()
    assert tourney_apr24.prized is True
    assert tourney_apr24.ranking[:4] == [c1, c2, c4, c3]


def test_apr24_finals_two_and_three(tourney_apr24):
    assert tourney_apr24.prized is False

    tourney_apr24.updateRanking()
    c1, c2, c3, c4 = tourney_apr24.ranking[:4]

    tourney_apr24.makeFinalTurn()
    assert tourney_apr24.prized is False
    finals = [m for m in tourney_apr24.matches if m.final]
    finals[0].score1 = 10
    finals[1].score2 = 10

    tourney_apr24.updateRanking()
    tourney_apr24.makeNextTurn()
    finals = [m for m in tourney_apr24.matches if m.final]
    assert len(finals) == 4
    finals[2].score1 = 10
    finals[3].score1 = 10

    tourney_apr24.updateRanking()
    tourney_apr24.makeNextTurn()
    finals = [m for m in tourney_apr24.matches if m.final]
    assert len(finals) == 5
    finals[4].score1 = 10

    tourney_apr24.updateRanking()
    assert tourney_apr24.prized is True
    assert tourney_apr24.ranking[:4] == [c1, c2, c3, c4]


def test_rated_finals_two(tourney_rated):
    assert tourney_rated.prized is False

    tourney_rated.updateRanking()
    c1, c2 = tourney_rated.ranking[:2]

    tourney_rated.makeFinalTurn()
    finals = [m for m in tourney_rated.matches if m.final]
    assert len(finals) == 1
    assert tourney_rated.finalturns is True
    finals[0].score2 = 10

    tourney_rated.updateRanking()
    tourney_rated.makeNextTurn()
    finals = [m for m in tourney_rated.matches if m.final]
    assert len(finals) == 2
    finals[1].score2 = 10

    tourney_rated.updateRanking()
    with pytest.raises(OperationAborted):
        tourney_rated.makeNextTurn()

    assert tourney_rated.prized is True
    assert tourney_rated.ranking[:2] == [c2, c1]


def test_rated_finals_three(tourney_rated):
    assert tourney_rated.prized is False

    tourney_rated.updateRanking()
    c1, c2 = tourney_rated.ranking[:2]

    tourney_rated.makeFinalTurn()
    finals = [m for m in tourney_rated.matches if m.final]
    assert len(finals) == 1
    assert tourney_rated.finalturns is True
    finals[0].score2 = 10

    tourney_rated.updateRanking()
    tourney_rated.makeNextTurn()
    finals = [m for m in tourney_rated.matches if m.final]
    assert len(finals) == 2
    finals[1].score1 = 10

    tourney_rated.updateRanking()
    tourney_rated.makeNextTurn()
    finals = [m for m in tourney_rated.matches if m.final]
    assert len(finals) == 3
    finals[2].score2 = 20

    tourney_rated.updateRanking()
    with pytest.raises(OperationAborted):
        tourney_rated.makeNextTurn()

    assert tourney_rated.prized is True
    assert tourney_rated.ranking[:2] == [c2, c1]


def test_trend70_retirements_with_final(
    tourney_trend,
    player_lele,
    player_pk,
    player_picol,
    player_varechina,
    player_blond,
    player_bob,
    player_fabiot,
    player_lorenzoh,
    player_elisam,
    player_danieled,
):
    assert tourney_trend.currentturn == 1
    tourney_trend.retirements = 'trend70'
    tourney_trend.finals = 1
    tourney_trend.finalkind = 'bestof3'
    tourney_trend.updateRanking()

    # 2nd turn
    tourney_trend.makeNextTurn()
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    # Lele-PK
    newmatches[0].score1 = 25
    newmatches[0].score2 = 1
    # Picol-Fabio
    newmatches[1].score1 = 24
    newmatches[1].score2 = 2
    # Lorenzo-Varechina
    newmatches[2].score1 = 23
    newmatches[2].score2 = 3
    # Elisa-Blond
    newmatches[3].score1 = 22
    newmatches[3].score2 = 4
    # Daniele-Bob
    newmatches[4].score1 = 21
    newmatches[4].score2 = 5
    tourney_trend.updateRanking()

    # Ok, now lele gives up
    r = tourney_trend.ranking
    assert r[0].player1 is player_lele
    r[0].retired = True

    # 3rd turn
    tourney_trend.makeNextTurn()
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    # Picol-Lorenzo
    newmatches[0].score1 = 25
    newmatches[0].score2 = 1
    # PK-Elisa
    newmatches[1].score1 = 24
    newmatches[1].score2 = 2
    # Fabio-Daniele
    newmatches[2].score1 = 23
    newmatches[2].score2 = 3
    # Blond-Varechina
    newmatches[3].score1 = 22
    newmatches[3].score2 = 4
    # Bob-Phantom
    newmatches[4].score1 = 25
    newmatches[4].score2 = 0
    tourney_trend.updateRanking()

    # Now also Bob gives up, so we can check that the win against the Phantom
    # gets discarded
    r = tourney_trend.ranking
    assert r[8].player1 is player_bob
    r[8].retired = True

    # 4th turn
    tourney_trend.makeNextTurn()
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    # Picol-PK
    newmatches[0].score1 = 25
    newmatches[0].score2 = 1
    # Fabio-Lorenzo
    newmatches[1].score1 = 24
    newmatches[1].score2 = 2
    # Elisa-Varechina
    newmatches[2].score1 = 23
    newmatches[2].score2 = 3
    # Daniele-Blond
    newmatches[3].score1 = 22
    newmatches[3].score2 = 4
    tourney_trend.updateRanking()

    # 5th turn
    tourney_trend.makeNextTurn()
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    # Picol-Daniele
    newmatches[0].score1 = 25
    newmatches[0].score2 = 1
    # Fabio-Elisa
    newmatches[1].score1 = 24
    newmatches[1].score2 = 2
    # PK-Varechina
    newmatches[2].score1 = 23
    newmatches[2].score2 = 3
    # Lorenzo-Blond
    newmatches[3].score1 = 22
    newmatches[3].score2 = 4
    tourney_trend.updateRanking()

    c1, c2 = tourney_trend.ranking[:2]
    assert c1.player1 is player_picol
    assert c2.player1 is player_fabiot

    bucholz_t5 = [c.bucholz for c in tourney_trend.ranking]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t5

    tourney_trend.makeFinalTurn()
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5

    finals = [m for m in tourney_trend.matches if m.final]
    assert len(finals) == 1
    assert tourney_trend.finalturns is True
    finals[0].score2 = 10

    tourney_trend.updateRanking()
    tourney_trend.makeNextTurn()
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t5
    finals = [m for m in tourney_trend.matches if m.final]
    assert len(finals) == 2
    finals[1].score2 = 10
