# -*- coding: utf-8 -*-
# :Project:   SoL -- Batched I/O controller
# :Created:   lun 09 feb 2009 10:32:22 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2009, 2010, 2013-2016, 2018, 2020, 2022, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from datetime import date
from io import BytesIO

import transaction
from metapensiero.sqlalchemy.proxy.json import JSON
from nacl.secret import SecretBox
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.settings import asbool
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InvalidRequestError
from translationstring import TranslationString

from ..i18n import ngettext
from ..i18n import translatable_string as _
from ..i18n import translator
from ..models import Championship
from ..models import Player
from ..models import Rating
from ..models import Tourney
from ..models.bio import changes_logger
from ..models.bio import dump_sol
from ..models.bio import load_sol
from ..models.bio import restore
from ..models.bio import save_changes
from ..models.errors import OperationAborted
from ..models.utils import njoin
from . import get_request_logger
from . import unauthorized_for_guest

logger = logging.getLogger(__name__)


@view_config(route_name='backup')
def backup(request):
    "Backup almost everything in a ZIP file."

    from ..models.bio import backup

    get_request_logger(request, logger).info('Full backup')

    settings = request.registry.settings
    if settings.get('desktop.version') == 'test':
        secret_key = request.params.get('secret_key', None)
    else:  # pragma: no cover
        secret_key = None

    if secret_key is None:
        secret_key = settings.get('sol.backup_secret_key')

    only_played_tourneys = asbool(request.params.get('only_played_tourneys', False))
    serialization_format = request.params.get('serialization_format', 'yaml')
    response = request.response

    result = backup(
        request.dbsession,
        settings['sol.portraits_dir'],
        settings['sol.emblems_dir'],
        only_played_tourneys=only_played_tourneys,
        serialization_format=serialization_format,
    )

    if secret_key is not None:
        box = SecretBox(bytes.fromhex(secret_key))
        result = box.encrypt(result)
        content_type = 'application/octet-stream'
        filename = '%s.box' % date.today().isoformat()
    else:
        content_type = 'application/zip'
        filename = '%s.zip' % date.today().isoformat()

    response.body = result
    response.content_type = content_type
    response.content_disposition = 'attachment; filename=%s' % filename

    return response


@view_config(route_name='dump')
def dump(request):
    "Dump tourneys in a portable format."

    from re import sub

    from sqlalchemy.orm import join

    params = request.params
    settings = request.registry.settings
    debug = asbool(settings['desktop.debug'])

    t = translator(request)

    try:
        sess = request.dbsession

        compress = asbool(params.get('gzip', not debug))
        ext = 'sol.gz' if compress else 'sol'

        if 'idtourney' in params:
            idtourney = int(params['idtourney'])
            tourney = sess.get(Tourney, idtourney)
            if tourney is None:  # pragma: no cover
                raise HTTPBadRequest(
                    t(
                        _(
                            'Tourney $idtourney does not exist',
                            mapping=dict(idtourney=idtourney),
                        )
                    )
                )

            tourneys = [tourney]
            sdesc = tourneys[0].championship.description
            sdesc = sdesc.encode('ascii', 'ignore').decode('ascii')
            cturn = tourneys[0].currentturn
            filename = '%s-%s%s.%s' % (
                sub(r'\W+', '_', sdesc),
                str(tourneys[0].date),
                '+%d' % cturn if cturn else '',
                ext,
            )
        elif 'idchampionship' in params:
            idchampionship = int(params['idchampionship'])
            tourneys = (
                sess.query(Tourney)
                .filter_by(idchampionship=idchampionship)
                .order_by(Tourney.date)
            ).all()
            if not tourneys:  # pragma: no cover
                raise HTTPBadRequest(
                    t(
                        _(
                            'No tourneys in championship $idchampionship',
                            mapping=dict(idchampionship=idchampionship),
                        )
                    )
                )

            desc = tourneys[0].championship.description
            sdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', sdesc), ext)
        elif 'idclub' in params:
            idclub = int(params['idclub'])
            tourneys = (
                sess.query(Tourney)
                .select_from(join(Tourney, Championship))
                .filter(Championship.idclub == idclub)
                .order_by(Tourney.date)
            ).all()
            if not tourneys:  # pragma: no cover
                raise HTTPBadRequest(
                    t(
                        _(
                            'No tourneys organized by club $idclub',
                            mapping=dict(idclub=idclub),
                        )
                    )
                )

            desc = tourneys[0].championship.club.description
            cdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', cdesc), ext)
        else:
            tourneys = sess.query(Tourney).order_by(Tourney.date).all()
            if not tourneys:  # pragma: no cover
                raise HTTPBadRequest(t(_('No tourneys at all')))

            filename = f'{date.today().isoformat()}.{ext}'

        response = request.response
        if compress:
            response.body = dump_sol(tourneys, compress)
            response.content_type = 'application/x-gzip'
        else:
            response.text = dump_sol(tourneys, compress)
            response.content_type = 'text/x-yaml'
        response.content_disposition = 'attachment; filename=%s' % filename

        return response

    except HTTPBadRequest as e:  # pragma: no cover
        get_request_logger(request, logger).error("Couldn't dump tourney: %s", e)
        raise

    except Exception as e:  # pragma: no cover
        get_request_logger(request, logger).critical(
            "Couldn't dump tourney: %s", e, exc_info=True
        )
        raise HTTPInternalServerError(str(e))


