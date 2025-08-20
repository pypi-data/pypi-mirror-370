# -*- coding: utf-8 -*-
# :Project:   SoL -- Override default mp.extjs.desktop app view
# :Created:   sab 14 lug 2018 11:26:09 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018, 2020, 2024 Lele Gaifax
#

from __future__ import annotations

from pyramid.settings import asbool
from pyramid.view import view_config


@view_config(route_name='app', renderer='app.mako')
def app_view(request):
    from metapensiero.extjs.desktop.pyramid import app_view

    data = app_view(request)
    data['locale'] = request.locale_name.replace('_', '-')
    settings = request.registry.settings
    data['signin_enabled'] = asbool(settings.get('sol.enable_signin'))
    data['password_reset_enabled'] = asbool(settings.get('sol.enable_password_reset'))
    data['admin_email'] = settings.get('sol.admin.email', '')
    return data
