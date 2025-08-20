# -*- coding: utf-8 -*-
# :Project:   SoL -- Views configuration
# :Created:   lun 15 apr 2013 11:42:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013, 2014, 2018, 2020, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from functools import wraps
from time import time

from metapensiero.sqlalchemy.proxy.json import register_json_decoder_encoder
from metapensiero.sqlalchemy.proxy.pyramid import expose as expose
from rapidjson import DM_ISO8601
from rapidjson import DM_NAIVE_IS_UTC
from rapidjson import Decoder
from rapidjson import Encoder
from rapidjson import NM_DECIMAL
from rapidjson import NM_NATIVE

from ..i18n import translatable_string as _
from ..i18n import translator
from ..models.bio import save_changes

logger = logging.getLogger(__name__)


class LoggerAdapter(logging.LoggerAdapter):
    "Add username and remote IP to the logged message"

    def process(self, msg: str, kwargs):
        extra: dict[str, str] = self.extra
        msg = '[%s@%s] ' % (extra['user'], extra['ip']) + msg
        return msg, kwargs


def get_request_logger(request, logger):
    "Get a specialized `logger` for a Pyramid `request`"

    extra = dict(
        ip=request.client_addr, user=request.session.get('user_name') or 'anonymous'
    )
    return LoggerAdapter(logger, extra)


def unauthorized_for_guest(f):
    """Prevent `guest` users to perform the operation."""

    @wraps(f)
    def wrapper(request):
        t = translator(request)

        log = get_request_logger(request, logger)

        if 'user_name' in request.session:
            if not request.session['is_guest']:
                return f(request)

            message = t(
                _('Guest users are not allowed to perform this operation, sorry!')
            )
        else:
            message = t(_('You must logon to perform this operation!'))

        log.warning('Not allowed to perform %s', f.__name__)

        return dict(success=False, message=message)

    return wrapper


def compute_elapsed_time(since: int | None, max_minutes: int) -> int | None:
    "Compute elapsed milliseconds since `since` timestamp, up to `max_minutes`."

    if since is None:
        elapsed = None
    else:
        elapsed = int(time() * 1000) - since
        if elapsed > max_minutes * 60 * 1000:  # pragma: no cover
            elapsed = None
    return elapsed


json_decode = Decoder(datetime_mode=DM_ISO8601, number_mode=NM_NATIVE).__call__
'Custom JSON decoder.'


json_encode = Encoder(
    datetime_mode=DM_ISO8601 | DM_NAIVE_IS_UTC,
    number_mode=NM_NATIVE | NM_DECIMAL,
    ensure_ascii=False,
).__call__
'Custom JSON encoder.'


register_json_decoder_encoder(json_decode, json_encode)
expose.create_session = staticmethod(lambda request: request.dbsession)
expose.save_changes = staticmethod(save_changes)
