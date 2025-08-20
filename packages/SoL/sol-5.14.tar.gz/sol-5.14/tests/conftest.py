# -*- coding: utf-8 -*-
# :Project:   SoL -- Pytest configuration
# :Created:   ven 06 lug 2018 12:50:04 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2025 Lele Gaifax
#

from pathlib import Path
import sys

import pytest

from metapensiero.sqlalchemy.dbloady.load import load
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sol.models import Championship, Club, Player, Rating, Tourney, User


def pytest_addoption(parser):
    parser.addoption(
        '--runslow', action='store_true', default=False, help='run slow tests'
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers', "slow: mark test as slow, enable with '--runslow'"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--runslow'):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason='need --runslow option to run')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


_clean_db = None


def setup_test_db(engine):
    global _clean_db

    if _clean_db is None:
        from sol.models import Base

        clean_engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(clean_engine)

        session = Session(clean_engine)
        load(Path(__file__).parent / 'data.dbloady', session)
        session.commit()

        _clean_db = session.connection().connection

    _clean_db.backup(engine.raw_connection().driver_connection)


@pytest.fixture(scope='module')
def engine():
    engine = create_engine('sqlite:///:memory:')
    setup_test_db(engine)
    return engine


@pytest.fixture
def session(engine):
    session = Session(engine)
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def championship_current(session):
    return (
        session.query(Championship).filter_by(description='Current championship').one()
    )


@pytest.fixture
def championship_next(session):
    return session.query(Championship).filter_by(description='Next championship').one()


@pytest.fixture
def championship_skip_worst(session):
    return session.query(Championship).filter_by(description='Skip worst prize').one()


@pytest.fixture
def club_ccm(session):
    return session.query(Club).filter_by(description='Carrom Club Milano').one()


@pytest.fixture
def club_ecc(session):
    return session.query(Club).filter_by(description='EuroCarromConf').one()


@pytest.fixture
def club_fic(session):
    return (
        session.query(Club).filter_by(description='Federazione Italiana Carrom').one()
    )


@pytest.fixture
def club_owned(session):
    return session.query(Club).filter_by(description='Owned Club').one()


@pytest.fixture
def club_scr(session):
    return session.query(Club).filter_by(description='Scarambol Club Rovereto').one()


@pytest.fixture
def player_blond(session):
    return session.query(Player).filter_by(firstname='Roberto', lastname='blond').one()


@pytest.fixture
def player_bob(session):
    return session.query(Player).filter_by(firstname='Bob', lastname='Rock').one()


@pytest.fixture
def player_danieled(session):
    return (
        session.query(Player).filter_by(firstname='Daniele', lastname='Da Fatti').one()
    )


@pytest.fixture
def player_elisam(session):
    return session.query(Player).filter_by(firstname='Elisa', lastname='M').one()


@pytest.fixture
def player_fabiot(session):
    return session.query(Player).filter_by(firstname='Fabio', lastname='T').one()


@pytest.fixture
def player_fata(session):
    return session.query(Player).filter_by(firstname='Fata', lastname='Turchina').one()


@pytest.fixture
def player_lele(session):
    return session.query(Player).filter_by(nickname='Lele').one()


@pytest.fixture
def player_lorenzoh(session):
    return session.query(Player).filter_by(firstname='Lorenzo', lastname='H').one()


@pytest.fixture
def player_lucab(session):
    return session.query(Player).filter_by(firstname='Luca', lastname='B').one()


@pytest.fixture
def player_merge1(session):
    return session.query(Player).filter_by(firstname='Merge', lastname='One').one()


@pytest.fixture
def player_merge2(session):
    return session.query(Player).filter_by(firstname='Merge', lastname='Two').one()


@pytest.fixture
def player_merge3(session):
    return session.query(Player).filter_by(firstname='Wrong', lastname='Tzè').one()


@pytest.fixture
def player_picol(session):
    return session.query(Player).filter_by(firstname='Juri', lastname='Picol').one()


@pytest.fixture
def player_pk(session):
    return session.query(Player).filter_by(firstname='Paolo', lastname='Pk').one()


@pytest.fixture
def player_varechina(session):
    return (
        session.query(Player).filter_by(firstname='Sandro', lastname='Varechina').one()
    )


