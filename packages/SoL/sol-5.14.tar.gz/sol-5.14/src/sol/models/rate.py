# -*- coding: utf-8 -*-
# :Project:   SoL -- The PlayerRating entity
# :Created:   ven 06 dic 2013 19:20:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013, 2014, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from datetime import date as dtdate
from decimal import Decimal
from typing import TYPE_CHECKING
from typing import TypedDict

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ..i18n import gettext
from ..i18n import translatable_string as _
from . import Base
from .domains import date_t
from .domains import int_t
from .domains import intid_t
from .domains import volatility_t

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .player import Player
    from .rating import Rating


logger = logging.getLogger(__name__)


class SerializedRate(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Rate`."

    rating: int
    player: int
    date: dtdate
    rate: int
    deviation: int
    volatility: str


class Rate(Base):
    """The Glicko rating of a player."""

    __tablename__ = 'rates'
    'Related table'

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index(
                '%s_uk' % cls.__tablename__, 'idrating', 'idplayer', 'date', unique=True
            ),
        )

    ## Columns

    idrate: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idrate', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Player rate ID'),
            hint=_('Unique ID of the player rate.'),
        ),
    )
    """Primary key."""

    idrating: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('ratings.idrating', name='fk_rate_rating'),
        nullable=False,
        info=dict(
            label=_('Rating ID'),
            hint=_('ID of the related rating.'),
        ),
    )
    """Related rating's ID."""

    idplayer: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_rate_player'),
        nullable=False,
        info=dict(
            label=_('Player ID'),
            hint=_('ID of the related player.'),
        ),
    )
    """Related :py:class:`player <.Player>` ID."""

    date: Mapped[dtdate] = mapped_column(
        date_t,
        nullable=False,
        info=dict(
            label=_('Date'),
            hint=_('Date of the rating.'),
        ),
    )
    """Rating date."""

    rate: Mapped[int] = mapped_column(
        int_t,
        nullable=False,
        info=dict(
            label=_('Rate'),
            hint=_('The value of Glicko rate.'),
        ),
    )
    """The value of Glicko rating."""

    deviation: Mapped[int] = mapped_column(
        int_t,
        nullable=False,
        info=dict(
            label=_('Deviation'),
            hint=_('The value of Glicko deviation.'),
        ),
    )
    """The value of Glicko deviation."""

    volatility: Mapped[Decimal] = mapped_column(
        volatility_t,
        nullable=False,
        info=dict(
            label=_('Volatility'),
            hint=_('The value of the Glicko volatility.'),
        ),
    )

    ## Relations

    player: Mapped[Player] = relationship('Player')
    """The related :py:class:`player <.Player>`."""

    rating: Mapped[Rating] = relationship('Rating', back_populates='rates')
    """The related :py:class:`rating <.Rating>`."""

    def __repr__(self):
        r = super().__repr__()
        r = r[:-1] + ': r=%s d=%s v=%s>' % (self.rate, self.deviation, self.volatility)
        return r

    def caption(self, html=None, localized=True):
        "A description of the rate."

        format = _('$player in $rating on $date')
        return gettext(
            format,
            just_subst=not localized,
            mapping=dict(
                player=self.player.caption(html, localized),
                rating=self.rating.caption(html, localized),
                date=self.date.strftime(gettext('%m-%d-%Y')),
            ),
        )

    def update(self, data, user_id, *, missing_only=False):
        if 'volatility' in data:
            data['volatility'] = Decimal(data['volatility'])
        return super().update(data, user_id, missing_only=missing_only)

    def serialize(self, serializer: Serializer) -> SerializedRate:
        """Reduce a single rate to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this rate
        """

        simple: SerializedRate = {
            'rating': serializer.addRating(self.rating),
            'player': serializer.addPlayer(self.player),
            'date': self.date,
            'rate': self.rate,
            'deviation': self.deviation,
            'volatility': str(self.volatility),
        }

        return simple
