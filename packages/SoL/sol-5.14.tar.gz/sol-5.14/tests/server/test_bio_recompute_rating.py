# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests for /bio/recomputeRating view
# :Created:   dom 08 lug 2018 11:35:49 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#


def test_recompute_rating(lele_user, rating_european):
    response = lele_user.post_route(
        {}, 'recompute_rating', _query={'idrating': rating_european.idrating}
    )
    assert response.json['success'] is True


def test_recompute_inheriting_rating(lele_user, rating_national):
    response = lele_user.post_route(
        {}, 'recompute_rating', _query={'idrating': rating_national.idrating}
    )
    assert response.json['success'] is True
