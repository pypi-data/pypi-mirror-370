# -*- coding: utf-8 -*-
# :Project:   SoL -- Club entity tests
# :Created:   ven 06 lug 2018 13:42:27 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020 Lele Gaifax
#


def test_country(club_ecc):
    assert club_ecc.country == 'Europe'


def test_counts(club_fic):
    assert club_fic.countChampionships() == 1
    assert club_fic.countPlayers() == 1


def test_owned(club_owned, user_lele):
    assert club_owned.owner is user_lele


def test_users(club_scr, user_lele):
    assert len(club_scr.users) == 1
    assert club_scr.users[0] is user_lele
