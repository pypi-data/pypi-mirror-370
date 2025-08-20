# -*- coding: utf-8 -*-
# :Project:   SoL -- Ranking printout
# :Created:   lun 13 giu 2016 11:41:01 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2020, 2022, 2023, 2024, 2025 Lele Gaifax
#

from __future__ import annotations

from collections.abc import Generator

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import TableStyle
from reportlab.platypus.tables import Table

from ..i18n import gettext
from ..i18n import ngettext
from ..i18n import ordinal
from ..i18n import translatable_string as _
from ..models.errors import InvalidUserArgument
from . import caption_style
from . import cardinfo_style
from . import cardname_style
from . import country_width
from . import heading_style
from . import normal_style
from . import prizes_width
from . import rank_width
from . import scores_width
from .basic import TourneyPrintout


class TourneyRankingPrintout(TourneyPrintout):
    "Current ranking of a tourney."

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

    def __init__(self, output, locale, tourney, turn=None):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Ranking after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final ranking')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Ranking after %s round') % ordinal(rt)
                else:
                    return gettext('Initial ranking')

    def getFinalElements(self):
        from collections import defaultdict

        finalmatches = [m for m in self.tourney.matches if m.final]
        results = defaultdict(list)
        order = []

        for match in finalmatches:
            caption = gettext(
                '$comp1 vs. $comp2',
                mapping=dict(comp1=match.competitor1, comp2=match.competitor2),
            )
            if caption not in results:
                order.append(caption)
            results[caption].append('%d/%d' % (match.score1, match.score2))

        for i, caption in enumerate(order):
            if i == 0:
                yield Paragraph(
                    ngettext(
                        'Result of the final for the 1st/2nd place',
                        'Results of the final for the 1st/2nd place',
                        len(results[caption]),
                    ),
                    heading_style,
                )
            else:
                yield Paragraph(
                    ngettext(
                        'Result of the final for the 3rd/4th place',
                        'Results of the final for the 3rd/4th place',
                        len(results[caption]),
                    ),
                    heading_style,
                )
            yield Paragraph(caption, cardname_style)
            yield Paragraph(', '.join(results[caption]), cardinfo_style)
            yield Spacer(0, 0.6 * cm)

    def getRanking(self):
        def player_caption(
            player, html, localized, css_class=None, omit_nickname=False
        ):
            caption = player.caption(
                html=html,
                localized=localized,
                css_class=css_class,
                omit_nickname=omit_nickname,
            )
            if (
                not self.tourney.rating or self.tourney.rating.level != '1'
            ) and player.club:
                caption += ' <font size=6>%s</font>' % player.club
            return caption

        if self.turn is not None:
            ranking = [
                (
                    i,
                    c.caption(player_caption=player_caption),
                    c.nationality,
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
                    c.caption(player_caption=player_caption),
                    c.nationality,
                    c.points,
                    c.bucholz,
                    c.netscore,
                    self.format_prize(c.prize),
                )
                for i, c in enumerate(self.tourney.ranking, 1)
            ]

        return ranking

    def getElements(self) -> Generator:
        yield from super().getElements()

        ranking = self.getRanking()
        if self.turn is None:
            if self.tourney.finals and self.tourney.prized:
                yield from self.getFinalElements()

        if not ranking:  # pragma: no cover
            return

        if ranking:
            pivot = ranking[0][2]
            is_intl = not all(pivot == r[2] for r in ranking)
        else:
            is_intl = False

        if self.tourney.championship.playersperteam > 1:
            caption = gettext('Team')
        else:
            caption = gettext('Player')

        rows: list[tuple]

        if self.tourney.prized and self.turn is None:
            if self.tourney.system == 'knockout':
                npointcols = 1
                rows = [
                    ('#', '', caption, gettext('Pts'))
                    if is_intl
                    else ('#', caption, gettext('Pts'))
                ]
                rows.extend(
                    (rank, country, Paragraph(description, normal_style), points)
                    if is_intl
                    else (rank, Paragraph(description, normal_style), points)
                    for (
                        rank,
                        description,
                        country,
                        points,
                        bucholz,
                        netscore,
                        prize,
                    ) in ranking
                )
                desc_width = (
                    self.doc.width
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 3
                )
                if is_intl:
                    widths = (rank_width, country_width, desc_width, scores_width)
                else:
                    widths = (rank_width, desc_width, scores_width)
            elif self.tourney.system == 'roundrobin':
                npointcols = 3
                rows = [
                    ('#', '', caption, gettext('Pts'), gettext('Net'), gettext('Prz'))
                    if is_intl
                    else ('#', caption, gettext('Pts'), gettext('Net'), gettext('Prz'))
                ]
                rows.extend(
                    (
                        rank,
                        country,
                        Paragraph(description, normal_style),
                        points,
                        netscore,
                        prize,
                    )
                    if is_intl
                    else (
                        rank,
                        Paragraph(description, normal_style),
                        points,
                        netscore,
                        prize,
                    )
                    for (
                        rank,
                        description,
                        country,
                        points,
                        bucholz,
                        netscore,
                        prize,
                    ) in ranking
                )
                desc_width = (
                    self.doc.width
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 2
                    - prizes_width
                )
                widths = (
                    (
                        rank_width,
                        country_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        prizes_width,
                    )
                    if is_intl
                    else (
                        rank_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        prizes_width,
                    )
                )
            elif self.tourney.championship.prizes == 'asis':
                npointcols = 3
                rows = [
                    ('#', '', caption, gettext('Pts'), gettext('Bch'), gettext('Net'))
                    if is_intl
                    else ('#', caption, gettext('Pts'), gettext('Bch'), gettext('Net'))
                ]
                rows.extend(
                    (
                        rank,
                        country,
                        Paragraph(description, normal_style),
                        points,
                        bucholz,
                        netscore,
                    )
                    if is_intl
                    else (
                        rank,
                        Paragraph(description, normal_style),
                        points,
                        bucholz,
                        netscore,
                    )
                    for (
                        rank,
                        description,
                        country,
                        points,
                        bucholz,
                        netscore,
                        prize,
                    ) in ranking
                )
                desc_width = (
                    self.doc.width
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 3
                )
                widths = (
                    (
                        rank_width,
                        country_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                    )
                    if is_intl
                    else (
                        rank_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                    )
                )
            else:
                npointcols = 4
                rows = [
                    (
                        '#',
                        '',
                        caption,
                        gettext('Pts'),
                        gettext('Bch'),
                        gettext('Net'),
                        gettext('Prz'),
                    )
                    if is_intl
                    else (
                        '#',
                        caption,
                        gettext('Pts'),
                        gettext('Bch'),
                        gettext('Net'),
                        gettext('Prz'),
                    )
                ]
                rows.extend(
                    (
                        rank,
                        country,
                        Paragraph(description, normal_style),
                        points,
                        bucholz,
                        netscore,
                        prize,
                    )
                    if is_intl
                    else (
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
                        country,
                        points,
                        bucholz,
                        netscore,
                        prize,
                    ) in ranking
                )
                desc_width = (
                    self.doc.width
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 3
                    - prizes_width
                )
                widths = (
                    (
                        rank_width,
                        country_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                        prizes_width,
                    )
                    if is_intl
                    else (
                        rank_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                        prizes_width,
                    )
                )

            if is_intl:
                country_align = [('ALIGN', (1, 1), (1, -1), 'CENTER')]
            else:
                country_align = []

            yield Table(
                rows,
                widths,
                style=TableStyle(
                    [
                        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                        ('ALIGN', (-npointcols, 0), (-1, -1), 'RIGHT'),
                    ]
                    + country_align
                    + [
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                        ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                        ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                        ('SIZE', (0, 1), (0, -1), normal_style.fontSize),
                        ('LEADING', (0, 1), (0, -1), normal_style.leading),
                        ('SIZE', (-npointcols, 1), (-1, -1), normal_style.fontSize),
                        ('LEADING', (-npointcols, 1), (-1, -1), normal_style.leading),
                        ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                    ]
                ),
            )
        else:
            if self.tourney.system == 'knockout':
                rows = [
                    ('#', '', caption, gettext('Pts'))
                    if is_intl
                    else ('#', caption, gettext('Pts'))
                ]
                rows.extend(
                    [
                        (rank, country, Paragraph(description, normal_style), points)
                        if is_intl
                        else (rank, Paragraph(description, normal_style), points)
                        for (
                            rank,
                            description,
                            country,
                            points,
                            bucholz,
                            netscore,
                            prize,
                        ) in ranking
                    ]
                )
                desc_width = (
                    self.doc.width / self.columns * 0.9
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 3
                )
                if is_intl:
                    widths = (rank_width, country_width, desc_width, scores_width)
                else:
                    widths = (rank_width, desc_width, scores_width)
                if is_intl:
                    country_align = [('ALIGN', (1, 1), (1, -1), 'CENTER')]
                else:
                    country_align = []
                yield Table(
                    rows,
                    widths,
                    style=TableStyle(
                        [
                            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                        ]
                        + country_align
                        + [
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                            ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                            ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                            ('SIZE', (0, 1), (0, -1), normal_style.fontSize),
                            ('LEADING', (0, 1), (0, -1), normal_style.leading),
                            ('SIZE', (-3, 1), (-1, -1), normal_style.fontSize),
                            ('LEADING', (-3, 1), (-1, -1), normal_style.leading),
                            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                        ]
                    ),
                )
            elif self.tourney.system == 'roundrobin':
                rows = [
                    ('#', '', caption, gettext('Pts'), gettext('Net'))
                    if is_intl
                    else ('#', caption, gettext('Pts'), gettext('Net'))
                ]
                rows.extend(
                    [
                        (
                            rank,
                            country,
                            Paragraph(description, normal_style),
                            points,
                            netscore,
                        )
                        if is_intl
                        else (
                            rank,
                            Paragraph(description, normal_style),
                            points,
                            netscore,
                        )
                        for (
                            rank,
                            description,
                            country,
                            points,
                            bucholz,
                            netscore,
                            prize,
                        ) in ranking
                    ]
                )
                desc_width = (
                    self.doc.width / self.columns * 0.9
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 2
                )
                widths = (
                    (rank_width, country_width, desc_width, scores_width, scores_width)
                    if is_intl
                    else (rank_width, desc_width, scores_width, scores_width)
                )
                if is_intl:
                    country_align = [('ALIGN', (1, 1), (1, -1), 'CENTER')]
                else:
                    country_align = []
                yield Table(
                    rows,
                    widths,
                    style=TableStyle(
                        [
                            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                            ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
                        ]
                        + country_align
                        + [
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                            ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                            ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                            ('SIZE', (0, 1), (0, -1), normal_style.fontSize),
                            ('LEADING', (0, 1), (0, -1), normal_style.leading),
                            ('SIZE', (-3, 1), (-1, -1), normal_style.fontSize),
                            ('LEADING', (-3, 1), (-1, -1), normal_style.leading),
                            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                        ]
                    ),
                )
            else:
                rows = [
                    ('#', '', caption, gettext('Pts'), gettext('Bch'), gettext('Net'))
                    if is_intl
                    else ('#', caption, gettext('Pts'), gettext('Bch'), gettext('Net'))
                ]
                rows.extend(
                    [
                        (
                            rank,
                            country,
                            Paragraph(description, normal_style),
                            points,
                            bucholz,
                            netscore,
                        )
                        if is_intl
                        else (
                            rank,
                            Paragraph(description, normal_style),
                            points,
                            bucholz,
                            netscore,
                        )
                        for (
                            rank,
                            description,
                            country,
                            points,
                            bucholz,
                            netscore,
                            prize,
                        ) in ranking
                    ]
                )
                desc_width = (
                    self.doc.width / self.columns * 0.9
                    - rank_width
                    - (country_width if is_intl else 0)
                    - scores_width * 3
                )
                widths = (
                    (
                        rank_width,
                        country_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                    )
                    if is_intl
                    else (
                        rank_width,
                        desc_width,
                        scores_width,
                        scores_width,
                        scores_width,
                    )
                )
                if is_intl:
                    country_align = [('ALIGN', (1, 1), (1, -1), 'CENTER')]
                else:
                    country_align = []
                yield Table(
                    rows,
                    widths,
                    style=TableStyle(
                        [
                            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                            ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
                        ]
                        + country_align
                        + [
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('FONT', (0, 0), (-1, 0), caption_style.fontName),
                            ('SIZE', (0, 0), (-1, 0), caption_style.fontSize),
                            ('LEADING', (0, 0), (-1, 0), caption_style.leading),
                            ('SIZE', (0, 1), (0, -1), normal_style.fontSize),
                            ('LEADING', (0, 1), (0, -1), normal_style.leading),
                            ('SIZE', (-3, 1), (-1, -1), normal_style.fontSize),
                            ('LEADING', (-3, 1), (-1, -1), normal_style.leading),
                            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
                        ]
                    ),
                )


