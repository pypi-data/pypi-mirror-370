# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   lun 13 ott 2008 16:24:21 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018-2020, 2022-2025 Lele Gaifax
#

"""
================
 Scarry On Line
================

Easy management of Carrom Tournaments
=====================================

This application implements the following features:

* basic tables editing, like adding a new player, opening a new
  championship, manually tweaking the scores, and so on

* handle a single tourney

  a. compose a list of `competitors`: usually this is just a single
     player, but there are two people in doubles, or more (teams)

  b. set up the first turn, made up of `matches`, each pairing two
     distinct `competitors`: this is usually done randomly, but the
     secretary must be able to manually change the combinations

  c. print the game sheets, where the player will write the scores

  d. possibly show a countdown, to alert the end of the game

  e. insert the score of each table

  f. compute the ranking

  g. print the current ranking

  h. possibly offer a way to retire some competitors, or to add a new
     competitor

  i. compute the next turn

  j. repeat steps c. thru i. usually up to seven turns

  k. possibly offer a way to go back, delete last turn, correct a
     score and repeat

  l. recompute the ranking, assigning prizes

* handle a championship of tourneys

  * each tourney is associated to one championship

  * print the championship ranking

* data exchange, to import/export whole tourneys in a portable way

* browseable history thru a light HTML readonly interface
"""

from __future__ import annotations

# This is injected automatically at release time
__exact_version__ = 'v5.14'

import logging
from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import join

import zope.sqlalchemy
from metapensiero.extjs.desktop.pyramid import configure
from pyramid.config import Configurator
from pyramid.csrf import SessionCSRFStoragePolicy
from pyramid.response import FileResponse
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from webob.cookies import JSONSerializer

from .i18n import locale_negotiator

logger = logging.getLogger(__name__)


def favicon_view(request):
    "Serve /favicon.ico as an alias to /static/favicon.png"

    here = dirname(__file__)
    icon = join(here, 'static', 'favicon.png')
    return FileResponse(icon, request=request)


def robots_view(request):
    "Serve /robots.txt as an alias to /static/robots.txt"

    here = dirname(__file__)
    icon = join(here, 'static', 'robots.txt')
    return FileResponse(icon, request=request)


class OnlyForTestingPredicate:
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'only_for_testing = %r' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return request.registry.settings.get('testing', False) == self.val