def _recognizeIntegrityError(e, t, rlogger):  # pragma: nocover
    # Catch most common reasons, ugly as it is
    excmsg = str(e)
    if (
        'columns date, idchampionship are not unique' in excmsg
        or (
            ' UNIQUE constraint failed:'
            ' tourneys.date, tourneys.description, tourneys.idchampionship'
        )
        in excmsg
    ):
        rlogger.warning('Not allowing duplicated event: %s', excmsg)
        message = t(
            _(
                'There cannot be two tourneys of the same'
                ' championship on the same day with exacly the same description!'
            )
        )
    elif (
        ' UNIQUE constraint failed: championships.description, championships.idclub'
    ) in excmsg:
        rlogger.warning('Not allowing duplicated championship: %s', excmsg)
        message = t(
            _(
                'There cannot be two championships with the same'
                ' description organized by the same club!'
            )
        )
    elif ' UNIQUE constraint failed: clubs.description' in excmsg:
        rlogger.warning('Not allowing duplicated club: %s', excmsg)
        message = t(_('There cannot be two clubs with the same description!'))
    elif ' UNIQUE constraint failed: ratings.description' in excmsg:
        rlogger.warning('Not allowing duplicated rating: %s', excmsg)
        message = t(_('There cannot be two ratings with the same description!'))
    elif ' UNIQUE constraint failed: championships.description' in excmsg:
        rlogger.warning('Not allowing duplicated championship: %s', excmsg)
        message = t(_('There cannot be two championships with the same description!'))
    elif (
        ' UNIQUE constraint failed: players.lastname, players.firstname,'
        ' players.nickname'
        in excmsg
        or 'columns lastname, firstname, nickname are not unique' in excmsg
    ):
        rlogger.warning('Not allowing duplicated player: %s', excmsg)
        message = t(
            _(
                'There cannot be two players with the same'
                ' firstname, lastname and nickname!'
            )
        )
    elif (
        ' UNIQUE constraint failed: matches.idtourney, matches.idcompetitor1,'
        ' matches.idcompetitor2'
    ) in excmsg:
        rlogger.warning('Not allowing duplicated match: %s', excmsg)
        message = t(_('There cannot be two matches involving the same competitors!'))
    elif (
        ' UNIQUE constraint failed: rates.idrating, rates.idplayer, rates.date'
    ) in excmsg:
        rlogger.warning('Not allowing duplicated rate: %s', excmsg)
        message = t(_('There cannot be two rates of the same player in the same date!'))
    elif ' may not be NULL' in excmsg or ' NOT NULL constraint failed' in excmsg:
        rlogger.warning('Incomplete data: %s', excmsg)
        message = t(_('Missing information prevents saving changes!'))
        message += '<br/>'
        message += t(_('Some mandatory fields were not filled in, please recheck.'))
    else:  # pragma: no cover
        rlogger.error('Could not save changes: %s', excmsg)
        message = t(_('Integrity error prevents saving changes!'))
        message += '<br/>'
        message += t(
            _(
                'Most probably a field contains an invalid value:'
                ' consult the application log for details.'
            )
        )
    # Explicit rollback, to avoid a pointless traceback
    transaction.doom()
    return message


