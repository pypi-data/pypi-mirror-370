# -*- coding: utf-8 -*-
# :Project:   SoL -- Retired players behaviour tests
# :Created:   ven 06 lug 2018 20:34:09 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2022 Lele Gaifax
#

from sol.models import Match


def test_retirement(tourney_first):
    tourney_first.prized = False
    comp = tourney_first.competitors[0]
    comp.retired = True
    lastturn = tourney_first.currentturn
    tourney_first.updateRanking()
    tourney_first.makeNextTurn()
    assert tourney_first.currentturn == lastturn + 1
    newmatches = [
        m for m in tourney_first.matches if m.turn == tourney_first.currentturn
    ]
    assert [m for m in newmatches if m.idcompetitor2 is None]
    assert not [
        m
        for m in newmatches
        if m.idcompetitor1 == comp.idcompetitor or m.idcompetitor2 == comp.idcompetitor
    ]


def test_trend_retirements(
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

    tourney_trend.updateRanking()
    bucholz_t1 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t1 == [0, 0, 0, 0, 0, 2, 2, 2, 2, 2]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t1

    # 2nd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 2
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_lele
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_picol
    assert newmatches[1].competitor2.player1 is player_fabiot
    assert newmatches[2].competitor1.player1 is player_lorenzoh
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_elisam
    assert newmatches[3].competitor2.player1 is player_blond
    assert newmatches[4].competitor1.player1 is player_danieled
    assert newmatches[4].competitor2.player1 is player_bob
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
    bucholz_t2 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t2 == [2, 2, 2, 6, 4, 4, 2, 6, 6, 6]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2

    # Ok, now lele gives up
    r = tourney_trend.ranking
    assert r[0].player1 is player_lele
    r[0].retired = True

    # 3rd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 3
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_lorenzoh
    assert newmatches[1].competitor1.player1 is player_pk
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_fabiot
    assert newmatches[2].competitor2.player1 is player_danieled
    assert newmatches[3].competitor1.player1 is player_blond
    assert newmatches[3].competitor2.player1 is player_varechina
    assert newmatches[4].competitor1.player1 is player_bob
    assert newmatches[4].competitor2 is None
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
    bucholz_t3 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t3 == [10, 10, 8, 8, 6, 10, 10, 8, 8, 10]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3

    # Now also Bob gives up, so we can check that the win against the Phantom
    # gets discarded
    r = tourney_trend.ranking
    assert r[7].player1 is player_bob
    r[7].retired = True

    # 4th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 4
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_lorenzoh
    assert newmatches[2].competitor1.player1 is player_elisam
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t4 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t4 == [16, 16, 24, 18, 14, 10, 6, 16, 12, 16]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4

    # 5th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 5
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_danieled
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_lorenzoh
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t5 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t5 == [26, 24, 28, 24, 28, 22, 8, 24, 14, 26]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5

    # 6th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 6
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_elisam
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_blond
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_lorenzoh
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_varechina
    # Picol-Elisa
    newmatches[0].score1 = 25
    newmatches[0].score2 = 1
    # Fabio-Blond
    newmatches[1].score1 = 24
    newmatches[1].score2 = 2
    # PK-Lorenzo
    newmatches[2].score1 = 23
    newmatches[2].score2 = 3
    # Daniele-Varechina
    newmatches[3].score1 = 22
    newmatches[3].score2 = 4
    tourney_trend.updateRanking()
    bucholz_t6 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t6 == [36, 30, 40, 36, 34, 38, 10, 38, 18, 36]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(6)] == bucholz_t6


