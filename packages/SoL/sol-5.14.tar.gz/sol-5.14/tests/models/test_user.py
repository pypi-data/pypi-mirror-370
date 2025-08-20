# -*- coding: utf-8 -*-
# :Project:   SoL -- Entity User tests
# :Created:   mar 10 lug 2018 09:33:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022 Lele Gaifax
#

import pytest

import transaction

from sol.models import User
from sol.models.errors import OperationAborted


def test_caption(user_lele):
    assert user_lele.caption() == 'Gaifax Lele \N{E-MAIL SYMBOL} lele@metapensiero.it'


def test_delete_owner(
    session,
    championship_current,
    club_scr,
    player_lele,
    rating_standalone,
    tourney_first,
):
    with transaction.manager:
        mrowner = User(
            firstname='Mister',
            lastname='Owner',
            email='mrowner@example.com',
            password='test123',
        )
        session.add(mrowner)
        session.flush()
        mrownerid = mrowner.iduser

        for obj in (
            championship_current,
            club_scr,
            player_lele,
            rating_standalone,
            tourney_first,
        ):
            obj.idowner = mrownerid

        session.flush()

    mrowner = session.get(User, mrownerid)
    with pytest.raises(OperationAborted):
        mrowner.delete()

    # NB: this must match the order in User.delete()!
    for obj in (tourney_first, player_lele, championship_current, club_scr):
        obj.idowner = None
        session.flush()
        with pytest.raises(OperationAborted):
            mrowner.delete()

    rating_standalone.idowner = None
    session.flush()
    mrowner.delete()


def test_password(session, user_lele):
    assert user_lele.check_password('lelegaifax')

    mrowner = User(
        firstname='Mister',
        lastname='Owner',
        email='mrowner@example.com',
        password='test123',
    )
    assert not mrowner.check_password('test123')

    mrowner.state = 'C'
    assert mrowner.check_password('test123')

    mrowner.password = ''
    assert mrowner.password is None