@view_config(route_name='merge_players', renderer='json')
@unauthorized_for_guest
def mergePlayers(request):
    "Merge several players into a single one."

    t = translator(request)
    rlogger = get_request_logger(request, logger)

    tid = int(request.params['tid'])
    sids = request.params.getall('sids')
    if not isinstance(sids, list):  # pragma: no cover
        sids = [sids]
    sids = [int(i) for i in sids]
    if not sids:
        return dict(success=False, message=t(_('Unspecified merge ids')))

    sas = request.dbsession
    player = sas.get(Player, tid)
    if player is None:  # pragma: no cover
        return dict(success=False, message=t(_('Invalid target player id')))

    success = False
    try:
        replaced = player.mergePlayers(
            sids, get_request_logger(request, changes_logger)
        )
    except OperationAborted as e:
        rlogger.error("Couldn't merge players: %s", e)
        message = t(e.message)
    except (IntegrityError, InvalidRequestError) as e:  # pragma: no cover
        message = _recognizeIntegrityError(e, t, rlogger)
    except Exception as e:  # pragma: no cover
        message = str(e)
        rlogger.exception("Couldn't merge players: %s", message)
    else:
        count = len(replaced)
        message = ngettext(
            '$count player has been merged into $player',
            '$count players has been merged into $player',
            count,
            mapping=dict(count=count, player=player.caption(False)),
        )
        success = True
    return dict(success=success, message=message)


@view_config(route_name='save_changes', renderer='json')
@unauthorized_for_guest
def saveChanges(request):
    """Save changes made to a set of records."""

    t = translator(request)
    rlogger = get_request_logger(request, logger)

    params = request.params
    mr = JSON.decode(params['modified_records'])
    dr = JSON.decode(params['deleted_records'])

    sess = request.dbsession

    success = False
    try:
        clogger = get_request_logger(request, changes_logger)
        iids, mids, dids = save_changes(sess, request, mr, dr, clogger)
        sess.flush()
        success = True
        message = 'Ok'
        infomsg = []
        ni = len(iids)
        if ni:
            infomsg.append('%d new records' % ni)
        nm = len(mids)
        if nm:
            infomsg.append('%d changed records' % nm)
        nd = len(dids)
        if nd:
            infomsg.append('%d deleted records' % nd)
        if infomsg:
            rlogger.info(
                'Changes successfully committed: %s', njoin(infomsg, localized=False)
            )
    except OperationAborted as e:
        rlogger.warning('Operation refused: %s', e)
        message = t(e.message)
    except (IntegrityError, InvalidRequestError) as e:
        message = _recognizeIntegrityError(e, t, rlogger)
    except DBAPIError as e:  # pragma: no cover
        rlogger.error('Could not save changes: %s', e)
        message = t(_('Error occurred while saving changes!'))
        message += '<br/>'
        message += t(_('Please inform the admin or consult the application log.'))
    except Exception as e:  # pragma: no cover
        rlogger.critical('Could not save changes: %s', e, exc_info=True)
        message = t(_('Internal error!'))
        message += '<br/>'
        message += t(_('Please inform the admin or consult the application log.'))
    if not success:
        sess.rollback()
    return dict(success=success, message=message)


