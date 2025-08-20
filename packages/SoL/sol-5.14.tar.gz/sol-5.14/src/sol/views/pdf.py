# -*- coding: utf-8 -*-
# :Project:   SoL -- Printouts views
# :Created:   ven 31 ott 2008 16:48:27 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013, 2014, 2016, 2018, 2020, 2022-2025 Lele Gaifax
#

from __future__ import annotations

import logging
from os import unlink
from tempfile import mktemp

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_config

from ..models.errors import InvalidUserArgument
from ..models.errors import OperationAborted
from ..printouts import BadgesPrintout
from ..printouts import BoardLabelsPrintout
from ..printouts import ChampionshipRankingPrintout
from ..printouts import MatchesPrintout
from ..printouts import NationalRankingPrintout
from ..printouts import ParticipantsPrintout
from ..printouts import PlaybillPrintout
from ..printouts import RatingRankingPrintout
from ..printouts import ResultsPrintout
from ..printouts import ScoreCardsPrintout
from ..printouts import TourneyOverRankingPrintout
from ..printouts import TourneyRankingPrintout
from ..printouts import TourneyUnderRankingPrintout
from ..printouts import TourneyWomenRankingPrintout

logger = logging.getLogger(__name__)


def _createPdf(request, maker):
    try:
        session = request.dbsession
        output = mktemp(prefix='sol')
        args = maker.getArgumentsFromRequest(session, request)
        builder = maker(output, *args)
        try:
            builder.execute(request)

            f = open(output, 'rb')
            content = f.read()
            f.close()
        finally:
            try:
                unlink(output)
            except OSError:  # pragma: nocover
                pass

        response = request.response
        response.content_type = 'application/pdf'
        cdisp = 'attachment; filename=%s.pdf' % maker.__name__
        response.content_disposition = cdisp
        response.body = content
        response.cache_control.public = True
        response.cache_control.max_age = builder.cache_max_age
        return response
    except InvalidUserArgument as e:
        logger.debug("Couldn't create report %s: %s", maker.__name__, e)
        raise HTTPBadRequest(request.localizer.translate(e.message))
    except OperationAborted as e:
        logger.error("Couldn't create report %s: %s", maker.__name__, e)
        raise HTTPBadRequest(request.localizer.translate(e.message))
    except Exception as e:  # pragma: nocover
        logger.critical(
            "Couldn't create report %s: %s", maker.__name__, e, exc_info=True
        )
        raise HTTPInternalServerError(str(e))


@view_config(route_name='pdf_participants')
def participants(request):
    from os.path import dirname
    from os.path import join

    import sol

    ParticipantsPrintout.flags = join(
        dirname(sol.__file__), 'static', 'images', 'flags'
    )
    return _createPdf(request, ParticipantsPrintout)


@view_config(route_name='pdf_tourneyranking')
def tourneyranking(request):
    return _createPdf(request, TourneyRankingPrintout)


@view_config(route_name='pdf_tourneyoverranking')
def tourneyoverranking(request):
    return _createPdf(request, TourneyOverRankingPrintout)


@view_config(route_name='pdf_tourneyunderranking')
def tourneyunderranking(request):
    return _createPdf(request, TourneyUnderRankingPrintout)


@view_config(route_name='pdf_tourneywomenranking')
def tourneywomenranking(request):
    return _createPdf(request, TourneyWomenRankingPrintout)


@view_config(route_name='pdf_nationalranking')
def nationalranking(request):
    from os.path import dirname
    from os.path import join

    import sol

    NationalRankingPrintout.flags = join(
        dirname(sol.__file__), 'static', 'images', 'flags'
    )
    return _createPdf(request, NationalRankingPrintout)


@view_config(route_name='pdf_results')
def results(request):
    return _createPdf(request, ResultsPrintout)


@view_config(route_name='pdf_matches')
def matches(request):
    return _createPdf(request, MatchesPrintout)


@view_config(route_name='pdf_scorecards')
def scorecards(request):
    return _createPdf(request, ScoreCardsPrintout)


@view_config(route_name='pdf_badges')
def badges(request):
    from os.path import dirname
    from os.path import join

    import sol

    settings = request.registry.settings
    BadgesPrintout.flags = join(dirname(sol.__file__), 'static', 'images', 'flags')
    BadgesPrintout.emblems = settings['sol.emblems_dir']
    return _createPdf(request, BadgesPrintout)


@view_config(route_name='pdf_championshipranking')
def championshipranking(request):
    return _createPdf(request, ChampionshipRankingPrintout)


@view_config(route_name='pdf_ratingranking')
def ratingranking(request):
    return _createPdf(request, RatingRankingPrintout)


@view_config(route_name='pdf_boardlabels')
def boardlabels(request):
    return _createPdf(request, BoardLabelsPrintout)


@view_config(route_name='pdf_playbill')
def playbill(request):
    from os.path import dirname
    from os.path import join

    import sol

    settings = request.registry.settings
    PlaybillPrintout.emblems = settings['sol.emblems_dir']
    return _createPdf(request, PlaybillPrintout)
