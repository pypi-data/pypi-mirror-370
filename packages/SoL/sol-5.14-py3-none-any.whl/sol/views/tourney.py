# -*- coding: utf-8 -*-
# :Project:   SoL -- Tourney controller
# :Created:   gio 23 ott 2008 11:13:02 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013, 2014, 2016-2018, 2020-2025 Lele Gaifax
#

from __future__ import annotations

import logging
import time
from operator import itemgetter
from random import randint

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query

from ..i18n import country_name
from ..i18n import ngettext
from ..i18n import ordinal
from ..i18n import translatable_string as _
from ..i18n import translator
from ..models import Championship
from ..models import Competitor
from ..models import Match
from ..models import Player
from ..models import Tourney
from ..models.competitor import competitors_sorters
from ..models.errors import OperationAborted
from . import compute_elapsed_time
from . import expose
from . import get_request_logger
from . import unauthorized_for_guest

logger = logging.getLogger(__name__)


@view_config(route_name='tourney_players', renderer='json')
@expose(Player, fields='idplayer,description'.split(','))
def players(request, results):
    return results


@view_config(route_name='competitors', renderer='json')
@expose(
    Competitor,
    fields=(
        'player1FullName,player2FullName,'
        'player3FullName,player4FullName,'
        'position,player1Nationality,player1Sex,'
        'idcompetitor,retired,idplayer1,'
        'idplayer2,idplayer3,idplayer4,'
        'rate,idtourney,player1LastName,player1FirstName'
    ).split(','),
    metadata=dict(
        player1FullName=dict(
            label=_('Player'),
            hint=_('Full name of the player.'),
            lookup=dict(
                url='/tourney/players?sort_by_lastname=ASC&sort_by_firstname=ASC',
                idField='idplayer',
                lookupField='idplayer1',
                displayField='description',
                width=200,
                pageSize=12,
            ),
        ),
        player2FullName=dict(
            label=_('2nd player'),
            hint=_('Full name of the second player.'),
            lookup=dict(
                url='/tourney/players?sort_by_lastname=ASC&sort_by_firstname=ASC',
                idField='idplayer',
                lookupField='idplayer2',
                displayField='description',
                width=200,
                pageSize=12,
            ),
        ),
        player3FullName=dict(
            label=_('3rd player'),
            hint=_('Full name of the third player.'),
            lookup=dict(
                url='/tourney/players?sort_by_lastname=ASC&sort_by_firstname=ASC',
                idField='idplayer',
                lookupField='idplayer3',
                displayField='description',
                width=200,
                pageSize=12,
            ),
        ),
        player4FullName=dict(
            label=_('4th player'),
            hint=_('Full name of the fourth player.'),
            lookup=dict(
                url='/tourney/players?sort_by_lastname=ASC&sort_by_firstname=ASC',
                idField='idplayer',
                lookupField='idplayer4',
                displayField='description',
                width=200,
                pageSize=12,
            ),
        ),
        player1Nationality=dict(
            label=_('Nationality'),
            hint=_('First player nationality.'),
            hidden=True,
            readOnly=True,
        ),
        player1Sex=dict(
            label=_('Gender'),
            hint=_('Gender of the first player.'),
            hidden=True,
            readOnly=True,
        ),
        player1FirstName=dict(
            label=_("First player's name"),
            hint=_('First name of the first player.'),
            hidden=True,
            readOnly=True,
        ),
        player1LastName=dict(
            label=_("First player's surname"),
            hint=_('Last name of the first player.'),
            hidden=True,
            readOnly=True,
        ),
        rate=dict(
            label=_('Rate'),
            hint=_('Most recent Glicko rate value of the competitor.'),
            hidden=True,
            readonly=True,
        ),
    ),
)
def competitors(request, results):
    # Add the full name of the first player country, used as an hint
    # on the competitors pane flag icons
    if 'metadata' in results:
        t = translator(request)
        results['metadata']['fields'].append(
            {
                'label': t(_('Country')),
                'hint': t(_('Country name')),
                'name': 'player1Country',
                'hidden': True,
            }
        )
    else:
        for r in results['root']:
            code = r['player1Nationality']
            if code:
                r['player1Country'] = country_name(code, request=request)
    return results