class TourneyUnderRankingPrintout(TourneyRankingPrintout):
    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        args = super().getArgumentsFromRequest(session, request)
        kw = request.params
        if 'age' in kw:
            try:
                args.append(int(kw['age']))
            except ValueError:
                raise InvalidUserArgument(
                    _('Invalid age: $age', mapping=dict(age=repr(kw['age'])))
                )
        return args

    def __init__(self, output, locale, tourney, turn=None, age=18):
        super().__init__(output, locale, tourney, turn)
        self.age = age

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Under %d ranking after %s round') % (
                self.age,
                ordinal(self.turn),
            )
        else:
            if self.tourney.prized:
                return gettext('Final under %d ranking') % self.age
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Under %d ranking after %s round') % (
                        self.age,
                        ordinal(rt),
                    )
                else:
                    return gettext('Initial under %d ranking') % self.age

    def computePlayerAge(self, player):
        td = self.tourney.date
        pd = player.birthdate
        return td.year - pd.year - ((td.month, td.day) < (pd.month, pd.day))

    def isPlayerAgeRight(self, player):
        return self.computePlayerAge(player) <= self.age

    def getRanking(self):
        def player_caption(
            player, html, localized, css_class=None, omit_nickname=False
        ):
            caption = player.caption(
                html=html,
                localized=localized,
                css_class=css_class,
                omit_nickname=omit_nickname,
            )
            if player.club:
                caption += '<font size=6> %s</font>' % player.club
            return caption

        if self.turn is not None:
            ranking = [
                (
                    i,
                    c.caption(player_caption=player_caption),
                    c.nationality,
                    r.points,
                    r.bucholz,
                    r.netscore,
                    0,
                )
                for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)
                if c.player1.birthdate is not None
                and self.isPlayerAgeRight(c.player1)
            ]
        else:
            ranking = [
                (
                    i,
                    c.caption(player_caption=player_caption),
                    c.nationality,
                    c.points,
                    c.bucholz,
                    c.netscore,
                    self.format_prize(c.prize),
                )
                for i, c in enumerate(self.tourney.ranking, 1)
                if c.player1.birthdate is not None
                and self.isPlayerAgeRight(c.player1)
            ]

        return ranking


