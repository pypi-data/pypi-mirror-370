# -*- coding: utf-8 -*-
# :Project:   SoL -- Statics access tests
# :Created:   sab 07 lug 2018 17:51:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#


def test_favicon(app):
    app.get('/favicon.ico')


def test_robots(app):
    app.get('/robots.txt')