def main(global_config, **settings):
    "This function returns a Pyramid WSGI application."

    if 'desktop.version' not in settings:  # pragma: no cover
        settings['desktop.version'] = __exact_version__

    if not exists(settings['sol.portraits_dir']):  # pragma: no cover
        makedirs(settings['sol.portraits_dir'], mode=0o700)

    if not exists(settings['sol.emblems_dir']):  # pragma: no cover
        makedirs(settings['sol.emblems_dir'], mode=0o700)

    bckdir = settings.get('sol.backups_dir', None)
    if bckdir and bckdir != 'None' and not exists(bckdir):  # pragma: nocover
        makedirs(bckdir, mode=0o700)

    timeout = settings.get('session.timeout', 24 * 60 * 60)
    if timeout == 'None':  # pragma: no cover
        timeout = None
    else:
        timeout = int(timeout)

    reissue_time = settings.get('session.reissue_time', 24 * 60 * 60)
    if reissue_time == 'None':  # pragma: no cover
        reissue_time = None
    else:
        reissue_time = int(reissue_time)

    session_factory = SignedCookieSessionFactory(
        settings['session.secret'],
        timeout=timeout,
        reissue_time=reissue_time,
        serializer=JSONSerializer(),
    )
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        locale_negotiator=locale_negotiator,
    )

    config.set_csrf_storage_policy(SessionCSRFStoragePolicy())

    config.include('pyramid_mako')

    configure(config)
    config.commit()

    config.add_route_predicate('only_for_testing', OnlyForTestingPredicate)

    config.add_translation_dirs('sol:locale/')

    config.add_static_view('static', 'static', cache_max_age=12 * 60 * 60)

    config.add_route('favicon', '/favicon.ico')
    config.add_view(favicon_view, route_name='favicon')

    config.add_route('robots', '/robots.txt')
    config.add_view(robots_view, route_name='robots')

    # auth

    config.add_route('login', '/auth/login')
    config.add_route('logout', '/auth/logout')
    config.add_route('change_language', '/auth/changeLanguage')
    config.add_route('change_password', '/auth/changePassword')
    config.add_route('lost_password', '/auth/lostPassword')
    config.add_route('reset_password', '/auth/resetPassword')
    config.add_route('signin', '/auth/signin')

    # bio

    config.add_route('backup', '/bio/backup')
    config.add_route('dump', '/bio/dump')
    config.add_route('merge_players', '/bio/mergePlayers')
    config.add_route('recompute_rating', '/bio/recomputeRating')
    config.add_route('save_changes', '/bio/saveChanges')
    config.add_route('upload', '/bio/upload')

    # data

    config.add_route('championships', '/data/championships')
    config.add_route('championships_lookup', '/data/championshipsLookup')
    config.add_route('clubs', '/data/clubs')
    config.add_route('clubs_lookup', '/data/clubsLookup')
    config.add_route('club_users', '/data/clubUsers')
    config.add_route('countries', '/data/countries')
    config.add_route('federations', '/data/federations')
    config.add_route('languages', '/data/languages')
    config.add_route('owners', '/data/owners')
    config.add_route('players', '/data/players')
    config.add_route('rated_players', 'data/ratedPlayers')
    config.add_route('ratings', '/data/ratings')
    config.add_route('ratings_lookup', '/data/ratingsLookup')
    config.add_route('tourneys', '/data/tourneys')
    config.add_route('users', '/data/users')

    # tourney

    config.add_route('assign_prizes', '/tourney/assignPrizes')
    config.add_route('competitors', '/tourney/competitors')
    config.add_route('countdown', '/tourney/countdown')
    config.add_route('current_matches', '/tourney/current_matches')
    config.add_route('delete_from_turn', '/tourney/deleteFromTurn')
    config.add_route('final_turn', '/tourney/finalTurn')
    config.add_route('matches', '/tourney/matches')
    config.add_route('new_turn', '/tourney/newTurn')
    config.add_route('pre_countdown', '/tourney/pre_countdown')
    config.add_route('ranking', '/tourney/ranking')
    config.add_route('replay_today', '/tourney/replayToday')
    config.add_route('create_knockout', '/tourney/createKnockout')
    config.add_route('reset_prizes', '/tourney/resetPrizes')
    config.add_route('send_training_urls', '/tourney/sendTrainingURLs')
    config.add_route('tourney_players', '/tourney/players')
    config.add_route('update_ranking', '/tourney/updateRanking')
    config.add_route('get_board_self_edit_url', '/tourney/getBoardSelfEditURL')
    config.add_route(
        'get_competitor1_self_edit_url', '/tourney/getCompetitor1SelfEditURL'
    )
    config.add_route(
        'get_competitor2_self_edit_url', '/tourney/getCompetitor2SelfEditURL'
    )

    config.add_route(
        'test_create_random_finals',
        '/tourney/createRandomFinals',
        only_for_testing=True,
    )
    config.add_route(
        'test_create_random_scores',
        '/tourney/createRandomScores',
        only_for_testing=True,
    )

    # lit

    config.add_route('lit', '/lit')
    config.add_route('lit_championship', '/lit/championship/{guid}')
    config.add_route('lit_club', '/lit/club/{guid}')
    config.add_route('lit_club_players', '/lit/club/{guid}/players')
    config.add_route('lit_country', '/lit/country/{country}')
    config.add_route('lit_latest', '/lit/latest')
    config.add_route('lit_player', '/lit/player/{guid}')
    config.add_route('lit_player_opponent', '/lit/player/{guid}/{opponent}')
    config.add_route('lit_player_matches', '/lit/matches/{guid}')
    config.add_route('lit_players', '/lit/players')
    config.add_route('lit_players_list', '/lit/players/{country}')
    config.add_route('lit_rating', '/lit/rating/{guid}')
    config.add_route('lit_tourney', '/lit/tourney/{guid}')

    config.add_static_view('/lit/emblem', settings['sol.emblems_dir'])
    config.add_static_view('/lit/portrait', settings['sol.portraits_dir'])

    # auto compiled scorecards

    config.add_route('match_form', '/lit/match/{board}')
    config.add_route('training_match_form', '/lit/training_match/{match}')

    # printouts

    config.add_route('pdf_badges', '/pdf/badges/{id}')
    config.add_route('pdf_boardlabels', '/pdf/boardlabels/{id}')
    config.add_route('pdf_championshipranking', '/pdf/championshipranking/{id}')
    config.add_route('pdf_matches', '/pdf/matches/{id}')
    config.add_route('pdf_nationalranking', '/pdf/nationalranking/{id}')
    config.add_route('pdf_participants', '/pdf/participants/{id}')
    config.add_route('pdf_playbill', '/pdf/playbill/{id}')
    config.add_route('pdf_ratingranking', '/pdf/ratingranking/{id}')
    config.add_route('pdf_results', '/pdf/results/{id}')
    config.add_route('pdf_scorecards', '/pdf/scorecards/{id}')
    config.add_route('pdf_tourneyranking', '/pdf/ranking/{id}')
    config.add_route('pdf_tourneyunderranking', '/pdf/underranking/{id}')
    config.add_route('pdf_tourneyoverranking', '/pdf/overranking/{id}')
    config.add_route('pdf_tourneywomenranking', '/pdf/womenranking/{id}')

    # spreadsheets

    config.add_route('xlsx_tourney', '/xlsx/tourney/{id}')

    config.scan(ignore='sol.tests')

    if settings.get('testing'):
        engine = global_config['engine']
    else:  # pragma: nocover
        engine = engine_from_config(settings, 'sqlalchemy.')

    def get_tm_session(transaction_manager, session_factory=sessionmaker(bind=engine)):
        session = session_factory()
        zope.sqlalchemy.register(session, transaction_manager=transaction_manager)
        return session

    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(r.tm),
        'dbsession',
        reify=True,
    )

    return config.make_wsgi_app()
