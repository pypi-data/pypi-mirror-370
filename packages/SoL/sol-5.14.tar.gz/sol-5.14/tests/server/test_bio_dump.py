# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests for /bio/dump
# :Created:   dom 08 lug 2018 09:52:41 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

from gzip import decompress

import pytest
import transaction


@pytest.fixture
def tourney_prized(session, tourney_rated):
    if not tourney_rated.prized:
        with transaction.manager:
            tourney_rated.updateRanking()
            for i, (scorer, points) in enumerate(
                (('score2', 10), ('score1', 10), ('score2', 20))
            ):
                tourney_rated.makeFinalTurn()
                finals = [m for m in tourney_rated.matches if m.final]
                setattr(finals[i], scorer, points)
                tourney_rated.updateRanking()
            session.flush()

    return tourney_rated


def test_dump_all(guest_user):
    response = guest_user.get_route('dump')
    assert response.content_type == 'text/x-yaml'
    assert 'competitors:' in response


def test_dump_tourney(guest_user, tourney_prized):
    response = guest_user.get_route(
        'dump', _query={'idtourney': tourney_prized.idtourney}
    )
    assert response.content_type == 'text/x-yaml'
    assert 'competitors:' in response
    assert 'final: true' in response


def test_dump_club(guest_user):
    response = guest_user.get_route('dump', _query={'idclub': 1})
    assert response.content_type == 'text/x-yaml'
    assert 'competitors:' in response


def test_dump_gzip(guest_user):
    response = guest_user.get_route('dump', _query={'idtourney': 1, 'gzip': 1})
    assert response.content_type == 'application/x-gzip'
    assert b'competitors:' in decompress(response.body)


def test_dump_championship(guest_user):
    response = guest_user.get_route('dump', _query={'idchampionship': 2})
    assert response.content_type == 'text/x-yaml'
    assert 'competitors:' in response
