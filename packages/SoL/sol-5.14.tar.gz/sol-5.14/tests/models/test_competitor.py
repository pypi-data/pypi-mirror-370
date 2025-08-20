# -*- coding: utf-8 -*-
# :Project:   SoL -- Competitor entity tests
# :Created:   ven 06 lug 2018 14:33:04 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2019 Lele Gaifax
#

from sol.models import Competitor, Player


def test_description(session):
    fcomp1 = session.query(Competitor).first()
    desc = fcomp1.description
    assert desc == '<b>Gaifas</b> Emanuele “Lele” and <b>Turchina</b> Fata'
    assert fcomp1.rank > 0

    empty = Competitor()
    assert 'NOT assigned' in repr(empty)

    fourp = iter(session.query(Player).limit(4))
    empty.player1 = next(fourp)
    empty.player2 = next(fourp)
    empty.player3 = next(fourp)
    empty.player4 = next(fourp)
    assert len(empty.caption(html=True, css_class='X').split('X')) == 5

    for i in range(1, 5):
        for a in ('FullName', 'Nationality'):
            assert getattr(empty, 'player%d%s' % (i, a)) is None