_championship_t = Championship.__table__
_matches_t = Match.__table__
_tourneys_t = Tourney.__table__


@view_config(route_name='current_matches', renderer='json')
@expose(
    Query([Match])
    .filter(_matches_t.c.turn == _tourneys_t.c.currentturn)
    .filter(_matches_t.c.idtourney == _tourneys_t.c.idtourney)
    .order_by(_matches_t.c.board),
    fields=(
        'board,idcompetitor1,competitor1FullName,idcompetitor2,competitor2FullName'
        ',idmatch,idtourney,score1,score2,score1_2,score2_2,score1_3,score2_3'
        ',competitor1Opponents,competitor2Opponents'
    ).split(','),
)
def currentMatches(request, results):
    return results


@view_config(route_name='matches', renderer='json')
@expose(
    Match,
    fields=(
        'board,description,score1,score2,score1_2,score2_2,score1_3,score2_3'
        ',turn,final,idmatch,idcompetitor1,idcompetitor2'
    ).split(','),
    asdict=False,
    metadata=dict(
        board=dict(readonly=True, sortable=False, width=40),
        description=dict(
            label=_('Match'),
            hint=_('Competitor 1 vs Competitor 2.'),
            sortable=False,
            readonly=True,
            flex=1,
        ),
        score1=dict(sortable=False, width=60),
        score2=dict(sortable=False, width=60),
        score1_2=dict(sortable=False, width=60),
        score2_2=dict(sortable=False, width=60),
        score1_3=dict(sortable=False, width=60),
        score2_3=dict(sortable=False, width=60),
        turn=dict(hidden=True, readonly=True, sortable=False, width=70),
        final=dict(hidden=True, readonly=True, sortable=False),
        idmatch=dict(sortable=False),
        idcompetitor1=dict(sortable=False),
        idcompetitor2=dict(sortable=False),
    ),
)
def matches():
    request, args = yield
    results = yield args

    q = (
        select(_championship_t.c.trainingboards)
        .select_from(_championship_t.join(_tourneys_t))
        .where(_tourneys_t.c.idtourney == int(request.params['filter_by_idtourney']))
    )
    tboards = request.dbsession.scalar(q) or 0

    root = results.get('root')
    if root:
        newroot = results['root'] = []
        for match in root:
            m = dict(
                board=match.board,
                description=match.description,
                score1=match.score1,
                score2=match.score2,
                score1_2=match.score1_2,
                score2_2=match.score2_2,
                score1_3=match.score1_3,
                score2_3=match.score2_3,
                turn=match.turn,
                final=match.final,
                idmatch=match.idmatch,
                idcompetitor1=match.idcompetitor1,
                idcompetitor2=match.idcompetitor2,
            )
            for i, board in enumerate(match.boards, 1):
                board = match.boards[i - 1] if match.boards else None
                m[f'coins1_{i}'] = board.coins1 if board else None
                m[f'coins2_{i}'] = board.coins2 if board else None
                m[f'queen_{i}'] = board.queen if board else None
            newroot.append(m)

    md = results.get('metadata')
    if md:
        t = translator(request)
        fields = md['fields']

        q = select(_tourneys_t.c.matcheskind).where(
            _tourneys_t.c.idtourney == int(request.params['filter_by_idtourney'])
        )
        matcheskind = request.dbsession.scalar(q)
        if matcheskind != 'bestof3':
            for f in fields:
                if f['name'] in {'score1_2', 'score2_2', 'score1_3', 'score2_3'}:
                    f['hidden'] = True
        else:
            for f in fields:
                if f['name'] == 'score1':
                    f['label'] = t(_('S1 (1)'))
                    f['hint'] = t(_('Score of the first competitor in the first game.'))
                elif f['name'] == 'score2':
                    f['label'] = t(_('S2 (1)'))
                    f['hint'] = t(
                        _('Score of the second competitor in the first game.')
                    )

        if tboards:
            for i in range(1, tboards + 1):
                fields.append(
                    dict(
                        type='integer',
                        align='right',
                        nullable=True,
                        # TRANSLATORS: this is the label for the "misses of the first competitor in
                        # given board" in the Matches grid, keep it as compact as possible
                        label=t(_('M1/$board', mapping=dict(board=i))),
                        hint=t(
                            _(
                                'Number of unsuccessful shots of the first competitor in board'
                                ' $board.',
                                mapping=dict(board=i),
                            )
                        ),
                        min=0,
                        width=50,
                        sortable=False,
                        name=f'coins1_{i}',
                    )
                )
            for i in range(1, tboards + 1):
                fields.append(
                    dict(
                        type='integer',
                        align='right',
                        nullable=True,
                        # TRANSLATORS: this is the label for the "misses of the second competitor
                        # in given board" in the Matches grid, keep it as compact as possible
                        label=t(_('M2/$board', mapping=dict(board=i))),
                        hint=t(
                            _(
                                'Number of unsuccessful shots of the second competitor in board'
                                ' $board.',
                                mapping=dict(board=i),
                            )
                        ),
                        min=0,
                        width=50,
                        sortable=False,
                        name=f'coins2_{i}',
                    )
                )
        else:
            for i in range(1, 20):
                fields.append(
                    dict(
                        type='integer',
                        align='right',
                        nullable=True,
                        # TRANSLATORS: this is the label for the "coins of the first competitor in
                        # given board" in the Matches grid, keep it as compact as possible
                        label=t(_('C1/$board', mapping=dict(board=i))),
                        hint=t(
                            _(
                                'Number of coins of the first competitor in board'
                                ' $board.',
                                mapping=dict(board=i),
                            )
                        ),
                        min=0,
                        max=9,
                        width=50,
                        sortable=False,
                        hidden=True,
                        name=f'coins1_{i}',
                    )
                )
            for i in range(1, 20):
                fields.append(
                    dict(
                        type='integer',
                        align='right',
                        nullable=True,
                        # TRANSLATORS: this is the label for the "coins of the second competitor
                        # in given board" in the Matches grid, keep it as compact as possible
                        label=t(_('C2/$board', mapping=dict(board=i))),
                        hint=t(
                            _(
                                'Number of coins of the second competitor in board'
                                ' $board.',
                                mapping=dict(board=i),
                            )
                        ),
                        min=0,
                        max=9,
                        width=50,
                        sortable=False,
                        hidden=True,
                        name=f'coins2_{i}',
                    )
                )
            for i in range(1, 20):
                fields.append(
                    dict(
                        type='string',
                        nullable=True,
                        # TRANSLATORS: this is the label for the "who pocketed the queen
                        # in given board" in the Matches grid, keep it as compact as possible
                        label=t(_('Q/$board', mapping=dict(board=i))),
                        hint=t(
                            _(
                                'Which competitor pocketed the Queen in board $board, if any.',
                                mapping=dict(board=i),
                            )
                        ),
                        width=50,
                        sortable=False,
                        hidden=True,
                        name=f'queen_{i}',
                        dictionary={
                            '1': t(_('First competitor')),
                            '2': t(_('Second competitor')),
                        },
                    )
                )

    yield results


