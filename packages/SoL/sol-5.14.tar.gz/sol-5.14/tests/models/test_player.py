# -*- coding: utf-8 -*-
# :Project:   SoL -- Player entity tests
# :Created:   ven 06 lug 2018 14:08:38 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2020, 2022, 2023, 2024 Lele Gaifax
#

import pytest

from sol.models import Player, Rate
from sol.models.errors import OperationAborted


def test_description(player_lele, player_picol):
    assert player_lele.agreedprivacy == 'A'
    assert player_lele.acceptedDiscernibility()
    assert player_lele.description == '<b>Gaifas</b> Emanuele “Lele”'
    assert player_picol.agreedprivacy == ' '
    assert not player_picol.acceptedDiscernibility()
    assert '<b>P' in player_picol.description and '</b> J' in player_picol.description


def test_counts(player_lele, player_picol):
    assert player_picol.participations()
    assert len(player_picol.matchesSummary()) == 4
    assert len(player_picol.opponents()) == 3
    assert len(player_picol.opponentMatches(player_lele)) == 3


def test_country(player_picol, player_pk, player_merge1):
    assert player_picol.country == 'World'
    assert player_pk.country == 'Zimbabwe'
    assert player_merge1.country == 'Europe'


def test_shouldOmitNickName(player_danieled):
    player_danieled.nickname = 'dd'
    assert not player_danieled.shouldOmitNickName()

    player_danieled.nickname = player_danieled.firstname
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = player_danieled.lastname
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'da fattid'
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'dafattid'
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'ddafatti'
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'dda fatti'
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'danieled'
    assert player_danieled.shouldOmitNickName()

    player_danieled.nickname = 'ddaniele'
    assert player_danieled.shouldOmitNickName()


def test_federation(player_elisam, club_fic):
    assert player_elisam.federation is club_fic


def test_guid(player_picol):
    assert player_picol.modified is not None
    assert player_picol.guid is not None
    with pytest.raises(ValueError):
        player_picol.guid = 'foo'


def test_owned(player_fata, user_lele):
    assert player_fata.owner is user_lele


def test_merge(session, player_picol, player_bob, player_merge1, player_merge2):
    assert player_picol.sex is None
    assert player_picol.merged == []
    m1_lastname = player_merge1.lastname
    m1_firstname = player_merge1.firstname
    tobemerged_ids = [player_merge1.idplayer, player_merge2.idplayer]
    tobemerged_guids = [player_merge1.guid, player_merge2.guid]
    juri_email = player_picol.email
    merge1_id = player_merge1.idplayer
    merge1_sex = player_merge1.sex
    player_picol.mergePlayers(tobemerged_ids)
    session.flush()
    assert {m.guid for m in player_picol.merged} == set(tobemerged_guids)
    assert player_picol.sex, merge1_sex
    assert 'One Merge' in (
        m.caption(html=False).split(' -> ')[0] for m in player_picol.merged
    )
    assert player_picol.email == juri_email
    assert session.query(Player).filter_by(firstname='Merge').all() == []
    assert session.query(Rate).filter_by(idplayer=merge1_id).all() == []
    assert Player.find(session, m1_lastname, m1_firstname, '') == (player_picol, True)


def test_bad_merge(session, player_picol, player_bob, player_lele, player_merge1):
    with pytest.raises(OperationAborted) as e:
        player_bob.mergePlayers([player_picol.idplayer])
    assert 'is present in tourney' in str(e.value)


def test_merge_guid(session, player_pk, player_merge3):
    assert player_pk.merged == []
    fn, ln = player_merge3.firstname, player_merge3.lastname
    tobemerged_guids = [player_merge3.guid]
    player_pk.mergePlayers(tobemerged_guids)
    session.flush()
    assert tobemerged_guids[0], {m.guid for m in player_pk.merged}
    assert session.query(Player).filter_by(firstname=fn, lastname=ln).all() == []
    player, merged_into = Player.find(session, ln, fn, '')
    assert player is player_pk
    assert merged_into