def test_none_retirements(
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
    # NB: Here we replay *exactly* the same tourney above, to spot the difference...

    assert tourney_trend.currentturn == 1
    tourney_trend.retirements = 'none'

    tourney_trend.updateRanking()
    bucholz_t1 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t1 == [0, 0, 0, 0, 0, 2, 2, 2, 2, 2]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t1

    # 2nd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 2
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_lele
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_picol
    assert newmatches[1].competitor2.player1 is player_fabiot
    assert newmatches[2].competitor1.player1 is player_lorenzoh
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_elisam
    assert newmatches[3].competitor2.player1 is player_blond
    assert newmatches[4].competitor1.player1 is player_danieled
    assert newmatches[4].competitor2.player1 is player_bob
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
    bucholz_t2 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t2 == [2, 2, 2, 6, 4, 4, 2, 6, 6, 6]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2

    # Ok, now lele gives up
    r = tourney_trend.ranking
    assert r[0].player1 is player_lele
    r[0].retired = True

    # 3rd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 3
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_lorenzoh
    assert newmatches[1].competitor1.player1 is player_pk
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_fabiot
    assert newmatches[2].competitor2.player1 is player_danieled
    assert newmatches[3].competitor1.player1 is player_blond
    assert newmatches[3].competitor2.player1 is player_varechina
    assert newmatches[4].competitor1.player1 is player_bob
    assert newmatches[4].competitor2 is None
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
    # We start to see differences from above: [10, 10, 8, 8, 6, 10, 10, 8, 8, 10] ...
    bucholz_t3 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t3 == [10, 8, 8, 8, 6, 10, 10, 8, 6, 10]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3

    # Now also Bob gives up, so we can check that the win against the Phantom
    # gets discarded
    r = tourney_trend.ranking
    assert r[8].player1 is player_bob
    r[8].retired = True

    # 4th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 4
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_lorenzoh
    assert newmatches[2].competitor1.player1 is player_elisam
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t4 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t4 == [16, 16, 20, 18, 14, 10, 6, 16, 8, 16]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4

    # 5th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 5
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_danieled
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_lorenzoh
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t5 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t5 == [26, 24, 24, 22, 28, 22, 8, 24, 8, 26]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5

    # Manually build the same couplings

    picol = [c for c in tourney_trend.competitors if c.player1 is player_picol][0]
    elisa = [c for c in tourney_trend.competitors if c.player1 is player_elisam][0]
    fabio = [c for c in tourney_trend.competitors if c.player1 is player_fabiot][0]
    blond = [c for c in tourney_trend.competitors if c.player1 is player_blond][0]
    pk = [c for c in tourney_trend.competitors if c.player1 is player_pk][0]
    lorenzo = [c for c in tourney_trend.competitors if c.player1 is player_lorenzoh][0]
    daniele = [c for c in tourney_trend.competitors if c.player1 is player_danieled][0]
    varechina = [c for c in tourney_trend.competitors if c.player1 is player_varechina][
        0
    ]

    # 6th turn
    tourney_trend.matches.append(
        Match(
            turn=6, board=1, competitor1=picol, competitor2=elisa, score1=25, score2=1
        )
    )
    tourney_trend.matches.append(
        Match(
            turn=6, board=2, competitor1=fabio, competitor2=blond, score1=24, score2=2
        )
    )
    tourney_trend.matches.append(
        Match(turn=6, board=3, competitor1=pk, competitor2=lorenzo, score1=23, score2=3)
    )
    tourney_trend.matches.append(
        Match(
            turn=6,
            board=4,
            competitor1=daniele,
            competitor2=varechina,
            score1=22,
            score2=4,
        )
    )

    tourney_trend.currentturn = 6
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_elisam
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_blond
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_lorenzoh
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_varechina
    tourney_trend.updateRanking()
    bucholz_t6 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t6 == [36, 30, 32, 36, 34, 38, 10, 38, 10, 36]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(6)] == bucholz_t6


