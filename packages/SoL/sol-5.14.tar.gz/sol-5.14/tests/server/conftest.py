# -*- coding: utf-8 -*-
# :Project:   SoL -- Server tests configuration
# :Created:   sab 07 lug 2018 17:08:49 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2024 Lele Gaifax
#

from os import environ, fspath
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import pytest

from pyramid.encode import url_quote, urlencode
from pyramid.paster import get_appsettings
from webtest import TestApp

from sol import main


@pytest.fixture(scope='module')
def settings():
    settings = get_appsettings(fspath(Path(__file__).parent / 'test.ini'))
    settings['testing'] = True
    with TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        emblems = tmppath / 'emblems'
        emblems.mkdir()
        (emblems / 'emblem.png').touch()
        portraits = tmppath / 'portraits'
        portraits.mkdir()
        (portraits / 'portrait.png').touch()
        settings['sol.emblems_dir'] = fspath(emblems)
        settings['sol.portraits_dir'] = fspath(portraits)
        if 'NIX_BUILD_TOP' in environ:  # in nix derivation's
            # checkPhase, backup cannot be in /tmp
            backups = tmppath / 'backups'
            backups.mkdir()
            settings['sol.backups_dir'] = fspath(backups)
        yield settings


class TestApp(TestApp):
    def route_url(self, name, *, _query=None, **args):
        url = self.app.routes_mapper.get_route(name).generate(args)
        if _query is not None:
            if isinstance(_query, str):
                qs = '?' + url_quote(_query)
            else:
                qs = '?' + urlencode(_query)
            url += qs
        return url

    def get_route(self, name, *, _query=None, **args):
        url = self.route_url(name, _query=_query, **args)
        return self.get(url)

    def post_route(self, data, name, *, _query=None, _upload_files=None, **args):
        url = self.route_url(name, _query=_query, **args)
        return self.post(url, data, upload_files=_upload_files)


@pytest.fixture
def app(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    return app


@pytest.fixture
def anonymous_user(app):
    result = app.get('/')
    app.csrf_token = re.search(r'__csrf_token__ = "([^"]+)"', result.text).group(1)
    return app


@pytest.fixture
def admin_user(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    app.post('/auth/login', {'username': 'admin', 'password': 'admin'})
    return app


@pytest.fixture
def guest_user(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    app.post('/auth/login', {'username': 'guest', 'password': 'guest'})
    return app


@pytest.fixture
def lele_user(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    app.post(
        '/auth/login', {'username': 'lele@metapensiero.it', 'password': 'lelegaifax'}
    )
    return app


@pytest.fixture
def johndoe_user(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    app.post(
        '/auth/login', {'username': 'johndoe@example.com', 'password': 'something'}
    )
    return app


@pytest.fixture
def worldadmin_user(settings, engine):
    app = TestApp(main({'engine': engine}, **settings))
    app.post('/auth/login', {'username': 'world@admin.com', 'password': 'something'})
    return app
