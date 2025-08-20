# -*- coding: utf-8 -*-
# :Project:   SoL -- The Board entity
# :Created:   dom 19 apr 2020, 09:49:47
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
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

from ..i18n import translatable_string as _
from . import Base
from .domains import flag_t
from .domains import intid_t
from .domains import smallint_t

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .match import Match


logger = logging.getLogger(__name__)


class SerializedBoard(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Board`."

    number: int
    coins1: NotRequired[int]
    coins2: NotRequired[int]
    queen: NotRequired[str]


class Board(Base):
    """A single board.

    This table contains the detailed scores of a single match.

    Since entering such details is very time-consuming, historically and usually only the final
    scores of the match are assigned.

    .. note:: In *normal boards* `coinsX` is the number of carrommen of the opponent competitor
              still on the table at the end of the board; `coins1` and `coins2` are thus
              mutually exclusive (ie, one is zero) and the board is won by the competitor with
              a `coins` number greater than zero, with a score equal to that number plus
              possibly the points of the `queen` if pocketed by him.

              In *training boards* `coins1` and `coins2` are actually the *number of misses* of
              the respective competitors, in other words how many unsuccessful shots they made:
              the meaning is reversed, the board is won by the competitor with the lower
              number. The `queen` field has no meaning.
    """

    __tablename__ = 'boards'
    'Related table'

    # Tell SA this class instances carry extra "temporary" fields
    __allow_unmapped__ = True

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index('%s_number' % cls.__tablename__, 'idmatch', 'number', unique=True),
        )

    ## Columns

    idboard: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idboard', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Board ID'),
            hint=_('Unique ID of the board.'),
        ),
    )
    """Primary key."""

    idmatch: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('matches.idmatch', name='fk_board_match'),
        nullable=False,
        info=dict(
            label=_('Match ID'),
            hint=_('ID of the match the board belongs to.'),
        ),
    )
    """Related :py:class:`match <.Match>`'s ID."""

    number: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        info=dict(
            label=_('Board #'),
            hint=_('Progressive number of the board.'),
        ),
    )
    """Progressive number of the board."""

    coins1: Mapped[int | None] = mapped_column(
        smallint_t,
        nullable=True,
        info=dict(
            label=_('Coins 1'),
            hint=_('Coins of the first competitor.'),
            min=0,
        ),
    )
    """Coins of the first :py:class:`competitor <.Competitor>` in this board."""

    coins2: Mapped[int | None] = mapped_column(
        smallint_t,
        nullable=True,
        info=dict(
            label=_('Coins 2'),
            hint=_('Coins of the second competitor.'),
            min=0,
        ),
    )
    """Coins of the second :py:class:`competitor <.Competitor>` in this board."""

    queen: Mapped[str | None] = mapped_column(
        flag_t,
        nullable=True,
        info=dict(
            label=_('Queen'),
            hint=_('Which competitor pocketed the Queen, if any.'),
            dictionary={
                '1': _('First competitor'),
                '2': _('Second competitor'),
            },
        ),
    )
    """Which competitor pocketed the Queen, if any."""

    score1: int | None = None
    """
    The score of this board for the first :py:class:`competitor <.Competitor>`.
    """

    total_score1: int | None = None
    """
    The partial score of the :py:class:`match <.Match>` up to this board, for the first
    :py:class:`competitor <.Competitor>`, while it is still being played.
    """

    score2: int | None = None
    """
    The score of this board for the second :py:class:`competitor <.Competitor>`.
    """

    total_score2: int | None = None
    """
    The partial score of the :py:class:`match <.Match>` up to this board, for the second
    :py:class:`competitor <.Competitor>`, while it is still being played.
    """

    ## Relations

    match: Mapped[Match] = relationship('Match', back_populates='boards')
    """The related :py:class:`match <.Match>.`"""

    ## Methods

    def __repr__(self):  # pragma: no cover
        if self.queen:
            queen = ', queen pocketed by competitor %s' % self.queen
        else:
            queen = ''
        match = self.match.caption(html=False, localized=False)
        return '<%s %d of match %s: %s-%s%s>' % (
            self.__class__.__name__,
            self.number,
            match,
            self.coins1,
            self.coins2,
            queen,
        )

    description = property(__repr__)

    def serialize(self, serializer: Serializer) -> SerializedBoard:
        """Reduce a single board to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :returns: a plain dictionary containing a flatified view of this board
        """

        simple: SerializedBoard = {'number': self.number}
        if self.coins1 is not None:
            simple['coins1'] = self.coins1
        if self.coins2 is not None:
            simple['coins2'] = self.coins2
        if self.queen:
            simple['queen'] = self.queen
        return simple
