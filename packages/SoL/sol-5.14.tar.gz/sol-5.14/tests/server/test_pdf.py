# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests for /pdf/* views
# :Created:   sab 07 lug 2018 19:06:51 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022, 2023, 2024, 2025 Lele Gaifax
#

from datetime import datetime

import pytest
from webtest.app import AppError

from metapensiero.sqlalchemy.proxy.json import JSON


def test_boardlabels(guest_user, tourney_knockout):
    app = guest_user

    app.get_route('pdf_boardlabels', id=tourney_knockout.idtourney)
    app.get_route(
        'pdf_boardlabels', id=tourney_knockout.idtourney, _query={'nboards': 2}
    )
    with pytest.raises(AppError):
        app.get_route(
            'pdf_boardlabels', id=tourney_knockout.idtourney, _query={'nboards': 'foo'}
        )


def test_participants(guest_user, tourney_rated, tourney_simple):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    app.get_route('pdf_participants', id=tourney_rated.idtourney)
    app.get_route('pdf_participants', id=tourney_rated.guid)

    app.get_route('pdf_participants', id=tourney_simple.idtourney)


def test_ranking(
    session,
    admin_user,
    guest_user,
    tourney_rated,
    tourney_apr24,
    tourney_asis,
    tourney_double,
    tourney_simple,
    tourney_knockout_bot,
    tourney_roundrobin,
):
    app = guest_user

    admin_user.get_route('update_ranking', _query={'idtourney': tourney_asis.idtourney})
    admin_user.get_route('assign_prizes', _query={'idtourney': tourney_asis.idtourney})
    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )

    app.get_route('pdf_tourneyranking', id=tourney_rated.idtourney)
    app.get_route('pdf_tourneyranking', id=tourney_rated.guid)

    app.get_route('pdf_tourneyranking', id=tourney_apr24.idtourney)
    app.get_route('pdf_tourneyranking', id=tourney_apr24.idtourney, _query={'turn': 1})

    app.get_route('pdf_tourneyranking', id=tourney_asis.idtourney)
    app.get_route('pdf_tourneyranking', id=tourney_asis.idtourney, _query={'turn': 1})

    app.get_route('pdf_tourneyranking', id=tourney_double.idtourney)
    app.get_route('pdf_tourneyranking', id=tourney_simple.idtourney)

    app.get_route(
        'pdf_tourneyranking', id=tourney_knockout_bot.idtourney, _query={'turn': 1}
    )
    app.get_route('pdf_tourneyranking', id=tourney_knockout_bot.idtourney)
    admin_user.get_route(
        'assign_prizes', _query={'idtourney': tourney_knockout_bot.idtourney}
    )
    app.get_route('pdf_tourneyranking', id=tourney_knockout_bot.idtourney)

    with pytest.raises(AppError):
        app.get_route(
            'pdf_tourneyranking', id=tourney_apr24.idtourney, _query={'turn': 'foo'}
        )

    for turn in range(1, 3):
        tourney_roundrobin.makeNextTurn()
        for m in tourney_roundrobin.matches:
            if m.turn == tourney_roundrobin.currentturn and m.competitor2 is not None:
                m.score1 = 10
                m.score2 = 0
        tourney_roundrobin.updateRanking()
        session.commit()
        app.get_route('pdf_tourneyranking', id=tourney_roundrobin.idtourney)

    admin_user.get_route(
        'assign_prizes', _query={'idtourney': tourney_roundrobin.idtourney}
    )
    app.get_route('pdf_tourneyranking', id=tourney_roundrobin.idtourney)


def test_under_over_ranking(guest_user, tourney_rated, tourney_apr24, tourney_asis):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    for route in ('pdf_tourneyunderranking', 'pdf_tourneyoverranking'):
        app.get_route(route, id=tourney_rated.idtourney, _query={'age': 69})
        app.get_route(route, id=tourney_rated.guid, _query={'age': 69})
        app.get_route(route, id=tourney_apr24.idtourney, _query={'age': 69})
        app.get_route(route, id=tourney_apr24.idtourney, _query={'age': 69, 'turn': 1})
        app.get_route(route, id=tourney_asis.idtourney)

        with pytest.raises(AppError):
            app.get_route(route, id=tourney_apr24.idtourney, _query={'turn': 'foo'})

        with pytest.raises(AppError):
            app.get_route(route, id=tourney_apr24.idtourney, _query={'age': 'foo'})


