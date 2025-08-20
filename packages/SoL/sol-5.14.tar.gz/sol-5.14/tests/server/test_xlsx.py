# -*- coding: utf-8 -*-
# :Project:   SoL -- Test XLSX views
# :Created:   sab 21 lug 2018 13:00:34 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2024 Lele Gaifax
#

import pytest
import transaction
from webtest.app import AppError


@pytest.fixture
def tourney_prized(session, tourney_rated):
    if not tourney_rated.prized:
        with transaction.manager:
            tourney_rated.updateRanking()
            for i, (scorer, points) in enumerate(
                (
                    ('score2', 10),
                    ('score1', 10),
                    ('score2', 20),
                )
            ):
                tourney_rated.makeFinalTurn()
                finals = [m for m in tourney_rated.matches if m.final]
                setattr(finals[i], scorer, points)
                tourney_rated.updateRanking()

    return tourney_rated


def test_bad_id(guest_user):
    app = guest_user

    with pytest.raises(AppError):
        app.get_route('xlsx_tourney', id=0)

    with pytest.raises(AppError):
        app.get_route('xlsx_tourney', id='abcdef')


def test_xlsx_tourney(guest_user, tourney_prized):
    app = guest_user

    app.get_route('xlsx_tourney', id=tourney_prized.idtourney)
    app.get_route('xlsx_tourney', id=tourney_prized.guid)
