# -*- coding: utf-8 -*-
# :Project:   SoL -- Admin tool tests
# :Created:   sab 07 lug 2018 14:29:25 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2020, 2022 Lele Gaifax
#

from contextlib import redirect_stdout
from io import StringIO
from os import fspath
from pathlib import Path
from re import search
from subprocess import run, PIPE

import pytest

from sol.scripts.admin import main


def execute_main(*args, exit_status=0):
    out = StringIO()
    try:
        with redirect_stdout(out):
            main(args)
    except SystemExit as e:
        assert e.code == exit_status
    return out.getvalue()


def spawn_admin(*args, exit_status=0):
    # This is needed because the admin script initializes the DBSession...
    res = run(['soladmin', *args], stdout=PIPE)
    assert res.returncode == exit_status
    return res.stdout


def test_config_create(tmpdir):
    rootdir = Path(__file__).parent.parent
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    execute_main(
        'create-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN',
        '-p',
        'NIMDA12345',
        '-d',
        fspath(tmpdir),
        fspath(solini),
    )

    content = solini.read_text()
    assert f'sqlite:///{tmpdir}/SoL.sqlite' in content
    assert 'sol.admin.user = ADMIN' in content
    assert 'sol.admin.password = NIMDA12345' in content

    assert 'already exists' in execute_main(
        'create-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'DMINA',
        '-p',
        '12345NIMDA',
        '-d',
        fspath(tmpdir),
        fspath(solini),
    )

    content = solini.read_text()
    assert f'sqlite:///{tmpdir}/SoL.sqlite' in content
    assert 'sol.admin.user = DMINA' in content
    assert 'sol.admin.password = 12345NIMDA' in content


def test_config_create_bad_password(tmpdir):
    rootdir = Path(__file__).parent.parent
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    assert 'Invalid admin name' in execute_main(
        'create-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'AD MIN',
        '-p',
        '12345',
        '-d',
        fspath(tmpdir),
        fspath(solini),
        exit_status=128,
    )

    assert 'Invalid password' in execute_main(
        'create-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN',
        '-p',
        '12345',
        '-d',
        fspath(tmpdir),
        fspath(solini),
        exit_status=128,
    )


def test_config_update(tmpdir):
    rootdir = Path(__file__).parent.parent
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    test_config_create(tmpdir)

    execute_main(
        'update-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN0',
        '-p',
        'NIMDA23415',
        fspath(solini),
    )

    content = solini.read_text()
    assert 'sol.admin.user = ADMIN0' in content
    assert 'sol.admin.password = NIMDA23415' in content

    assert 'already up-to-date' in execute_main(
        'update-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN0',
        '-p',
        'NIMDA23415',
        fspath(solini),
    )

    assert 'Invalid password' in execute_main(
        'update-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN0',
        '-p',
        '23415',
        fspath(solini),
        exit_status=128,
    )

    assert 'Invalid admin name' in execute_main(
        'update-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'AD MIN',
        '-p',
        '23415',
        fspath(solini),
        exit_status=128,
    )

    execute_main(
        'update-config',
        '--alembic-dir',
        fspath(rootdir / 'alembic'),
        '-a',
        'ADMIN0',
        '-p',
        'NIMDA23415',
        fspath(solini) + '-nonexisting',
        exit_status=128,
    )


def test_backup(tmpdir):
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    test_config_create(tmpdir)
    spawn_admin('initialize-db', fspath(solini))
    spawn_admin('backup', fspath(solini), fspath(tempdir))
    assert b'not exist' in spawn_admin(
        'backup', fspath(solini) + '-nonexisting', fspath(tempdir), exit_status=128
    )


@pytest.mark.slow
def test_all_db_actions(tmpdir):
    testdir = Path(__file__).parent
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    test_config_create(tmpdir)
    spawn_admin('initialize-db', fspath(solini))
    spawn_admin('upgrade-db', fspath(solini))
    (tempdir / 'emblems').mkdir()
    (tempdir / 'portraits').mkdir()

    clear_backup = testdir / 'scr' / 'backup.zip'
    spawn_admin('restore', fspath(solini), fspath(clear_backup))

    boxed_backup = testdir / 'scr' / 'backup.box'
    spawn_admin(
        'restore', '--secret-key', 'a' * 64, fspath(solini), fspath(boxed_backup)
    )
    spawn_admin(
        'restore',
        '--secret-key',
        'b' * 64,
        fspath(solini),
        fspath(boxed_backup),
        exit_status=128,
    )


