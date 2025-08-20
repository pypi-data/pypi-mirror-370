# -*- coding: utf-8 -*-
# :Project:   SoL -- Matches printout
# :Created:   lun 13 giu 2016 11:49:26 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import gettext
from ..i18n import ordinalp
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from . import caption_style
from . import normal_style
from . import rank_width
from .basic import TourneyPrintout


class MatchesPrintout(TourneyPrintout):
    "Next turn matches."

    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        args = super().getArgumentsFromRequest(session, request)
        kw = request.params
        if 'turn' in kw:
            try:
                args.append(int(kw['turn']))
            except ValueError:
                raise InvalidUserArgument(
                    _('Invalid turn number: $turn', mapping=dict(turn=repr(kw['turn'])))
                )
        else:
            args.append(None)

        return args

    def __init__(self, output, locale, tourney, turn):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getLitURL(self, request):
        functional_testing = request.registry.settings['desktop.version'] == 'test'
        if not request.host.startswith('localhost') or functional_testing:
            return request.route_url(
                'lit_tourney',
                guid=self.tourney.guid,
                _query=dict(
                    turn=(
                        self.turn if self.turn is not None else self.tourney.currentturn
                    )
                ),
            )

    def getSubTitle(self):
        turn = self.turn if self.turn is not None else self.tourney.currentturn
        if self.tourney.finalturns:
            return gettext('Matches %s final round') % ordinalp(turn)
        else:
            return gettext('Matches %s round') % ordinalp(turn)

    def getElements(self):
        yield from super().getElements()

        phantom = gettext('Phantom')
        turn = self.turn if self.turn is not None else self.tourney.currentturn
        matches = [
            (
                m.board,
                m.competitor1.caption(nationality=True),
                m.competitor2.caption(nationality=True) if m.competitor2 else phantom,
            )
            for m in self.tourney.matches
            if m.turn == turn
        ]
        if not turn:
            return

        matches.sort()
        rows = [(gettext('#'), gettext('Match'))]
        rows.extend(
            [
                (board, Paragraph(c1, normal_style), Paragraph(c2, normal_style))
                for (board, c1, c2) in matches
            ]
        )

        desc_width = (self.doc.width / self.columns * 0.9 - rank_width) / 2
        yield Table(
            rows,
            (rank_width, desc_width, desc_width),
            style=TableStyle(
                [
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                    ('SPAN', (1, 0), (-1, 0)),
                    ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                    ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                    ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                    ('SIZE', (0, 1), (-1, -1), normal_style.fontSize),
                    ('LEADING', (0, 1), (-1, -1), normal_style.leading),
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.black),
                ]
            ),
        )
