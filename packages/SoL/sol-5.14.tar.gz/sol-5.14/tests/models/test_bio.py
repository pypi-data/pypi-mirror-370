# -*- coding: utf-8 -*-
# :Project:   SoL -- Test low level details
# :Created:   ven 20 lug 2018 21:14:39 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

import pytest

import transaction

from sol.models.bio import TourneyXlsxDumper


@pytest.fixture
def tourney_first_prized(session, tourney_first):
    if not tourney_first.prized:
        with transaction.manager:
            tourney_first.updateRanking()
            tourney_first.assignPrizes()

    return tourney_first


@pytest.fixture
def tourney_odd_prized(session, tourney_odd):
    if not tourney_odd.prized:
        with transaction.manager:
            tourney_odd.updateRanking()
            tourney_odd.makeNextTurn()
            for m in tourney_odd.matches:
                if m.turn == tourney_odd.currentturn:
                    m.score1 = 20
                    m.score2 = 15
            tourney_odd.updateRanking()
            tourney_odd.assignPrizes()

    return tourney_odd


def test_xlsx_dumper(tourney_first_prized, tourney_odd_prized):
    dumper = TourneyXlsxDumper(tourney_first_prized)
    data = dumper()
    assert data.startswith(b'PK')
    assert b'sheet1.xml' in data

    dumper = TourneyXlsxDumper(tourney_odd_prized)
    data = dumper()
    assert data.startswith(b'PK')
    assert b'sheet1.xml' in data