def test_women_ranking(guest_user, tourney_rated, tourney_apr24, tourney_asis):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    app.get_route(
        'pdf_tourneywomenranking', id=tourney_rated.idtourney, _query={'age': 69}
    )
    app.get_route('pdf_tourneywomenranking', id=tourney_rated.guid, _query={'age': 69})

    app.get_route(
        'pdf_tourneywomenranking', id=tourney_apr24.idtourney, _query={'age': 69}
    )
    app.get_route(
        'pdf_tourneywomenranking',
        id=tourney_apr24.idtourney,
        _query={'age': 69, 'turn': 1},
    )

    app.get_route('pdf_tourneywomenranking', id=tourney_asis.idtourney)

    with pytest.raises(AppError):
        app.get_route(
            'pdf_tourneywomenranking',
            id=tourney_apr24.idtourney,
            _query={'turn': 'foo'},
        )


def test_nationalranking(
    guest_user,
    tourney_first,
    tourney_double,
    tourney_rated,
    tourney_apr24,
    tourney_simple,
):
    app = guest_user

    app.get_route('pdf_nationalranking', id=tourney_first.idtourney)
    app.get_route('pdf_nationalranking', id=tourney_double.idtourney)

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    app.get_route('pdf_nationalranking', id=tourney_rated.idtourney)
    app.get_route('pdf_nationalranking', id=tourney_rated.guid)

    app.get_route('pdf_nationalranking', id=tourney_apr24.idtourney)
    app.get_route('pdf_nationalranking', id=tourney_apr24.idtourney, _query={'turn': 1})

    app.get_route('pdf_nationalranking', id=tourney_simple.idtourney)

    with pytest.raises(AppError):
        app.get_route(
            'pdf_nationalranking', id=tourney_apr24.idtourney, _query={'turn': 'foo'}
        )


def test_results(guest_user, tourney_rated, tourney_simple, tourney_knockout_bot):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    app.get_route('pdf_results', id=tourney_rated.idtourney)
    app.get_route('pdf_results', id=tourney_rated.guid)
    app.get_route('pdf_results', id=tourney_rated.idtourney, _query={'turn': 0})
    app.get_route('pdf_results', id=tourney_rated.guid, _query={'turn': 0})
    app.get_route('pdf_results', id=tourney_rated.idtourney, _query={'turn': 'all'})
    app.get_route('pdf_results', id=tourney_rated.guid, _query={'turn': 'all'})
    app.get_route('pdf_results', id=tourney_simple.idtourney)
    with pytest.raises(AppError):
        app.get_route('pdf_results', id=tourney_rated.idtourney, _query={'turn': 'foo'})

    app.get_route('pdf_results', id=tourney_knockout_bot.idtourney, _query={'turn': 1})
    app.get_route(
        'pdf_results', id=tourney_knockout_bot.idtourney, _query={'turn': 'all'}
    )


def test_results_knockout(admin_user, guest_user, tourney_knockout):
    app = guest_user

    app.get_route(
        'test_create_random_scores', _query={'idtourney': tourney_knockout.idtourney}
    )
    admin_user.get_route(
        'update_ranking', _query={'idtourney': tourney_knockout.idtourney}
    )
    admin_user.get_route(
        'assign_prizes', _query={'idtourney': tourney_knockout.idtourney}
    )

    app.get_route('pdf_results', id=tourney_knockout.idtourney, _query={'turn': 'all'})


def test_matches(guest_user, tourney_double, tourney_odd, tourney_rated):
    app = guest_user

    app.get_route('pdf_matches', id=tourney_double.idtourney)
    app.get_route('pdf_matches', id=tourney_odd.idtourney)

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )
    app.get_route('pdf_matches', id=tourney_rated.idtourney)
    app.get_route('pdf_matches', id=tourney_rated.guid)
    app.get_route('pdf_matches', id=tourney_rated.idtourney, _query={'turn': 1})
    app.get_route('pdf_matches', id=tourney_rated.guid, _query={'turn': 1})
    with pytest.raises(AppError):
        app.get_route('pdf_matches', id=tourney_rated.idtourney, _query={'turn': 'foo'})


def test_scorecards(guest_user, tourney_rated):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )

    app.get_route('pdf_scorecards', id='blank')
    app.get_route('pdf_scorecards', id=tourney_rated.idtourney)
    app.get_route(
        'pdf_scorecards',
        id=tourney_rated.guid,
        _query={'starttime': datetime.now().timestamp()},
    )
    app.get_route(
        'pdf_scorecards',
        id=tourney_rated.guid,
        _query={'starttime': int(datetime.now().timestamp() * 1000)},
    )
    with pytest.raises(AppError):
        app.get_route(
            'pdf_scorecards', id=tourney_rated.guid, _query={'starttime': 'foo'}
        )
    with pytest.raises(AppError):
        app.get_route('pdf_scorecards', id='foo')
    with pytest.raises(AppError):
        app.get_route('pdf_scorecards', id=-1)


