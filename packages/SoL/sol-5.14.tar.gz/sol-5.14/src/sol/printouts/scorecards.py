# -*- coding: utf-8 -*-
# :Project:   SoL -- Score cards printout
# :Created:   lun 13 giu 2016 11:51:34 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from importlib.metadata import metadata

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import FrameBreak
from reportlab.platypus import KeepTogether
from reportlab.platypus import PageTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import gettext
from ..i18n import ordinal
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from . import cardname_style
from . import cardtitle_style
from .basic import TourneyPrintout


class ScoreCardsPrintout(TourneyPrintout):
    "Score cards, where match results are written by the competitors."

    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        args = super().getArgumentsFromRequest(session, request)
        if request.matchdict['id'] != 'blank':
            kw = request.params
            if 'starttime' in kw:
                try:
                    starttime = float(kw['starttime'])
                    if starttime > 9999999999:
                        starttime = starttime / 1000
                    starttime = datetime.fromtimestamp(starttime, timezone.utc)
                    if 'tzoffset' in kw:
                        starttime -= timedelta(minutes=int(kw['tzoffset']))
                    args.append(starttime)
                except ValueError:
                    raise InvalidUserArgument(
                        _(
                            'Invalid starttime: $starttime',
                            mapping=dict(starttime=repr(kw['starttime'])),
                        )
                    )
        return args

    def __init__(self, output, locale, tourney, starttime=None, columns=2):
        super().__init__(output, locale, tourney, columns)
        self.starttime = starttime

    def execute(self, request):
        """Create and build the document.

        :param request: the Pyramid request instance
        """

        self.request = request
        self.createDocument()
        self.doc.build(list(self.getElements()))

    @property
    def cache_max_age(self):
        "Cache for one year blank score cards, no cache otherwise."

        if self.tourney is None:
            return 60 * 60 * 24 * 365
        else:
            return 0

    def createDocument(self):
        if self.tourney is not None:
            if not self.tourney.prized:
                title = gettext('Score cards for %s round') % ordinal(
                    self.tourney.currentturn
                )
            else:
                title = gettext('Finals score cards')
        else:
            title = gettext('Score cards')

        doc = self.doc = BaseDocTemplate(
            self.output,
            pagesize=A4,
            showBoundary=0,
            leftMargin=0.5 * cm,
            rightMargin=0.5 * cm,
            topMargin=0.5 * cm,
            bottomMargin=0.5 * cm,
            author='SoL %s' % metadata('sol')['Version'],
            creator='https://gitlab.com/metapensiero/SoL',
            subject=self.__class__.__name__,
            title=title,
        )

        lp_frames = []

        fwidth = doc.width / self.columns
        fheight = doc.height

        bmargin = doc.bottomMargin
        for f in range(self.columns):
            lmargin = doc.leftMargin + f * fwidth
            lp_frames.append(Frame(lmargin, bmargin, fwidth, fheight))

        templates = [PageTemplate(frames=lp_frames, onPage=self.decoratePage)]
        doc.addPageTemplates(templates)

    def decoratePage(self, canvas, doc):
        "Add crop-marks to the page."

        line = canvas.line
        for iy in range(0, 4):
            y = doc.bottomMargin + iy * (doc.height / 3)
            for ix in range(0, 3):
                x = doc.leftMargin + ix * (doc.width / 2)
                line(x - 5, y, x + 5, y)
                line(x, y - 5, x, y + 5)

    def getElements(self):
        if self.tourney is not None:
            currentturn = self.tourney.currentturn
            boards = [
                (m.board, m.competitor1.description, m.competitor2.description, m.final)
                for m in self.tourney.matches
                if m.turn == currentturn and m.idcompetitor2
            ]
        else:
            # Six blank score cards
            boards = [(i, '', '') for i in range(1, 7)]

        if not boards:
            return

        boards.sort()

        # Fill the last page with empty score cards, when they are less than 3: this has been
        # initially requested by Daniele to minimize the waste of paper (see commit
        # fbf3d84b7de17955c16f98e762048112ffe61d4d), who collects empty cards and use them when
        # playing at home; on the other hand, printing more than two empty cards at each turn
        # is a waste of ink, as noticed by Carlito

        if 0 < len(boards) % 6 < 3:
            boards.extend([(None, '', '', False)] * (6 - (len(boards) % 6)))

        data = [
            [
                gettext('Points'),
                '',
                gettext('Score'),
                gettext('Coins'),
                gettext('Queen'),
                '',
                '',
                gettext('Coins'),
                gettext('Score'),
                '',
                gettext('Points'),
            ]
        ]

        max_rounds = 9
        for i in range(1, max_rounds + 1):
            data.append(['', '', '', '', '', i, '', '', '', '', ''])

        sw = self.doc.width / self.columns * 0.95 / 23
        ssw = sw / 2
        qw = sw * 2
        nw = sw * 3
        table_widths = (nw, ssw, nw, nw, qw, ssw, qw, nw, nw, ssw, nw)
        table_style = TableStyle(
            [
                ('GRID', (0, 1), (0, max_rounds), 1.0, colors.black),
                ('GRID', (-1, 1), (-1, max_rounds), 1.0, colors.black),
                ('GRID', (2, 1), (-3, max_rounds), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('SIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (5, 1), (5, -1), 'CENTER'),
                ('BACKGROUND', (5, 1), (5, -2), colors.lightgrey),
                ('SIZE', (5, 1), (5, -1), 8),
                ('SPAN', (4, 0), (6, 0)),
                ('ALIGN', (0, max_rounds + 1), (-1, max_rounds + 1), 'CENTER'),
                ('SIZE', (0, max_rounds + 1), (-1, max_rounds + 1), 8),
                ('BOX', (0, max_rounds + 2), (0, max_rounds + 2), 2.0, colors.black),
                ('BOX', (-1, max_rounds + 2), (-1, max_rounds + 2), 2.0, colors.black),
                ('ALIGN', (0, max_rounds + 3), (-1, max_rounds + 3), 'CENTER'),
                ('SIZE', (0, max_rounds + 3), (-1, max_rounds + 3), 8),
                ('BOX', (0, max_rounds + 4), (0, max_rounds + 4), 0.5, colors.black),
                ('BOX', (-1, max_rounds + 4), (-1, max_rounds + 4), 0.5, colors.black),
                ('SPAN', (1, max_rounds + 1), (4, max_rounds + 3)),
                ('SPAN', (6, max_rounds + 1), (-2, max_rounds + 3)),
                ('VALIGN', (0, max_rounds + 1), (-1, max_rounds + 4), 'MIDDLE'),
                ('SPAN', (1, -1), (-2, -1)),
            ]
        )

        if self.tourney is not None:
            if self.starttime:
                start = self.starttime
            else:
                now = datetime.now()
                start = now + timedelta(minutes=9, seconds=45)
                start += timedelta(minutes=5 - start.minute % 5)
            end = start + timedelta(minutes=self.tourney.duration)
            # TRANSLATORS: this is strftime() format, see
            # http://docs.python.org/3/library/time.html#time.strftime
            time_format = gettext('%I:%M %p')
            estimated_start = start.strftime(time_format)
            estimated_end = end.strftime(time_format)

            if not self.tourney.prized:
                boardno_format = '%s<br/><font size=6>%s</font>' % (
                    gettext('Round %(turn)d — Carromboard %(board)d'),
                    gettext('estimated start %(start)s — end %(end)s'),
                )

        for i, board in enumerate(boards):
            boardno = ['']
            if self.tourney is not None and board[0]:
                if self.tourney.prized or board[3]:
                    if board[1] == self.tourney.ranking[0].description:
                        caption = gettext('1st/2nd place final')
                    else:
                        caption = gettext('3rd/4th place final')
                    if self.tourney.finalkind == 'bestof3':
                        finalmatches = [m for m in self.tourney.matches if m.final]
                        nfinalturns = len({m.turn for m in finalmatches})
                        caption += ' (%d/3)' % nfinalturns
                    boardno.append(Paragraph(caption, cardtitle_style))
                else:
                    boardno.append(
                        Paragraph(
                            boardno_format
                            % dict(
                                turn=currentturn,
                                board=board[0],
                                start=estimated_start,
                                end=estimated_end,
                            ),
                            cardtitle_style,
                        )
                    )
            else:
                boardno.append('')
            boardno.extend([''] * 9)
            names = [
                [
                    gettext('Total'),
                    Paragraph(board[1], cardname_style),
                    '',
                    '',
                    '',
                    '',
                    Paragraph(board[2], cardname_style),
                    '',
                    '',
                    '',
                    gettext('Total'),
                ],
                [''] * 11,
                [gettext('Break')] + [''] * 9 + [gettext('Break')],
                boardno,
            ]
            table = Table(data + names, table_widths, style=table_style)
            if i == 0 or (i + 1) % 3:
                yield KeepTogether([table, Spacer(0, 0.6 * cm)])
            else:
                yield table
                yield FrameBreak()
