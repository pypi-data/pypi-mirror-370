# -*- coding: utf-8 -*-
# :Project:   SoL -- Entity Rate tests
# :Created:   sab 14 lug 2018 16:21:47 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

from sol.models import Rate


def test_description(session, rating_national, player_lele):
    rate = (
        session.query(Rate)
        .filter_by(idrating=rating_national.idrating, idplayer=player_lele.idplayer)
        .first()
    )
    desc = repr(rate)
    assert desc == (
        '<Rate "Gaifas Emanuele “Lele” in National rating on 07-05-2018":'
        ' r=1000 d=350 v=0.006>'
    )