@view_config(route_name='upload')
def upload(request):
    "Handle the upload of tourneys data."

    from metapensiero.sqlalchemy.proxy.json import JSON

    t = translator(request)

    params = request.params
    archive = params.get('archive')

    if 'user_name' not in request.session or request.session['is_guest']:
        get_request_logger(request, logger).warning('Not allowed to upload %s', archive)

        msg = t(_('Guest users are not allowed to perform this operation, sorry!'))

        # The answer must be "text/html", even if we really return JSON:
        # see the remark regarding `fileUpload` in the ExtJS BasicForm.js

        response = request.response
        response.content_type = 'text/html'
        response.text = JSON.encode(dict(success=False, message=msg))

        return response

    settings = request.registry.settings
    idowner = request.session['user_id']

    success = False
    load = None

    if archive is not None:
        fnendswith = archive.filename.endswith

        if fnendswith(('.sol', '.sol.gz')):
            load = load_sol
        elif fnendswith(('.box', '.zip')):
            if request.session['is_admin']:

                def load(sasess, url, content, idowner):
                    if settings.get('desktop.version') == 'test':
                        secret_key = request.params.get('secret_key', None)
                    else:  # pragma: no cover
                        secret_key = None

                    if secret_key is None:
                        secret_key = settings.get('sol.backup_secret_key')

                    if secret_key is not None:
                        box = SecretBox(bytes.fromhex(secret_key))
                        try:
                            content = box.decrypt(content.read())
                        except Exception:  # pragma: no cover
                            raise OperationAborted(_('Unallowed, wrong encryption!'))
                        else:
                            content = BytesIO(content)

                    return restore(
                        sasess,
                        settings['sol.portraits_dir'],
                        settings['sol.emblems_dir'],
                        url,
                        content,
                        idowner,
                    )
            else:
                msg = t(_('Only admin can restore whole ZIPs, sorry!'))
                get_request_logger(request, logger).warning(
                    'Attempt to restore %s rejected', archive.filename
                )
        else:
            msg = t(_('Unknown file type: $file', mapping=dict(file=archive.filename)))
            get_request_logger(request, logger).warning(
                'Attempt to upload %s rejected', archive.filename
            )
    else:
        msg = t(_('Required "archive" parameter is missing!'))

    if load is not None:
        sas = request.dbsession
        try:
            with transaction.manager:
                tourneys, skipped = load(
                    sas, url=archive.filename, content=archive.file, idowner=idowner
                )
        except OperationAborted as e:  # pragma: no cover
            msg = e.message
            if isinstance(msg, TranslationString):
                msg = t(msg)
            success = False
            get_request_logger(request, logger).error(
                'Upload of %s failed: %s', archive.filename, e
            )
        except Exception as e:  # pragma: no cover
            transaction.abort()
            success = False
            msg = t(
                _(
                    'Upload of $file failed: $error',
                    mapping=dict(file=archive.filename, error=type(e).__name__),
                )
            )
            get_request_logger(request, logger).error(
                'Upload of %s failed: %s', archive.filename, e
            )
        else:
            success = True
            msg = ngettext(
                '$num tourney successfully loaded',
                '$num tourneys successfully loaded',
                len(tourneys),
                mapping=dict(num=len(tourneys)),
            )
            if skipped:
                msg += ', ' + ngettext(
                    '$num skipped because already present',
                    '$num skipped because already present',
                    skipped,
                    mapping=dict(num=skipped),
                )
            get_request_logger(request, logger).info(
                'Successful upload of %s: %d new tourneys, %d skipped because'
                ' already present',
                archive.filename,
                len(tourneys),
                skipped,
            )

    # The answer must be "text/html", even if we really return JSON:
    # see the remark regarding `fileUpload` in the ExtJS BasicForm.js

    response = request.response
    response.content_type = 'text/html'
    response.text = JSON.encode(dict(success=success, message=msg))

    return response


@view_config(route_name='recompute_rating', renderer='json')
@unauthorized_for_guest
def recomputeRating(request):
    "Recompute a whole Rating."

    t = translator(request)

    rid = int(request.params['idrating'])

    sas = request.dbsession
    rating = sas.get(Rating, rid)
    if rating is None:  # pragma: no cover
        raise HTTPBadRequest(
            t(_('Rating $idrating does not exist', mapping=dict(idrating=rid)))
        )
    else:
        try:
            rating.recompute(scratch=True)
        except Exception as e:  # pragma: no cover
            msg = str(e)
            get_request_logger(request, logger).exception(
                "Couldn't recompute rating: %s", msg
            )
            success = False
        else:
            msg = t(
                _(
                    'Recomputed rating “$rating”',
                    mapping=dict(rating=rating.caption(False)),
                )
            )
            get_request_logger(request, logger).info('Recomputed rating %r', rating)
            success = True
    return dict(success=success, message=msg)
