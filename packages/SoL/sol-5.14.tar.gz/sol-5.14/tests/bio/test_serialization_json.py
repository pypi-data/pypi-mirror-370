# -*- coding: utf-8 -*-
# :Project:   SoL -- Bio serialization tests
# :Created:   sab 07 lug 2018 09:19:35 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2024 Lele Gaifax
#

from .test_serialization import full_dump_reload


def test_full_dump_reload_json(session, tourney_rated, player_fata, player_lele):
    full_dump_reload(
        session, tourney_rated, player_fata, player_lele, serialization_format='json'
    )
