# -*- coding: utf-8 -*-
# :Project:   SoL -- Test /data/* views
# :Created:   lun 09 lug 2018 11:11:25 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022, 2024 Lele Gaifax
#

from metapensiero.sqlalchemy.proxy.json import JSON

from sol.models import Club, Player, Rating, Tourney


def test_clubs(guest_user, session):
    response = guest_user.get_route('clubs')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == session.query(Club).count()


def test_clubs_lookups(guest_user, session):
    response = guest_user.get_route('clubs_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] < session.query(Club).count()


def test_clubs_metadata(guest_user):
    response = guest_user.get_route('clubs', _query={'metadata': 'metadata'})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['metadata']['fields'][-1]['name'] == 'Owner'


def test_clubs_no_owner_metadata(guest_user):
    response = guest_user.get_route(
        'clubs', _query={'metadata': 'metadata', 'only_cols': 'description'}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert 'Owner' not in [f['name'] for f in result['metadata']['fields']]


def test_clubs_no_owner(guest_user):
    response = guest_user.get_route(
        'clubs', _query={'only_cols': 'description,nationality'}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert 'Owner' not in result['root'][0]


def test_club_by_description(guest_user, club_scr):
    response = guest_user.get_route(
        'clubs', _query={'filter_by_description': club_scr.description}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    club = result['root'][0]
    assert club['description'] == club_scr.description
    assert club['Championships'] == 8
    assert club['Owner'] == 'Administrator \N{E-MAIL SYMBOL} test@example.com'


def test_owned_club(guest_user, club_owned, user_lele):
    response = guest_user.get_route(
        'clubs', _query={'filter_by_description': club_owned.description}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    club = result['root'][0]
    assert user_lele.firstname in club['Owner']


def test_visible_clubs(admin_user, guest_user, lele_user, user_lele):
    response = lele_user.get_route(
        'clubs', _query={'filter_by_idowner': user_lele.iduser}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 2
    club = result['root'][0]
    assert 'Amministratore' in club['Owner']
    club = result['root'][1]
    assert user_lele.firstname in club['Owner']

    response = admin_user.get_route(
        'clubs', _query={'filter_by_idowner': user_lele.iduser}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1

    response = guest_user.get_route(
        'clubs', _query={'filter_by_idowner': user_lele.iduser}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0


def test_clubs_lookup_by_guest(guest_user):
    response = guest_user.get_route('clubs_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0


def test_clubs_lookup_by_admin(admin_user):
    response = admin_user.get_route('clubs_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] > 1


def test_clubs_lookup_by_lele(lele_user):
    response = lele_user.get_route('clubs_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 2


def test_club_users(guest_user, lele_user):
    response = guest_user.get_route('club_users')
    result = response.json
    assert result['success'] is False

    response = lele_user.get_route('club_users')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0


def test_federations(guest_user):
    response = guest_user.get_route('federations')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1


def test_owners(guest_user, lele_user):
    response = guest_user.get_route('owners')
    result = response.json
    assert result['success'] is False

    response = lele_user.get_route('owners')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 4


def test_owners_metadata(lele_user):
    response = lele_user.get_route('owners', _query={'metadata': 'metadata'})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['metadata']['fields'][-1]['name'] == 'Fullname'


def test_players(guest_user, session):
    response = guest_user.get_route('players')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == session.query(Player).count()
    for p in result['root']:
        if p['firstname'] == 'Fata':
            assert p['Owner'] == 'Gaifax Lele \N{E-MAIL SYMBOL} lele@metapensiero.it'
            assert p['Language'] == 'Zulu'
            break
    else:
        assert False, 'No Fata??'


def test_players_metadata(guest_user):
    response = guest_user.get_route('players', _query={'metadata': 'metadata'})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert 'Owner' in (f['name'] for f in result['metadata']['fields'])
    assert 'Language' in (f['name'] for f in result['metadata']['fields'])


def test_duplicated_players(guest_user):
    response = guest_user.get_route('players', _query={'dups': 1})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 4


def test_active_players(guest_user, session, club_scr):
    response = guest_user.get_route('players', _query={'played4club': club_scr.idclub})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert 1 < result['count'] < session.query(Player).count()


def test_player_by_nickname(guest_user, player_lele, tourney_closed):
    response = guest_user.get_route(
        'players', _query={'filter_by_nickname': player_lele.nickname}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    player = result['root'][0]
    assert player['firstname'] == player_lele.firstname
    assert player['lastname'] == player_lele.lastname
    assert player['LastPlayed'] == tourney_closed.date.isoformat()


def test_player_by_name(lele_user):
    filters = '[{"property":"firstname","value":"rob","operator":"~"}]'
    response = lele_user.get_route('players', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 6
    assert {player['firstname'] for player in result['root']} == {
        'Roberto',
        'Cheryl',
        'Darren',
        'Robert',
        'Daniel',
    }

    filters = (
        '[{"property":"firstname","value":"rob","operator":"~"}'
        ',{"property":"lastname","value":"blo","operator":"~"}]'
    )
    response = lele_user.get_route('players', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    assert result['root'][0]['firstname'] == 'Roberto'


def test_owned_player(guest_user, player_fata, user_lele):
    response = guest_user.get_route(
        'players',
        _query={
            'filter_by_firstname': player_fata.firstname,
            'filter_by_lastname': player_fata.lastname,
        },
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    player = result['root'][0]
    assert user_lele.firstname in player['Owner']


def test_championships(guest_user):
    response = guest_user.get_route('championships')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 12


def test_championships_lookup(guest_user, lele_user, admin_user):
    response = guest_user.get_route('championships_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0

    response = lele_user.get_route('championships_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 7

    response = admin_user.get_route('championships_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 9


def test_championship_by_description(guest_user, club_scr):
    response = guest_user.get_route(
        'championships', _query={'filter_by_description': 'SCR 2010 (test)'}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    championship = result['root'][0]
    assert championship['Club'] == club_scr.description


def test_owned_championship(guest_user, championship_current, user_lele):
    idc = championship_current.idchampionship
    response = guest_user.get_route(
        'championships', _query={'filter_by_idchampionship': idc}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    championship = result['root'][0]
    assert user_lele.firstname in championship['Owner']


def test_tourneys(guest_user, session):
    response = guest_user.get_route('tourneys')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == session.query(Tourney).count()


def test_player_tourneys(guest_user, player_fata):
    response = guest_user.get_route(
        'tourneys', _query={'idplayer': player_fata.idplayer}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 9


def test_tourney_by_description(guest_user, tourney_first, user_lele):
    td = tourney_first.description
    response = guest_user.get_route('tourneys', _query={'filter_by_description': td})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    tourney = result['root'][0]
    assert tourney['description'] == tourney_first.description
    assert tourney['date'] == tourney_first.date.isoformat()
    assert tourney['Championship'] == tourney_first.championship.description
    assert user_lele.firstname in tourney['Owner']


def test_countries(guest_user):
    guest_user.extra_environ['HTTP_ACCEPT_LANGUAGE'] = 'it-IT'
    response = guest_user.get_route('countries')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert set(result['root'][0].keys()) == {'code', 'name'}
    cnames = {c['code']: c['name'] for c in result['root']}
    assert cnames['ABW'] == 'Aruba'
    assert cnames['ITA'] == 'Italia'
    assert cnames['CZE'] in ('Cechia', 'Repubblica Ceca')
    assert cnames['eur'] == 'Europa'
    assert cnames['wrl'] == 'Mondo'


def test_languages(guest_user):
    guest_user.extra_environ['HTTP_ACCEPT_LANGUAGE'] = 'it-IT'
    response = guest_user.get_route('languages')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert set(result['root'][0].keys()) == {'code', 'name'}
    lnames = {c['code']: c['name'] for c in result['root']}
    assert lnames['en_GB'] == 'Inglese (Regno Unito)'
    assert lnames['en_US'] == 'Inglese (Stati Uniti)'
    assert lnames['it'] == 'Italiano'


def test_ratings(guest_user, session, rating_european):
    response = guest_user.get_route('ratings')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == session.query(Rating).count()
    assert result['root'][0]['description'] == rating_european.description
    assert result['root'][0]['Players'] == 5
    assert result['root'][0]['Tourneys'] == 1


def test_ratings_lookup(admin_user, guest_user, lele_user, session):
    response = admin_user.get_route('ratings_lookup')
    result = response.json
    assert result['count'] == session.query(Rating).count()

    response = guest_user.get_route('ratings_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0
    # assert all(rec['level'] == '4' for rec in result['root'])

    response = lele_user.get_route('ratings_lookup')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert all(rec['level'] > '1' for rec in result['root'])


def test_rated_players(guest_user, rating_european, player_varechina):
    response = guest_user.get_route(
        'rated_players', _query={'filter_by_idrating': rating_european.idrating}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 5
    assert result['root'][0]['lastname'] == player_varechina.lastname


def test_owned_rating(guest_user, rating_standalone, user_lele):
    rd = rating_standalone.description
    response = guest_user.get_route('ratings', _query={'filter_by_description': rd})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    rating = result['root'][0]
    assert user_lele.firstname in rating['Owner']


def test_users(guest_user, lele_user):
    response = guest_user.get_route('users')
    result = response.json
    assert result['success'] is False

    response = lele_user.get_route('users')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 4
    assert result['root'][0]['lastname'] == 'Gaifax'
    assert result['root'][1]['firstname'] == 'Suspended'
    assert result['root'][1]['Language'] == 'Inglese (Stati Uniti)'


def test_users_filter(lele_user):
    filters = '[{"property":"lastname","value":"lele","operator":"~"}]'
    response = lele_user.get_route('users', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    assert result['root'][0]['lastname'] == 'Gaifax'

    filters = '[{"property":"email","value":"lele","operator":"~"}]'
    response = lele_user.get_route('users', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    assert result['root'][0]['lastname'] == 'Gaifax'

    filters = '[{"property":"firstname","value":"metap","operator":"~"}]'
    response = lele_user.get_route('users', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 1
    assert result['root'][0]['lastname'] == 'Gaifax'

    filters = (
        '[{"property":"firstname","value":"lele","operator":"~"}'
        ',{"property":"lastname","value":"metap","operator":"~"}]'
    )
    response = lele_user.get_route('users', _query={'filter': filters})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 0


def test_users_metadata(lele_user):
    response = lele_user.get_route('users', _query={'metadata': 'metadata'})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'


def test_save_club_users(session, lele_user, club_fic, club_owned, user_lele):
    modified = []
    response = lele_user.post_route(
        dict(idclub=0, modified_records=JSON.encode(modified)), 'club_users'
    )
    assert response.json['success'] is False
    assert response.json['message'] == 'Il club specificato non esiste!'

    response = lele_user.post_route(
        dict(idclub=club_fic.idclub, modified_records=JSON.encode(modified)),
        'club_users',
    )
    assert response.json['success'] is False
    assert response.json['message'] == 'Tentativo non autorizzato di modifica del club!'

    modified = [('iduser', dict(iduser=0, associated=True))]
    response = lele_user.post_route(
        dict(idclub=club_owned.idclub, modified_records=JSON.encode(modified)),
        'club_users',
    )
    assert response.json['success'] is False
    assert response.json['message'] == "L'utente specificato non esiste!"

    modified = [('iduser', dict(iduser=user_lele.iduser, associated=True))]
    response = lele_user.post_route(
        dict(idclub=club_owned.idclub, modified_records=JSON.encode(modified)),
        'club_users',
    )
    assert response.json['success'] is True
    assert response.json['message'] == 'Ok'

    session.expunge_all()
    owned = session.get(Club, club_owned.idclub)
    assert user_lele.iduser in (u.iduser for u in owned.users)

    modified = [('iduser', dict(iduser=user_lele.iduser, associated=False))]
    response = lele_user.post_route(
        dict(idclub=club_owned.idclub, modified_records=JSON.encode(modified)),
        'club_users',
    )
    assert response.json['success'] is True
    assert response.json['message'] == 'Ok'

    session.expunge_all()
    owned = session.get(Club, club_owned.idclub)
    assert not owned.users
