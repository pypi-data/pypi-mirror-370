# -*- coding: utf-8 -*-
# :Project:   SoL -- Test /tourney/* views
# :Created:   dom 08 lug 2018 12:22:26 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020-2024 Lele Gaifax
#

from datetime import date, timedelta
from pathlib import Path
from os import fspath

from metapensiero.sqlalchemy.proxy.json import JSON
from pyramid_mailer import get_mailer
import transaction

from sol.models import Board, Tourney
from sol.models.bio import load_sol


def test_guest_competitors_metadata(guest_user, tourney_first):
    response = guest_user.get_route(
        'competitors',
        _query={'metadata': 'metadata', 'filter_by_idtourney': tourney_first.idtourney},
    )
    result = response.json
    assert result['success'] is True
    assert result['metadata']['fields'][-1]['name'] == 'player1Country'
    assert result['count'] == 6


def test_guest_competitors(guest_user, tourney_first):
    response = guest_user.get_route(
        'competitors', _query={'filter_by_idtourney': tourney_first.idtourney}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 6


def test_guest_players(guest_user):
    response = guest_user.get_route('tourney_players')
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'


def test_guest_matches(guest_user, tourney_first):
    response = guest_user.get_route(
        'matches',
        _query={'metadata': 'metadata', 'filter_by_idtourney': tourney_first.idtourney},
    )
    assert [f['name'] for f in response.json['metadata']['fields']] == [
        'board',
        'description',
        'score1',
        'score2',
        'score1_2',
        'score2_2',
        'score1_3',
        'score2_3',
        'turn',
        'final',
        'idmatch',
        'idcompetitor1',
        'idcompetitor2',
    ] + [f'coins1_{i}' for i in range(1, 20)] + [
        f'coins2_{i}' for i in range(1, 20)
    ] + [f'queen_{i}' for i in range(1, 20)]
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 9


def test_guest_ranking_metadata(guest_user, tourney_first):
    response = guest_user.get_route(
        'ranking',
        _query={'metadata': 'metadata', 'filter_by_idtourney': tourney_first.idtourney},
    )
    result = response.json
    assert result['success'] is True
    assert result['metadata']['fields'][0]['name'] == 'rank'


def test_guest_update_ranking(guest_user, tourney_first):
    response = guest_user.get_route(
        'update_ranking', _query={'idtourney': tourney_first.idtourney}
    )
    result = response.json
    assert result['success'] is False
    assert 'not allowed' in result['message']


def test_guest_current_matches(guest_user, tourney_first):
    response = guest_user.get_route(
        'current_matches', _query={'filter_by_idtourney': tourney_first.idtourney}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 3
    b = result['root'][0]
    assert b['competitor1Opponents'] == [5, 4]
    assert b['competitor2Opponents'] == [1, 3]
    b = result['root'][1]
    assert b['competitor1Opponents'] == [2, 5]
    assert b['competitor2Opponents'] == [4, 2]
    b = result['root'][2]
    assert b['competitor1Opponents'] == [6, 1]
    assert b['competitor2Opponents'] == [3, 6]


def test_guest_countdown(guest_user, tourney_first):
    response = guest_user.get_route(
        'countdown', _query={'idtourney': tourney_first.idtourney}
    )
    assert 'Countdown' in response.text


def test_guest_start_countdown(guest_user, tourney_first):
    response = guest_user.post_route(
        {},
        'countdown',
        _query={'idtourney': tourney_first.idtourney, 'start': '12121212'},
    )
    result = response.json
    assert result['success'] is False
    assert 'not owned by you' in result['message']


def test_guest_pre_countdown(guest_user, tourney_first):
    response = guest_user.get_route(
        'pre_countdown',
        _query={'idtourney': tourney_first.idtourney, 'duration': 2, 'prealarm': 1},
    )
    assert 'Countdown' in response.text


def test_odd_current_matches(admin_user, tourney_odd):
    idt = tourney_odd.idtourney

    response = admin_user.get_route('new_turn', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    response = admin_user.get_route(
        'current_matches', _query={'filter_by_idtourney': idt}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 9

    opps = {}
    for b in result['root']:
        assert b['competitor1Opponents'] == []
        assert b['competitor2Opponents'] == []
        if b['idcompetitor2']:
            opps[b['idcompetitor1']] = [b['idcompetitor2']]
            opps[b['idcompetitor2']] = [b['idcompetitor1']]
        else:
            opps[b['idcompetitor1']] = opps[b['idcompetitor2']] = []

    results = [
        ('idmatch', dict(idmatch=b['idmatch'], score1=25, score2=0))
        for b in result['root']
    ]
    response = admin_user.post_route(
        dict(modified_records=JSON.encode(results), deleted_records=JSON.encode([])),
        'save_changes',
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    response = admin_user.get_route('update_ranking', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    response = admin_user.get_route('new_turn', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    response = admin_user.get_route(
        'current_matches', _query={'filter_by_idtourney': idt}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 9
    for b in result['root']:
        assert b['competitor1Opponents'] == opps[b['idcompetitor1']]
        assert b['competitor2Opponents'] == opps[b['idcompetitor2']]


def test_ranking(admin_user, tourney_first):
    idt = tourney_first.idtourney

    response = admin_user.get_route('update_ranking', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['currentturn'] == result['rankedturn']
    assert result['prized'] is False

    response = admin_user.get_route('ranking', _query={'filter_by_idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 6
    assert [r['rank'] for r in result['root']] == list(range(1, 7))
    astuples = [
        (r['prize'], r['points'], r['bucholz'], r['netscore'], r['totscore'], r['rank'])
        for r in result['root']
    ]
    astuples.sort()
    assert [r[5] for r in astuples] == list(range(6, 0, -1))


def test_ranking_at_turn(admin_user, tourney_first):
    idt = tourney_first.idtourney
    c3desc = tourney_first.competitors[2].description

    response = admin_user.get_route(
        'ranking', _query={'filter_by_idtourney': idt, 'turn': 1}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 6
    assert result['root'][0]['description'] == c3desc
    assert result['root'][0]['points'] == 2

    response = admin_user.get_route(
        'ranking', _query={'filter_by_idtourney': idt, 'turn': 2}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 6
    assert result['root'][0]['description'] == c3desc
    assert result['root'][0]['points'] == 4


def test_delete_turns(admin_user, tourney_first):
    idt = tourney_first.idtourney

    response = admin_user.get_route(
        'delete_from_turn', _query={'idtourney': idt, 'fromturn': 2}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['currentturn'] == result['rankedturn']
    assert result['currentturn'] == 1
    assert result['finalturns'] is False
    assert result['prized'] is False


def test_finals(admin_user, session, tourney_apr24):
    idt = tourney_apr24.idtourney

    response = admin_user.get_route('update_ranking', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True

    response = admin_user.get_route('final_turn', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['rankedturn'] == result['currentturn'] - 1
    assert result['finalturns'] is True

    admin_user.get_route('pdf_scorecards', id=idt)

    session.expunge_all()

    apr24 = session.get(Tourney, idt)
    results = [
        ('idmatch', dict(idmatch=m.idmatch, score1=10, score2=20))
        for m in apr24.matches
        if m.final
    ]
    assert len(results) == 2
    response = admin_user.post_route(
        dict(modified_records=JSON.encode(results), deleted_records=JSON.encode([])),
        'save_changes',
    )
    assert response.json['success'] is True
    assert response.json['message'] == 'Ok'

    response = admin_user.get_route('update_ranking', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['rankedturn'] == result['currentturn']
    assert result['prized'] is False


def test_replay_gets_right_owner(lele_user, session, tourney_apr24, user_lele):
    idt = tourney_apr24.idtourney
    idc = tourney_apr24.idchampionship

    response = lele_user.get_route('replay_today', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    nidt = result['new_idtourney']
    assert nidt is not None

    n = session.get(Tourney, result['new_idtourney'])
    assert n.idchampionship == idc
    assert n.date == date.today()
    assert n.owner is user_lele

    response = lele_user.post_route(
        {}, 'countdown', _query={'idtourney': nidt, 'start': '12121212'}
    )
    result = response.json
    assert result['success'] is True
    assert 'started' in result['message']

    response = lele_user.post_route({}, 'countdown', _query={'idtourney': nidt})
    result = response.json
    assert result['success'] is True
    assert 'terminated' in result['message']


def test_finals_swap(lele_user, session):
    testdir = Path(__file__).parent.parent
    fullname = testdir / 'scr' / 'Campionato_CCM_2014_2015-2014-12-14+7.sol'

    with transaction.manager:
        tourneys, skipped = load_sol(session, fspath(fullname))
        guid = tourneys[0].guid
        session.flush()

    tourney = session.query(Tourney).filter_by(guid=guid).one()
    idt = tourney.idtourney

    assert tourney.prized is False
    assert tourney.finalturns is False
    assert tourney.currentturn == 7
    assert tourney.rankedturn == tourney.currentturn

    response = lele_user.get_route('final_turn', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['prized'] is False
    assert result['currentturn'] == 8
    assert result['finalturns'] is True

    session.expunge_all()

    tourney = session.get(Tourney, idt)
    finalmatches = [m for m in tourney.matches if m.final]
    assert len(finalmatches) == 1

    final = finalmatches[0]
    assert final.competitor1.player1.firstname == 'Ayesh Nilan'
    assert final.competitor2.player1.firstname == 'Suresh'

    results = [('idmatch', dict(idmatch=final.idmatch, score1=4, score2=23))]
    response = lele_user.post_route(
        dict(modified_records=JSON.encode(results), deleted_records=JSON.encode([])),
        'save_changes',
    )
    assert response.json['success'] is True
    assert response.json['message'] == 'Ok'

    response = lele_user.get_route('update_ranking', _query={'idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['rankedturn'] == result['currentturn']
    assert result['prized'] is True

    currentturn = result['currentturn']
    response = lele_user.get_route('ranking', _query={'filter_by_idtourney': idt})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['count'] == 17

    ranking = result['root']
    first = ranking[0]
    second = ranking[1]
    assert first['prize'] == 1000
    assert '<b>F' in first['description'] and '</b> S' in first['description']
    assert second['prize'] == 900
    assert '<b>V' in second['description'] and '/b> A' in second['description']

    response = lele_user.get_route(
        'delete_from_turn', _query={'idtourney': idt, 'fromturn': currentturn - 1}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'
    assert result['currentturn'] == result['rankedturn']
    assert result['finalturns'] is False
    assert result['prized'] is False


def assign_prizes(app, session, idtourney):
    response = app.get_route('update_ranking', _query={'idtourney': idtourney})
    result = response.json
    assert result['success'] is True

    response = app.get_route('assign_prizes', _query={'idtourney': idtourney})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    session.expunge_all()

    t = session.get(Tourney, idtourney)
    assert t.prized is True
    assert t.ranking[0].prize == 18

    return t


def test_assign_and_reset_prizes(admin_user, session, tourney_second):
    assign_prizes(admin_user, session, tourney_second.idtourney)

    response = admin_user.get_route(
        'reset_prizes', _query={'idtourney': tourney_second.idtourney}
    )
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    session.expunge_all()

    t = session.get(Tourney, tourney_second.idtourney)
    assert t.prized is False


def test_assign_prizes_with_rating(admin_user, session, tourney_rated):
    t = assign_prizes(admin_user, session, tourney_rated.idtourney)
    assert t.rating.rates[-1].date == t.date


def test_send_training_urls(admin_user, tourney_corona):
    admin_user.get_route(
        'send_training_urls', _query={'idtourney': tourney_corona.idtourney}
    )
    registry = admin_user.app.registry
    mailer = get_mailer(registry)
    outbox = mailer.outbox
    assert len(outbox) == 4


def test_send_training_urls_odd(admin_user, tourney_corona_odd):
    admin_user.get_route(
        'send_training_urls', _query={'idtourney': tourney_corona_odd.idtourney}
    )
    registry = admin_user.app.registry
    mailer = get_mailer(registry)
    outbox = mailer.outbox
    assert len(outbox) == 3


def test_send_training_urls_aaa(admin_user, session, tourney_corona_all_against_all):
    tourney_corona_all_against_all.makeNextTurn()
    session.flush()
    try:
        admin_user.get_route(
            'send_training_urls',
            _query={'idtourney': tourney_corona_all_against_all.idtourney},
        )
        registry = admin_user.app.registry
        mailer = get_mailer(registry)
        outbox = mailer.outbox
        assert len(outbox) == 6
    finally:
        session.rollback()


def test_get_self_edit_urls(admin_user, tourney_corona):
    result = admin_user.get_route(
        'get_board_self_edit_url',
        _query={'idtourney': tourney_corona.idtourney, 'board': 1},
    ).json
    assert result['success']

    result = admin_user.get_route(
        'get_competitor1_self_edit_url',
        _query={'idmatch': tourney_corona.matches[-1].idmatch},
    ).json
    assert result['success']

    result = admin_user.get_route(
        'get_competitor2_self_edit_url',
        _query={'idmatch': tourney_corona.matches[-1].idmatch},
    ).json
    assert result['success']


def test_corona_matches(admin_user, session, tourney_corona):
    for m in tourney_corona.matches:
        m.boards = [
            Board(number=1, coins1=10, coins2=20),
            Board(number=2, coins1=10, coins2=20),
            Board(number=3, coins1=10, coins2=20),
            Board(number=4, coins1=10, coins2=20),
        ]
    session.flush()

    response = admin_user.get_route(
        'matches',
        _query={
            'metadata': 'metadata',
            'filter_by_idtourney': tourney_corona.idtourney,
        },
    )
    assert [f['name'] for f in response.json['metadata']['fields']] == [
        'board',
        'description',
        'score1',
        'score2',
        'score1_2',
        'score2_2',
        'score1_3',
        'score2_3',
        'turn',
        'final',
        'idmatch',
        'idcompetitor1',
        'idcompetitor2',
        'coins1_1',
        'coins1_2',
        'coins2_1',
        'coins2_2',
    ]
    root = response.json['root']
    root0 = root[0]
    assert root0['board'] == 1
    assert root0['score1'] == root0['score1'] == 0
    assert root0['coins1_1'] == 10
    assert root0['coins2_1'] == 20


def test_create_knockout(admin_user, session, tourney_pre_knockout):
    idtourney = tourney_pre_knockout.idtourney
    response = admin_user.get_route('update_ranking', _query={'idtourney': idtourney})
    result = response.json
    assert result['success'] is True

    response = admin_user.get_route('assign_prizes', _query={'idtourney': idtourney})
    result = response.json
    assert result['success'] is True
    assert result['message'] == 'Ok'

    tomorrow = date.today() + timedelta(days=1)
    response = admin_user.get_route(
        'create_knockout',
        _query={
            'idtourney': idtourney,
            'ncompetitors': 16,
            'date': tomorrow.isoformat(),
        },
    )
    result = response.json
    assert result['success'] is True, result['message']
    nidt = result['new_idtourney']
    assert nidt is not None


def test_knockout_matches(admin_user, session, tourney_knockout_bot):
    response = admin_user.get_route(
        'matches',
        _query={
            'metadata': 'metadata',
            'filter_by_idtourney': tourney_knockout_bot.idtourney,
        },
    )
    fmetas = response.json['metadata']['fields']
    assert fmetas[0]['name'] == 'board'
    assert fmetas[1]['name'] == 'description'
    assert fmetas[2]['name'] == 'score1'
    assert fmetas[2]['label'] == 'S1 (1)'
    assert fmetas[3]['name'] == 'score2'
    assert fmetas[3]['label'] == 'S2 (1)'
