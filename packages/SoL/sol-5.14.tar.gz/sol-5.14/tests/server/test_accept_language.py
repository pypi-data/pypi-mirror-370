# -*- coding: utf-8 -*-
# :Project:   SoL -- Accept-language behaviour
# :Created:   sab 07 lug 2018 17:25:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020 Lele Gaifax
#


def test_reload_l10n(lele_user):
    response = lele_user.post(
        '/auth/login',
        {'username': 'lele@metapensiero.it', 'password': 'lelegaifax'},
        headers={'Accept-Language': 'en'},
    )
    assert response.json['reload_l10n'] is True


def test_unavailable_language(guest_user):
    response = guest_user.get('/catalog', headers={'Accept-Language': 'xxx'})
    assert '_l10n_.lang = "en_GB";\n' in response.text


def test_available_language(guest_user):
    response = guest_user.get('/catalog', headers={'Accept-Language': 'it'})
    assert '_l10n_.lang = "it";\n' in response.text
