# -*- coding: utf-8 -*-
# :Project:   SoL -- Match entity tests
# :Created:   ven 06 lug 2018 14:41:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

from sol.models import Match


def test_description(session, tourney_first, tourney_odd, tourney_double):
    match = tourney_first.matches[0]
    assert 'vs.' in match.description

    tourney_odd.makeNextTurn()
    match = tourney_odd.matches[-1]
    assert match.competitor2 is None and 'Phantom' in match.description

    tourney_double.makeNextTurn()
    match = tourney_double.matches[-1]
    assert '<br/>' in match.description
    assert '<br/>' not in match.caption(html=False)