@pytest.mark.slow
def test_restore_sol3(tmpdir):
    testdir = Path(__file__).parent
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    test_config_create(tmpdir)
    spawn_admin('initialize-db', fspath(solini))
    (tempdir / 'emblems').mkdir()
    (tempdir / 'portraits').mkdir()
    spawn_admin('restore', fspath(solini), fspath(testdir / 'scr' / '2018-07-10.zip'))


HISTORICAL_RATING = """\
id,cognome,nome,nomignolo,valutazione,partite_giocate,club,sesso
1,Gaifas,EMANUELE,,1000,30,,Scarambol Club Rovereto,M
2,Rossi,Paolo,,1468,6,Scarambol Club Rovereto,M
3,Verdi,Giuseppe,,1427,34,Italian Carrom Federation,M
4,Bianchi,Stefania,,1495,7,,F
"""


@pytest.mark.slow
def test_load_historical_rating(tmpdir):
    tempdir = Path(tmpdir)
    solini = tempdir / 'sol-config.ini'

    test_config_create(tmpdir)
    spawn_admin('initialize-db', fspath(solini))

    csv = tempdir / 'historical.csv'
    csv.write_text(HISTORICAL_RATING)

    assert b'not exist' in spawn_admin(
        'load-historical-rating',
        '--dry-run',
        fspath(solini) + '-nonexisting',
        fspath(csv),
        exit_status=128,
    )

    assert b'deviation is invalid' in spawn_admin(
        'load-historical-rating',
        '--deviation',
        'foobar',
        '--dry-run',
        fspath(solini),
        fspath(csv),
        exit_status=128,
    )

    assert b'volatility is invalid' in spawn_admin(
        'load-historical-rating',
        '--volatility',
        'foobar',
        '--dry-run',
        fspath(solini),
        fspath(csv),
        exit_status=128,
    )

    assert b'rate is invalid' in spawn_admin(
        'load-historical-rating',
        '--rate',
        'foobar',
        '--dry-run',
        fspath(solini),
        fspath(csv),
        exit_status=128,
    )

    assert b'"bar" not found' in spawn_admin(
        'load-historical-rating',
        '--map',
        'lastname=cognome',
        '--map',
        'firstname=nome',
        '--map',
        'nickname=nomignolo',
        '--map',
        'rate=valutazione',
        '--map',
        'foo=bar',
        '--map',
        'partite_giocate',
        '--map',
        'club',
        '--map',
        'sex=sesso',
        '--description',
        'Historical rating',
        '--dry-run',
        fspath(solini),
        fspath(csv),
        exit_status=128,
    )

    output = spawn_admin(
        'load-historical-rating',
        '--map',
        'lastname=cognome',
        '--map',
        'firstname=nome',
        '--map',
        'nickname=nomignolo',
        '--map',
        'rate=valutazione',
        '--map',
        'partite_giocate',
        '--map',
        'club',
        '--map',
        'sex=sesso',
        '--deviation',
        '350.0 / (10.0 - 9.0*exp(-partite_giocate / 60.0))',
        '--description',
        'Historical rating',
        '--dry-run',
        fspath(solini),
        fspath(csv),
    ).decode('utf-8')

    assert search(r'NEW G[^ ]+ E[^ ]+ \(None\): rate=1000', output)
    assert search(r'NEW R[^ ]+ P[^ ]+ \(Scarambol Club Rovereto\): rate=1468', output)
    assert search(r'NEW V[^ ]+ G[^ ]+ \(Italian Carrom Federation\): rate=1427', output)
    assert search(r'NEW B[^ ]+ S[^ ]+ \(None\): rate=1495', output)

    spawn_admin(
        'load-historical-rating',
        '--map',
        'lastname=cognome',
        '--map',
        'firstname=nome',
        '--map',
        'nickname=nomignolo',
        '--map',
        'rate=valutazione',
        '--map',
        'partite_giocate',
        '--map',
        'club',
        '--map',
        'sex=sesso',
        '--deviation',
        '350.0 / (10.0 - 9.0*exp(-partite_giocate / 60.0))',
        '--description',
        'Historical rating',
        fspath(solini),
        fspath(csv),
    ).decode('utf-8')