def _fill_in_opponents_in_ranking(
        tourney: Tourney,
        turn: int,
        ranking: list[dict]
) -> None:
    "Add opponent's info to each competitor in the given `ranking`."

    prev_turn_ranking = [
        dict(
            rank=i,
            idcompetitor=c.idcompetitor,
            description=c.description,
            points=r.points,
            netscore=r.netscore,
            totscore=r.totscore,
            bucholz=r.bucholz,
            rate=r.rate,
            position=c.position,
            prize=0,
            player1Nationality=c.player1Nationality,
        )
        for i, (c, r) in enumerate(tourney.computeRanking(turn-1), 1)
    ]

    rank_by_comp = {r['idcompetitor']: r for r in prev_turn_ranking}
    opponent_by_comp = {}
    for m in tourney.matches:
        if m.turn > turn:
            break
        elif m.turn != turn:
            continue

        opp = opponent_by_comp[m.idcompetitor1] = {}
        if m.idcompetitor2 is None:
            opp['copp'] = m.competitor2FullName
        else:
            opprank = rank_by_comp[m.idcompetitor2]
            opp['copp'] = opprank['description']
            opp['copp_rank'] = opprank['rank']
            opp['copp_pts'] = opprank['points']
            opp['copp_bch'] = opprank['bucholz']
            opp['copp_ns'] = opprank['netscore']

        if m.idcompetitor2 is not None:
            opprank = rank_by_comp[m.idcompetitor1]
            opp = opponent_by_comp[m.idcompetitor2] = {}
            opp['copp'] = opprank['description']
            opp['copp_rank'] = opprank['rank']
            opp['copp_pts'] = opprank['points']
            opp['copp_bch'] = opprank['bucholz']
            opp['copp_ns'] = opprank['netscore']

    for competitor in ranking:
        if competitor['idcompetitor'] in opponent_by_comp:
            competitor.update(opponent_by_comp[competitor['idcompetitor']])


