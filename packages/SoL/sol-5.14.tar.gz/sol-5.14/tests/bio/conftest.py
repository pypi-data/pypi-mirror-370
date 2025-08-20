# -*- coding: utf-8 -*-
# :Project:   SoL -- Bio specific test fixtures
# :Created:   sab 07 lug 2018 08:42:35 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2020, 2024 Lele Gaifax
#

from types import SimpleNamespace

import pytest

from metapensiero.sqlalchemy.proxy.json import register_json_decoder_encoder

from rapidjson import Decoder, Encoder, DM_ISO8601, NM_NATIVE, NM_DECIMAL


@pytest.fixture
def fake_admin_request():
    class FakeRequest:
        def __init__(self):
            self.registry = SimpleNamespace()
            self.registry.settings = {
                'sol.portraits_dir': '/tmp',
                'sol.emblems_dir': '/tmp',
            }
            self.session = dict(
                user_id=None,
                is_admin=True,
                is_nationalliable=False,
                is_ownersadmin=True,
                is_playersmanager=True,
            )

    return FakeRequest()


@pytest.fixture
def fake_johndoe_request():
    class FakeRequest:
        def __init__(self):
            self.registry = SimpleNamespace()
            self.registry.settings = {
                'sol.portraits_dir': '/tmp',
                'sol.emblems_dir': '/tmp',
            }
            self.session = dict(
                user_id=999,
                is_admin=False,
                is_nationalliable=False,
                is_ownersadmin=False,
                is_playersmanager=False,
            )

    return FakeRequest()


json_decode = Decoder(datetime_mode=DM_ISO8601, number_mode=NM_NATIVE).__call__


json_encode = Encoder(
    datetime_mode=DM_ISO8601, number_mode=NM_NATIVE | NM_DECIMAL, ensure_ascii=False
).__call__


register_json_decoder_encoder(json_decode, json_encode)
