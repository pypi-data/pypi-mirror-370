# -*- coding: utf-8 -*-
# :Project:   SoL -- The Tourney entity
# :Created:   gio 27 nov 2008 13:54:14 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018-2024 Lele Gaifax
#

from __future__ import annotations

import logging
from collections import Counter
from collections import defaultdict
from collections.abc import Iterable
from datetime import date as dtdate
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from itertools import chain
from itertools import combinations
from math import ceil
from math import log2
from operator import attrgetter
from operator import itemgetter
from typing import Any
from typing import NamedTuple
from typing import TYPE_CHECKING
from typing import TypedDict

from itsdangerous import Signer
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import gettext
from ..i18n import translatable_string as _
from . import Base
from . import GloballyUnique
from .domains import boolean_t
from .domains import code_t
from .domains import date_t
from .domains import description_t
from .domains import int_t
from .domains import intid_t
from .domains import smallint_t
from .domains import url_t
from .errors import OperationAborted
from .utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .championship import Championship
    from .club import Club
    from .competitor import Competitor
    from .competitor import SerializedCompetitor
    from .match import Match
    from .match import SerializedMatch
    from .rating import Rating
    from .user import User


logger = logging.getLogger(__name__)


class Rank(NamedTuple):
    points: int
    bucholz: int
    netscore: int
    totscore: int
    position: int
    rate: int