@view_config(route_name='ranking', renderer='json', request_param='turn')
def rankingForTurn(request):
    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['filter_by_idtourney'])
        turn = int(params['turn'])

        tourney = sess.get(Tourney, idtourney)

        ranking = [
            dict(
                rank=i,
                idcompetitor=c.idcompetitor,
                description=c.description,
                points=r.points,
                netscore=r.netscore,
                totscore=r.totscore,
                bucholz=r.bucholz,
                rate=r.rate,
                position=c.position,
                prize=0,
                player1Nationality=c.player1Nationality,
            )
            for i, (c, r) in enumerate(tourney.computeRanking(turn), 1)
        ]

        _fill_in_opponents_in_ranking(tourney, int(params['turn']), ranking)

        return dict(success=True, message='Ok', count=len(ranking), root=ranking)
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't compute ranking: %s", message, exc_info=True
        )
        return dict(success=False, message=message)


@view_config(route_name='ranking', renderer='json')
@expose(
    Competitor,
    fields=(
        'description,points,bucholz,netscore,prize,totscore,'
        'position,rate,player1Nationality,idcompetitor'
    ).split(','),
    metadata=dict(
        description=dict(
            label=_('Competitor'),
            hint=_('Full name of the players.'),
            sortable=False,
            readonly=True,
            flex=1,
        ),
        points=dict(readonly=True, width=40, sortable=False),
        bucholz=dict(readonly=True, width=40, sortable=False),
        netscore=dict(readonly=True, width=40, sortable=False),
        totscore=dict(hidden=True, readonly=True, width=40, sortable=False),
        prize=dict(hidden=True, width=55, sortable=False, decimals=2, type='numeric'),
        position=dict(readonly=True, hidden=True, width=40, sortable=False),
        rate=dict(
            label=_('Rate'),
            hint=_(
                'Most recent Glicko rate of the competitor (if'
                ' tourney is associated with a rating).'
            ),
            hidden=True,
            align='right',
            type='integer',
            readonly=True,
            width=50,
        ),
        player1Nationality=dict(
            label=_('Nationality'),
            hint=_('Nationality of the competitor.'),
            hidden=True,
            readonly=True,
            width=40,
        ),
    ),
)
def ranking(request, results):
    t = translator(request)
    if 'metadata' in results:
        results['metadata']['fields'].insert(
            0,
            {
                'label': t(_('#')),
                'hint': t(_('Position in the ranking.')),
                'width': 35,
                'readonly': True,
                'name': 'rank',
                'align': 'right',
                'type': 'integer',
            },
        )
        results['metadata']['fields'].extend((
            {
                'label': t(_('Opponent')),
                'hint': t(_('Full name of current opponent.')),
                'readonly': True,
                'sortable': False,
                'name': 'copp',
                'hidden': True,
            },
            {
                'label': t(_("Opponent's pts")),
                'hint': t(_('Current opponent points.')),
                'readonly': True,
                'sortable': False,
                'name': 'copp_pts',
                'hidden': True,
                'align': 'right',
                'type': 'integer',
            },
            {
                'label': t(_("Opponent's bch")),
                'hint': t(_('Current opponent bucholz.')),
                'readonly': True,
                'sortable': False,
                'name': 'copp_bch',
                'hidden': True,
                'align': 'right',
                'type': 'integer',
            },
            {
                'label': t(_("Opponent's ns")),
                'hint': t(_('Current opponent net score.')),
                'readonly': True,
                'sortable': False,
                'name': 'copp_ns',
                'hidden': True,
                'align': 'right',
                'type': 'integer',
            },
            {
                'label': t(_("Opponent's #")),
                'hint': t(_('Current opponent position in the ranking.')),
                'readonly': True,
                'sortable': False,
                'name': 'copp_rank',
                'hidden': True,
                'align': 'right',
                'type': 'integer',
            },
        ))
    else:
        tourney = request.dbsession.get(Tourney, int(request.params['filter_by_idtourney']))
        ranking = results['root']
        # Match the local ordering applied by the Ranking panel, so the "rank" field is
        # reasonable: by ascending player's name, then by descending ranking position.
        ranking.sort(key=itemgetter('description'))
        ranking.sort(key=competitors_sorters[(tourney.system, 'dict')], reverse=True)
        for rank, competitor in enumerate(ranking, 1):
            competitor['rank'] = rank

        # To make it easier study/debug pairing doubts/issues,
        # https://gitlab.com/metapensiero/SoL/-/issues/42 proposed to add some information
        # about the current opponent of each competitor in the ranking
        _fill_in_opponents_in_ranking(tourney, tourney.currentturn, ranking)

    return results


