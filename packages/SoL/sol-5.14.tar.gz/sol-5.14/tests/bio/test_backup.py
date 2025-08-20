# -*- coding: utf-8 -*-
# :Project:   SoL -- Backup/restore tests
# :Created:   sab 07 lug 2018 12:24:19 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2021, 2024 Lele Gaifax
#

from io import BytesIO
from pathlib import Path
from time import sleep

import pytest
import transaction

from sol.models import Club, Player, Tourney, User, wipe_database
from sol.models.bio import backup, restore


def test_plain_backup(session, club_scr, player_lele, tmpdir):
    backup(session, tmpdir, tmpdir, tmpdir)


@pytest.mark.parametrize('native', (True, False))
def test_native_backup(session, club_scr, player_lele, tmpdir, native):
    with transaction.manager:
        portrait = Path(tmpdir) / 'lele.jpg'
        portrait.write_bytes(b'foo')
        player_lele.portrait = 'lele.jpg'
        emblem = Path(tmpdir) / 'scr.png'
        emblem.write_bytes(b'bar')
        club_scr.emblem = 'scr.png'
        session.flush()

    backup(
        session,
        tmpdir,
        tmpdir,
        tmpdir,
        serialization_format='json',
        native_when_possible=native,
    )


def test_keep_max_backups(session, club_scr, player_lele, tmpdir):
    backup(session, tmpdir, tmpdir, tmpdir, keep_only_if_changed=False)
    sleep(1.5)
    backup(session, tmpdir, tmpdir, tmpdir, keep_only_if_changed=False)
    nbackups = list(Path(tmpdir).glob('sol-backup_*.zip'))
    assert len(nbackups) >= 2
    sleep(1.5)
    backup(session, tmpdir, tmpdir, tmpdir, keep_only_if_changed=False, keep_max=1)
    nbackups = list(Path(tmpdir).glob('sol-backup_*.zip'))
    assert len(nbackups) == 1


def full_backup_restore(session, tmpdir, serialization_format='yaml'):
    tourneysc = len(session.query(Tourney).all())

    try:
        Player._FORCE_DISCERNABILITY = True
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = True
        archive = backup(session, tmpdir, tmpdir)
    finally:
        Player._FORCE_DISCERNABILITY = False
        Player._FORCE_PRIVACY_AGREEMENT_FOR_SERIALIZATION_TESTS = False

    session.expunge_all()
    wipe_database(session)

    tourneys, skipped = restore(session, content=BytesIO(archive))
    session.commit()

    assert len(tourneys) == tourneysc
    assert skipped == 0

    # Reloading the same archive: not played tourneys are skipped
    tourneys, skipped = restore(session, content=BytesIO(archive))
    session.commit()

    assert len(tourneys) + skipped == tourneysc
    assert skipped == 11

    # Our test data isn't completely consistent, as we have player ratings
    # that does not have a corresponding tourney: when we reload everything,
    # the ratings gets recomputed from scratch, so we cannot compare the
    # number of current player ratings with the previous one.
    # TODO: this annoyed me enough, should find a better and more effective
    # way to assert that the rating got recomputed...
    # rates = s.query(models.Rate).all()
    # self.assertEqual(len(rates), 13)

    # Test club owner, deserialization is bit tricky
    owned = session.query(Club).filter_by(description='Owned Club').one()
    lele = session.query(User).filter_by(email='lele@metapensiero.it').one()
    assert owned.owner is lele

    scr = session.query(Club).filter_by(description='Scarambol Club Rovereto').one()
    assert scr.rating.description == 'Standalone rating'
    assert scr.rating.club is scr


@pytest.mark.parametrize('serialization_format', ('json', 'yaml'))
def test_full_backup_restore(session, tmpdir, serialization_format):
    full_backup_restore(session, tmpdir, serialization_format)
