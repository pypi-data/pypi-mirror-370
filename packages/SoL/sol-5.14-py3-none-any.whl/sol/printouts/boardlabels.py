# -*- coding: utf-8 -*-
# :Project:   SoL -- Board labels printout
# :Created:   lun 27 apr 2020, 16:49:51
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020, 2022-2024 Lele Gaifax
#

from __future__ import annotations

from importlib.metadata import metadata

from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import FrameBreak
from reportlab.platypus import PageTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

from ..i18n import gettext
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from . import BASE_FONT_NAME
from . import boardnumber_style
from . import subtitle_style
from .basic import TourneyPrintout


class BoardLabelsPrintout(TourneyPrintout):
    "Carromboard labels."

    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        args = super().getArgumentsFromRequest(session, request)
        kw = request.params
        if 'nboards' in kw:
            try:
                args.append(int(kw['nboards']))
            except ValueError:
                raise InvalidUserArgument(
                    _(
                        'Invalid number of carromboards: $nboards',
                        mapping=dict(nboards=repr(kw['nboards'])),
                    )
                )
        else:
            args.append(None)

        return args

    def __init__(self, output, locale, tourney, nboards):
        super().__init__(output, locale, tourney, 3)

        if not nboards:
            nboards = len(tourney.competitors) // 2
        self.nboards = nboards

    def execute(self, request):
        """Create and build the document.

        :param request: the Pyramid request instance
        """

        self.request = request
        self.createDocument()
        self.doc.build(list(self.getElements()))

    def createDocument(self):
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
            title=gettext('Carromboard labels'),
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
        for iy in range(0, 5):
            y = doc.bottomMargin + iy * (doc.height / 4)
            for ix in range(0, 4):
                x = doc.leftMargin + ix * (doc.width / 3)
                line(x - 5, y, x + 5, y)
                line(x, y - 5, x, y + 5)

        if self.nboards:
            nboards = min(self.nboards - 12 * (canvas._pageNumber - 1), 12)

            canvas.saveState()
            canvas.setFont(BASE_FONT_NAME, 6)

            tdesc = self.tourney.description
            canvas.rotate(90)
            for boardno in range(nboards):
                column, row = divmod(boardno, 4)
                x = doc.bottomMargin + (4 - row) * doc.height / 4 - doc.height / 8
                y = doc.leftMargin + column * doc.width / 3 + 0.4 * cm
                canvas.drawCentredString(x, -y, tdesc)

            tdate = self.tourney.date.strftime(gettext('%m-%d-%Y'))
            canvas.rotate(-180)
            for boardno in range(nboards):
                column, row = divmod(boardno, 4)
                x = doc.bottomMargin + (4 - row) * doc.height / 4 - doc.height / 8
                y = doc.leftMargin + (column + 1) * doc.width / 3 - 0.4 * cm
                canvas.drawCentredString(-x, y, tdate)

            canvas.restoreState()

    def getElements(self):
        nboards = self.nboards
        if not nboards:
            return

        size = 3 * cm

        for boardno in range(1, nboards + 1):
            url = self.tourney.getEditBoardURL(self.request, boardno)
            drawing = createBarcodeDrawing('QR', value=url, width=size, height=size)
            drawing.hAlign = 'CENTER'
            yield Paragraph(gettext('Carromboard'), subtitle_style)
            yield Paragraph(str(boardno), boardnumber_style)
            yield drawing
            if boardno % 4 == 0:
                yield FrameBreak()
            else:
                yield Spacer(0, 0.8 * cm)