@view_config(route_name='delete_from_turn', renderer='json')
@unauthorized_for_guest
def deleteFromTurn(request):
    "Delete already played turns, recomputing the ranking."

    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])
        fromturn = int(params['fromturn'])

        tourney = sess.get(Tourney, idtourney)

        if tourney.prized:
            tourney.resetPrizes()

        delmatches = [m for m in tourney.matches if m.turn >= fromturn]
        for match in delmatches:
            sess.delete(match)

        tourney.currentturn = fromturn - 1
        if tourney.finalturns:
            tourney.finalturns = any(
                m for m in tourney.matches if m.turn < fromturn and m.final
            )
        tourney.countdownstarted = None
        sess.flush()

        # recompute the ranking
        sess.expunge(tourney)
        tourney = sess.get(Tourney, idtourney)
        tourney.updateRanking()
        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't delete turns: %s", message, exc_info=True
        )
        success = False
        return dict(
            success=success,
            message=message,
        )

    return dict(
        success=success,
        message=message,
        currentturn=tourney.currentturn,
        rankedturn=tourney.rankedturn,
        finalturns=tourney.finalturns,
        prized=tourney.prized,
    )


def _new_turn(request, final):
    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.get(Tourney, idtourney)
        if final:
            tourney.makeFinalTurn()
        else:
            tourney.makeNextTurn()

        sess.flush()

        success = True
        message = 'Ok'
    except OperationAborted as e:  # pragma: no cover
        get_request_logger(request, logger).error("Couldn't create next turn: %s", e)
        message = request.localizer.translate(e.message)
        success = False
        return dict(
            success=success,
            message=message,
        )
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't create next turn: %s", message, exc_info=True
        )
        success = False
        return dict(
            success=success,
            message=message,
        )

    return dict(
        success=success,
        message=message,
        currentturn=tourney.currentturn,
        rankedturn=tourney.rankedturn,
        finalturns=tourney.finalturns,
        prized=tourney.prized,
        generated_turns=(
            0 if not tourney.matches else max(m.turn for m in tourney.matches)
        ),
    )


@view_config(route_name='new_turn', renderer='json')
@unauthorized_for_guest
def newTurn(request):
    "Create next turn, or all possible turns when coupling is “all against all”."

    return _new_turn(request, False)


@view_config(route_name='final_turn', renderer='json')
@unauthorized_for_guest
def finalTurn(request):
    "Create final turn."

    return _new_turn(request, True)


@view_config(route_name='send_training_urls', renderer='json')
@unauthorized_for_guest
def sendTrainingURLs(request):
    sess = request.dbsession
    params = request.params
    idtourney = int(params['idtourney'])

    tourney = sess.get(Tourney, idtourney)
    if tourney is not None and tourney.championship.trainingboards:
        tourney.sendTrainingURLs(request)
        return dict(success=True, message='Ok')
    else:  # pragma: no cover
        return dict(
            success=False, message=request.localizer.translate(_('Bad request!'))
        )


