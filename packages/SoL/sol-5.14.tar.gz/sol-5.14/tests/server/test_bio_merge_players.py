# -*- coding: utf-8 -*-
# :Project:   SoL -- Test /bio/mergePlayers view
# :Created:   dom 08 lug 2018 11:40:15 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

from metapensiero.sqlalchemy.proxy.json import JSON

from sol.models import Player


def test_merge_ok(lele_user, session, player_picol):
    to_be_merged = session.query(Player).filter_by(firstname='Merge').all()
    m1_lastname = to_be_merged[0].lastname
    m1_firstname = to_be_merged[0].firstname
    q = (('tid', player_picol.idplayer), *(('sids', m.idplayer) for m in to_be_merged))
    response = lele_user.post_route({}, 'merge_players', _query=q)
    assert response.json['success'] is True

    modified = [
        ('idplayer', dict(idplayer=0, lastname=m1_lastname, firstname=m1_firstname))
    ]
    deleted = []
    response = lele_user.post_route(
        dict(
            modified_records=JSON.encode(modified), deleted_records=JSON.encode(deleted)
        ),
        'save_changes',
    )
    assert response.json['success'] is False
    assert 'sia stato sostituito da' in response.json['message']


def test_merge_ko(lele_user, player_picol):
    response = lele_user.post_route(
        {}, 'merge_players', _query={'tid': -1, 'sid': player_picol.idplayer}
    )
    assert response.json['success'] is False

    response = lele_user.post_route(
        {},
        'merge_players',
        _query={'tid': player_picol.idplayer, 'sid': player_picol.idplayer},
    )
    assert response.json['success'] is False

    response = lele_user.post_route(
        {},
        'merge_players',
        _query={'tid': player_picol.idplayer, 'sids': player_picol.idplayer},
    )
    assert response.json['success'] is False