class TourneyOverRankingPrintout(TourneyUnderRankingPrintout):
    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Over %d ranking after %s round') % (
                self.age,
                ordinal(self.turn),
            )
        else:
            if self.tourney.prized:
                return gettext('Final over %d ranking') % self.age
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Over %d ranking after %s round') % (
                        self.age,
                        ordinal(rt),
                    )
                else:
                    return gettext('Initial over %d ranking') % self.age

    def isPlayerAgeRight(self, player):
        return self.computePlayerAge(player) >= self.age


class TourneyWomenRankingPrintout(TourneyRankingPrintout):
    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Women ranking after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final women ranking')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Women ranking after %s round') % ordinal(rt)
                else:
                    return gettext('Initial women ranking')

    def getRanking(self):
        def player_caption(
            player, html, localized, css_class=None, omit_nickname=False
        ):
            caption = player.caption(
                html=html,
                localized=localized,
                css_class=css_class,
                omit_nickname=omit_nickname,
            )
            if player.club:
                caption += '<font size=6> %s</font>' % player.club
            return caption

        if self.turn is not None:
            ranking = [
                (
                    i,
                    c.caption(player_caption=player_caption),
                    c.nationality,
                    r.points,
                    r.bucholz,
                    r.netscore,
                    0,
                )
                for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)
                if c.player1.sex == 'F'
            ]
        else:
            ranking = [
                (
                    i,
                    c.caption(player_caption=player_caption),
                    c.nationality,
                    c.points,
                    c.bucholz,
                    c.netscore,
                    self.format_prize(c.prize),
                )
                for i, c in enumerate(self.tourney.ranking, 1)
                if c.player1.sex == 'F'
            ]

        return ranking