@view_config(route_name='update_ranking', renderer='json')
@unauthorized_for_guest
def updateRanking(request):
    "Recompute current ranking."

    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.get(Tourney, idtourney)
        tourney.updateRanking()

        sess.flush()

        success = True
        message = 'Ok'
    except OperationAborted as e:  # pragma: no cover
        get_request_logger(request, logger).error("Couldn't update the ranking: %s", e)
        message = request.localizer.translate(e.message)
        success = False
        tourney = None
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't update the ranking: %s", message, exc_info=True
        )
        success = False
        tourney = None
    result = dict(
        success=success,
        message=message,
    )
    if tourney is not None:
        result.update(
            currentturn=tourney.currentturn,
            rankedturn=tourney.rankedturn,
            finalturns=tourney.finalturns,
            prized=tourney.prized,
        )
    return result


@view_config(route_name='assign_prizes', renderer='json')
@unauthorized_for_guest
def assignPrizes(request):
    "Assign final prizes."

    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.get(Tourney, idtourney)
        tourney.assignPrizes()

        if tourney.rating is not None:
            tourney.rating.recompute(tourney.date)

        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't assign prizes: %s", message, exc_info=True
        )
        success = False
        tourney = None
    return (
        dict(
            success=success,
            message=message,
        )
        | dict(
            currentturn=tourney.currentturn,
            rankedturn=tourney.rankedturn,
            finalturns=tourney.finalturns,
            prized=tourney.prized,
        )
        if tourney is not None
        else {}
    )


@view_config(route_name='reset_prizes', renderer='json')
@unauthorized_for_guest
def resetPrizes(request):
    "Reset assigned final prizes."

    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.get(Tourney, idtourney)
        tourney.resetPrizes()

        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't reset prizes: %s", message, exc_info=True
        )
        success = False
        tourney = None
    return (
        dict(
            success=success,
            message=message,
        )
        | dict(
            currentturn=tourney.currentturn,
            rankedturn=tourney.rankedturn,
            finalturns=tourney.finalturns,
            prized=tourney.prized,
        )
        if tourney is not None
        else {}
    )


@view_config(route_name='replay_today', renderer='json')
@unauthorized_for_guest
def replayToday(request):
    "Replicate the given tourney today."

    from datetime import date

    t = translator(request)

    new_idtourney = None
    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.get(Tourney, idtourney)
        new = tourney.replay(date.today(), request.session['user_id'])

        sess.flush()

        new_idtourney = new.idtourney
        success = True
        message = t(
            _(
                'Created "$tourney" in championship "$championship"',
                mapping=dict(
                    tourney=new.description, championship=new.championship.description
                ),
            )
        )
    except IntegrityError:  # pragma: no cover
        message = t(
            _(
                'Could not duplicate the tourney because there is'
                ' already an event today, sorry!'
            )
        )
        get_request_logger(request, logger).error(
            "Couldn't duplicate tourney:" ' there is already an event today, sorry!'
        )
        success = False
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't duplicate tourney: %s", message, exc_info=True
        )
        success = False
    return dict(success=success, message=message, new_idtourney=new_idtourney)


@view_config(route_name='create_knockout', renderer='json')
@unauthorized_for_guest
def createKnockout(request):
    "Create a knockout tourney from a previous one."

    from datetime import date

    t = translator(request)

    new_idtourney = None
    try:
        sess = request.dbsession
        params = request.params
        idtourney = int(params['idtourney'])
        ncompetitors = int(params['ncompetitors'])
        if 'date' in params:
            when = date.fromisoformat(params['date'])
        else:  # pragma: no cover
            when = date.today()

        tourney = sess.get(Tourney, idtourney)
        new = tourney.createKnockout(when, ncompetitors, request.session['user_id'])

        sess.flush()

        new_idtourney = new.idtourney
        success = True
        message = t(
            _(
                'Created "$tourney" in championship "$championship"',
                mapping=dict(
                    tourney=new.description, championship=new.championship.description
                ),
            )
        )
    except IntegrityError:  # pragma: no cover
        message = t(
            _(
                'Could not duplicate the tourney because there is'
                ' already an event today, sorry!'
            )
        )
        get_request_logger(request, logger).error(
            "Couldn't duplicate tourney:" ' there is already an event today, sorry!'
        )
        success = False
    except Exception as e:  # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical(
            "Couldn't duplicate tourney: %s", message, exc_info=True
        )
        success = False
    return dict(success=success, message=message, new_idtourney=new_idtourney)


