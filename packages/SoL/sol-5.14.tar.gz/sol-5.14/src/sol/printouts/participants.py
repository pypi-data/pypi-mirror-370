# -*- coding: utf-8 -*-
# :Project:   SoL -- Participants printout
# :Created:   lun 13 giu 2016 11:36:32 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2020, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from reportlab.platypus import Image
from reportlab.platypus import Paragraph
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import country_name
from ..i18n import ngettext
from ..i18n import translatable_string as gettext
from . import normal_style
from . import rank_width
from .basic import TourneyPrintout


class ParticipantsPrintout(TourneyPrintout):
    "List of participants of a tourney."

    def __init__(self, output, locale, tourney):
        super().__init__(
            output, locale, tourney, len(tourney.competitors) < 35 and 1 or 2
        )

    def getSubTitle(self):
        num = len(self.tourney.competitors)
        return ngettext(
            '$num Participant', '$num Participants', num, mapping=dict(num=num)
        )

    def getElements(self):
        from os.path import join

        yield from super().getElements()

        nsummary = {}
        for c in sorted(self.tourney.competitors, key=lambda c: c.description):
            ncomps = nsummary.setdefault(c.player1Nationality, [])
            ncomps.append(c.description)

        if not nsummary:
            return

        style = TableStyle(
            [
                ('SIZE', (0, 0), (0, -1), normal_style.fontSize),
                ('LEADING', (0, 0), (0, -1), normal_style.leading),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
        )

        nations = list(nsummary.items())
        if len(nations) > 1:
            nations.sort(key=lambda n: -len(n[1]))

            rows = []
            for ccode, comps in nations:
                if ccode:
                    flag = join(self.flags, ccode + '.png')
                    country = country_name(ccode)
                    caption = ngettext(
                        '$country: $num competitor',
                        '$country: $num competitors',
                        len(comps),
                        mapping=dict(country=country, num=len(comps)),
                    )
                    rows.append((Image(flag), Paragraph(caption, normal_style)))
                else:
                    rows.append(
                        ('', Paragraph(gettext('Unspecified country'), normal_style))
                    )
                rnum = len(rows) - 1
                if rnum > 1:
                    style.add('TOPPADDING', (0, rnum), (-1, rnum), 15)
                style.add('FONT', (0, rnum), (-1, rnum), 'Times-Bold')

                rows.extend(
                    (i, Paragraph(c, normal_style))
                    for i, c in enumerate(sorted(comps), 1)
                )
        else:
            rows = [
                (i, Paragraph(c, normal_style)) for i, c in enumerate(nations[0][1], 1)
            ]

        desc_width = self.doc.width / self.columns * 0.9 - rank_width
        yield Table(rows, (rank_width, desc_width), style=style)