def test_trend70_retirements(
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

    tourney_trend.updateRanking()
    bucholz_t1 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t1 == [0, 0, 0, 0, 0, 2, 2, 2, 2, 2]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking()] == bucholz_t1

    # 2nd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 2
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_lele
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_picol
    assert newmatches[1].competitor2.player1 is player_fabiot
    assert newmatches[2].competitor1.player1 is player_lorenzoh
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_elisam
    assert newmatches[3].competitor2.player1 is player_blond
    assert newmatches[4].competitor1.player1 is player_danieled
    assert newmatches[4].competitor2.player1 is player_bob
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
    bucholz_t2 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t2 == [2, 2, 2, 6, 4, 4, 2, 6, 6, 6]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2

    # Ok, now lele gives up
    r = tourney_trend.ranking
    assert r[0].player1 is player_lele
    r[0].retired = True

    # 3rd turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 3
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_lorenzoh
    assert newmatches[1].competitor1.player1 is player_pk
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_fabiot
    assert newmatches[2].competitor2.player1 is player_danieled
    assert newmatches[3].competitor1.player1 is player_blond
    assert newmatches[3].competitor2.player1 is player_varechina
    assert newmatches[4].competitor1.player1 is player_bob
    assert newmatches[4].competitor2 is None
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
    # We start to see differences from above: [10, 10, 8, 8, 6, 10, 10, 8, 8, 10] ...
    bucholz_t3 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t3 == [10, 9, 8, 8, 6, 10, 10, 8, 7, 10]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3

    # Now also Bob gives up, so we can check that the win against the Phantom
    # gets discarded
    r = tourney_trend.ranking
    assert r[8].player1 is player_bob
    r[8].retired = True

    # 4th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 4
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_pk
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_lorenzoh
    assert newmatches[2].competitor1.player1 is player_elisam
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t4 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t4 == [16, 16, 22, 18, 14, 10, 6, 16, 10, 16]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4

    # 5th turn
    tourney_trend.makeNextTurn()
    assert tourney_trend.currentturn == 5
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_danieled
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_elisam
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_varechina
    assert newmatches[3].competitor1.player1 is player_lorenzoh
    assert newmatches[3].competitor2.player1 is player_blond
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
    bucholz_t5 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t5 == [26, 24, 26, 24, 28, 22, 8, 24, 12, 26]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5

    # Manually build the same couplings

    picol = [c for c in tourney_trend.competitors if c.player1 is player_picol][0]
    elisa = [c for c in tourney_trend.competitors if c.player1 is player_elisam][0]
    fabio = [c for c in tourney_trend.competitors if c.player1 is player_fabiot][0]
    blond = [c for c in tourney_trend.competitors if c.player1 is player_blond][0]
    pk = [c for c in tourney_trend.competitors if c.player1 is player_pk][0]
    lorenzo = [c for c in tourney_trend.competitors if c.player1 is player_lorenzoh][0]
    daniele = [c for c in tourney_trend.competitors if c.player1 is player_danieled][0]
    varechina = [c for c in tourney_trend.competitors if c.player1 is player_varechina][
        0
    ]

    # 6th turn
    tourney_trend.matches.append(
        Match(
            turn=6, board=1, competitor1=picol, competitor2=elisa, score1=25, score2=1
        )
    )
    tourney_trend.matches.append(
        Match(
            turn=6, board=2, competitor1=fabio, competitor2=blond, score1=24, score2=2
        )
    )
    tourney_trend.matches.append(
        Match(turn=6, board=3, competitor1=pk, competitor2=lorenzo, score1=23, score2=3)
    )
    tourney_trend.matches.append(
        Match(
            turn=6,
            board=4,
            competitor1=daniele,
            competitor2=varechina,
            score1=22,
            score2=4,
        )
    )

    tourney_trend.currentturn = 6
    assert [c.bucholz for c in tourney_trend.ranking] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    newmatches = [
        m for m in tourney_trend.matches if m.turn == tourney_trend.currentturn
    ]
    assert newmatches[0].competitor1.player1 is player_picol
    assert newmatches[0].competitor2.player1 is player_elisam
    assert newmatches[1].competitor1.player1 is player_fabiot
    assert newmatches[1].competitor2.player1 is player_blond
    assert newmatches[2].competitor1.player1 is player_pk
    assert newmatches[2].competitor2.player1 is player_lorenzoh
    assert newmatches[3].competitor1.player1 is player_danieled
    assert newmatches[3].competitor2.player1 is player_varechina
    tourney_trend.updateRanking()
    bucholz_t6 = [c.bucholz for c in tourney_trend.ranking]
    assert bucholz_t6 == [36, 30, 37, 36, 34, 38, 10, 38, 15, 36]
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(1)] == bucholz_t1
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(2)] == bucholz_t2
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(3)] == bucholz_t3
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(4)] == bucholz_t4
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(5)] == bucholz_t5
    assert [cr[1].bucholz for cr in tourney_trend.computeRanking(6)] == bucholz_t6