@view_config(route_name='countdown', request_method='POST', renderer='json')
def countdownStarted(request):
    "Register the countdown start timestamp."

    curruser = request.session.get('user_id', '*nouser*')
    isadmin = request.session.get('is_admin', False)
    params = request.params
    try:
        idtourney = int(params['idtourney'])
        if 'start' in params:
            start = int(time.time() * 1000)
        else:
            start = None
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).warning(
            'Bad Attempt to start/stop countdown: %s', str(e)
        )
        return dict(success=False, message='Bad request')

    tourney = request.dbsession.get(Tourney, idtourney)
    if tourney is None:  # pragma: no cover
        get_request_logger(request, logger).warning(
            'Attempt to start/stop countdown a non-existing tourney (%s)', idtourney
        )
        return dict(success=False, message='Invalid tourney ID')

    if not tourney.prized and (isadmin or curruser == tourney.idowner):
        tourney.countdownstarted = start
        logger.debug(
            'Countdown for %s %s',
            repr(tourney),
            'terminated' if start is None else 'started',
        )
        return dict(
            success=True,
            message='Ok, countdown %s' % ('terminated' if start is None else 'started'),
        )
    else:
        get_request_logger(request, logger).warning(
            'Attempt to start/stop countdown for %s ignored', repr(tourney)
        )
        return dict(success=False, message='Tourney is prized, or not owned by you')


@view_config(route_name='countdown', renderer='countdown.mako')
def countdown(request):
    "Show the game countdown."

    t = translator(request)

    params = request.params
    try:
        idtourney = int(params['idtourney'])
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).error("Couldn't show the countdown: %s", e)
        raise HTTPBadRequest('Bad request')

    tourney = request.dbsession.get(Tourney, idtourney)
    if tourney is None:  # pragma: no cover
        get_request_logger(request, logger).error(
            "Couldn't show the countdown:" ' unknown tourney ID (%s)' % idtourney
        )
        raise HTTPNotFound('Invalid tourney ID')

    curruser = request.session.get('user_id', '*nouser*')
    isadmin = request.session.get('is_admin', False)
    return dict(
        _=t,
        ngettext=ngettext,
        duration=tourney.duration,
        prealarm=tourney.prealarm,
        currentturn=ordinal(tourney.currentturn),
        elapsed=compute_elapsed_time(tourney.countdownstarted, tourney.duration),
        notifystart=request.path_qs,
        isowner=isadmin or curruser == tourney.idowner,
    )


@view_config(route_name='pre_countdown', renderer='pre_countdown.mako')
def preCountdown(request):
    "Show a countdown while preparing the next round."

    t = translator(request)
    params = request.params
    try:
        idtourney = int(params['idtourney'])
        duration = int(params['duration'])
        prealarm = int(params['prealarm'])
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).error("Couldn't show the countdown: %s", e)
        raise HTTPBadRequest('Bad request')

    tourney = request.dbsession.get(Tourney, idtourney)
    if tourney is None:  # pragma: no cover
        get_request_logger(request, logger).error(
            "Couldn't show the countdown:" ' unknown tourney ID (%s)' % idtourney
        )
        raise HTTPNotFound('Invalid tourney ID')

    return dict(
        _=t,
        ngettext=ngettext,
        duration=duration,
        prealarm=prealarm,
        nextturn=ordinal(tourney.currentturn + 1),
    )