@pytest.fixture
def rating_european(session):
    return session.query(Rating).filter_by(description='European rating').one()


@pytest.fixture
def rating_national(session):
    return session.query(Rating).filter_by(description='National rating').one()


@pytest.fixture
def rating_standalone(session):
    return session.query(Rating).filter_by(description='Standalone rating').one()


@pytest.fixture
def tourney_apr24(session):
    return session.query(Tourney).filter_by(description='5 torneo').one()


@pytest.fixture
def tourney_asis(session):
    return session.query(Tourney).filter_by(description='AsIs tournament').one()


@pytest.fixture
def tourney_closed(session):
    return session.query(Tourney).filter_by(description='Closed tournament').one()


@pytest.fixture
def tourney_dazed_odd(session):
    return session.query(Tourney).filter_by(description='Dazed odd tourney').one()


@pytest.fixture
def tourney_double(session):
    return session.query(Tourney).filter_by(description='Double event').one()


@pytest.fixture
def tourney_first(session):
    return session.query(Tourney).filter_by(description='First test tournament').one()


@pytest.fixture
def tourney_odd(session):
    return session.query(Tourney).filter_by(description='Odd tourney').one()


@pytest.fixture
def tourney_rated(session):
    return session.query(Tourney).filter_by(description='Rated test tournament').one()


@pytest.fixture
def tourney_rated_empty(session):
    return session.query(Tourney).filter_by(description='Rated empty tournament').one()


@pytest.fixture
def tourney_rated_empty_odd(session):
    return (
        session.query(Tourney).filter_by(
            description='Rated empty tournament odd number of players'
        )
    ).one()


@pytest.fixture
def tourney_second(session):
    return session.query(Tourney).filter_by(description='Second test tournament').one()


@pytest.fixture
def tourney_second_replica(session):
    return (
        session.query(Tourney)
        .filter_by(description='Replica of Second test tournament')
        .one()
    )


@pytest.fixture
def tourney_simple(session):
    return session.query(Tourney).filter_by(description='VerySimpleTourney').one()


@pytest.fixture
def tourney_third(session):
    return session.query(Tourney).filter_by(description='Another tourney').one()


@pytest.fixture
def tourney_trend(session):
    return (
        session.query(Tourney).filter_by(
            description='Trend retirements test tournament'
        )
    ).one()


@pytest.fixture
def tourney_rated_no_turns_odd(session):
    return (
        session.query(Tourney).filter_by(
            description='Rated empty tournament odd number of players'
        )
    ).one()


@pytest.fixture
def tourney_skipworstprize(session):
    return (
        session.query(Tourney).filter_by(description='Skip worst prize tourney')
    ).one()


@pytest.fixture
def tourney_corona(session):
    return session.query(Tourney).filter_by(description='Corona Carrom').one()


@pytest.fixture
def tourney_corona_all_against_all(session):
    return (
        session.query(Tourney)
        .filter_by(description='Corona Carrom All against All')
        .one()
    )


@pytest.fixture
def tourney_corona_all_against_all_odd(session):
    return (
        session.query(Tourney)
        .filter_by(description='Corona Carrom All against All Odd')
        .one()
    )


@pytest.fixture
def tourney_corona_odd(session):
    return session.query(Tourney).filter_by(description='Corona Carrom Odd').one()


@pytest.fixture
def tourney_knockout(session):
    return session.query(Tourney).filter_by(description='Knockout').one()


@pytest.fixture
def tourney_knockout_bot(session):
    return session.query(Tourney).filter_by(description='Knockout Best Of Three').one()


@pytest.fixture
def tourney_pre_knockout(session):
    return session.query(Tourney).filter_by(description='PreKnockout').one()


@pytest.fixture
def tourney_knockout_odd(session):
    return session.query(Tourney).filter_by(description='Odd Knockout').one()


@pytest.fixture
def tourney_roundrobin(session):
    return session.query(Tourney).filter_by(description='Roundrobin').one()


@pytest.fixture
def tourney_hosted(session):
    return session.query(Tourney).filter_by(description='Hosted tourney').one()


@pytest.fixture
def user_lele(session):
    return session.query(User).filter_by(email='lele@metapensiero.it').one()


@pytest.fixture
def user_suspended(session):
    return session.query(User).filter_by(email='suspended@example.com').one()
