# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests for /bio/upload
# :Created:   dom 08 lug 2018 10:53:15 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2023, 2024 Lele Gaifax
#

from datetime import datetime
from pathlib import Path
from os import fspath

import pytest

from webtest.app import AppError

from metapensiero.sqlalchemy.proxy.json import JSON

from sol.models import Championship, Club, Player, Tourney


def test_anonymous_restore(app):
    with pytest.raises(AppError):
        app.post_route({}, 'upload', _upload_files=[('archive', '/tmp/foo.zip', b'')])


def test_guest_upload_portrait(guest_user):
    response = guest_user.post_route(
        {}, 'upload', _upload_files=[('portrait', 'foo.png', b'')]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is False


def test_guest_upload_emblem(guest_user):
    response = guest_user.post_route(
        {}, 'upload', _upload_files=[('emblem', 'foo.png', b'')]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is False


def test_guest_upload_sol(guest_user):
    testdir = Path(__file__).parent.parent
    dump = testdir / 'scr' / 'Campionato_CCM_2014_2015-2014-12-14+7.sol'
    response = guest_user.post_route(
        {}, 'upload', _upload_files=[('archive', fspath(dump))]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is False


def test_admin_upload_portrait(admin_user):
    response = admin_user.post_route(
        {}, 'upload', _upload_files=[('portrait', 'bar.png', b'')]
    )
    assert response.content_type == 'text/html'
    # Dropped support in 3.0
    assert JSON.decode(response.text)['success'] is False


def test_admin_upload_emblem(admin_user):
    response = admin_user.post_route(
        {}, 'upload', _upload_files=[('emblem', 'bar.png', b'')]
    )
    assert response.content_type == 'text/html'
    # Dropped support in 3.0
    assert JSON.decode(response.text)['success'] is False


def test_admin_restore(admin_user):
    testdir = Path(__file__).parent.parent
    dump = testdir / 'scr' / 'backup.zip'
    response = admin_user.post_route(
        {}, 'upload', _upload_files=[('archive', fspath(dump))]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is True
    settings = admin_user.app.registry.settings
    edir = Path(settings['sol.emblems_dir'])
    pdir = Path(settings['sol.portraits_dir'])
    assert (edir / 'scr.png').exists()
    assert (pdir / 'lele.png').exists()


def test_admin_restore_boxed(admin_user):
    testdir = Path(__file__).parent.parent
    dump = testdir / 'scr' / 'backup.box'
    response = admin_user.post_route(
        {},
        'upload',
        _query={'secret_key': 'a' * 64},
        _upload_files=[('archive', fspath(dump))],
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is True
    settings = admin_user.app.registry.settings
    edir = Path(settings['sol.emblems_dir'])
    pdir = Path(settings['sol.portraits_dir'])
    assert (edir / 'scr.png').exists()
    assert (pdir / 'lele.png').exists()


def test_upload_sol(lele_user, session, user_lele):
    testdir = Path(__file__).parent.parent
    dump = testdir / 'scr' / 'Campionato_CCM_2014_2015-2014-12-14+7.sol'
    response = lele_user.post_route(
        {}, 'upload', _upload_files=[('archive', fspath(dump))]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is True

    mario = session.query(Player).filter_by(lastname='BeltramiTest').one()
    assert mario.idowner == user_lele.iduser

    cship = (
        session.query(Championship)
        .filter_by(description='Campionato CCM 2014-2015 Test')
        .one()
    )
    assert cship.idowner == user_lele.iduser

    tourney = (
        session.query(Tourney).filter_by(description='Open Milano 2014-2015 Test').one()
    )
    assert tourney.idowner == user_lele.iduser

    club = session.query(Club).filter_by(description='Carrom Club Milano Test').one()
    assert club.idowner == user_lele.iduser

    dump = testdir / 'scr' / 'Swiss_Championship_2023_24-2024-05-25+15.sol.gz'
    response = lele_user.post_route(
        {}, 'upload', _upload_files=[('archive', fspath(dump))]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is True

    # We want to reload it again to exercise a different path: do to that we must remove all
    # matches first

    tourney = session.query(Tourney).filter_by(description='MS-Final 2024').one()

    tourney.resetPrizes()
    tourney.matches = []
    tourney.finalturns = False
    tourney.countdownstarted = None
    session.flush()
    # recompute the ranking
    session.expunge(tourney)
    tourney = session.get(Tourney, tourney.idtourney)
    tourney.updateRanking()
    tourney.modified = datetime(2024, 1, 1, 1, 1, 1)
    session.flush()

    response = lele_user.post_route(
        {}, 'upload', _upload_files=[('archive', fspath(dump))]
    )
    assert response.content_type == 'text/html'
    assert JSON.decode(response.text)['success'] is True


def test_upload_zip(lele_user):
    response = lele_user.post_route(
        {}, 'upload', _upload_files=[('archive', '/tmp/foo.zip', b'')]
    )
    assert '"success":false' in response.text


def test_upload_other(lele_user):
    response = lele_user.post_route(
        {}, 'upload', _upload_files=[('archive', '/tmp/foo.bar', b'')]
    )
    assert '"success":false' in response.text
