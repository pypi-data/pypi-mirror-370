# -*- coding: utf-8 -*-
# :Project:   SoL -- Glick2 tests
# :Created:   ven 06 lug 2018 19:40:29 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2023 Lele Gaifax
#

import pytest

from sol.models.glicko2 import Glicko2, Rating, WIN, LOSS


def assert_rating_equal(rate1, rate2):
    assert isinstance(rate1, Rating)
    assert isinstance(rate2, Rating)

    assert rate1.mu == pytest.approx(rate2.mu, abs=1e-3)
    assert rate1.phi == pytest.approx(rate2.phi, abs=1e-3)
    assert rate1.sigma == pytest.approx(rate2.sigma, abs=1e-5)


def test_glickman():
    env = Glicko2(tau=0.5)
    r1 = env.create_rating(1500, 200, 0.06)
    r2 = env.create_rating(1400, 30)
    r3 = env.create_rating(1550, 100)
    r4 = env.create_rating(1700, 300)
    rated = env.rate(r1, [(WIN, r2), (LOSS, r3), (LOSS, r4)])
    expected = env.create_rating(1464.051, 151.516, 0.05999)
    assert_rating_equal(rated, expected)
