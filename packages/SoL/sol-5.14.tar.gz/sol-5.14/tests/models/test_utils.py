# -*- coding: utf-8 -*-
# :Project:   SoL -- Utility functions tests
# :Created:   ven 06 lug 2018 19:26:50 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

import pytest

from sol.models import Club, Player
from sol.models.utils import (
    entity_from_primary_key,
    njoin,
    normalize,
    table_from_primary_key,
)


def test_njoin():
    assert njoin(['a', 'b', 'c']) == 'a, b and c'
    assert njoin([1, 2]) == '1 and 2'
    assert njoin(['a']) == 'a'


def test_normalize():
    assert normalize(None) is None
    assert normalize('lele') == 'Lele'
    assert normalize('LELE') == 'Lele'
    assert normalize('LeLe') == 'LeLe'
    assert normalize('LeLe', True) == 'Lele'
    assert normalize('lele', False) == 'lele'
    assert normalize(' le   le ') == 'Le Le'


def test_efpk():
    assert entity_from_primary_key('idplayer') is Player
    with pytest.raises(ValueError):
        entity_from_primary_key('dummy')


def test_tfpk():
    assert table_from_primary_key('idclub') is Club.__table__
    with pytest.raises(ValueError):
        table_from_primary_key('dummy')
