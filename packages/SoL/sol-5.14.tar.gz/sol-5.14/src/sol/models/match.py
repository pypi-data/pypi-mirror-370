# -*- coding: utf-8 -*-
# :Project:   SoL -- The Match entity
# :Created:   gio 27 nov 2008 13:52:02 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018, 2020-2025 Lele Gaifax
#

from __future__ import annotations

import logging
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict

from itsdangerous import Signer
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
from .domains import flag_t
from .domains import intid_t
from .domains import smallint_t
from .errors import OperationAborted

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .board import Board
    from .board import SerializedBoard
    from .tourney import Tourney


logger = logging.getLogger(__name__)


class SerializedMatch(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Match`."

    competitor1: int
    competitor2: int
    turn: int
    board: int
    score1: int
    score2: int
    score1_2: NotRequired[int]
    score2_2: NotRequired[int]
    score1_3: NotRequired[int]
    score2_3: NotRequired[int]
    breaker: NotRequired[str]
    final: NotRequired[bool]
    boards: NotRequired[list[SerializedBoard]]


class Match(Base):
    """A single match.

    This table contains all the matches played in the various rounds of a tourney. A match may
    be between two different competitors or between a competitor and a *placeholder* (amicably
    referred to as "phantom"), when the number of competitors is odd.
    """

    __tablename__ = 'matches'
    'Related table'

    # Tell SA this class instances carry extra "temporary" fields
    __allow_unmapped__ = True

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index(
                '%s_board' % cls.__tablename__,
                'idtourney',
                'turn',
                'board',
                unique=True,
            ),
            Index(
                '%s_c1_vs_c2' % cls.__tablename__,
                'idtourney',
                'idcompetitor1',
                'idcompetitor2',
                unique=True,
                sqlite_where=(cls.final == 0),
            ),
        )

    ## Columns

    idmatch: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idmatch', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Match ID'),
            hint=_('Unique ID of the match.'),
        ),
    )
    """Primary key."""

    idtourney: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('tourneys.idtourney', name='fk_match_tourney'),
        nullable=False,
        info=dict(
            label=_('Tourney ID'),
            hint=_('ID of the tourney the match belongs to.'),
        ),
    )
    """Related :py:class:`tourney <.Tourney>`'s ID."""

    turn: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        info=dict(
            label=_('Round #'),
            hint=_('Round number.'),
        ),
    )
    """Round number of the match."""

    board: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        info=dict(
            label=_('#'),
            hint=_(
                'The number identifying the carromboard where this match is played.'
            ),
        ),
    )
    """The number of the carromboard this match is played on."""

    final: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Final'),
            hint=_('Whether the match is a normal one or a final.'),
        ),
    )
    """Whether the match is a normal one or a final."""

    idcompetitor1: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('competitors.idcompetitor', name='fk_match_competitor1'),
        nullable=False,
        info=dict(
            label=_('1st competitor ID'),
            hint=_('ID of the first competitor.'),
        ),
    )
    """First :py:class:`competitor <.Competitor>`'s ID."""

    idcompetitor2: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('competitors.idcompetitor', name='fk_match_competitor2'),
        nullable=True,
        info=dict(
            label=_('2nd competitor ID'),
            hint=_('ID of the second competitor.'),
        ),
    )
    """Second :py:class:`competitor <.Competitor>`'s ID (possibly None)."""

    breaker: Mapped[str | None] = mapped_column(
        flag_t,
        nullable=True,
        info=dict(
            label=_('Breaker'),
            hint=_('Which competitor started the match.'),
            dictionary={
                '1': _('First competitor'),
                '2': _('Second competitor'),
            },
        ),
    )
    """Which competitor started the break."""

    score1: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        # TRANSLATORS: this is the label for the "score of the first competitor" in the Matches
        # grid, keep it as compact as possible
        info=dict(
            label=_('S1'),
            hint=_('Score of the first competitor.'),
            min=0,
            max=25,
        ),
    )
    """Score of the first :py:class:`competitor <.Competitor>`."""

    score2: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        # TRANSLATORS: this is the label for the "score of the second competitor" in the
        # Matches grid, keep it as compact as possible
        info=dict(
            label=_('S2'),
            hint=_('Score of the second competitor.'),
            min=0,
            max=25,
        ),
    )
    """Score of the second :py:class:`competitor <.Competitor>`."""

    score1_2: Mapped[int] = mapped_column(
        smallint_t,
        nullable=True,
        # TRANSLATORS: this is the label for the "score of the first competitor in the
        # second-of-three game" in the Matches grid, keep it as compact as possible
        info=dict(
            label=_('S1 (2)'),
            hint=_('Score of the first competitor in the second game.'),
            min=0,
            max=25,
        ),
    )
    """
    Score of the first :py:class:`competitor <.Competitor>` in the second game, when playing
    in *best-of-three games* mode.
    """

    score2_2: Mapped[int] = mapped_column(
        smallint_t,
        nullable=True,
        # TRANSLATORS: this is the label for the "score of the second competitor in the
        # second-of-three game" in the Matches grid, keep it as compact as possible
        info=dict(
            label=_('S2 (2)'),
            hint=_('Score of the second competitor in the second game.'),
            min=0,
            max=25,
        ),
    )
    """
    Score of the second :py:class:`competitor <.Competitor>` in the second game, when playing
    in *best-of-three games* mode.
    """

    score1_3: Mapped[int] = mapped_column(
        smallint_t,
        nullable=True,
        # TRANSLATORS: this is the label for the "score of the first competitor in the
        # second-of-three game" in the Matches grid, keep it as compact as possible
        info=dict(
            label=_('S1 (3)'),
            hint=_('Score of the first competitor in the third game.'),
            min=0,
            max=25,
        ),
    )
    """
    Score of the first :py:class:`competitor <.Competitor>` in the third game, when playing
    in *best-of-three games* mode.
    """

    score2_3: Mapped[int] = mapped_column(
        smallint_t,
        nullable=True,
        # TRANSLATORS: this is the label for the "score of the second competitor in the
        # second-of-three game" in the Matches grid, keep it as compact as possible
        info=dict(
            label=_('S2 (3)'),
            hint=_('Score of the second competitor in the third game.'),
            min=0,
            max=25,
        ),
    )
    """
    Score of the second :py:class:`competitor <.Competitor>` in the third game, when playing
    in *best-of-three* mode.
    """

    partial_score1: int | None = None
    """
    The running score of the first :py:class:`competitor <.Competitor>`,
    while the match is still being played.
    """

    partial_score2: int | None = None
    """
    The running score of the second :py:class:`competitor <.Competitor>`,
    while the match is still being played.
    """

    ## Relations

    competitor1 = relationship(
        'Competitor', primaryjoin='Competitor.idcompetitor==Match.idcompetitor1'
    )
    """First :py:class:`competitor <.Competitor>`"""

    competitor2 = relationship(
        'Competitor', primaryjoin='Competitor.idcompetitor==Match.idcompetitor2'
    )
    """Second :py:class:`competitor <.Competitor>`
    (may be ``None``, the Phantom)."""

    boards: Mapped[list[Board]] = relationship(
        'Board',
        back_populates='match',
        cascade='all, delete-orphan',
        order_by='Board.number',
    )
    """List of :py:class:`boards <.Board>`."""

    tourney: Mapped[Tourney] = relationship('Tourney', back_populates='matches')
    """Related :py:class:`tourney <.Tourney>`."""

    ## Methods

    def __repr__(self):  # pragma: no cover
        r = super().__repr__()
        trepr = repr(self.tourney)[2:-1]
        details = f' in turn {self.turn} of t{trepr}: {self.score1}-{self.score2}'
        if self.tourney is not None and self.tourney.matcheskind == 'bestof3':
            if self.score1_2 is not None and self.score2_2 is not None:
                details += f' / {self.score1_2}-{self.score2_2}'
                if self.score1_3 is not None and self.score2_3 is not None:
                    details += f' / {self.score1_3}-{self.score2_3}'
        r = r[:-1] + f'{details}>'
        return r

    def caption(self, html=None, localized=True):
        "A description of the match, made up with the description of each competitor."

        comp1 = self.competitor1.caption(html, localized, css_class='c1')
        if self.competitor2:
            comp2 = self.competitor2.caption(html, localized, css_class='c2')
        else:
            # TRANSLATORS: this is the name used for the "missing"
            # player, when there's an odd number of them
            comp2 = gettext('Phantom', just_subst=not localized)
        if html is None or html:
            if self.tourney.championship.playersperteam > 1:
                # TRANSLATORS: this is used to format the description
                # of a match for double events
                format = _('$comp1<br/><i>vs.</i><br/>$comp2')
            else:
                # TRANSLATORS: this is used to format the description
                # of a match for single events
                format = _('$comp1 <i>vs.</i> $comp2')
        else:
            format = _('$comp1 vs. $comp2')
        return gettext(
            format, mapping=dict(comp1=comp1, comp2=comp2), just_subst=not localized
        )

    description = property(caption)

    @property
    def competitor1FullName(self):
        "Full name of the first :py:class:`competitor <.Competitor>`"
        c1 = self.competitor1
        return c1.description if c1 is not None else gettext('Player NOT assigned yet!')

    @property
    def competitor2FullName(self):
        "Full name of the second :py:class:`competitor <.Competitor>`"
        c2 = self.competitor2
        return c2.description if c2 is not None else gettext('Phantom')

    @property
    def competitor1Opponents(self):
        "List of competitors ID who played against the first competitor"
        c1 = self.competitor1
        return c1.getOpponentsPreceedingTurns(self.turn) if c1 is not None else []

    @property
    def competitor2Opponents(self):
        "List of competitors ID who played against the second competitor"
        c2 = self.competitor2
        return c2.getOpponentsPreceedingTurns(self.turn) if c2 is not None else []

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Check scores validity, and possibly create :py:class:`~Board` instances."

        from .board import Board

        if self.tourney.matcheskind == 'bestof3':
            for game in ('', '_2', '_3'):
                s1fname = f'score1{game}'
                s2fname = f'score2{game}'
                if s1fname in fields and s2fname in fields:
                    if (
                        fields[s1fname] is not None
                        and fields[s1fname] == fields[s2fname]
                    ):
                        raise OperationAborted(
                            _('Ties are not allowed in best-of-three games matches')
                        )

        existing = len(self.boards)
        game = 1
        while game < 20:
            if (
                f'coins1_{game}' in fields
                or f'coins2_{game}' in fields
                or f'queen_{game}' in fields
            ):
                coins1 = fields.pop(f'coins1_{game}', None)
                coins2 = fields.pop(f'coins2_{game}', None)
                queen = fields.pop(f'queen_{game}', None)
                while existing < game:
                    existing += 1
                    self.boards.append(Board(number=existing))
                if not coins1 and not coins2 and not queen:
                    break
                if coins1 is not None:
                    self.boards[game - 1].coins1 = coins1
                if coins2 is not None:
                    self.boards[game - 1].coins2 = coins2
                self.boards[game - 1].queen = queen
            game += 1

    @property
    def isScored(self) -> bool:
        "Tell whether the match has been compiled."

        if self.score1 == self.score2 == 0:
            return False

        if self.tourney.matcheskind == 'simple':
            return True

        # Should never happen, we are called in all-against-all training events
        won1, won2 = self._bestOf3Results()  # pragma: no cover
        return won1 >= 2 or won2 >= 2  # pragma: no cover

    def _bestOf3Results(self) -> tuple[int, int]:
        if self.tourney.matcheskind != 'bestof3':  # pragma: nocover
            logger.error(
                'Something weird happened: Match._bestOf3Results() called'
                ' but tourney.matcheskind is %s!',
                self.tourney.matcheskind,
            )
            raise OperationAborted(
                _('Internal error occurred, please contact the administrator')
            )

        won1 = won2 = 0
        if self.score1 > self.score2:
            won1 = 1
        elif self.score1 < self.score2:
            won2 = 1
        else:
            raise OperationAborted(
                _(
                    'How could game $game of "$match" end with a draw in a best of three'
                    ' tourney?!?',
                    mapping=dict(game=1, match=self.description),
                )
            )

        if not (self.score1_2 is None or self.score2_2 is None):
            if self.score1_2 > self.score2_2:
                won1 += 1
            elif self.score1_2 < self.score2_2:
                won2 += 1
            else:
                raise OperationAborted(
                    _(
                        'How could game $game of "$match" end with a draw in a best of three'
                        ' tourney?!?',
                        mapping=dict(game=2, match=self.description),
                    )
                )

            if not (self.score1_3 is None or self.score2_3 is None):
                if self.score1_3 > self.score2_3:
                    won1 += 1
                elif self.score1_3 < self.score2_3:
                    won2 += 1
                else:
                    raise OperationAborted(
                        _(
                            'How could game $game of "$match" end with a draw in a best of three'
                            ' tourney?!?',
                            mapping=dict(game=3, match=self.description),
                        )
                    )

        return won1, won2

    def results(self):
        """Results of this match, comparing competitor' scores.

        :rtype: tuple
        :returns: winner, loser, netscore
        """

        if self.competitor2 is None:
            return self.competitor1, None, self.tourney.phantomscore

        if self.tourney.matcheskind == 'simple':
            if self.score1 > self.score2:
                return self.competitor1, self.competitor2, self.score1 - self.score2

            if self.score1 < self.score2:
                return self.competitor2, self.competitor1, self.score2 - self.score1

            if self.score1 == self.score2 == 0:
                raise OperationAborted(
                    _(
                        'How could match "$match" end without result?!?',
                        mapping=dict(match=self.description),
                    )
                )

            if (
                self.score1 == self.score2 and self.tourney.system == 'knockout'
            ):  # pragma: no cover
                raise OperationAborted(
                    _(
                        'How could match "$match" end with a draw in a Knockout tourney?!?',
                        mapping=dict(match=self.description),
                    )
                )

            return self.competitor1, self.competitor2, 0
        else:
            won1, won2 = self._bestOf3Results()

            if won1 < 2 and won2 < 2:
                raise OperationAborted(
                    _(
                        'No one won enough games in match "$match"!',
                        mapping=dict(match=self.description),
                    )
                )

            # FIXME: how should we compute the netscore??
            if won1 > won2:
                return self.competitor1, self.competitor2, won1 - won2

            if won2 > won1:
                return self.competitor2, self.competitor1, won2 - won1

            return self.competitor1, self.competitor2, 0

    def serialize(
        self, serializer: Serializer, competitors: dict[int | None, int | None]
    ) -> SerializedMatch:
        """Reduce a single match to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :param competitors: a mapping between competitor integer ID to its integer marker
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this match
        """

        simple: SerializedMatch = {
            'competitor1': competitors[self.idcompetitor1],
            'competitor2': competitors[self.idcompetitor2],
            'turn': self.turn,
            'board': self.board,
            'score1': self.score1,
            'score2': self.score2,
        }
        if self.score1_2 is not None:
            simple['score1_2'] = self.score1_2
            simple['score2_2'] = self.score2_2
            if self.score1_3 is not None:
                simple['score1_3'] = self.score1_3
                simple['score2_3'] = self.score2_3
        if self.breaker:
            simple['breaker'] = self.breaker
        if self.final:
            simple['final'] = self.final
        if self.boards:
            boards = simple['boards'] = []
            for b in self.boards:
                sb = b.serialize(serializer)
                boards.append(sb)

        return simple

    def getEditCompetitorURL(self, request, cnum):
        settings = request.registry.settings
        s = Signer(settings['sol.signer_secret_key'])
        signed_match = s.sign('%d-%d' % (self.idmatch, cnum)).decode('ascii')
        return request.route_url('training_match_form', match=signed_match)

    def computePartialScores(self):
        "Enrich played boards with partial scores."

        total1 = total2 = self.partial_score1 = self.partial_score2 = 0
        if not self.boards:
            return
        for board in self.boards:
            score1 = board.coins1 or 0
            score2 = board.coins2 or 0
            if board.coins1 == board.coins2 == 0:
                # When both coins where explicitly set to 0 it means that one of the player
                # committed suicide: the Queen must be considered unconditionally
                if board.queen == '1':
                    score1 += 3 if total1 < 22 else 1
                elif board.queen == '2':
                    score2 += 3 if total2 < 22 else 1
            else:
                # Normal case: Queen is considered only when is has been pocketed
                # by the winner, and she has less than 22 points
                if board.queen == '1' and score1 > score2 and total1 < 22:
                    score1 += 3
                elif board.queen == '2' and score1 < score2 and total2 < 22:
                    score2 += 3
            board.score1 = score1
            board.score2 = score2
            total1 += score1
            total2 += score2
            board.total_score1 = min(total1, 25)
            board.total_score2 = min(total2, 25)
        self.partial_score1 = total1
        self.partial_score2 = total2