def test_badges(
    admin_user,
    guest_user,
    tourney_rated,
    tourney_apr24,
    tourney_asis,
    tourney_closed,
    tourney_simple,
):
    app = guest_user

    admin_user.get_route('update_ranking', _query={'idtourney': tourney_asis.idtourney})
    admin_user.get_route('assign_prizes', _query={'idtourney': tourney_asis.idtourney})
    admin_user.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )

    app.get_route('pdf_badges', id=tourney_rated.idtourney)
    app.get_route('pdf_badges', id=tourney_rated.guid)

    app.get_route('pdf_badges', id=tourney_apr24.idtourney)
    app.get_route('pdf_badges', id=tourney_apr24.guid)

    app.get_route('pdf_badges', id=tourney_asis.idtourney)

    app.get_route('pdf_badges', id=tourney_closed.idtourney)

    app.get_route('pdf_badges', id=tourney_simple.idtourney)

    app.get_route('pdf_badges', id=tourney_simple.idtourney, _query={'blank': True})
    app.get_route('pdf_badges', id=tourney_simple.idtourney, _query={'blank': 10})

    with pytest.raises(AppError):
        app.get_route('pdf_badges', id='foo')
    with pytest.raises(AppError):
        app.get_route('pdf_badges', id=-1)


def test_badges_centesimal_prized(admin_user, guest_user, tourney_closed):
    app = guest_user

    app.get_route(
        'test_create_random_scores', _query={'idtourney': tourney_closed.idtourney}
    )
    admin_user.get_route(
        'update_ranking', _query={'idtourney': tourney_closed.idtourney}
    )
    admin_user.get_route(
        'assign_prizes', _query={'idtourney': tourney_closed.idtourney}
    )
    app.get_route('pdf_badges', id=tourney_closed.idtourney)


def test_badges_emblem(admin_user, tourney_closed):
    app = admin_user

    img = (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
        'AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO'
        '9TXL0Y4OHwAAAABJRU5ErkJggg=='
    )

    app.get_route(
        'test_create_random_scores', _query={'idtourney': tourney_closed.idtourney}
    )
    app.get_route('update_ranking', _query={'idtourney': tourney_closed.idtourney})
    app.get_route('assign_prizes', _query={'idtourney': tourney_closed.idtourney})

    modified = [
        (
            'idclub',
            dict(
                idclub=tourney_closed.championship.club.idclub,
                image=img,
                emblem='foo.png',
            ),
        )
    ]
    deleted = []
    admin_user.post_route(
        dict(
            modified_records=JSON.encode(modified), deleted_records=JSON.encode(deleted)
        ),
        'save_changes',
    )
    admin_user.get_route('pdf_badges', id=tourney_closed.idtourney)


def test_championshipranking(
    session,
    admin_user,
    guest_user,
    tourney_closed,
    tourney_double,
    tourney_rated,
    tourney_skipworstprize,
    tourney_second,
    tourney_second_replica,
):
    app = guest_user

    admin_user.get_route(
        'update_ranking', _query={'idtourney': tourney_skipworstprize.idtourney}
    )
    admin_user.get_route(
        'assign_prizes', _query={'idtourney': tourney_skipworstprize.idtourney}
    )
    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )

    app.get_route(
        'pdf_championshipranking', id=tourney_closed.championship.idchampionship
    )
    app.get_route(
        'pdf_championshipranking', id=tourney_double.championship.idchampionship
    )
    app.get_route(
        'pdf_championshipranking', id=tourney_rated.championship.idchampionship
    )
    app.get_route('pdf_championshipranking', id=tourney_rated.championship.guid)
    app.get_route(
        'pdf_championshipranking', id=tourney_skipworstprize.championship.guid
    )

    with pytest.raises(AppError):
        app.get_route('pdf_championshipranking', id='foo')
    with pytest.raises(AppError):
        app.get_route('pdf_championshipranking', id=-1)

    for tourney in (tourney_second, tourney_second_replica):
        for turn in range(1, 3):
            tourney.updateRanking()
            tourney.makeNextTurn()
            for m in tourney.matches:
                if m.turn == tourney.currentturn and m.competitor2 is not None:
                    m.score1 = 10
                    m.score2 = 0
        tourney.updateRanking()
        tourney.assignPrizes()

    session.commit()

    app.get_route('pdf_championshipranking', id=tourney_second.idchampionship)


def test_ratingranking(guest_user, tourney_rated):
    app = guest_user

    app.get_route(
        'test_create_random_finals', _query={'idtourney': tourney_rated.idtourney}
    )

    app.get_route('pdf_ratingranking', id=tourney_rated.rating.idrating)
    app.get_route('pdf_ratingranking', id=tourney_rated.rating.guid)
    with pytest.raises(AppError):
        app.get_route('pdf_ratingranking', id='foo')
    with pytest.raises(AppError):
        app.get_route('pdf_ratingranking', id=-1)


def test_playbill(guest_user, tourney_hosted, tourney_knockout):
    app = guest_user

    app.get_route('pdf_playbill', id=tourney_hosted.idtourney)
    app.get_route('pdf_playbill', id=tourney_knockout.idtourney)
