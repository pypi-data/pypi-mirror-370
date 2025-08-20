# -*- coding: utf-8 -*-
# :Project:   SoL -- XLSX views
# :Created:   sab 21 lug 2018 12:09:17 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2022, 2024 Lele Gaifax
#

from __future__ import annotations

from re import sub

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from sqlalchemy.exc import NoResultFound

from ..models import Tourney
from ..models.bio import TourneyXlsxDumper


@view_config(route_name='xlsx_tourney')
def tourneySpreadsheet(request):
    sas = request.dbsession

    try:
        idtourney = int(request.matchdict['id'])
    except ValueError:
        try:
            tourney = sas.query(Tourney).filter_by(guid=request.matchdict['id']).one()
        except NoResultFound:
            raise HTTPBadRequest('Bad tourney guid')
    else:
        tourney = sas.get(Tourney, idtourney)
        if tourney is None:
            raise HTTPBadRequest('Bad tourney id')

    dumper = TourneyXlsxDumper(tourney)

    sdesc = tourney.championship.description
    sdesc = sdesc.encode('ascii', 'ignore').decode('ascii')
    filename = '%s-%s.xlsx' % (sub(r'\W+', '_', sdesc), tourney.date)

    response = request.response
    response.body = dumper()
    response.content_type = (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response.content_disposition = 'attachment; filename=%s' % filename

    return response
