# -*- coding: utf-8 -*-
# :Project:   SoL -- Reload same tourney tests
# :Created:   sab 07 lug 2018 12:18:16 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2022 Lele Gaifax
#

from datetime import date, timedelta
from io import StringIO
from os import fspath
from pathlib import Path

from sol.models import Competitor, Player, Tourney
from sol.models.bio import dump_sol, load_sol


def test_reload(session):
    testdir = Path(__file__).parent.parent
    fullname = testdir / 'scr' / 'Campionato_CCV_2015_2016-2016-06-02+0.sol'

    for i in range(2):
        tourneys, skipped = load_sol(session, fspath(fullname))
        assert tourneys[0].description == 'Replica of Campionato CCV - 1\xb0 Tappa'
        assert skipped == 0

    fullname = testdir / 'scr' / 'Campionato_CCV_2015_2016-2016-06-02+1.sol'

    tourneys, skipped = load_sol(session, fspath(fullname))
    assert tourneys[0].description == 'Replica of Campionato CCV - 1\xb0 Tappa'
    assert skipped == 0


def test_update_incomplete_tourney(session, tourney_first):
    n = tourney_first.replay(date.today() + timedelta(days=1))
    session.flush()
    dump = dump_sol([n])
    newguy = Player(firstname='New', lastname='Guy')
    n.competitors.append(Competitor(player1=newguy))
    session.flush()
    nid = n.idtourney
    pid = newguy.idplayer
    load_sol(session, 'dump.sol', StringIO(dump))
    session.flush()

    session.expunge_all()
    reloaded = session.get(Tourney, nid)
    assert pid not in (p.idplayer for p in reloaded.allPlayers())
