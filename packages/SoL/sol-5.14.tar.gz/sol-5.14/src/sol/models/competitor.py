# -*- coding: utf-8 -*-
# :Project:   SoL -- The Competitor entity
# :Created:   gio 27 nov 2008 13:51:08 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013, 2014, 2016, 2018-2020, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from collections.abc import Callable
from decimal import Decimal
from typing import ClassVar
from typing import TYPE_CHECKING
from typing import TypedDict

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import gettext
from ..i18n import translatable_string as _
from . import Base
from .domains import boolean_t
from .domains import intid_t
from .domains import prize_t
from .domains import smallint_t

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .player import Player
    from .tourney import Tourney


logger = logging.getLogger(__name__)


class SerializedCompetitor(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Competitor`."

    players: list[int]
    points: int
    netscore: int
    totscore: int
    bucholz: int
    prize: NotRequired[str]
    retired: NotRequired[bool]


def _knockout_dict_sorter(d: dict) -> tuple[Decimal | int | float, ...]:
    return d['prize'], d['points'], -d['position'], d.get('rate', 0)


def _knockout_comp_sorter(c: Competitor) -> tuple[Decimal | int | float, ...]:
    return c.prize, c.points, -c.position, c.rate or 0


def _roundrobin_dict_sorter(d: dict) -> tuple[Decimal | int | float, ...]:
    return (
        d['prize'],
        d['points'],
        d['netscore'],
        d['totscore'],
        -d['position'],
        d.get('rate', 0),
    )


def _roundrobin_comp_sorter(c: Competitor) -> tuple[Decimal | int | float, ...]:
    return c.prize, c.points, c.netscore, c.totscore, -c.position, c.rate or 0


def _swiss_dict_sorter(d: dict) -> tuple[Decimal | int | float, ...]:
    return (
        d['prize'],
        d['points'],
        d['bucholz'],
        d['netscore'],
        d['totscore'],
        -d['position'],
        d.get('rate', 0),
    )


def _swiss_comp_sorter(c: Competitor) -> tuple[Decimal | int | float, ...]:
    return (
        c.prize,
        c.points,
        c.bucholz,
        c.netscore,
        c.totscore,
        -c.position,
        c.rate or 0,
    )


competitors_sorters: dict[
    tuple[str, str], Callable[[Competitor | dict], tuple[Decimal | int | float, ...]]
] = {
    ('knockout', 'comp'): _knockout_comp_sorter,
    ('knockout', 'dict'): _knockout_dict_sorter,
    ('roundrobin', 'comp'): _roundrobin_comp_sorter,
    ('roundrobin', 'dict'): _roundrobin_dict_sorter,
    ('swiss', 'comp'): _swiss_comp_sorter,
    ('swiss', 'dict'): _swiss_dict_sorter,
}


class Competitor(Base):
    """A single competitor in a game.

    A competitor may be a single person or a team of up to four
    players, that participate to a given tourney. On each competitor
    this table keeps the `points`, the `netscore` and his `bucholz`,
    as well as the final `prize`. To disambiguate the ranking it
    maintains also a `totscore`, the total number of pocketed
    carrommen summing up competitor' scores in all played games.
    """

    __tablename__ = 'competitors'
    'Related table'

    # Cache for the competitor's rate
    _rate: ClassVar[int | None]

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index('%s_uk_1' % cls.__tablename__, 'idplayer1', 'idtourney', unique=True),
            Index('%s_uk_2' % cls.__tablename__, 'idplayer2', 'idtourney', unique=True),
            Index('%s_uk_3' % cls.__tablename__, 'idplayer3', 'idtourney', unique=True),
            Index('%s_uk_4' % cls.__tablename__, 'idplayer4', 'idtourney', unique=True),
        )

    ## Columns

    idcompetitor: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idcompetitor', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Competitor ID'),
            hint=_('Unique ID of the competitor.'),
        ),
    )
    """Primary key."""

    idtourney: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('tourneys.idtourney', name='fk_competitor_tourney'),
        nullable=False,
        info=dict(
            label=_('Tourney ID'),
            hint=_('ID of the tourney the competitor belongs to.'),
        ),
    )
    """Subscribed :py:class:`tourney <.Tourney>`'s ID."""

    idplayer1: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_competitor_player1'),
        nullable=False,
        info=dict(
            label=_('Player ID'),
            hint=_('ID of the player.'),
        ),
    )
    """First :py:class:`player <.Player>`'s ID."""

    idplayer2: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_competitor_player2'),
        nullable=True,
        info=dict(
            label=_('2nd player ID'),
            hint=_('ID of the second player.'),
        ),
    )
    """Second :py:class:`player <.Player>`'s ID."""

    idplayer3: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_competitor_player3'),
        nullable=True,
        info=dict(
            label=_('3rd player ID'),
            hint=_('ID of the third player.'),
        ),
    )
    """Third :py:class:`player <.Player>`'s ID."""

    idplayer4: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_competitor_player4'),
        nullable=True,
        info=dict(
            label=_('4th player ID'),
            hint=_('ID of the fourth player.'),
        ),
    )
    """Fourth :py:class:`player <.Player>`'s ID."""

    points: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Points'),
            hint=_('Points of the competitor.'),
        ),
    )
    """Points (number of wins * 2 + number of draws)."""

    bucholz: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Bucholz'),
            hint=_('Weight of the opponents.'),
        ),
    )
    """*Weight* of the opponents (sum of opponents' points and netscore)."""

    netscore: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Net score'),
            hint=_('Net score of all games.'),
        ),
    )
    """Net score (sum of carrommen difference in each match)."""

    totscore: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Total score'),
            hint=_('Total score of all games.'),
        ),
    )
    """Total score (sum of carrommen in each match)."""

    prize: Mapped[Decimal] = mapped_column(
        prize_t,
        nullable=False,
        default=0.0,
        info=dict(
            label=_('Final prize'),
            hint=_('Final prize assigned at end of tourney.'),
        ),
    )
    """Final prize."""

    retired: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Withdrawn'),
            hint=_('Whether this competitor will play further matches.'),
        ),
    )
    """A competitor may stop playing in the middle of the tourney."""

    position: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Position'),
            hint=_(
                'Relative position used to order competitors when generating the'
                ' first round, overriding their current rate.'
            ),
        ),
    )
    """The relative position of this competitor, used to generate the first round in knockout
    tournaments, overriding their current rate."""

    ## Relations

    player1: Mapped[Player] = relationship(
        'Player', primaryjoin='Player.idplayer==Competitor.idplayer1', lazy='joined'
    )
    """First :py:class:`player <.Player>`."""

    player2: Mapped[Player | None] = relationship(
        'Player', primaryjoin='Player.idplayer==Competitor.idplayer2', lazy='joined'
    )
    """Second :py:class:`player <.Player>`."""

    player3: Mapped[Player | None] = relationship(
        'Player', primaryjoin='Player.idplayer==Competitor.idplayer3', lazy='joined'
    )
    """Third :py:class:`player <.Player>`."""

    player4: Mapped[Player | None] = relationship(
        'Player', primaryjoin='Player.idplayer==Competitor.idplayer4', lazy='joined'
    )
    """Fourth :py:class:`player <.Player>`."""

    tourney: Mapped[Tourney] = relationship('Tourney', back_populates='competitors')

    ## Methods

    def __repr__(self):  # pragma: no cover
        r = super().__repr__()
        r = r[:-1] + ' of t%s: p=%s b=%s ns=%s>' % (
            repr(self.tourney)[2:-1],
            self.points,
            self.bucholz,
            self.netscore,
        )
        if self.position:
            r = r[:-1] + ' position=%d>' % self.position
        if self.idtourney and self.rate:
            r = r[:-1] + ' rate=%d>' % self.rate
        return r

    def caption(
        self,
        html=None,
        localized=True,
        player_caption=None,
        css_class=None,
        nationality=False,
        omit_nicknames=False,
    ):
        "A description of the competitor, made up with the name of each player."

        from .utils import njoin

        ignore_privacy = not self.tourney.prized if self.tourney else False

        if player_caption is None:

            def player_caption(player, h, l, cc, on):
                return player.caption(
                    html=h,
                    localized=l,
                    css_class=cc,
                    ignore_privacy=ignore_privacy,
                    omit_nickname=on,
                )

        if self.player1 is None:
            return gettext('Player NOT assigned yet!', just_subst=not localized)
        else:
            captions = [
                player_caption(self.player1, html, localized, css_class, omit_nicknames)
            ]
            if self.player2 is not None:
                captions.append(
                    player_caption(
                        self.player2, html, localized, css_class, omit_nicknames
                    )
                )
            if self.player3 is not None:
                captions.append(
                    player_caption(
                        self.player3, html, localized, css_class, omit_nicknames
                    )
                )
            if self.player4 is not None:
                captions.append(
                    player_caption(
                        self.player4, html, localized, css_class, omit_nicknames
                    )
                )
            caption = njoin(captions, localized=localized)
            if nationality:
                if html is None or html:
                    caption += ' <font size=6>(%s)</font>' % self.player1.nationality
                else:
                    caption += ' (%s)' % self.player1.nationality
            return caption

    description = property(caption)

    @property
    def player1FullName(self):
        "Full name of the first player"
        if self.idplayer1:
            return self.player1.caption(ignore_privacy=not self.tourney.prized)

    @property
    def player1Nationality(self):
        "Nationality of the first player"
        return self.idplayer1 and self.player1.nationality or None

    nationality = player1Nationality

    @property
    def player1Sex(self):
        "Gender of the first player"
        return self.idplayer1 and self.player1.sex or None

    @property
    def player1FirstName(self):
        "First name of the first player"
        return self.idplayer1 and self.player1.firstname or None

    @property
    def player1LastName(self):
        "Last name of the first player"
        return self.idplayer1 and self.player1.lastname or None

    @property
    def player2FullName(self):
        "Full name of the second player"
        if self.idplayer2:
            return self.player2.caption(ignore_privacy=not self.tourney.prized)

    @property
    def player2Nationality(self):
        "Nationality of the second player"
        return self.idplayer2 and self.player2.nationality or None

    @property
    def player3FullName(self):
        "Full name of the third player"
        if self.idplayer3:
            return self.player3.caption(ignore_privacy=not self.tourney.prized)

    @property
    def player3Nationality(self):
        "Nationality of the third player"
        return self.idplayer3 and self.player3.nationality or None

    @property
    def player4FullName(self):
        "Full name of the fourth player"
        if self.idplayer4:
            return self.player4.caption(ignore_privacy=not self.tourney.prized)

    @property
    def player4Nationality(self):
        "Nationality of the fourth player"
        return self.idplayer4 and self.player4.nationality or None

    @property
    def rate(self) -> int | None:
        "Rate of this competitor, summing up all players rates"

        try:
            return self._rate
        except AttributeError:
            pass

        if self.tourney.idrating is None:
            self._rate = None
            return None

        rating = self.tourney.rating
        date = self.tourney.date
        total = 0

        if self.idplayer1:
            rate = rating.getPlayerRating(self.player1, date)
            if rate is not None:
                total = rate.mu

            if self.idplayer2:
                rate = rating.getPlayerRating(self.player2, date)
                if rate is not None:
                    total += rate.mu

                if self.idplayer3:
                    rate = rating.getPlayerRating(self.player3, date)
                    if rate is not None:
                        total += rate.mu

                    if self.idplayer4:
                        rate = rating.getPlayerRating(self.player4, date)
                        if rate is not None:
                            total += rate.mu

        self._rate = total

        return total

    @property
    def rank(self) -> int:
        "The position of this competitor in the tourney's ranking."

        ranking = self.tourney.ranking
        return ranking.index(self) + 1

    def getOpponentsPreceedingTurns(self, turn):
        "List of competitors ID who played against this competitor."

        cid = self.idcompetitor
        oppids = []

        for match in self.tourney.matches:
            if match.turn >= turn:
                break

            if match.idcompetitor1 == cid and match.idcompetitor2:
                oppids.append(match.idcompetitor2)
            elif match.idcompetitor2 == cid:
                oppids.append(match.idcompetitor1)

        return oppids

    def update(self, data, idowner, *, missing_only=False):
        value = data.get('prize', None)
        if isinstance(value, str):
            data['prize'] = Decimal(value)
        return super().update(data, idowner, missing_only=missing_only)

    def serialize(self, serializer: Serializer) -> SerializedCompetitor:
        """Reduce a single competitor to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this competitor
        """

        players: list[int] = []
        if self.idplayer1:
            players.append(serializer.addPlayer(self.player1))
        if self.idplayer2:
            players.append(serializer.addPlayer(self.player2))
        if self.idplayer3:  # pragma: nocover
            players.append(serializer.addPlayer(self.player3))
            if self.idplayer4:  # pragma: nocover
                players.append(serializer.addPlayer(self.player4))
        simple: SerializedCompetitor = {
            'players': players,
            'points': self.points,
            'netscore': self.netscore,
            'totscore': self.totscore,
            'bucholz': self.bucholz,
        }
        if self.prize:
            simple['prize'] = str(self.prize)
        if self.retired:
            simple['retired'] = self.retired

        return simple
