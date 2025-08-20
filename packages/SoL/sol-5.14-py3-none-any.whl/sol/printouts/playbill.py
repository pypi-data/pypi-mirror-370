# -*- coding: utf-8 -*-
# :Project:   SoL — Tourney playbill
# :Created:   dom 22 gen 2023, 18:00:43
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2023, 2024, 2025 Lele Gaifax
#

from __future__ import annotations

from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

from ..i18n import gettext
from . import subtitle_style
from . import title_style
from .basic import TourneyPrintout
from .utils import reduce_fontsize_to_fit_width


class PlaybillPrintout(TourneyPrintout):
    "Tourney playbill."

    showBoundary = False
    emblems = '.'

    def __init__(self, output, locale, tourney):
        super().__init__(output, locale, tourney, 1)

    def getSubTitle(self):
        return ''

    def execute(self, request):
        """Create and build the document.

        :param request: the Pyramid request instance
        """

        # Superclass draws the QRCode in the title frame
        self.lit_url = None
        self._lit_url = self.getLitURL(request)
        self.createDocument()
        self.doc.build(list(self.getElements()))

    def decoratePage(self, canvas, doc):
        from os.path import exists
        from os.path import join

        super().decoratePage(canvas, doc)

        if self.tourney.championship.club.emblem:
            hh = doc.bottomMargin + doc.height + doc.topMargin / 2
            hl = doc.leftMargin
            hc = doc.leftMargin + doc.width / 2.0
            hr = doc.leftMargin + doc.width
            image = join(self.emblems, self.tourney.championship.club.emblem)
            if exists(image):
                canvas.drawImage(
                    image, hr - 4*cm, hh - 4.5*cm, 4 * cm, 4 * cm, preserveAspectRatio=True
                )
            if self.tourney.hosting_club and self.tourney.hosting_club.emblem:
                image = join(self.emblems, self.tourney.hosting_club.emblem)
                if exists(image):
                    canvas.drawImage(
                        image, hl, hh - 4.5*cm, 4 * cm, 4 * cm, preserveAspectRatio=True
                    )

    def getElements(self):
        if self.tourney.championship.club.emblem:
            yield Spacer(0, 4 * cm)

        title = self.getTitle()
        tstyle, ststyle = reduce_fontsize_to_fit_width(
            title, self.title_width - 1 * cm, title_style, subtitle_style
        )

        yield Paragraph(title, tstyle)
        subtitle = self.getSubTitle()
        if subtitle:
            yield Paragraph(subtitle, ststyle)

        url = self._lit_url
        if not url:
            return

        size = 10 * cm
        drawing = createBarcodeDrawing('QR', value=url, width=size, height=size)
        drawing.hAlign = 'CENTER'

        # Extend original draw() method to add a clickable area over the QRCode
        def drawAndAddLink(*args, __orig_draw=drawing.draw, __url=url, **kwargs):
            __orig_draw(*args, **kwargs)
            drawing.canv.linkURL(__url, (0, 0, size, size), relative=1)
        drawing.__dict__['draw'] = drawAndAddLink

        yield drawing
        yield Spacer(0, 1 * cm)
        yield Paragraph(
            gettext('Scan the QRCode and visit the URL to follow the tournament live!'),
            subtitle_style,
        )
