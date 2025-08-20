# -*- coding: utf-8 -*-
# :Project:   SoL -- Bio serialization tests
# :Created:   sab 07 lug 2018 08:56:43 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from io import BytesIO, StringIO
from os import fspath
from pathlib import Path

from sol.models import Player, Tourney, wipe_database
from sol.models.bio import dump_sol, load_sol


def full_dump_reload(
    session,
    tourney_rated,
    player_fata,
    player_lele,
    serialization_format='yaml',
    gzip=False,
):
    tdescription = tourney_rated.description
    rdescription = tourney_rated.rating.description
    flastname = player_fata.lastname
    fnationality = player_fata.nationality
    flanguage = player_fata.language
    fcitizenship = player_fata.citizenship
    femail = player_fata.email
    lnickname = player_lele.nickname
    lnationality = player_lele.nationality
    llanguage = player_lele.language
    lcitizenship = player_lele.citizenship
    lemail = player_lele.email
    lbirthdate = player_lele.birthdate

    tourneys = session.query(Tourney).all()
    ntourneys = len(tourneys)

    try:
        Player._FORCE_DISCERNABILITY = True
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = True
        dump = dump_sol(tourneys, gzip, serialization_format)
    finally:
        Player._FORCE_DISCERNABILITY = False
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = False

    session.expunge_all()
    wipe_database(session)

    load_sol(
        session,
        'dump.sol' + ('.gz' if gzip else ''),
        (BytesIO if gzip else StringIO)(dump),
    )
    tourneys = session.query(Tourney).all()
    newntourneys = len(tourneys)

    assert ntourneys == newntourneys

    t = session.query(Tourney).filter_by(description=tdescription).one()

    assert t.rating.description == rdescription

    p = session.query(Player).filter_by(lastname=flastname).one()

    assert p.nationality == fnationality
    assert p.language == flanguage
    assert p.citizenship == fcitizenship
    assert p.email == femail

    p = session.query(Player).filter_by(nickname=lnickname).one()

    assert p.nationality == lnationality
    assert p.language == llanguage
    assert p.citizenship == lcitizenship
    assert p.email == lemail
    assert p.birthdate == lbirthdate

    if not gzip:
        dump2 = dump_sol(tourneys, gzip, serialization_format)
        assert dump == dump2


def test_full_dump_reload(session, tourney_rated, player_fata, player_lele):
    full_dump_reload(session, tourney_rated, player_fata, player_lele)
