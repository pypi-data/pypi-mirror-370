# -*- coding: utf-8 -*-
# :Project:   SoL -- Merged player tests
# :Created:   sab 07 lug 2018 12:53:30 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022, 2024 Lele Gaifax
#

from io import BytesIO
from os import fspath
from pathlib import Path

import pytest
import transaction
from sqlalchemy.exc import NoResultFound

from sol.models import Player, wipe_database
from sol.models.bio import backup, load_sol, restore


@pytest.mark.slow
def test_merge_lucia(session, tmpdir):
    testdir = Path(__file__).parent.parent
    fullname = testdir / 'scr' / 'Lazio_2011_2012-2012-01-29+6.sol'
    load_sol(session, fspath(fullname))

    fullname = testdir / 'scr' / 'Single_Event-2013-06-22+11.sol'
    load_sol(session, fspath(fullname))

    elene = session.query(Player).filter_by(firstname='Lucia Elene').one()
    elena = session.query(Player).filter_by(firstname='Lucia Elena').one()
    assert len(elena.merged) == 0

    elena_id = elena.idplayer
    elena_guid = elena.guid
    elene_guid = elene.guid

    with transaction.manager:
        elena.mergePlayers([elene_guid])
        session.flush()
        session.expunge_all()

    elena = session.get(Player, elena_id)
    assert elene_guid in {m.guid for m in elena.merged}

    with pytest.raises(NoResultFound):
        session.query(Player).filter_by(firstname='Lucia Elene').one()

    fullname = testdir / 'scr' / 'Double_Event-2013-06-19+7.sol'
    with transaction.manager:
        load_sol(session, fspath(fullname))
        session.flush()
        session.expunge_all()

    with pytest.raises(NoResultFound):
        session.query(Player).filter_by(firstname='Lucia Elene').one()

    try:
        Player._FORCE_DISCERNABILITY = True
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = True
        archive = backup(session, tmpdir, tmpdir)
    finally:
        Player._FORCE_DISCERNABILITY = False
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = False
    session.expunge_all()
    wipe_database(session)

    restore(session, content=BytesIO(archive))
    elena = session.query(Player).filter_by(guid=elena_guid).one()
    assert elene_guid in {m.guid for m in elena.merged}


@pytest.mark.slow
def test_merge_lucia_and_load_another(session, tmpdir):
    testdir = Path(__file__).parent.parent
    fullname = testdir / 'scr' / 'Lazio_2011_2012-2012-01-29+6.sol'
    load_sol(session, fspath(fullname))

    fullname = testdir / 'scr' / 'Single_Event-2013-06-22+11.sol'
    load_sol(session, fspath(fullname))

    elene = session.query(Player).filter_by(firstname='Lucia Elene').one()
    elena = session.query(Player).filter_by(firstname='Lucia Elena').one()
    assert len(elena.merged) == 0

    elena_id = elena.idplayer
    elena_guid = elena.guid
    elene_guid = elene.guid

    with transaction.manager:
        elena.mergePlayers([elene_guid])
        session.flush()
        session.expunge_all()

    elena = session.get(Player, elena_id)
    assert elene_guid in {m.guid for m in elena.merged}

    with pytest.raises(NoResultFound):
        session.query(Player).filter_by(firstname='Lucia Elene').one()

    fullname = testdir / 'scr' / 'Lazio_2011_2012-2012-03-18+6.sol'
    with transaction.manager:
        load_sol(session, fspath(fullname))
        session.flush()
        session.expunge_all()

    with pytest.raises(NoResultFound):
        session.query(Player).filter_by(guid=elene_guid).one()

    elena = session.query(Player).filter_by(guid=elena_guid).one()
    assert elene_guid in {m.guid for m in elena.merged}
