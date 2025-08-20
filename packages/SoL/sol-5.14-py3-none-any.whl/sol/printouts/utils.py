# -*- coding: utf-8 -*-
# :Project:   SoL -- Utility functions
# :Created:   lun 13 giu 2016 11:13:42 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2021, 2024 Lele Gaifax
#

from __future__ import annotations

from copy import copy

from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas

from ..i18n import gettext
from ..i18n import translatable_string as _
from . import BASE_FONT_NAME


def reduce_fontsize_to_fit_width(text, maxwidth, *styles):
    """Reduce the font size of the given styles to fit a max width.

    :param text: the string of text
    :param maxwidth: maximum width that can be used
    :param styles: the list of styles that should be adapted
    :returns: a list of (copies of) the styles with the adapted font size
    """

    from reportlab.pdfbase.pdfmetrics import stringWidth

    copies = styles
    mainstyle = styles[0]

    while stringWidth(text, mainstyle.fontName, mainstyle.fontSize) > maxwidth:
        if mainstyle is styles[0]:  # pragma: no cover
            copies = [copy(style) for style in styles]
            mainstyle = copies[0]

        for style in copies:
            style.fontSize -= 1
            style.leading = style.fontSize * 1.1

    return copies


# Adapted from http://code.activestate.com/recipes/576832/


class TotalCountOfPagesCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._drawPageNumber(num_pages)
            super().showPage()
        super().save()

    def _drawPageNumber(self, page_count):
        self.setFont(BASE_FONT_NAME, 6)
        self.drawCentredString(
            self._pagesize[0] / 2,
            0.25 * cm,
            gettext('Page %d of %d') % (self._pageNumber, page_count),
        )
