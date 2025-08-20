# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests backups views
# :Created:   dom 08 lug 2018 08:31:59 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2021 Lele Gaifax
#

from io import BytesIO
from pathlib import Path
import zipfile

from metapensiero.sqlalchemy.proxy.json import JSON
from ruamel.yaml import YAML
import transaction

from sol.models import Tourney


def extract_everything_sol(archive):
    zipf = zipfile.ZipFile(BytesIO(archive), 'r')
    return zipf.read('everything.sol')


def extract_tourneys_yaml(archive):
    content = extract_everything_sol(archive)
    yaml = YAML(typ='safe')
    return list(yaml.load_all(content))[1:]


def extract_tourneys_json(archive):
    content = extract_everything_sol(archive)
    return list(JSON.decode(content))[1:]


def test_backup(guest_user, session):
    response = guest_user.get_route('backup')
    assert response.content_type == 'application/zip'
    tourneys = extract_tourneys_yaml(response.body)
    assert len(tourneys) == session.query(Tourney).count()


def test_backup_json(guest_user, session):
    response = guest_user.get_route('backup', _query={'serialization_format': 'json'})
    assert response.content_type == 'application/zip'
    tourneys = extract_tourneys_json(response.body)
    assert len(tourneys) == session.query(Tourney).count()


def test_backup_boxed(guest_user, session):
    response = guest_user.get_route('backup', _query={'secret_key': 'a' * 64})
    assert response.content_type == 'application/octet-stream'


def test_backup_played_tourneys(guest_user, session, tourney_first):
    response = guest_user.get_route('backup', _query={'only_played_tourneys': 1})
    assert response.content_type == 'application/zip'
    tourneys = extract_tourneys_yaml(response.body)
    assert len(tourneys) == 0

    with transaction.manager:
        tourney_first.updateRanking()
        session.flush()

    response = guest_user.get_route('backup', _query={'only_played_tourneys': 1})
    assert response.content_type == 'application/zip'
    tourneys = extract_tourneys_yaml(response.body)
    assert len(tourneys) == 1


def test_backup_on_logout(admin_user):
    settings = admin_user.app.registry.settings
    bdir = Path(settings['sol.backups_dir'])
    for zip in bdir.glob('*.zip'):
        zip.unlink()
    response = admin_user.get_route('logout')
    assert response.json['message'] == 'Goodbye'
    assert list(bdir.glob('*.zip'))
