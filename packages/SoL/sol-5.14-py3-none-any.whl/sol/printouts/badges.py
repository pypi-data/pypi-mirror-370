# -*- coding: utf-8 -*-
# :Project:   SoL -- Personal badges printout
# :Created:   lun 13 giu 2016 11:57:56 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018-2020, 2022-2025 Lele Gaifax
#

from __future__ import annotations

from importlib.metadata import metadata

from babel.numbers import format_decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from sqlalchemy.exc import NoResultFound

from ..i18n import country_name
from ..i18n import gettext
from ..i18n import translatable_string as _
from ..models import Tourney
from ..models.errors import InvalidUserArgument
from . import badgename_style
from . import cardinfo_style
from . import cardname_style
from . import cardsmall_style
from . import cardtitle_style
from . import subtitle_style
from .utils import reduce_fontsize_to_fit_width


class BadgesPrintout:
    "Personal badges."

    emblems = '.'
    height = 5.4 * cm
    width = 8.5 * cm
    bottom_margin = 1 * cm
    left_margin = 2 * cm

    @classmethod
    def getArgumentsFromRequest(cls, session, request):
        id = request.matchdict['id']
        try:
            idtourney = int(id)
        except ValueError:
            try:
                entity = session.query(Tourney).filter_by(guid=id).one()
            except NoResultFound:
                raise InvalidUserArgument(
                    _('No tourney with guid $id', mapping=dict(id=id))
                )
        else:
            entity = session.get(Tourney, idtourney)
            if entity is None:
                raise InvalidUserArgument(
                    _('No tourney with id $id', mapping=dict(id=str(idtourney)))
                )
        if 'blank' in request.params:
            try:
                blank = int(request.params['blank'])
            except ValueError:
                blank = 10
        else:
            blank = alt_c = alt_d = alt_t = None
        alt_c = request.params.get('alt_championship')
        alt_d = request.params.get('alt_date')
        alt_t = request.params.get('alt_tourney')
        return [request.locale_name, entity, blank, alt_c, alt_d, alt_t]

    def __init__(self, output, locale, tourney, blank, alt_cship, alt_date, alt_tourney):
        self.output = output
        self.locale = locale
        self.tourney = tourney
        self.blank = blank
        self.alt_championship = alt_cship
        self.alt_date = alt_date
        self.alt_tourney = alt_tourney

    @property
    def cache_max_age(self):
        "Cache for one year prized tourneys, no cache otherwise."

        if self.blank or self.tourney.prized:
            return 60 * 60 * 24 * 365
        else:
            return 0

    def format_prize(self, prize):
        if self.blank is None:
            if self.tourney.championship.prizes != 'centesimal':
                return format_decimal(prize, '###0', self.locale)
            else:
                return format_decimal(prize, '###0.00', self.locale)
        else:
            return ''

    def getPlayers(self):
        if self.blank is None:
            if self.tourney.prized:
                competitors = self.tourney.ranking
            else:
                competitors = self.tourney.competitors
            for r, c in enumerate(competitors, start=1):
                for p in (c.player1, c.player2, c.player3, c.player4):
                    if p:
                        yield c, p, r
        else:
            for r in range(self.blank):
                yield None, None, r

    def execute(self, request):
        self.request = request
        canvas = self.canvas = Canvas(self.output)
        canvas.setAuthor('SoL %s' % metadata('sol')['Version'])
        canvas.setSubject(self.__class__.__name__)
        canvas.setTitle(gettext('Badges'))

        players = self.getPlayers()
        while self.drawOnePage(players):
            canvas.showPage()

        canvas.save()

    def drawOnePage(self, players):
        canvas = self.canvas
        try:
            c, p, r = next(players)
        except StopIteration:
            return False
        first = True

        line = canvas.line
        for i in range(0, 6):
            y = self.bottom_margin + i * self.height
            line(5, y, 20, y)
            line(A4[0] - 5, y, A4[0] - 20, y)

        for i in range(0, 3):
            x = self.left_margin + i * self.width
            line(x, 5, x, 20)
            line(x, A4[1] - 5, x, A4[1] - 20)

        canvas.translate(self.left_margin, self.bottom_margin)
        for i in range(5):
            if not first:
                try:
                    c, p, r = next(players)
                except StopIteration:
                    return False
            else:
                first = False

            self.drawLeftSide(c, p, r)
            canvas.saveState()
            canvas.translate(self.width, 0)
            if self.blank is None and self.tourney.prized:
                self.drawRightSide(c, p, r)
            else:
                try:
                    c, p, r = next(players)
                except StopIteration:
                    canvas.restoreState()
                    return False
                self.drawLeftSide(c, p, r)
            canvas.restoreState()
            canvas.translate(0, self.height)
        return True

    def drawLeftSide(self, competitor, player, rank):
        from os.path import exists
        from os.path import join

        canvas = self.canvas
        max_text_width = self.width
        center = self.width / 2
        image_width = 0

        if self.tourney.championship.club.emblem:
            image = join(self.emblems, self.tourney.championship.club.emblem)
            if exists(image):
                image_width = self.width / 5 * 2
                canvas.drawImage(
                    image, 0, 0, image_width, self.height, preserveAspectRatio=True
                )
                max_text_width -= image_width
                center = image_width + max_text_width / 2

        c_value = self.alt_championship or self.tourney.championship.description
        d_value = self.alt_date or self.tourney.date.strftime(gettext('%m-%d-%Y'))
        t_value = self.alt_tourney or self.tourney.description

        style = reduce_fontsize_to_fit_width(c_value, max_text_width, cardtitle_style)[0]
        canvas.setFont(style.fontName, style.fontSize, style.leading)
        canvas.drawCentredString(center, self.height - 0.8 * cm, c_value)

        style = cardinfo_style
        canvas.setFont(style.fontName, style.fontSize, style.leading)
        canvas.drawCentredString(center, self.height - 1.4 * cm, d_value)

        style = reduce_fontsize_to_fit_width(t_value, max_text_width, cardinfo_style)[0]
        canvas.setFont(style.fontName, style.fontSize, style.leading)
        canvas.drawCentredString(center, self.height - 2 * cm, t_value)

        if self.blank is None:
            if self.tourney.prized:
                style = subtitle_style
                canvas.setFont(style.fontName, style.fontSize, style.leading)
                canvas.drawCentredString(center, self.height - 2.8 * cm, str(rank))

                style = cardname_style
                canvas.setFont(style.fontName, style.fontSize, style.leading)
                if self.tourney.championship.prizes == 'asis':
                    rx = image_width + 1.6 * cm
                    canvas.drawRightString(rx, self.height - 4.1 * cm, gettext('Points:'))
                    canvas.drawRightString(
                        rx + 0.8 * cm, self.height - 4.1 * cm, str(competitor.points)
                    )
                    canvas.setFont(style.fontName, style.fontSize - 2, style.leading)
                    rx = center + 1.7 * cm
                    canvas.drawRightString(rx, self.height - 3.9 * cm, gettext('Bucholz:'))
                    canvas.drawRightString(
                        rx + 0.6 * cm, self.height - 3.9 * cm, str(competitor.bucholz)
                    )
                    canvas.drawRightString(
                        rx, self.height - 4.2 * cm, gettext('Net score:')
                    )
                    canvas.drawRightString(
                        rx + 0.6 * cm, self.height - 4.2 * cm, str(competitor.netscore)
                    )
                else:
                    rx = image_width + 1.6 * cm
                    canvas.drawRightString(rx, self.height - 4.2 * cm, gettext('Bounty:'))
                    canvas.drawRightString(
                        rx + 1 * cm, self.height - 4.2 * cm, str(competitor.prize)
                    )
                    canvas.setFont(style.fontName, style.fontSize - 2, style.leading)
                    rx = center + 1.7 * cm
                    canvas.drawRightString(rx, self.height - 3.9 * cm, gettext('Points:'))
                    canvas.drawRightString(
                        rx + 0.6 * cm, self.height - 3.9 * cm, str(competitor.points)
                    )
                    canvas.drawRightString(rx, self.height - 4.2 * cm, gettext('Bucholz:'))
                    canvas.drawRightString(
                        rx + 0.6 * cm, self.height - 4.2 * cm, str(competitor.bucholz)
                    )
                    canvas.drawRightString(
                        rx, self.height - 4.5 * cm, gettext('Net score:')
                    )
                    canvas.drawRightString(
                        rx + 0.6 * cm, self.height - 4.5 * cm, str(competitor.netscore)
                    )

            caption = player.caption(html=False)
            style = reduce_fontsize_to_fit_width(caption, max_text_width, badgename_style)[
                0
            ]
            canvas.setFont(style.fontName, style.fontSize, style.leading)
            canvas.drawCentredString(center, self.height - 3.5 * cm, caption)

            style = cardname_style
            canvas.setFont(style.fontName, style.fontSize, style.leading)

            if competitor.player1Nationality:
                country = country_name(competitor.player1Nationality)
                flag = join(self.flags, competitor.player1Nationality + '.png')
                if exists(flag):
                    canvas.drawRightString(
                        center - 0.1 * cm, self.height - 5.2 * cm, country
                    )
                    canvas.drawImage(flag, center + 0.1 * cm, self.height - 5.3 * cm)
                else:  # pragma: nocover
                    canvas.drawCentredString(center, self.height - 5.1 * cm, country)

    def drawRightSide(self, competitor, player, rank):
        canvas = self.canvas

        def e(string, length):
            if canvas.stringWidth(string) > length:
                length -= canvas.stringWidth('…')
                while canvas.stringWidth(string) > length:
                    string = string[:-1]
                string += '…'
            return string

        canvas.setFont(
            cardsmall_style.fontName, cardsmall_style.fontSize, cardsmall_style.leading
        )

        canvas.drawCentredString(1.8 * cm, self.height - 1 * cm, gettext('You met…'))
        canvas.drawString(0.2 * cm, self.height - 1.25 * cm, gettext('Opponent'))

        # TRANSLATORS: this is the "score of this player" in the badge
        your = gettext('your')
        canvas.drawRightString(2.9 * cm, self.height - 1.25 * cm, your)

        # TRANSLATORS: this is the "opponent score" in the badge
        his = gettext('his')
        canvas.drawRightString(3.3 * cm, self.height - 1.25 * cm, his)

        pmatches = [
            m
            for m in self.tourney.matches
            if m.idcompetitor1 == competitor.idcompetitor
            or m.idcompetitor2 == competitor.idcompetitor
        ]
        for i, m in enumerate(pmatches):
            if m.idcompetitor1 == competitor.idcompetitor:
                other = m.competitor2
                myscore = m.score1
                otherscore = m.score2
            elif m.idcompetitor2 == competitor.idcompetitor:
                other = m.competitor1
                myscore = m.score2
                otherscore = m.score1
            else:  # pragma: nocover
                continue
            h = self.height - 1.6 * cm - i * 0.3 * cm
            canvas.drawString(
                0.2 * cm,
                h,
                e(other.caption(html=False), 2.3 * cm) if other else gettext('Phantom'),
            )
            canvas.drawRightString(2.9 * cm, h, str(myscore))
            canvas.drawRightString(3.3 * cm, h, str(otherscore))

        canvas.drawCentredString(
            6.0 * cm, self.height - 1 * cm, gettext('Final ranking')
        )
        canvas.drawString(3.7 * cm, self.height - 1.25 * cm, gettext('Competitor'))
        if self.tourney.championship.prizes == 'asis':
            # TRANSLATORS: this is the points in the badge
            pts = gettext('pts')
            canvas.drawRightString(7.3 * cm, self.height - 1.25 * cm, pts)
            # TRANSLATORS: this is the bucholz in the badge
            bch = gettext('bch')
            canvas.drawRightString(7.8 * cm, self.height - 1.25 * cm, bch)
            # TRANSLATORS: this is the net score in the badge
            net = gettext('net')
            canvas.drawRightString(8.4 * cm, self.height - 1.25 * cm, net)

            for i, ctor in enumerate(self.tourney.ranking):
                if i > 15:  # pragma: nocover
                    break
                h = self.height - 1.6 * cm - i * 0.22 * cm
                canvas.drawRightString(3.8 * cm, h, str(i + 1))
                canvas.drawString(3.9 * cm, h, e(ctor.caption(html=False), 3 * cm))
                canvas.drawRightString(7.3 * cm, h, str(ctor.points))
                canvas.drawRightString(7.8 * cm, h, str(ctor.bucholz))
                canvas.drawRightString(8.4 * cm, h, str(ctor.netscore))
        else:
            # TRANSLATORS: this is the points in the badge
            pts = gettext('pts')
            canvas.drawRightString(6.7 * cm, self.height - 1.25 * cm, pts)
            # TRANSLATORS: this is the bucholz in the badge
            bch = gettext('bch')
            canvas.drawRightString(7.2 * cm, self.height - 1.25 * cm, bch)
            # TRANSLATORS: this is the net score in the badge
            net = gettext('net')
            canvas.drawRightString(7.7 * cm, self.height - 1.25 * cm, net)
            # TRANSLATORS: this is the prize in the badge
            prz = gettext('prz')
            canvas.drawRightString(8.5 * cm, self.height - 1.25 * cm, prz)

            for i, ctor in enumerate(self.tourney.ranking):
                if i > 15:
                    break
                h = self.height - 1.6 * cm - i * 0.22 * cm
                canvas.drawRightString(3.7 * cm, h, str(i + 1))
                canvas.drawString(3.8 * cm, h, e(ctor.caption(html=False), 2.6 * cm))
                canvas.drawRightString(6.7 * cm, h, str(ctor.points))
                canvas.drawRightString(7.2 * cm, h, str(ctor.bucholz))
                canvas.drawRightString(7.7 * cm, h, str(ctor.netscore))
                canvas.drawRightString(8.5 * cm, h, self.format_prize(ctor.prize))