@view_config(route_name='get_board_self_edit_url', renderer='json')
@unauthorized_for_guest
def getBoardSelfEditURL(request):
    "Get the URL to the self-edit form for a given board."

    try:
        params = request.params
        idtourney = int(params['idtourney'])
        board = int(params['board'])
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).warning(
            'Bad request for board edit URL: %s', e
        )
        raise HTTPBadRequest('Bad request')

    try:
        tourney = request.dbsession.get(Tourney, idtourney)
        if (
            tourney is None
            or tourney.prized
            or tourney.currentturn == tourney.rankedturn
        ):  # pragma: no cover
            get_request_logger(request, logger).warning(
                'Invalid request for board edit URL'
            )
            return dict(
                success=False,
                message=translator(request)(_('Invalid request for board edit URL')),
            )

        return dict(success=True, url=tourney.getEditBoardURL(request, board))
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).error(
            'Could not compute board edit URL: %s', e
        )
        return dict(success=False, message=translator(request)(_('Internal error!')))


@view_config(route_name='get_competitor1_self_edit_url', renderer='json')
@unauthorized_for_guest
def getCompetitor1SelfEditURL(request):
    "Get the URL of the self-edit form for the first competitor of a match."

    try:
        params = request.params
        idmatch = int(params['idmatch'])
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).warning(
            'Bad request for competitor 1 edit URL: %s', e
        )
        raise HTTPBadRequest('Bad request')

    try:
        match = request.dbsession.get(Match, idmatch)
        if (
            match is None
            or match.tourney.prized
            or match.tourney.currentturn == match.tourney.rankedturn
        ):  # pragma: no cover
            get_request_logger(request, logger).warning(
                'Invalid request for competitor 1 edit URL'
            )
            return dict(
                success=False,
                message=translator(request)(
                    _('Invalid request for competitor 1 edit URL')
                ),
            )

        return dict(success=True, url=match.getEditCompetitorURL(request, 1))
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).error(
            'Could not compute competitor 1 edit URL: %s', e
        )
        return dict(success=False, message='Unauthorized')


@view_config(route_name='get_competitor2_self_edit_url', renderer='json')
@unauthorized_for_guest
def getCompetitor2SelfEditURL(request):
    "Get the URL of the self-edit form for the second competitor of a match."

    try:
        params = request.params
        idmatch = int(params['idmatch'])
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).warning(
            'Bad request for competitor 2 edit URL: %s', e
        )
        raise HTTPBadRequest('Bad request')

    try:
        match = request.dbsession.get(Match, idmatch)
        if (
            match is None
            or match.tourney.prized
            or match.tourney.currentturn == match.tourney.rankedturn
        ):  # pragma: no cover
            get_request_logger(request, logger).warning(
                'Invalid request for competitor 2 edit URL'
            )
            return dict(
                success=False,
                message=translator(request)(
                    _('Invalid request for competitor 2 edit URL')
                ),
            )

        return dict(success=True, url=match.getEditCompetitorURL(request, 2))
    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).error(
            'Could not compute competitor 2 edit URL: %s', e
        )
        return dict(success=False, message='Unauthorized')


@view_config(
    route_name='test_create_random_finals',
    renderer='json',
)
def createRandomFinals(request):
    sess = request.dbsession
    idtourney = int(request.params['idtourney'])
    tourney = sess.get(Tourney, idtourney)
    if not tourney.prized and tourney.finals and not tourney.finalturns:
        tourney.updateRanking()
        while True:
            try:
                tourney.makeFinalTurn()
            except OperationAborted:
                break
            match = [m for m in tourney.matches if m.turn == tourney.currentturn][0]
            match.score1 = randint(1, 25)
            match.score2 = randint(1, 25)
            tourney.updateRanking()
        return dict(success=True)
    else:
        return dict(success=False)


@view_config(
    route_name='test_create_random_scores',
    renderer='json',
)
def createRandomScores(request):
    sess = request.dbsession
    idtourney = int(request.params['idtourney'])
    tourney = sess.get(Tourney, idtourney)
    if not tourney.prized:
        tourney.updateRanking()
        while True:
            try:
                tourney.makeNextTurn()
            except OperationAborted:
                break
            for match in [m for m in tourney.matches if m.turn == tourney.currentturn]:
                match.score1 = randint(1, 25)
                match.score2 = randint(1, 25)
                if tourney.system == 'knockout':
                    while match.score2 == match.score1:
                        match.score2 = randint(1, 25)
            tourney.updateRanking()
        return dict(success=True)
    else:
        return dict(success=False)