class SerializedTourney(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Tourney`."

    guid: str
    modified: datetime
    championship: int
    description: str
    date: dtdate
    currentturn: int
    rankedturn: int
    prized: bool
    system: str
    couplings: str
    delaytoppairing: int
    delaycompatriotpairing: int
    duration: int
    prealarm: int
    phantomscore: int
    retirements: str
    finalkind: str
    competitors: list[SerializedCompetitor]
    matches: list[SerializedMatch]
    hosting_club: NotRequired[int]
    rating: NotRequired[int]
    owner: NotRequired[int]
    location: NotRequired[str]
    socialurl: NotRequired[str]
    finals: NotRequired[int]
    finalturns: NotRequired[bool]
    matcheskind: str


class RankingStats:
    """
    An interim object used keep the ongoing values needed to compute the ranking of a single
    competitor.
    """

    __slots__ = (
        'points',
        'netscore',
        'totscore',
        'bucholz',
        'real_points',
        'played_matches',
        'virtual_points',
        'retired',
    )

    def __init__(self, retired):
        self.points = 0
        'Overall points.'

        self.netscore = 0
        'Net score.'

        self.totscore = 0
        'Total score.'

        self.bucholz = 0
        'Bucholz.'

        self.real_points = 0
        'Points made against real competitors.'

        self.played_matches = 0
        'Number of played matches.'

        self.virtual_points = 0
        'Estimated further points, after retirement.'

        self.retired = retired
        'Whether it is a retired competitor.'

    def won(self, netscore: int, against_phantom: bool) -> None:
        "Update stats after a winned match."

        self.played_matches += 1
        self.netscore += netscore
        self.points += 2
        if not against_phantom:
            self.real_points += 2

    def lost(self, netscore: int) -> None:
        "Update stats after a lost match."

        self.played_matches += 1
        self.netscore -= netscore

    def drawn(self) -> None:
        "Update stats after a tie."

        self.played_matches += 1
        self.points += 1
        self.real_points += 1

    def rank(self, position: int | None, rate: int | None) -> Rank:
        "Return the final :class:`Rank`."

        return Rank(
            points=self.points,
            bucholz=self.bucholz,
            netscore=self.netscore,
            totscore=self.totscore,
            position=None if position is None else -position,
            rate=rate,
        )


class NoMoreCombinationsError(OperationAborted):
    pass


class Tourney(GloballyUnique, Base):
    """A single tournament."""

    __tablename__ = 'tourneys'
    'Related table'

    @declared_attr.directive
    def __table_args__(cls):
        return GloballyUnique.__table_args__(cls) + (
            Index(
                '%s_uk' % cls.__tablename__,
                'date',
                'description',
                'idchampionship',
                unique=True,
            ),
        )

    ## Columns

    idtourney: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idtourney', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Tourney ID'),
            hint=_('Unique ID of the tourney.'),
        ),
    )
    """Primary key."""

    idchampionship: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('championships.idchampionship', name='fk_tourney_championship'),
        nullable=False,
        info=dict(
            label=_('Championship ID'),
            hint=_('ID of the championship the tourney belongs to.'),
        ),
    )
    """Related :py:class:`championship <.Championship>`'s ID."""

    idhostingclub: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('clubs.idclub', name='fk_championship_club'),
        nullable=True,
        info=dict(
            label=_('Hosting club ID'),
            hint=_('ID of the club hosting the tournament.'),
        ),
    )
    """Hosting :py:class:`club <.Club>`'s ID."""

    idrating: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('ratings.idrating', name='fk_tourney_rating'),
        nullable=True,
        info=dict(label=_('Rating ID'), hint=_('ID of the rating this tourney uses.')),
    )
    """Possible :py:class:`rating <.Rating>` ID this tourney uses and updates."""

    idowner: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('users.iduser', name='fk_tourney_owner', ondelete='SET NULL'),
        nullable=True,
        info=dict(
            label=_('Owner ID'),
            hint=_('ID of the user that is responsible for this record.'),
        ),
    )
    """ID of the :py:class:`user <.User>` that is responsible for this record."""

    date: Mapped[dtdate] = mapped_column(
        date_t,
        nullable=False,
        info=dict(
            label=_('Date'),
            hint=_('Date of the event.'),
        ),
    )
    """Event date."""

    description: Mapped[str] = mapped_column(
        description_t,
        nullable=False,
        info=dict(
            label=_('Description'),
            hint=_('Description of the tourney.'),
        ),
    )
    """Event description."""

    location: Mapped[str | None] = mapped_column(
        description_t,
        nullable=True,
        info=dict(
            label=_('Location'),
            hint=_('Location of the tourney.'),
        ),
    )
    """Event location."""

    socialurl: Mapped[str | None] = mapped_column(
        url_t,
        nullable=True,
        info=dict(
            label=_('Social site'),
            hint=_('URL of the social site dedicated to the tournament, if any.'),
        ),
    )
    """Social site URL."""

    duration: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=45,
        info=dict(
            label=_('Duration'),
            hint=_('Duration in minutes of each round, set to 0 to disable countdown.'),
            min=0,
        ),
    )
    """Duration in minutes of each round, used by the clock."""

    prealarm: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=5,
        info=dict(
            label=_('Prealarm'),
            hint=_(
                'Prealarm before the end of the round, usually no more games'
                ' after that.'
            ),
            min=0,
        ),
    )
    """Prealarm before the end of the round."""

    system: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='swiss',
        info=dict(
            label=_('System'),
            hint=_('Kind of tournament.'),
            dictionary=dict(
                swiss=_('Swiss'),
                knockout=_('Knockout'),
                roundrobin=_('Round-robin'),
            ),
        ),
    )
    """The type of tournament, it may be `swiss` (the default), `knockout` or `roundrobin`."""

    couplings: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='serial',
        info=dict(
            label=_('Pairings'),
            hint=_('Method used to pair competitors at each round.'),
            dictionary=dict(
                all=_('All possible matches'),
                serial=_('Ranking order'),
                dazed=_('Cross ranking order'),
                staggered=_('Staggered ranking order'),
                seeds=_('Standard seeding [KO and RR]'),
                circle=_('Circular [RR]'),
            ),
        ),
    )
    """Kind of pairing method used to build next round. It may be `serial`, `dazed`,
    `staggered` or `seeds`, the latter valid only for knockout or round-robin tourneys."""

    delaytoppairing: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=1,
        info=dict(
            label=_('Delay top players pairing'),
            hint=_(
                'Number of rounds for which pairing of top players should be'
                ' postponed, if possible. Meaningful only if using a rating.'
            ),
            min=0,
        ),
    )
    """Number of rounds for which pairing of top players should be postponed, if possible."""

    delaycompatriotpairing: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Delay compatriots pairing'),
            hint=_(
                'Number of rounds for which pairing of players belonging to the'
                ' same country should be postponed, if possible.'
            ),
            min=0,
        ),
    )
    """Number of rounds for which pairing of players belonging to the same country should be
    postponed, if possible."""

    currentturn: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Round'),
            hint=_('The highest generated round number.'),
        ),
    )
    """The current round."""

    countdownstarted: Mapped[int | None] = mapped_column(
        int_t,
        nullable=True,
        info=dict(
            label=_('Countdown start'),
            hint=_('The timestamp of the start of the clock countdown.'),
        ),
    )
    """Timestamp of the start of the clock countdown, milliseconds since Unix epoch."""

    rankedturn: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Ranked round'),
            hint=_('To which round the ranking is up-to-date with.'),
        ),
    )
    """The highest round considered in the ranking."""

    prized: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Closed'),
            hint=_('Whether the final prizes have been assigned.'),
        ),
    )
    """Whether the tourney is closed, and final prizes updated."""

    phantomscore: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=25,
        info=dict(
            label=_('Phantom score'),
            hint=_('The score assigned to a player in matches against the Phantom.'),
            min=1,
            max=25,
        ),
    )
    """The score assigned to a player in matches against the Phantom."""

    retirements: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='none',
        info=dict(
            label=_('Drop outs'),
            hint=_(
                'Policy used to adjust the bucholz of competitors who played against'
                ' withdrawn players.'
            ),
            dictionary=dict(
                none=_('No adjustment'),
                trend=_('Average trend'),
                trend70=_('70％ of average trend'),
            ),
        ),
    )
    'Policy used to adjust the bucholz of competitors who played against withdrawn players.'

    finals: Mapped[int | None] = mapped_column(
        smallint_t,
        nullable=True,
        default=0,
        info=dict(
            label=_('Finals'),
            hint=_(
                'The number of finals that will be played: 0 means no finals,'
                ' 1 means one final for the 1st and 2nd place, 2 also for the'
                ' 3rd and fourth place. Only for Swiss system.'
            ),
            min=0,
            max=2,
        ),
    )
    """The number of finals that will be played."""

    finalkind: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='simple',
        info=dict(
            label=_('Final kind'),
            hint=_('The kind of finals.'),
            dictionary=dict(
                simple=_('Single game'),
                bestof3=_('Best of three games'),
            ),
        ),
    )
    """Kind of finals. It may be `simple` or `bestof3`."""

    finalturns: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Final rounds'),
            hint=_('Whether the tourney is in final rounds state.'),
        ),
    )
    """Whether the tourney is in final rounds state."""

    matcheskind: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='simple',
        info=dict(
            label=_('Matches kind'),
            hint=_('The kind of matches.'),
            dictionary=dict(
                simple=_('Single game'),
                bestof3=_('Best of three games'),
            ),
        ),
    )
    """Kind of matches. It may be `simple` or `bestof3`."""

    ## Relations

    owner: Mapped[User | None] = relationship('User', back_populates='owned_tourneys')
    """The :py:class:`owner <.User>` of this record, `admin` when ``None``."""

    championship: Mapped[Championship] = relationship(
        'Championship', back_populates='tourneys'
    )
    """The :py:class:`championship <.Championship>` of this tournament."""

    competitors: Mapped[list[Competitor]] = relationship(
        'Competitor',
        back_populates='tourney',
        cascade='all, delete-orphan',
        lazy='joined',
    )
    """List of :py:class:`competitors <.Competitor>`."""

    hosting_club: Mapped[Club] = relationship('Club', back_populates='hosted_tourneys')
    """The :py:class:`club <.Club> that hosts this tourney.`"""

    matches: Mapped[list[Match]] = relationship(
        'Match',
        back_populates='tourney',
        cascade='all, delete-orphan',
        order_by='Match.turn, Match.board',
    )
    """List of :py:class:`matches <.Match>`, sorted by round and board."""

    rating: Mapped[Rating] = relationship('Rating', back_populates='tourneys')
    """The :py:class:`rating <.Rating>` used by this tourney."""

    ## Methods

    @classmethod
    def check_insert(
        cls, session: Session, fields: dict[str, Any], user_id: str | int
    ) -> None:
        "Check new tournament validity."

        from . import Championship
        from .club import Club
        from .club import clubusers
        from .rating import Rating
        from .user import User

        try:
            desc = normalize(fields['description'])
        except KeyError:
            raise OperationAborted(
                _('For a new tourney the "description" field is mandatory')
            )

        if not desc:
            raise OperationAborted(
                _('For a new tourney the "description" field is mandatory')
            )

        idcship = fields.get('idchampionship')
        if idcship is None:  # pragma: no cover
            raise OperationAborted(
                _('For a new tourney the "championship" field is mandatory')
            )

        couplings = fields.get('couplings', cls.couplings.default.arg)
        cmethod = cls.couplings.info['dictionary'].get(couplings)
        if cmethod is None:
            raise OperationAborted(
                _(
                    'Invalid pairing method: $couplings',
                    mapping=dict(couplings=repr(couplings)),
                )
            )
        system = fields.get('system')
        if couplings == 'all':
            if system not in ('roundrobin', 'swiss'):
                cmethod = cls.couplings.info['dictionary'][couplings]
                raise OperationAborted(
                    _(
                        'Invalid pairing method, $couplings is allowed'
                        ' only in Swiss or Round-robin system tourney',
                        mapping=dict(couplings=repr(_(cmethod))),
                    )
                )
        elif couplings == 'seeds':
            if system not in ('knockout', 'roundrobin'):
                cmethod = cls.couplings.info['dictionary'][couplings]
                raise OperationAborted(
                    _(
                        'Invalid pairing method, $couplings is allowed'
                        ' only in Knockout or Round-robin tourney',
                        mapping=dict(couplings=repr(_(cmethod))),
                    )
                )
        elif couplings == 'circle':
            if system != 'roundrobin':
                cmethod = cls.couplings.info['dictionary'][couplings]
                raise OperationAborted(
                    _(
                        'Invalid pairing method, $couplings is allowed'
                        ' only in Round-robin tourney',
                        mapping=dict(couplings=repr(_(cmethod))),
                    )
                )
        elif couplings is not None:
            if fields.get('system', cls.system.default.arg) != 'swiss':
                raise OperationAborted(
                    _(
                        'Invalid pairing method, $couplings is allowed'
                        ' only in Swiss system tourney',
                        mapping=dict(couplings=repr(_(cmethod))),
                    )
                )

        matcheskind = fields.get('matcheskind', cls.matcheskind.default.arg)
        mkind = cls.matcheskind.info['dictionary'].get(matcheskind)
        if mkind is None:
            raise OperationAborted(
                _(
                    'Invalid matches kind: $matcheskind',
                    mapping=dict(couplings=repr(matcheskind)),
                )
            )
        if matcheskind == 'bestof3' and system != 'knockout':
            raise OperationAborted(
                _(
                    'Invalid matches kind, $matcheskind is allowed'
                    ' only in Knockout tourney',
                    mapping=dict(matcheskind=repr(_(mkind))),
                )
            )

        if system != 'swiss' and fields.get('finals'):
            raise OperationAborted(
                _('Finals can be done only in Swiss system tourneys')
            )

        if user_id != 'admin':
            clubs = Club.__table__
            cships = Championship.__table__
            if not session.scalar(
                select(1).where(
                    exists()
                    .where(cships.c.idchampionship == idcship)
                    .where(
                        or_(
                            cships.c.idowner == user_id,
                            exists()
                            .where(clubs.c.idclub == cships.c.idclub)
                            .where(clubs.c.idowner == user_id),
                            exists()
                            .where(clubusers.c.idclub == cships.c.idclub)
                            .where(clubusers.c.iduser == user_id),
                        )
                    )
                )
            ):
                raise OperationAborted(
                    _(
                        'You are not allowed to add a tourney to the'
                        ' selected championship'
                    )
                )

            idrating = fields.get('idrating')
            if idrating is not None:
                ratings = Rating.__table__
                users = User.__table__
                if session.scalar(
                    select(ratings.c.level < users.c.maxratinglevel)
                    .select_from(ratings.join(users, true()))
                    .where(ratings.c.idrating == idrating)
                    .where(users.c.iduser == user_id)
                ):
                    raise OperationAborted(
                        _('You are not allowed to use that level of ratings')
                    )

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Perform various validity checks."

        if 'description' in fields:
            desc = normalize(fields['description'])
            if not desc:
                raise OperationAborted(
                    _('The "description" field of a tourney cannot be empty')
                )

        system = fields.get('system', self.system)
        if 'couplings' in fields or 'system' in fields or 'matcheskind' in fields:
            couplings = fields.get('couplings', self.couplings)
            cmethod = self.__table__.c.couplings.info['dictionary'].get(couplings)
            if cmethod is None:
                raise OperationAborted(
                    _(
                        'Invalid pairing method: $couplings',
                        mapping=dict(couplings=repr(couplings)),
                    )
                )
            if couplings == 'all':
                if system not in ('roundrobin', 'swiss'):
                    cmethod = self.__table__.c.couplings.info['dictionary'][couplings]
                    raise OperationAborted(
                        _(
                            'Invalid pairing method, $couplings is allowed'
                            ' only in Swiss or Round-robin system tourney',
                            mapping=dict(couplings=repr(_(cmethod))),
                        )
                    )
            elif couplings == 'seeds':
                if system not in ('knockout', 'roundrobin'):
                    raise OperationAborted(
                        _(
                            'Invalid pairing method, $couplings is allowed'
                            ' only in Knockout or Round-robin tourney',
                            mapping=dict(couplings=repr(_(cmethod))),
                        )
                    )
            elif couplings == 'circle':
                if system != 'roundrobin':
                    raise OperationAborted(
                        _(
                            'Invalid pairing method, $couplings is allowed'
                            ' only in Round-robin tourney',
                            mapping=dict(couplings=repr(_(cmethod))),
                        )
                    )
            else:
                if system != 'swiss':
                    raise OperationAborted(
                        _(
                            'Invalid pairing method, $couplings is allowed'
                            ' only in Swiss tourney',
                            mapping=dict(couplings=repr(_(cmethod))),
                        )
                    )
            matcheskind = fields.get('matcheskind', self.matcheskind)
            mkind = self.__table__.c.matcheskind.info['dictionary'].get(matcheskind)
            if mkind is None:
                raise OperationAborted(
                    _(
                        'Invalid matches kind: $matcheskind',
                        mapping=dict(couplings=repr(matcheskind)),
                    )
                )
            if matcheskind == 'bestof3' and system != 'knockout':
                raise OperationAborted(
                    _(
                        'Invalid matches kind, $matcheskind is allowed'
                        ' only in Knockout tourney',
                        mapping=dict(matcheskind=repr(_(mkind))),
                    )
                )

        if system != 'swiss' and fields.get('finals', self.finals):
            raise OperationAborted(
                _('Finals can be done only in Swiss system tourneys')
            )

        if user_id != 'admin' and 'idrating' in fields:
            from .rating import Rating
            from .user import User

            ratings = Rating.__table__
            users = User.__table__
            session = object_session(self)
            assert session

            if session.scalar(
                select(ratings.c.level < users.c.maxratinglevel)
                .select_from(ratings.join(users, true()))
                .where(ratings.c.idrating == fields['idrating'])
                .where(users.c.iduser == user_id)
            ):
                raise OperationAborted(
                    _('You are not allowed to use that level of ratings')
                )

    def caption(self, html=None, localized=True):
        return gettext(
            '$tourney — $championship, $date',
            just_subst=not localized,
            mapping=dict(
                tourney=self.description,
                championship=self.championship.caption(html, localized),
                date=self.date.strftime(gettext('%m-%d-%Y')),
            ),
        )

    def allPlayers(self):
        "Generator that return all involved players."

        for c in self.competitors:
            yield c.player1
            if c.player2 is not None:  # pragma: nocover
                yield c.player2
                if c.player3 is not None:
                    yield c.player3
                    if c.player4 is not None:
                        yield c.player4

    @property
    def isAllAgainstAllTraining(self):
        return bool(
            self.system in ('roundrobin', 'swiss')
            and self.couplings == 'all'
            and self.championship.trainingboards
        )

    @property
    def ranking(self):
        """Competitors sorted by their rank.

        :rtype: sequence
        :returns: sorted list of :py:class:`competitors <.Competitor>`
        """

        from .competitor import competitors_sorters

        # Initial sort on ascending players name, to match the ordering used by the Ranking
        # panel: thanks to Python's sort stability further sorts will maintain this ordering
        # for equal keys
        competitors = sorted(
            self.competitors, key=attrgetter('player1.lastname', 'player1.firstname')
        )

        if self.rankedturn == 0:

            def key(c: Competitor, /) -> tuple[Decimal | int | float, ...]:
                return (-c.position, c.rate or 0)
        else:
            key = competitors_sorters[(self.system, 'comp')]

        ranking = sorted(competitors, key=key, reverse=True)

        if not self.prized and self.finals and self.finalturns:
            enough, nfinalturns, wins = self._areFinalTurnsEnoughForPrizing()
            if enough:
                # Possibly swap positions of finalists
                for final in range(self.finals):
                    i1 = final * 2
                    i2 = i1 + 1
                    c1 = ranking[i1]
                    c2 = ranking[i2]
                    if wins.get(c1, 0) < wins.get(c2, 0):
                        ranking[i1 : i2 + 1] = [c2, c1]

        return ranking

    @property
    def firstFinalTurn(self):
        "The number of the first final match, if any."

        from . import Match

        if self.finalturns:
            matches = Match.__table__
            session = object_session(self)
            assert session
            return session.scalar(
                select(func.min(matches.c.turn))
                .where(matches.c.idtourney == self.idtourney)
                .where(matches.c.final)
            )

    def _computeFinalWins(self) -> tuple[int, Counter[Competitor]]:
        """Compute the number of matches won by each competitor in the finals"""

        finalmatches = [m for m in self.matches if m.final]
        nfinalturns = len({m.turn for m in finalmatches})

        wins: Counter[Competitor] = Counter()
        for match in finalmatches:
            if match.score1 != match.score2:
                winner, loser, netscore = match.results()
                wins[winner] += 1

        return nfinalturns, wins

    def _areFinalTurnsEnoughForPrizing(self) -> tuple[bool, int, Counter[Competitor]]:
        "Determine whether final rounds are enough to complete the tourney with prize-giving."

        nfinalturns, wins = self._computeFinalWins()

        if self.finalkind == 'simple':
            return nfinalturns == 1, nfinalturns, wins
        else:
            if nfinalturns == 3:
                return True, nfinalturns, wins
            else:
                # If all competitors won at least two matches, we are done
                return bool(wins and all(wins[c] >= 2 for c in wins)), nfinalturns, wins

    def updateRanking(self) -> None:
        """Recompute and update competitors ranking."""

        if self.prized:
            raise OperationAborted(_('Cannot update rankings after prize-giving!'))

        is_aaat = self.isAllAgainstAllTraining

        ranking = dict(self.computeRanking())

        for comp in self.competitors:
            r = ranking[comp]
            comp.points = r.points
            comp.netscore = r.netscore
            comp.totscore = r.totscore
            comp.bucholz = r.bucholz

        if is_aaat:
            if self.matches:
                match = None
                for match in self.matches:
                    if not match.isScored:
                        self.currentturn = match.turn
                        self.rankedturn = match.turn - 1
                        break
                else:
                    assert match
                    self.currentturn = self.rankedturn = match.turn
        else:
            self.rankedturn = self.currentturn

        self.modified = func.now()

        if self.finals and self.finalturns and self._areFinalTurnsEnoughForPrizing()[0]:
            # Automatically assign final prizes, so the user isn't bothered with that
            # (the "prizes" button is hidden)
            self.assignPrizes()

    def computeRanking(self, turn=None) -> list[tuple[Competitor, Rank]]:
        """Recompute competitors ranking.

        :param turn: if given, compute the ranking up to that turn
        :returns: a list of tuples, each containing one of the competitors and a :class:`Rank`
                  instance, sorted on the second item in descending order

        Compute each competitor rank by examining the matches of this tourney, summing up each
        other's current ranking position as the bucholz.
        """

        # Start from scratch, assigning zero to all competitors
        ranking: dict[Competitor | None, RankingStats] = {
            comp: RankingStats(comp.retired) for comp in self.competitors
        }

        is_aaat = self.isAllAgainstAllTraining

        # First of all, sum up points and netscore
        highest_scored_turn = 0
        for match in self.matches:
            if (turn is not None and match.turn > turn) or match.final:
                break

            if is_aaat and not match.isScored:
                continue

            highest_scored_turn = match.turn

            winner, loser, netscore = match.results()
            if netscore == 0:
                ranking[winner].drawn()
                ranking[loser].drawn()
            else:
                ranking[winner].won(netscore, loser is None)
                if loser is not None:
                    ranking[loser].lost(netscore)

        # Then compute the bucholz, summing up each competitor's points, possibly adjusted by
        # the configured policy
        if self.retirements != 'none':
            factor: int | Fraction
            if self.retirements == 'trend':
                factor = 1
            else:
                assert self.retirements == 'trend70'
                factor = Fraction(70, 100)
            current_turn = highest_scored_turn if turn is None else turn
            for r in ranking.values():
                if r.retired:
                    if r.real_points != 0:
                        average = Fraction(r.real_points, r.played_matches) * factor
                        adjustment = average * (current_turn - r.played_matches)
                    else:
                        adjustment = 0
                    r.virtual_points = int(adjustment)

        # Add phantom
        ranking[None] = RankingStats(False)

        for match in self.matches:
            if (turn is not None and match.turn > turn) or match.final:
                break

            r1 = ranking[match.competitor1]
            r2 = ranking[match.competitor2]
            r1.totscore += match.score1
            r2.totscore += match.score2
            r1.bucholz += r2.points + r2.virtual_points
            r2.bucholz += r1.points + r1.virtual_points

        # Compute the final ranking, properly sorted
        final_ranking = [
            (c, r.rank(c.position, c.rate)) for c, r in ranking.items() if c is not None
        ]
        return sorted(final_ranking, key=itemgetter(1), reverse=True)

    def _checkSeedsAmbiguities(self):
        activecomps = [c for c in self.competitors if not c.retired]
        if self.idrating is None:
            if not all(c.position for c in activecomps):
                logger.warning(
                    'Missing seeds position for some competitor: %s',
                    ', '.join(
                        repr(c)
                        for c in self.competitors
                        if not c.retired and not c.position
                    ),
                )
                raise OperationAborted(
                    _(
                        'Missing seed for some competitor,'
                        ' must be entered manually in the'
                        " tourney's “Competitors” window"
                    )
                )

            if len({c.position for c in activecomps}) != len(activecomps):
                seen = set()
                dups = []
                for c in activecomps:
                    if c.position in seen:
                        dups.append(c)
                    else:
                        seen.add(c.position)
                logger.warning(
                    'Following competitors have duplicated seed: %s',
                    ', '.join(repr(c) for c in dups),
                )
                raise OperationAborted(
                    _(
                        'At least two competitors have the same seed,'
                        ' please disambiguate the positions in the'
                        " tourney's “Competitors” window"
                    )
                )
        else:
            if len({c.rate for c in activecomps}) != len(activecomps):
                seen = set()
                dups = []
                for c in activecomps:
                    if c.rate in seen:
                        dups.append(c)
                    else:
                        seen.add(c.rate)
                logger.warning(
                    'Following competitors have duplicated rate: %s',
                    ', '.join(repr(c) for c in dups),
                )
                raise OperationAborted(
                    _(
                        'At least two competitors have the same rate,'
                        ' please disambiguate assigning explicit seeds'
                        " in the tourney's “Competitors” window"
                    )
                )

            if any(c.position for c in activecomps):
                if not all(c.position for c in activecomps):
                    logger.warning(
                        'Missing seed for some competitor: %s',
                        ', '.join(
                            repr(c)
                            for c in self.competitors
                            if not c.retired and not c.position
                        ),
                    )
                    raise OperationAborted(
                        _(
                            'Missing seed for some competitor,'
                            ' must be entered manually in the'
                            " tourney's “Competitors” window"
                        )
                    )

                if len({c.position for c in activecomps}) != len(activecomps):
                    seen = set()
                    dups = []
                    for c in activecomps:
                        if c.position in seen:
                            dups.append(c)
                        else:
                            seen.add(c.position)
                    logger.warning(
                        'Following competitors have duplicated seed: %s',
                        ', '.join(repr(c) for c in dups),
                    )
                    raise OperationAborted(
                        _(
                            'At least two competitors have the same'
                            ' seed, please disambiguate the positions'
                            " in the tourney's “Competitors” window"
                        )
                    )

    def makeNextTurn(self) -> None:
        """Setup the next round.

        If there are no matches, build up the first round using a random coupler. Otherwise,
        using current ranking, create the next round pairing any given competitor with a
        not-yet-met other one that follows him in the ranking.
        """

        if self.prized:
            raise OperationAborted(_('Cannot create other rounds after prize-giving!'))

        if self.couplings == 'seeds':
            self._checkSeedsAmbiguities()

        # Happens in test, for transient, non-committed Tourney instances
        if self.currentturn is None:
            self.currentturn = 0

        if self.championship.trainingboards:
            noemail = [c.player1 for c in self.competitors if not c.player1.email]
            if noemail:  # pragma: no cover
                names = ', '.join(p.caption(localized=False) for p in noemail)
                raise OperationAborted(
                    _(
                        'Cannot proceed, following competitors do not have'
                        ' an email address: ${names}',
                        mapping=dict(names=names),
                    )
                )

        is_aaat = self.isAllAgainstAllTraining

        if not is_aaat:
            if self.currentturn and self.currentturn != self.rankedturn:
                raise OperationAborted(_('The ranking is not up-to-date!'))

        if self.finalturns:
            self.currentturn = self._makeNextFinalTurn()
        elif is_aaat:
            self._makeAllTurns()
            self.currentturn = 1
        elif self.couplings == 'all':
            self._makeNextAAATurn()
            self.currentturn += 1
        elif self.system == 'knockout' and not self.currentturn:
            self._makeFirstKnockoutTurn()
            self.currentturn = 1
        elif self.system == 'roundrobin' and self.couplings == 'circle':
            self._makeNextRoundrobinCircleTurn()
            self.currentturn += 1
        elif (
            self.idrating is not None or self.currentturn or self.system == 'roundrobin'
        ):
            # If the tourney is using a rating, create the first round
            # with the usual rules instead of random couplings
            self._makeNextTurn()
            self.currentturn += 1
        else:
            self._makeFirstTurn()
            self.currentturn = 1

        self.countdownstarted = None
        self.modified = func.now()

    def _addMatches(
        self, turn: int, pairings: Iterable[tuple[Competitor, Competitor | None]]
    ) -> None:
        "Add matches to the tourney for the given `turn` as indicated by `pairings`."

        from . import Match

        done = set()
        for m in self.matches:
            c1 = m.competitor1
            c2 = m.competitor2
            done.add((c1, c2))
            done.add((c2, c1))

        phantommatch = None
        matches = []
        ranking = self.ranking
        for c1, c2 in pairings:
            if (c1, c2) in done:
                continue
            if c1 is None:
                assert c2 is not None
                c1, c2 = c2, c1
            done.add((c1, c2))
            done.add((c2, c1))
            # Prefer seeing the stronger competitor in first position
            if c2 is not None and ranking.index(c1) > ranking.index(c2):
                c1, c2 = c2, c1
            m = Match(
                turn=turn,
                competitor1=c1,
                competitor2=c2,
                score1=self.phantomscore if c2 is None else 0,
                score2=0,
            )
            # Put match against phantom last, but not in Knockouts
            if self.system != 'knockout' and c2 is None:
                phantommatch = m
            else:
                matches.append(m)

            if self.matcheskind == 'bestof3' and c2 is None:
                m.score1_2 = self.phantomscore
                m.score2_2 = 0
            # The following can happen in KO/RR, where we keep retired competitors
            if c1.retired:
                m.score1 = 0
                m.score2 = 25
                if self.matcheskind == 'bestof3':
                    m.score1_2 = 0
                    m.score2_2 = 25
            elif c2 is not None and c2.retired:
                m.score1 = 25
                m.score2 = 0
                if self.matcheskind == 'bestof3':
                    m.score1_2 = 25
                    m.score2_2 = 0

        if not matches:
            raise NoMoreCombinationsError(
                _('Cannot create another round: no more possible combinations!')
            )

        if self.system == 'swiss' or self.system == 'roundrobin':
            self._assignBoards(matches)
            if phantommatch is not None:
                phantommatch.board = len(matches) + 1
                matches.append(phantommatch)
        else:
            if phantommatch is not None:
                matches.append(phantommatch)
            for board, match in enumerate(matches, 1):
                match.board = board

        self.matches.extend(matches)

    def _makeFirstTurn(self) -> None:
        "Create the first round of a tourney, pairing competitors in a random way."

        from random import randint

        comps = self.competitors[:]
        count = len(comps)
        pairings = []
        while count > 0:
            c1 = comps.pop(randint(0, count - 1))
            if count == 1:
                c2 = None
            else:
                c2 = comps.pop(randint(0, count - 2))
            pairings.append((c1, c2))
            count -= 2
        self._addMatches(1, pairings)

    def _makeFirstKnockoutTurn(self) -> None:
        "Create first turn of a knockout tourney."

        comps = self.competitors[:]
        if self.idrating is not None:
            comps.sort(key=attrgetter('rate'), reverse=True)
        comps.sort(key=attrgetter('position'))
        count = len(comps)
        if count % 2:
            comps.append(None)
            count += 1

        # Adapted from https://stackoverflow.com/a/45572051

        pairings = [(1, 2)]
        rounds = ceil(log2(count))
        if rounds != log2(count):
            raise OperationAborted(
                _(
                    'For a Knockout tourney there must be a power-of-two'
                    ' (i.e. 2, 4, 8, 16…) number of competitors!'
                )
            )

        for round in range(1, rounds):
            new_pairings = []
            sum = 2 ** (round + 1) + 1

            for p1, p2 in pairings:
                new_pairings.append((p1, sum - p1))
                new_pairings.append((sum - p2, p2))

            pairings = new_pairings

        self._addMatches(1, ((comps[p1 - 1], comps[p2 - 1]) for p1, p2 in pairings))

    def _makeAllTurns(self) -> None:
        """Create all possible turns in a training tournament using the circle__ method.

        __ https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method
        """

        comps = [c for c in self.competitors if not c.retired]
        count = len(comps)
        if count % 2:
            comps.append(None)
            count += 1
        half = count // 2

        for turn in range(1, count):
            self._addMatches(turn, zip(comps[:half], reversed(comps[half:])))
            last = comps.pop()
            comps.insert(1, last)

    def _makeNextAAATurn(self) -> None:
        """Create next turn, out of all possible pairings."""

        comps = [c for c in self.competitors if not c.retired]
        ncomps = len(comps)
        if ncomps % 2:
            comps.append(None)
            ncomps += 1

        done = set()
        for m in self.matches:
            c1 = m.competitor1
            c2 = m.competitor2
            done.add((c1, c2))
            done.add((c2, c1))

        playing = set()
        nextround = []
        for c1, c2 in combinations(comps, 2):
            if (c1, c2) not in done and c1 not in playing and c2 not in playing:
                nextround.append((c1, c2))
                playing.add(c1)
                playing.add(c2)
                if len(playing) == ncomps:
                    break

        self._addMatches(self.currentturn + 1, nextround)

    def _makeNextRoundrobinCircleTurn(self) -> None:
        """Create next round-robin turn mechanically pairing competitors using the circle__
        method.

        __ https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method
        """

        comps = self.competitors[:]
        # Sort also by description, in case neither rate nor position are given
        comps.sort(key=attrgetter('description'))
        if self.idrating is not None:
            comps.sort(key=attrgetter('rate'), reverse=True)
        comps.sort(key=attrgetter('position'))
        count = len(comps)
        if count % 2:
            comps.append(None)
            count += 1

        for turn in range(self.currentturn):
            last = comps.pop()
            comps.insert(1, last)

        half = count // 2
        self._addMatches(
            self.currentturn + 1, zip(comps[:half], reversed(comps[half:]))
        )

    class AbstractVisitor:
        """Abstract visitor.

        :param tourney: a :py:class:`.Tourney` instance
        :param pivot: a :py:class:`.Competitor` instance
        :param competitors: a list of possible opponents
        :param done: the set of already played pairings

        This is an `iterator class`__, used by the method :py:meth:`Tourney._combine`: it
        yields all possible competitors to `pivot` in some order, without repeating already
        played matches present in `done`, a set containing previous matches (both ``(a, b)``
        and ``(b, a)``).

        The iteration honors the tourney's `delaycompatriotpairing`: when ``True``, players
        with the same nationality of the `pivot` will be considered last.

        Concrete subclasses must reimplement the method ``computeVisitOrder()``, that
        determines the actual *order*.

        __ https://docs.python.org/3.12/library/stdtypes.html#iterator-types
        """

        def __init__(self, tourney, pivot, competitors, done):
            self.tourney = tourney
            self.pivot = pivot
            self.competitors = competitors
            self.done = done

        def computeVisitOrder(self):  # pragma: no cover
            "Return a sequence of *positions*, the indexes into the list `self.competitors`."

            raise NotImplementedError(
                'Class %s must reimplement method computeVisitOrder()' % self.__class__
            )

        def __iter__(self):
            pivot = self.pivot
            competitors = self.competitors
            positions = self.computeVisitOrder()

            if self.tourney.rankedturn < self.tourney.delaycompatriotpairing:
                prev_points = pivot.points
                old_positions = list(positions)
                positions = []
                postponed = []
                phantompos = None

                while old_positions:
                    pos = old_positions.pop(0)
                    c = competitors[pos]
                    if c is None:
                        phantompos = pos
                    else:
                        if c.points != prev_points:
                            if postponed:
                                positions.extend(postponed)
                                postponed = []
                            prev_points = c.points
                        if c.nationality == pivot.nationality:
                            postponed.append(pos)
                        else:
                            positions.append(pos)

                if postponed:
                    positions.extend(postponed)
                if phantompos is not None:
                    positions.append(phantompos)

            done = self.done
            for pos in positions:
                c = competitors[pos]
                if c is not pivot and (pivot, c) not in done:
                    yield c

    class RoundrobinSeedsVisitor(AbstractVisitor):
        """Visit the `competitors` in reverse order.

        Given that the list of competitors is sorted by their rank, this emits the usual
        `Round-robin`__ pairings.

        __ https://en.wikipedia.org/wiki/Round-robin_tournament
        """

        def computeVisitOrder(self):
            return range(len(self.competitors) - 1, 0, -1)

    class SwissSerialVisitor(AbstractVisitor):
        """Visit the `competitors` in order.

        Given that the list of competitors is sorted by their rank, this effectively tries to
        combine players with the same strength.
        """

        def computeVisitOrder(self):
            "Simply return ``range(len(self.competitors))``."

            return range(len(self.competitors))

    class SwissDazedVisitor(AbstractVisitor):
        """Visit the `competitors`, giving precedence to the competitors with the same points.

        This starts looking at the competitors with the same points as the `pivot`, and then
        goes on with the others: this is to postpone as much as possible the match between the
        strongest competitors.
        """

        def countSamePointsAsPivot(self):
            "Return the count of competitors with the same points as the `pivot`."

            same_points = 0
            pivot_points = self.pivot.points
            for c in self.competitors:
                # The competitors may contain the phantom, ie a None
                if c is not None and c.points == pivot_points:
                    same_points += 1
                else:
                    break
            return same_points

        def computeVisitOrder(self):
            """First count how many competitors have the same points as the `pivot`, then if
            possible iterate over the second half of them, then over the first half, and
            finally over the remaining ones.
            """

            same_points = self.countSamePointsAsPivot()
            all_players = len(self.competitors)
            if same_points > 2:
                # If the group cardinality is odd, try to include the first player of
                # the next group
                if same_points < all_players and same_points % 2:
                    # Considering the presence of the phantom, don't to that if we are
                    # building the very first round, ie when all players have 0 points
                    if None not in self.competitors or same_points != (all_players - 1):
                        if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
                            border_c = self.competitors[same_points].caption(
                                False, False
                            )
                            logger.debug(
                                'Considering competitor “%s” as belonging to'
                                ' the group with %d points',
                                border_c,
                                self.pivot.points,
                            )
                        same_points += 1
                middle = same_points // 2
                positions = chain(
                    range(middle, same_points),
                    range(0, middle),
                    range(same_points, all_players),
                )
            else:
                positions = range(all_players)
            return positions

    class SwissStaggeredVisitor(SwissDazedVisitor):
        """Visit the `competitors`, giving precedence to the competitors with the same points.

        This is similar to :py:class:`.DazedVisitor` except that when there are 50 or more
        competitors with the same points, instead of splitting them in two halves of the same
        size it uses an arbitrary offset of 25 (i.e. the 1st competitor is paired with the
        26th, the 2nd with the 27th, and so on): this should placate the gripes about unfair
        pairings between strongest and weakest competitors at the first turn.
        """

        def computeVisitOrder(self):
            same_points = self.countSamePointsAsPivot()
            all_players = len(self.competitors)
            if same_points > 2:
                if same_points < all_players and same_points % 2:
                    # Considering the presence of the phantom, don't to that if we are
                    # building the very first round, ie when all players have 0 points
                    if None not in self.competitors or same_points != (all_players - 1):
                        if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
                            border_c = self.competitors[same_points].caption(
                                False, False
                            )
                            logger.debug(
                                'Considering competitor “%s” as belonging to'
                                ' the group with %d points',
                                border_c,
                                self.pivot.points,
                            )
                        same_points += 1
                if same_points >= 50:
                    positions = chain(
                        range(25, same_points),
                        range(0, 25),
                        range(same_points, all_players),
                    )
                else:
                    middle = same_points // 2
                    positions = chain(
                        range(middle, same_points),
                        range(0, middle),
                        range(same_points, all_players),
                    )
            else:
                positions = range(all_players)
            return positions

    def _combine(
        self,
        competitors: list[Competitor | None],
        done: set[tuple[Competitor, Competitor | None]],
        _level=0,
    ) -> list[tuple[Competitor, Competitor | None]]:
        """Build the next round, based on current ranking.

        This recursively tries to build the next round, pairing together competitors that did
        not already played against each other.
        """

        if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
            ranking = self.ranking

            def debug(msg, *args):
                logger.debug('%sL%02d ' + msg, '=' * _level, _level, *args)

            def C(c):
                if c:
                    position = f'{ranking.index(c) + 1}. '
                    return f'{position}{c.caption(False, False)} ({c.points}p)'
                else:
                    return 'Phantom'

            if _level == 0 and done:
                done_matches: dict[Competitor, list[Competitor]] = {}
                for c1, c2 in done:
                    if c1:
                        matches = done_matches.setdefault(c1, [])
                        if c2 not in matches:
                            matches.append(c2)
                            matches = done_matches.setdefault(c2, [])
                            matches.append(c1)
                logger.debug(
                    'Done matches:\n%s',
                    '\n'.join(
                        f"  {C(c)}: {', '.join(C(o) for o in done_matches[c])}"
                        for c in ranking
                    ),
                )

            debug(
                'Competitors to be paired:\n%s',
                '\n'.join(f'  {C(c)}' for c in competitors),
            )
        else:
            debug = None  # type: ignore[reportAssignmentType]
            C = None  # type: ignore[reportAssignmentType]

        if len(competitors) < 2:  # pragma: nocover
            if debug:
                debug('Backtracking: no more combinations')
            return []

        try:
            visitor = getattr(
                self, self.system.capitalize() + self.couplings.capitalize() + 'Visitor'
            )
        except AttributeError:  # pragma: nocover
            raise AttributeError(
                'No %r method to pair competitors with' % self.couplings
            )

        c1 = competitors[0]
        if debug:  # pragma: nocover
            remainingc = tuple(visitor(self, c1, competitors, done))
            if remainingc:
                debug(
                    'Looking for a competitor for %s within\n%s',
                    C(c1),
                    '\n'.join(f'  {C(c)}' for c in remainingc),
                )
            else:
                debug('Backtracking: no possible competitors for %s', C(c1))

        for n, c2 in enumerate(visitor(self, c1, competitors, done), 1):
            if debug:  # pragma: nocover
                debug('Tentative %d: trying %s vs %s', n, C(c1), C(c2))
            if len(competitors) > 2:
                remainings = self._combine(
                    [c for c in competitors if c is not c1 and c is not c2],
                    done,
                    _level=_level + 1,
                )
                if remainings:
                    newturn = [(c1, c2)] + remainings
                    if debug:  # pragma: nocover
                        if _level == 0:
                            debug(
                                'OK =>\n%s',
                                '\n'.join(
                                    f'  {C(_c1)} vs {C(_c2)}' for _c1, _c2 in newturn
                                ),
                            )
                        else:
                            debug('OK')
                    return newturn
            else:
                if debug:  # pragma: nocover
                    debug('OK => %s vs %s', C(c1), C(c2))
                return [(c1, c2)]

        return []

    def _assignBoards(self, matches) -> None:
        """Assign a table to each match, possibly the least used by both competitors."""

        used_boards = defaultdict(Counter)
        for match in self.matches:
            c1 = match.competitor1
            c2 = match.competitor2
            used_boards[c1][match.board] += 1
            used_boards[c2][match.board] += 1

        available_boards = range(1, len(matches) + 1)
        for match in matches:
            available_boards = sorted(
                available_boards,
                key=lambda b: (
                    used_boards[match.competitor1][b],
                    used_boards[match.competitor2][b],
                    b,
                ),
            )
            match.board = available_boards.pop(0)

    def _makeNextTurn(self) -> None:
        """Build the next round of the game."""

        ranking = self.ranking

        if self.system == 'roundrobin':
            ranking = sorted(
                ranking,
                key=lambda c: (
                    (c.position, -(c.rate or 0), c.description)
                    if c is not None
                    else (1_234_567_890,)
                ),
            )
        elif self.idrating is not None and self.rankedturn < self.delaytoppairing:
            # Reorder the ranking taking into account the rate of each competitors
            # just after the bucholz, to delay top players pairing
            if self.system == 'swiss':
                key = attrgetter('points', 'bucholz', 'rate', 'netscore', 'totscore')  # type: ignore[reportAssignmentType]
            else:

                def key(c):
                    return (
                        c.points,
                        c.bucholz,
                        -c.position,
                        c.rate,
                        c.netscore,
                        c.totscore,
                    )

            ranking = sorted(ranking, key=key, reverse=True)

        done = set()
        for m in self.matches:
            c1 = m.competitor1
            c2 = m.competitor2
            done.add((c1, c2))
            done.add((c2, c1))

        activecomps: list[Competitor | None]

        if self.system == 'knockout':
            if not self.currentturn:  # pragma: nocover
                raise OperationAborted(
                    _('Internal error occurred, please contact the administrator')
                )

            activecomps = []
            for m in self.matches:
                if m.turn != self.currentturn:
                    continue
                c = m.results()[0]
                activecomps.append(c)
        else:
            activecomps = [c for c in ranking if not c.retired]

        if len(activecomps) == 1:
            raise NoMoreCombinationsError(
                _('Cannot create another round: no more possible combinations!')
            )

        # Append the phantom if the number is odd
        if len(activecomps) % 2:
            activecomps.append(None)

        if self.system == 'knockout':
            combination = self._makeNextKnockoutTurn(activecomps)
        else:
            combination = self._combine(activecomps, done, self.currentturn + 1)

        if combination:
            self._addMatches(self.currentturn + 1, combination)
        else:
            if self.system == 'swiss':
                remaining = self._countRemainingMatches(activecomps, done)
                if remaining:
                    raise OperationAborted(
                        _(
                            'Cannot create next round: there are further $remaining possible'
                            ' matches but they cannot be grouped together with the current'
                            ' pairing rules. Nevertheless, you can switch to the “All possible'
                            ' matches” pairing method to generate remaining rounds.',
                            mapping=dict(remaining=remaining),
                        )
                    )
            raise NoMoreCombinationsError(
                _('Cannot create another round: no more possible combinations!')
            )

    def _makeNextKnockoutTurn(
        self, competitors: list[Competitor | None]
    ) -> list[tuple[Competitor, Competitor | None]]:
        "Couple the first with the last, the second with the second-last and so on."

        if len(competitors) % 2 != 0:  # pragma: nocover
            raise OperationAborted(
                _('Internal error occurred, please contact the administrator')
            )

        result = []
        while competitors:
            c1 = competitors.pop(0)
            c2 = competitors.pop(0)
            result.append((c1, c2))
        return result

    def _countRemainingMatches(
        self,
        competitors: list[Competitor | None],
        done: set[tuple[Competitor, Competitor | None]],
    ) -> int:
        remaining = 0
        playing = set()

        for c1, c2 in combinations(competitors, 2):
            if (c1, c2) not in done and c1 not in playing and c2 not in playing:
                remaining += 1
                playing.add(c1)
                playing.add(c2)

        return remaining

    def makeFinalTurn(self):
        "Generate the final matches."

        if self.prized:
            raise OperationAborted(_('Cannot generate final turn after prize-giving!'))

        if not self.finals:
            raise OperationAborted(_('Finals are not considered for this tourney!'))

        self.finalturns = True
        self.makeNextTurn()

    def _makeNextFinalTurn(self):
        from . import Match

        enough, _nfinalturns, wins = self._areFinalTurnsEnoughForPrizing()
        if enough:  # pragma: no cover
            raise OperationAborted(_('No further final matches are needed!!'))

        ranking = self.ranking
        newturn = self.currentturn + 1
        boardno = 1

        assert self.finals
        for final in range(self.finals):
            c1 = ranking[final * 2]
            c2 = ranking[final * 2 + 1]
            if wins.get(c1, 0) < 2 and wins.get(c2, 0) < 2:
                self.matches.append(
                    Match(
                        turn=newturn,
                        board=boardno,
                        final=True,
                        competitor1=c1,
                        competitor2=c2,
                        score1=0,
                        score2=0,
                    )
                )
                boardno += 1

        return newturn

    def assignPrizes(self):
        """Consolidate final points."""

        if self.prized:  # pragma: nocover
            raise OperationAborted(_('Cannot update prizes after prize-giving!'))

        cturn = self.currentturn

        if cturn and cturn != self.rankedturn:  # pragma: nocover
            raise OperationAborted(_('The ranking is not up-to-date!'))

        kind = (
            self.championship.prizes.capitalize()
            if self.championship.prizes
            else 'Fixed'
        )

        name = '_assign%sPrizes' % kind

        try:
            method = getattr(self, name)
        except AttributeError:  # pragma: nocover
            raise AttributeError('No %r method to assign prizes with' % kind)

        method()

        self.prized = True
        self.modified = func.now()

        if self.rating is not None and self.rating.shouldConsiderTourney(self):
            self.rating.recompute(self.date)

        logger.info('Assigned final prizes for %r', self)

    def _assignAsisPrizes(self):
        "Assign decreasing integer numbers as final prizes, down to 1 to the last competitor."

        prize = len(self.ranking)
        for c in self.ranking:
            c.prize = Decimal(prize)
            prize -= 1

    def _assignFixedPrizes(self, prizes=None):
        "Assign fixed prizes to the first 16 competitors."

        if prizes is None:
            # This is what Scarry used to do.
            prizes = [18, 16, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

        for c in self.ranking:
            if prizes:
                prize = prizes.pop(0)
            else:
                prize = 0
            c.prize = Decimal(prize)

    def _assignFixed40Prizes(self):
        "Assign fixed prizes to the first 40 competitors."

        # This is the Francesco Beltrami's series of prizes, used
        # in the 2009-2010 italian national championship.
        self._assignFixedPrizes(
            prizes=[
                1000,
                900,
                800,
                750,
                700,
                650,
                600,
                550,
                500,
                450,
                400,
                375,
                350,
                325,
                300,
                275,
                250,
                225,
                200,
                175,
                150,
                140,
                130,
                120,
                110,
                100,
                90,
                80,
                70,
                60,
                50,
                40,
                35,
                30,
                25,
                20,
                15,
                10,
                5,
                1,
            ]
        )

    def _assignMillesimalPrizes(self):
        "Assign 1000 points to the winner stepping down in fixed amount."

        # This is how the FIC currently assigns the prizes.

        ranking = self.ranking
        prize = 1000
        fraction = prize // len(ranking)
        for c in ranking:
            c.prize = Decimal(prize)
            prize -= fraction

    def _assignCentesimalPrizes(self):
        "Assigns 100 to the winner, 1 to the last, linear interpolation to the others."

        # This was suggested by Carlito

        ranking = self.ranking
        prize = 100.0
        fraction = (prize - 1) / (len(ranking) - 1)
        for c in ranking:
            c.prize = Decimal(round(prize, 2))
            prize -= fraction

    def resetPrizes(self):
        """Reset assigned final points."""

        for c in self.competitors:
            c.prize = Decimal(0.0)

        self.prized = False
        self.modified = func.now()
        if self.rating is not None and self.rating.shouldConsiderTourney(self):
            self.rating.recompute(self.date)

    def replay(self, date, newidowner=None):
        """Clone this tourney, creating new one at given date.

        Of the original, only the competitors are copied. This is particularly useful for
        doubles (or team), so that the players get copied in the same order.
        """

        from . import Championship
        from . import Competitor
        from . import Rating
        from . import User

        if newidowner is not None and self.idrating is not None:
            ratings = Rating.__table__
            users = User.__table__
            session = object_session(self)
            assert session

            if session.scalar(
                select(ratings.c.level < users.c.maxratinglevel)
                .select_from(ratings.join(users, true()))
                .where(ratings.c.idrating == self.idrating)
                .where(users.c.iduser == newidowner)
            ):
                raise OperationAborted(
                    _(
                        'You are not allowed to replicate that tourney,'
                        ' it uses a rating level inaccessible by you'
                    )
                )

        new = Tourney(
            idrating=self.idrating,
            idowner=newidowner,
            date=date,
            description=gettext(
                'Replica of $tourney', mapping=dict(tourney=self.description)
            ),
            location=self.location,
            duration=self.duration,
            prealarm=self.prealarm,
            couplings=self.couplings,
            system=self.system,
            delaytoppairing=self.delaytoppairing,
            delaycompatriotpairing=self.delaycompatriotpairing,
            phantomscore=self.phantomscore,
            retirements=self.retirements,
            finals=self.finals,
            finalkind=self.finalkind,
            matcheskind=self.matcheskind,
        )

        if not self.championship.closed:
            championship = self.championship
        else:
            session = object_session(self)
            assert session
            championship = (
                session.query(Championship)
                .filter_by(
                    idclub=self.championship.idclub,
                    playersperteam=self.championship.playersperteam,
                    closed=False,
                )
                .first()
            )
            if championship is None:
                raise OperationAborted(
                    _('Cannot replicate tourney, no open championships!')
                )

        championship.tourneys.append(new)

        append = new.competitors.append
        for c in self.competitors:
            append(
                Competitor(
                    player1=c.player1,
                    player2=c.player2,
                    player3=c.player3,
                    player4=c.player4,
                    position=c.position,
                )
            )
        return new

    def createKnockout(self, date, ncompetitors, newidowner=None):
        """Create a "knockout" tourney with `ncompetitors` top players."""

        from . import Championship
        from . import Competitor

        if int(log2(ncompetitors)) != log2(ncompetitors):  # pragma: no cover
            raise OperationAborted(
                _(
                    'For a Knockout tourney there must be a power-of-two'
                    ' (i.e. 2, 4, 8, 16…) number of competitors!'
                )
            )

        if len(self.competitors) < ncompetitors:  # pragma: no cover
            raise OperationAborted(
                _(
                    'There are only $n competitors in the tourney!',
                    mapping=dict(n=len(self.competitors)),
                )
            )

        new = Tourney(
            idrating=self.idrating,
            idowner=newidowner,
            date=date,
            description=gettext(
                'Knockout of $tourney', mapping=dict(tourney=self.description)
            ),
            location=self.location,
            duration=self.duration,
            prealarm=self.prealarm,
            couplings='seeds',
            system='knockout',
            delaytoppairing=self.delaytoppairing,
            delaycompatriotpairing=self.delaycompatriotpairing,
            phantomscore=self.phantomscore,
            retirements=self.retirements,
            finals=self.finals,
            finalkind=self.finalkind,
        )

        if not self.championship.closed:
            championship = self.championship
        else:
            session = object_session(self)
            assert session
            championship = (
                session.query(Championship)
                .filter_by(
                    idclub=self.championship.idclub,
                    playersperteam=self.championship.playersperteam,
                    closed=False,
                )
                .first()
            )
            if championship is None:
                raise OperationAborted(
                    _('Cannot replicate tourney, no open championships!')
                )

        championship.tourneys.append(new)

        append = new.competitors.append
        for i, c in enumerate(self.ranking, 1):
            if i > ncompetitors:
                break
            append(
                Competitor(
                    player1=c.player1,
                    player2=c.player2,
                    player3=c.player3,
                    player4=c.player4,
                    position=i,
                )
            )

        return new

    def serialize(self, serializer: Serializer) -> SerializedTourney:
        """Reduce a single tourney to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this tourney
        """

        from operator import attrgetter

        simple: SerializedTourney = {
            'guid': self.guid,
            'modified': self.modified,
            'championship': serializer.addChampionship(self.championship),
            'description': self.description,
            'date': self.date,
            'currentturn': self.currentturn,
            'rankedturn': self.rankedturn,
            'prized': self.prized,
            'system': self.system,
            'couplings': self.couplings,
            'delaytoppairing': self.delaytoppairing,
            'delaycompatriotpairing': self.delaycompatriotpairing,
            'duration': self.duration,
            'prealarm': self.prealarm,
            'phantomscore': self.phantomscore,
            'retirements': self.retirements,
            'finalkind': self.finalkind,
            'matcheskind': self.matcheskind,
        }

        cmap: dict[int | None, int | None] = {None: None}
        ctors = simple['competitors'] = []

        # Sort competitors by first player name, to aid the tests
        fullname = attrgetter('player1.lastname', 'player1.firstname')
        for i, c in enumerate(sorted(self.competitors, key=fullname), 1):
            cmap[c.idcompetitor] = i
            sctor = c.serialize(serializer)
            ctors.append(sctor)

        matches = simple['matches'] = []
        for m in self.matches:
            sm = m.serialize(serializer, cmap)
            matches.append(sm)

        if self.idhostingclub:
            simple['hosting_club'] = serializer.addClub(self.hosting_club)
        if self.idrating:
            simple['rating'] = serializer.addRating(self.rating)
        if self.idowner:
            simple['owner'] = serializer.addUser(self.owner)
        if self.location:
            simple['location'] = self.location
        if self.socialurl:
            simple['socialurl'] = self.socialurl
        if self.finals is not None:
            simple['finals'] = self.finals
        if self.finalturns:
            simple['finalturns'] = self.finalturns

        return simple

    def sendTrainingURLs(self, request):
        if not self.championship.trainingboards:  # pragma: nocover
            raise OperationAborted(_('Not a training tournament!'))

        if self.couplings == 'all':
            byp = {}
            for m in self.matches:
                pm = byp.setdefault(m.competitor1.player1, [])
                pm.append(
                    (m, 1, m.competitor2.player1 if m.competitor2 is not None else None)
                )
                if m.competitor2 is not None:
                    pm = byp.setdefault(m.competitor2.player1, [])
                    pm.append((m, 2, m.competitor1.player1))
            for p in byp:
                p.sendTrainingURLs(request, byp[p])
        else:
            for m in self.matches:
                if m.turn == self.currentturn:
                    m.competitor1.player1.sendTrainingURL(
                        request,
                        m,
                        1,
                        m.competitor2.player1 if m.competitor2 is not None else None,
                    )
                    if m.competitor2 is not None:
                        m.competitor2.player1.sendTrainingURL(
                            request, m, 2, m.competitor1.player1
                        )

    def getEditBoardURL(self, request, boardno):
        settings = request.registry.settings
        s = Signer(settings['sol.signer_secret_key'])
        signed_board = s.sign('%d-%d' % (self.idtourney, boardno)).decode('ascii')
        return request.route_url('match_form', board=signed_board)
