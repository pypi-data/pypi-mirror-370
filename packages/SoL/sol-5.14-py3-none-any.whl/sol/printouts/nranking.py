# -*- coding: utf-8 -*-
# :Project:   SoL -- Ranking printout
# :Created:   lun 13 giu 2016 11:41:01 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.platypus import Paragraph
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import country_name
from ..i18n import gettext
from ..i18n import ngettext
from ..i18n import ordinal
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from . import caption_style
from . import normal_style
from . import prizes_width
from . import rank_width
from . import scores_width
from .basic import TourneyPrintout


class NationalRankingPrintout(TourneyPrintout):
    "Current ranking of a tourney by nationality."

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
        return args

    def __init__(self, output, locale, tourney, turn=None):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Ranking by nationality after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final ranking by nationality')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Ranking by nationality after %s round') % ordinal(
                        rt
                    )
                else:
                    return gettext('Initial ranking by nationality')

    def getElements(self):
        from operator import itemgetter
        from os.path import join

        yield from super().getElements()

        if self.turn is not None:
            ranking = [
                (
                    i,
                    c.description,
                    c.player1Nationality,
                    r.points,
                    r.bucholz,
                    r.netscore,
                    0,
                )
                for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)
            ]
        else:
            ranking = [
                (
                    i,
                    c.description,
                    c.player1Nationality,
                    c.points,
                    c.bucholz,
                    c.netscore,
                    c.prize,
                )
                for i, c in enumerate(self.tourney.ranking, 1)
            ]

        if not ranking:
            return

        nsummary = {}
        for r in ranking:
            sum = nsummary.get(r[2], [0, 0, 0, 0, 0])
            sum[0] += r[6]
            sum[1] += r[3]
            sum[2] += r[4]
            sum[3] += r[5]
            sum[4] += 1
            nsummary[r[2]] = sum

        nations = list(nsummary.items())
        nations.sort(key=itemgetter(1))
        nations.reverse()

        if self.tourney.championship.playersperteam > 1:
            caption = gettext('Team')
        else:
            caption = gettext('Player')

        if self.tourney.prized:
            style = TableStyle(
                [
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                    ('ALIGN', (-4, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                    ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                    ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                    ('SIZE', (0, 1), (-1, -1), normal_style.fontSize),
                    ('LEADING', (0, 1), (-1, -1), normal_style.leading),
                    ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                ]
            )
            rows = [
                (
                    '#',
                    caption,
                    gettext('Pts'),
                    gettext('Bch'),
                    gettext('Net'),
                    gettext('Prz'),
                )
            ]
            for n in nations:
                if n[0]:
                    flag = join(self.flags, n[0] + '.png')
                    country = country_name(n[0])
                    caption = ngettext(
                        '$country: $num competitor',
                        '$country: $num competitors',
                        n[1][4],
                        mapping=dict(country=country, num=n[1][4]),
                    )
                    rows.append(
                        (
                            Image(flag),
                            Paragraph(caption, normal_style),
                            n[1][1],
                            n[1][2],
                            n[1][3],
                            n[1][0],
                        )
                    )
                else:
                    rows.append(
                        (
                            '',
                            Paragraph(gettext('Unspecified country'), normal_style),
                            n[1][1],
                            n[1][2],
                            n[1][3],
                            n[1][0],
                        )
                    )
                rnum = len(rows) - 1
                if rnum > 1:
                    style.add('LINEABOVE', (0, rnum), (-1, rnum), 1, colors.black)
                    style.add('TOPPADDING', (0, rnum), (-1, rnum), 15)
                style.add('FONT', (0, rnum), (-1, rnum), 'Times-Bold')
                rows.extend(
                    [
                        (
                            rank,
                            Paragraph(description, normal_style),
                            points,
                            bucholz,
                            netscore,
                            prize,
                        )
                        for (
                            rank,
                            description,
                            nationality,
                            points,
                            bucholz,
                            netscore,
                            prize,
                        ) in ranking
                        if nationality == n[0]
                    ]
                )
            desc_width = (
                self.doc.width / self.columns * 0.9
                - rank_width
                - scores_width * 4
                - prizes_width
            )
            yield Table(
                rows,
                (
                    rank_width,
                    desc_width,
                    scores_width,
                    scores_width,
                    scores_width,
                    prizes_width,
                ),
                style=style,
            )
        else:
            style = TableStyle(
                [
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                    ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                    ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                    ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                    ('SIZE', (0, 1), (-1, -1), normal_style.fontSize),
                    ('LEADING', (0, 1), (-1, -1), normal_style.leading),
                    ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                ]
            )
            rows = [('#', caption, gettext('Pts'), gettext('Bch'), gettext('Net'))]

            for n in nations:
                if n[0]:
                    flag = join(self.flags, n[0] + '.png')
                    country = country_name(n[0])
                    caption = ngettext(
                        '$country: $num competitor',
                        '$country: $num competitors',
                        n[1][4],
                        mapping=dict(country=country, num=n[1][4]),
                    )
                    rows.append(
                        (
                            Image(flag),
                            Paragraph(caption, normal_style),
                            n[1][1],
                            n[1][2],
                            n[1][3],
                        )
                    )
                else:
                    rows.append(
                        (
                            '',
                            Paragraph(gettext('Unspecified country'), normal_style),
                            n[1][1],
                            n[1][2],
                            n[1][3],
                        )
                    )
                rnum = len(rows) - 1
                if rnum > 1:
                    style.add('LINEABOVE', (0, rnum), (-1, rnum), 1, colors.black)
                style.add('FONT', (0, rnum), (-1, rnum), 'Times-Bold')
                rows.extend(
                    [
                        (
                            rank,
                            Paragraph(description, normal_style),
                            points,
                            bucholz,
                            netscore,
                        )
                        for (
                            rank,
                            description,
                            nationality,
                            points,
                            bucholz,
                            netscore,
                            prize,
                        ) in ranking
                        if nationality == n[0]
                    ]
                )

            desc_width = (
                self.doc.width / self.columns * 0.9 - rank_width - scores_width * 3
            )
            yield Table(
                rows,
                (rank_width, desc_width, scores_width, scores_width, scores_width),
                style=style,
            )
