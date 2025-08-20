# -*- coding: utf-8 -*-
# :Project:   SoL -- Results printout
# :Created:   lun 13 giu 2016 11:46:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import CondPageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import gettext
from ..i18n import ordinalp
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from ..models.errors import OperationAborted
from . import BOLD_FONT_NAME
from . import caption_style
from . import heading_style
from . import normal_style
from . import rank_width
from . import scores_width
from .basic import TourneyPrintout


class ResultsPrintout(TourneyPrintout):
    "Results of the last turn."

    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        args = super().getArgumentsFromRequest(session, request)
        kw = request.params
        if 'turn' in kw:
            if kw['turn'] == 'all':
                args.append(None)
            else:
                try:
                    args.append(int(kw['turn']))
                except ValueError:
                    raise InvalidUserArgument(
                        _(
                            'Invalid turn number: $turn',
                            mapping=dict(turn=repr(kw['turn'])),
                        )
                    )
        else:
            args.append(args[1].rankedturn)

        return args

    def __init__(self, output, locale, tourney, turn):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getLitURL(self, request):
        functional_testing = request.registry.settings['desktop.version'] == 'test'
        if not request.host.startswith('localhost') or functional_testing:
            otherargs = {}
            if self.turn:
                otherargs['_query'] = {'turn': self.turn}
            return request.route_url('lit_tourney', guid=self.tourney.guid, **otherargs)

    def getTurnDescription(self, turn, count):
        if count == 1:
            title = gettext('Result of final')
        elif count == 2:
            title = gettext('Results of semifinals')
        elif count == 4:
            title = gettext('Results of quarterfinals')
        elif count == 8:
            title = gettext('Results of pre-quarterfinals')
        elif count == 16:
            title = gettext('Results of 16th-finals')
        elif count == 32:
            title = gettext('Results of 32nd-finals')
        elif count == 64:
            title = gettext('Results of 64th-finals')
        else:
            title = gettext('Results %s round') % ordinalp(turn)
        return title

    def getSubTitle(self):
        if self.turn:
            matches = [m.final for m in self.tourney.matches if m.turn == self.turn]
            if self.tourney.system == 'knockout':
                return self.getTurnDescription(self.turn, len(matches))
            else:
                if matches[0]:
                    return gettext('Results %s final round') % ordinalp(self.turn)
                else:
                    return gettext('Results %s round') % ordinalp(self.turn)
        else:
            return gettext('All results')

    def getElements(self):
        yield from super().getElements()

        turn = self.turn

        def player_caption(player, h, l, cc, on):
            return player.caption(html=False)

        phantom = gettext('Phantom')
        results = []
        for m in self.tourney.matches:
            if turn is None or m.turn == turn:
                try:
                    winner, loser, netscore = m.results()
                except (InvalidUserArgument, OperationAborted):
                    winner = netscore = None
                c1 = m.competitor1.caption(
                    nationality=True, player_caption=player_caption
                )
                c2 = (
                    m.competitor2.caption(
                        nationality=True, player_caption=player_caption
                    )
                    if m.competitor2
                    else phantom
                )
                s1 = m.score1
                s2 = m.score2
                if netscore:
                    if winner is m.competitor1:
                        c1 = '<b>%s</b>' % c1
                    elif winner is m.competitor2:
                        c2 = '<b>%s</b>' % c2
                s1_2 = s2_2 = s1_3 = s2_3 = None
                if self.tourney.matcheskind == 'bestof3':
                    if m.score1_2 or m.score2_2:
                        s1_2 = m.score1_2
                        s2_2 = m.score2_2
                        if m.score1_3 or m.score2_3:
                            s1_3 = m.score1_3
                            s2_3 = m.score2_3
                results.append(
                    (m.turn, m.board, c1, c2, s1, s2, s1_2, s2_2, s1_3, s2_3, m.final)
                )
        if not results:
            return

        results.sort()

        if turn:
            yield from self.getSingleTurnElements(results)
        else:
            yield from self.getAllTurnElements(results)

    def getSingleTurnElements(self, results):
        from reportlab.pdfbase.pdfmetrics import stringWidth

        slash_w = stringWidth('/', normal_style.fontName, normal_style.fontSize)

        rows = [(gettext('#'), gettext('Match'), '', gettext('Result'), '')]

        styles = []
        row = 1
        for turn, board, c1, c2, s1, s2, s1_2, s2_2, s1_3, s2_3, final in results:
            rows.append(
                (
                    board,
                    Paragraph(c1, normal_style),
                    Paragraph(c2, normal_style),
                    str(s1),
                    '/',
                    str(s2),
                )
            )
            styles.append(
                (
                    'FONT',
                    (-3 if s1 > s2 else -1, row),
                    (-3 if s1 > s2 else -1, row),
                    BOLD_FONT_NAME,
                )
            )
            if self.tourney.matcheskind == 'bestof3':
                if s1_2 or s2_2:
                    row += 1
                    rows.append(('', '', '', str(s1_2), '/', str(s2_2)))
                    styles.append(
                        (
                            'FONT',
                            (-3 if s1 > s2 else -1, row),
                            (-3 if s1 > s2 else -1, row),
                            BOLD_FONT_NAME,
                        )
                    )
                    if s1_3 or s2_3:
                        row += 1
                        rows.append(('', '', '', str(s1_3), '/', str(s2_3)))
                        styles.append(
                            (
                                'FONT',
                                (-3 if s1 > s2 else -1, row),
                                (-3 if s1 > s2 else -1, row),
                                BOLD_FONT_NAME,
                            )
                        )
                styles.append(('LINEBELOW', (0, row), (-1, row), 0.25, colors.black))
            row += 1

        desc_width = (
            self.doc.width / self.columns * 0.9
            - rank_width
            - scores_width * 2
            - slash_w
        ) / 2
        yield Table(
            rows,
            (rank_width, desc_width, desc_width, scores_width, slash_w, scores_width),
            style=TableStyle(
                [
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                    ('SPAN', (1, 0), (2, 0)),
                    ('ALIGN', (1, 0), (2, 0), 'CENTER'),
                    ('SPAN', (-3, 0), (-1, 0)),
                    ('ALIGN', (-3, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (-3, 1), (-3, -1), 'RIGHT'),
                    ('ALIGN', (-2, 1), (-2, -1), 'CENTER'),
                    ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                    ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                    ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                    ('SIZE', (0, 1), (-1, -1), normal_style.fontSize),
                    ('LEADING', (0, 1), (-1, -1), normal_style.leading),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
                ]
                + styles
            ),
        )

    def getAllTurnElements(self, results):
        from itertools import groupby
        from operator import itemgetter

        key = itemgetter(0)
        for turn, res in groupby(results, key):
            yield CondPageBreak(4 * cm)
            res = list(res)
            if self.tourney.system == 'knockout':
                title = Paragraph(
                    self.getTurnDescription(turn, len(res)), heading_style
                )
            else:
                if res[0][6]:
                    title = Paragraph(
                        gettext('Results %s final round') % ordinalp(turn),
                        heading_style,
                    )
                else:
                    title = Paragraph(
                        gettext('Results %s round') % ordinalp(turn), heading_style
                    )
            yield title
            yield from self.getSingleTurnElements(res)
            yield Spacer(0, 0.4 * cm)
