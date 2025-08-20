# -*- coding: utf-8 -*-
# :Project:   SoL -- The Rating entity
# :Created:   gio 05 dic 2013 09:05:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013-2016, 2018, 2020, 2022-2024 Lele Gaifax
#

from __future__ import annotations

import logging
from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import translatable_string as _
from . import Base
from . import GloballyUnique
from .domains import boolean_t
from .domains import code_t
from .domains import description_t
from .domains import flag_t
from .domains import intid_t
from .domains import prize_t
from .domains import smallint_t
from .domains import volatility_t
from .errors import OperationAborted
from .glicko2 import DRAW
from .glicko2 import Glicko2
from .glicko2 import LOSS
from .glicko2 import WIN
from .utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .championship import Championship
    from .club import Club
    from .competitor import Competitor
    from .player import Player
    from .rate import Rate
    from .tourney import Tourney
    from .user import User


logger = logging.getLogger(__name__)


class SerializedRating(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Rating`."

    guid: str
    modified: datetime
    description: str
    level: str
    inherit: bool
    tau: str
    default_rate: int
    default_deviation: int
    default_volatility: str
    lower_rate: int
    higher_rate: int
    outcomes: str
    owner: NotRequired[int]
    club: NotRequired[int]


class Rating(GloballyUnique, Base):
    """A particular rating a tournament can be related to."""

    __tablename__ = 'ratings'
    'Related table'

    @declared_attr.directive
    def __table_args__(cls):
        return GloballyUnique.__table_args__(cls) + (
            Index('%s_uk' % cls.__tablename__, 'description', unique=True),
        )

    ## Columns

    idrating: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idrating', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Rating ID'),
            hint=_('Unique ID of the rating.'),
        ),
    )
    """Primary key."""

    idowner: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('users.iduser', name='fk_rating_owner', ondelete='SET NULL'),
        nullable=True,
        info=dict(
            label=_('Owner ID'),
            hint=_('ID of the user that is responsible for this record.'),
        ),
    )
    """ID of the :py:class:`user <.User>` that is responsible for this record."""

    idclub: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('clubs.idclub', name='fk_rating_club', ondelete='SET NULL'),
        nullable=True,
        info=dict(
            label=_('Club ID'),
            hint=_('ID of the club the rating is restricted to.'),
        ),
    )
    """Restricted to :py:class:`club <.Club>`'s ID."""

    description: Mapped[str] = mapped_column(
        description_t,
        nullable=False,
        info=dict(
            label=_('Description'),
            hint=_('Description of the rating.'),
        ),
    )
    """Description of the rating."""

    level: Mapped[str] = mapped_column(
        flag_t,
        nullable=False,
        info=dict(
            label=_('Level'),
            hint=_('Rating level.'),
            dictionary={
                str(level): desc
                for level, desc in enumerate(
                    (
                        _('Historical (imported) rating'),
                        _('Level 1, international tourneys'),
                        _('Level 2, national/open tourneys'),
                        _('Level 3, regional tourneys'),
                        _('Level 4, courtyard tourneys'),
                    )
                )
            },
        ),
    )
    """Rating level."""

    tau: Mapped[Decimal] = mapped_column(
        prize_t,
        nullable=False,
        default='0.5',
        info=dict(
            label=_('Tau'),
            hint=_('The TAU value for the Glicko2 algorithm.'),
            min=0.01,
            max=2,
        ),
    )
    """Value of TAU for the Glicko2 algorithm."""

    default_rate: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=1500,
        info=dict(
            label=_('Rate'),
            hint=_('The default rate value for the Glicko2 algorithm.'),
            min=1,
            max=3000,
        ),
    )
    """Default value of rate (MU) for the Glicko2 algorithm."""

    default_deviation: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=350,
        info=dict(
            label=_('Deviation'),
            hint=_('The default deviation value for the Glicko2 algorithm.'),
            min=1,
            max=500,
        ),
    )
    """Default value of deviation (PHI) for the Glicko2 algorithm."""

    default_volatility: Mapped[Decimal] = mapped_column(
        volatility_t,
        nullable=False,
        default='0.06',
        info=dict(
            label=_('Volatility'),
            hint=_('The default volatility value for the Glicko2 algorithm.'),
            min=0.00001,
            max=1,
        ),
    )
    """Default value of volatility (SIGMA) for the Glicko2 algorithm."""

    inherit: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Inherit'),
            hint=_('Whether to lookup rates in higher levels ratings.'),
        ),
    )
    """Whether to lookup rates in higher levels ratings."""

    lower_rate: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=1600,
        info=dict(
            label=_('Lower points'),
            hint=_(
                'Lower value of the range used to interpolate players rates'
                ' when (almost) all competitors are unrated.'
            ),
        ),
    )
    """
    Lower value of the range used to interpolate players rates when (almost) all competitors
    are unrated.
    """

    higher_rate: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=2600,
        info=dict(
            label=_('Higher points'),
            hint=_('Higher value of the range used to interpolate players rates.'),
        ),
    )
    """Higher value of the range used to interpolate players rates."""

    outcomes: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='guido',
        info=dict(
            label=_('Match outcomes'),
            hint=_('Kind of formula used to compute match outcomes.'),
            dictionary=dict(glicko=_('Standard Glicko'), guido=_("Guido's formula")),
        ),
    )
    """Kind of formula used to compute match outcomes.

    This is used to determine which formula will be used to compute the match outcomes to feed
    Glicko2 algorithm. It may be:

    `glicko2`
      standard Glicko, giving 1.0 to the winner and 0.0 to the loser, 0.5 in case of draw,
      developed with Chess in mind;

    `guido`
      Guido's variant, better suited to Carrom: basically each player is assigned a fraction of
      his own score divided by the sum of the scores of both players.
    """

    ## Relations

    championships: Mapped[list[Championship]] = relationship(
        'Championship', back_populates='rating', passive_updates=False
    )
    """:py:class:`Championships <.Championship>` using this rating by default."""

    club: Mapped[Club | None] = relationship(
        'Club', back_populates='ratings', primaryjoin='Rating.idclub == Club.idclub'
    )
    """The particular :py:class:`club <.Club>` this rating is restricted to, if any."""

    owner: Mapped[User] = relationship('User', back_populates='owned_ratings')
    """The :py:class:`owner <.User>` of this record, `admin` when ``None``."""

    tourneys: Mapped[list[Tourney]] = relationship(
        'Tourney',
        back_populates='rating',
        passive_updates=False,
        order_by='Tourney.date',
    )
    """:py:class:`Tourneys <.Tourney>` using this rating."""

    rates: Mapped[list[Rate]] = relationship(
        'Rate',
        back_populates='rating',
        cascade='all, delete-orphan',
        order_by='Rate.date, Rate.idplayer',
    )
    """List of :py:class:`rates <.Rate>`."""

    ## Methods

    @classmethod
    def check_insert(
        cls, session: Session, fields: dict[str, Any], user_id: str | int
    ) -> None:
        "Check new rating validity."

        from .club import Club
        from .club import clubusers
        from .user import User

        try:
            desc = normalize(fields['description'])
        except KeyError:
            raise OperationAborted(
                _('For a new rating the "description" field is mandatory')
            )

        if not desc:
            raise OperationAborted(
                _('For a new rating the "description" field is mandatory')
            )

        if user_id != 'admin':
            idclub = fields.get('idclub')

            if idclub is None:
                raise OperationAborted(
                    _(
                        'You are not allowed to add a global rating,'
                        ' not associated to a specific club'
                    )
                )

            clubs = Club.__table__
            if not session.scalar(
                select(1).where(
                    or_(
                        exists()
                        .where(clubs.c.idclub == idclub)
                        .where(clubs.c.idowner == user_id),
                        exists()
                        .where(clubusers.c.idclub == idclub)
                        .where(clubusers.c.iduser == user_id),
                    )
                )
            ):
                raise OperationAborted(
                    _('You are not allowed to add a rating to the selected club')
                )

            users = User.__table__
            if (
                session.scalar(
                    select(users.c.maxratinglevel).where(users.c.iduser == user_id)
                )
                > fields['level']
            ):
                raise OperationAborted(
                    _('You are not allowed to create a rating at that level')
                )

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Check validity of rating's changes."

        from .user import User

        if 'description' in fields:
            desc = normalize(fields['description'])
            if not desc:
                raise OperationAborted(
                    _('The "description" field of a rating cannot be empty')
                )

        if 'level' in fields:
            users = User.__table__

            session = object_session(self)
            assert session

            maxratinglevel = session.scalar(
                select(users.c.maxratinglevel).where(users.c.iduser == user_id)
            )
            if maxratinglevel > fields['level']:
                raise OperationAborted(
                    _('You are not allowed to create a rating at that level')
                )

    def getPlayerRating(self, player: Player, before=None):
        """Return the rate of a `player`

        :param player: a Player instance
        :param before: a date instance
        :rtype: an instance of glicko2.Rating

        If `before` is not specified fetch the latest rate, otherwise the most recent one
        preceeding `before`.

        The method considers the referenced rating as well as all those with an higher level.
        """

        from . import Rate
        from . import Rating

        sasess = object_session(self)
        assert sasess

        rt = Rate.__table__

        q = select(rt.c.rate, rt.c.deviation, rt.c.volatility).where(
            rt.c.idplayer == player.idplayer
        )

        if before is not None:
            q = q.where(rt.c.date < before)

        if self.level > '0' and self.inherit:
            rts = Rating.__table__
            q = q.where(
                or_(
                    rt.c.idrating == self.idrating,
                    rt.c.idrating.in_(
                        select(rts.c.idrating).where(rts.c.level < self.level)
                    ),
                )
            )
        else:
            q = q.where(rt.c.idrating == self.idrating)

        r = sasess.execute(q.order_by(rt.c.date.desc())).first()

        cr = Glicko2(
            tau=float(self.tau),
            mu=self.default_rate,
            phi=self.default_deviation,
            sigma=float(self.default_volatility),
        ).create_rating

        return cr(r[0], r[1], r[2]) if r is not None else cr()

    @property
    def ranking(self):
        """Players sorted by their latest rate.

        :rtype: sequence
        :returns: a sorted list of tuples containing the
                  :py:class:`player <.Player>`,
                  its latest rate, deviation and volatility, and the number of rates
                  in this rating.
        """

        from . import Player
        from . import Rate

        sasess = object_session(self)
        assert sasess

        rt = Rate.__table__
        rta = rt.alias()
        rtc = rt.alias()

        lastrate = (
            select(func.max(rta.c.date))
            .where(rta.c.idrating == rt.c.idrating)
            .where(rta.c.idplayer == rt.c.idplayer)
        )

        ratecount = (
            select(func.count(rtc.c.idrate))
            .where(rtc.c.idrating == rt.c.idrating)
            .where(rtc.c.idplayer == rt.c.idplayer)
        )

        q = (
            select(
                rt.c.idplayer,
                rt.c.rate,
                rt.c.deviation,
                rt.c.volatility,
                ratecount.scalar_subquery().label('rates_count'),
            )
            .where(rt.c.idrating == self.idrating)
            .where(rt.c.date == lastrate.scalar_subquery())
            .order_by(rt.c.rate.desc())
        )

        rates: list[tuple[int, int, int, Decimal, int]] = sasess.execute(q).fetchall()

        return [
            (sasess.get_one(Player, idplayer), r, rd, rv, rc)
            for idplayer, r, rd, rv, rc in rates
        ]

    @property
    def time_span(self):
        "Return the time span of this rating."

        from . import Rate

        sasess = object_session(self)
        assert sasess

        rt = Rate.__table__

        timespan = select(func.min(rt.c.date), func.max(rt.c.date)).where(
            rt.c.idrating == self.idrating
        )
        return sasess.execute(timespan).one()

    def isPhantom(self, competitor: Competitor | None):
        """Determine whether the given `competitor` is actually a Phantom.

        :param competitor: a Competitor instance

        This is needed because someone uses a concrete player as Phantom,
        to customize its name (not everybody have a good sense of humor…)
        """

        if competitor is None:
            # The "real" Phantom
            return True

        phantomscore = competitor.tourney.phantomscore
        if (
            competitor.points == 0
            and competitor.totscore == 0
            and competitor.netscore % phantomscore == 0
        ):
            # Uhm, either a very very weak player, or a "named" Phantom, let's see: if he lost
            # all matches by the configured phantom score, then it is very probably a phantom
            cid = competitor.idcompetitor
            for m in competitor.tourney.matches:
                if m.idcompetitor1 == cid:
                    if m.score2 != phantomscore:
                        break
                elif m.idcompetitor2 == cid:
                    if m.score1 != phantomscore:
                        break
            else:
                return True

        return False

    def shouldConsiderTourney(self, tourney: Tourney):
        """Determine whether the given tourney should be considered.

        :param tourney: a Tourney instance

        Only singles using the Swiss System should be considered. Also, "online" tournaments
        are excluded.
        """

        return (
            tourney.system == 'swiss'
            and tourney.championship.playersperteam == 1
            and not tourney.championship.trainingboards
        )

    def _computeGlickoOutcomes(self, score1: int, score2: int) -> tuple[float, float]:
        # Standard Glicko, best suited to Chess matches

        if score1 > score2:
            outcome1 = WIN
            outcome2 = LOSS
        elif score1 == score2:
            outcome1 = DRAW
            outcome2 = DRAW
        else:
            outcome1 = LOSS
            outcome2 = WIN

        return outcome1, outcome2

    def _computeGuidoOutcomes(self, score1: int, score2: int) -> tuple[float, float]:
        # This is Guido Truffelli <truffelli.guido@gmail.com> adaptation to Carrom,
        # approved by dr. Glickman himself: use the whole range of values from 0 to 1,
        # not simply 0, 0.5 and 1.

        if score1 == 25 and score2 == 0:
            outcome1 = WIN
            outcome2 = LOSS
        elif score1 == 0 and score2 == 25:
            outcome1 = LOSS
            outcome2 = WIN
        elif score1 == score2:
            outcome1 = DRAW
            outcome2 = DRAW
        else:
            totalscore = score1 + score2
            outcome1 = score1 / totalscore
            outcome2 = score2 / totalscore

        return outcome1, outcome2

    def recompute(self, mindate=None, scratch=False):
        """Recompute the whole rating.

        :param mindate: either ``None`` or a date
        :param scratch: a boolean, True to recompute from scratch

        If `mindate` is given, recompute the rating ignoring the tourneys
        *before* that date.
        """

        from collections import defaultdict

        from . import Player
        from . import Rate

        if self.level == '0' or not self.tourneys:
            return

        try:
            compute_outcomes = getattr(
                self, '_compute%sOutcomes' % self.outcomes.capitalize()
            )
        except AttributeError:  # pragma: nocover
            raise AttributeError(
                'No %r method to compute match outcomes' % self.outcomes
            )

        logger.debug('Using the %r method to compute match outcomes', self.outcomes)

        firstdate = self.time_span[0]
        if scratch or (
            firstdate
            and (
                (mindate is None and self.tourneys[0].date < firstdate)
                or (mindate is not None and mindate < firstdate)
            )
        ):
            logger.debug('Recomputing %r from scratch', self)

            # TODO: find a more elegant way to do the following!
            # Non-inheriting ratings may contain historical rates, that does not have
            # a corresponding tourney, so we don't want to delete them...
            mindate = date(1900, 12, 31)
            if not self.inherit:
                rates = self.rates
                while rates and rates[-1].date > mindate:
                    rates.pop()
            else:
                self.rates = []
            mindate = None
        elif mindate:
            rates = self.rates
            while rates and rates[-1].date >= mindate:
                rates.pop()

        sasess = object_session(self)
        assert sasess

        logger.debug(
            'Glicko2 parameters: tau=%s mu=%s phi=%s sigma=%s',
            self.tau,
            self.default_rate,
            self.default_deviation,
            self.default_volatility,
        )

        glicko2 = Glicko2(
            tau=float(self.tau),
            mu=self.default_rate,
            phi=self.default_deviation,
            sigma=float(self.default_volatility),
        )

        rcache = {}
        phantom_p = self.isPhantom

        for tourney in self.tourneys:
            if mindate is not None and tourney.date < mindate:
                continue

            if not tourney.prized or not self.shouldConsiderTourney(tourney):
                continue

            logger.debug('Considering tourney %s', tourney)

            outcomes = defaultdict(list)

            for match in tourney.matches:
                # Ignore final matches, per Guido advice
                if match.final:
                    continue

                c1 = match.competitor1
                c2 = match.competitor2

                # Usually a match against the Phantom is recognizable by the fact that the
                # second competitor is not assigned, but some people insist in using a concrete
                # player to customize the name
                if phantom_p(c1) or phantom_p(c2):
                    # Skip matches against Phantom
                    continue

                outcome1, outcome2 = compute_outcomes(match.score1, match.score2)

                # Player 1
                occ = outcomes[c1.idplayer1]
                if c2.idplayer1 not in rcache:
                    rcache[c2.idplayer1] = self.getPlayerRating(
                        c2.player1, tourney.date
                    )
                    if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
                        logger.debug(
                            '%s rate is: %s',
                            sasess.get(Player, c2.idplayer1),
                            rcache[c2.idplayer1],
                        )
                occ.append((outcome1, rcache[c2.idplayer1]))

                # Player 2
                occ = outcomes[c2.idplayer1]
                if c1.idplayer1 not in rcache:
                    rcache[c1.idplayer1] = self.getPlayerRating(
                        c1.player1, tourney.date
                    )
                    if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
                        logger.debug(
                            '%s rate is: %s',
                            sasess.get(Player, c1.idplayer1),
                            rcache[c1.idplayer1],
                        )
                occ.append((outcome2, rcache[c1.idplayer1]))

            # If there are unrated players interpolate their rate
            if any(rcache[idplayer].is_default for idplayer in outcomes):
                logger.debug('Interpolating unrated players rate')
                interpolate_unrated(
                    rcache,
                    tourney.ranking,
                    glicko2,
                    phantom_p,
                    self.lower_rate,
                    self.higher_rate,
                )

            for idplayer in outcomes:
                current = rcache[idplayer]

                if logger.isEnabledFor(logging.DEBUG):  # pragma: nocover
                    logger.debug(
                        'Computing new rate for %s', sasess.get(Player, idplayer)
                    )
                    logger.debug('Player current rate: %s', current)
                    logger.debug('Player outcomes: %s', outcomes[idplayer])

                new = glicko2.rate(current, outcomes[idplayer])

                try:
                    pr = (
                        sasess.query(Rate)
                        .filter(Rate.idrating == self.idrating)
                        .filter(Rate.idplayer == idplayer)
                        .filter(Rate.date == tourney.date)
                        .one()
                    )
                except NoResultFound:
                    pr = Rate(idplayer=idplayer, date=tourney.date)
                    sasess.add(pr)
                    pr.rating = self

                pr.rate = max(new.rate, 800)
                pr.deviation = new.deviation
                pr.volatility = new.volatility

                rcache[idplayer] = new

                logger.debug(
                    'Recomputed rate=%s deviation=%s volatility=%s',
                    pr.rate,
                    pr.deviation,
                    pr.volatility,
                )

    def update(self, data, user_id, *, missing_only=False):
        for field in ('tau', 'default_volatility'):
            value = data.get(field, None)
            if isinstance(value, str):
                data[field] = Decimal(value)
        return super().update(data, user_id, missing_only=missing_only)

    def serialize(self, serializer: Serializer) -> SerializedRating:
        """Reduce a single rating to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this rating
        """

        simple: SerializedRating = {
            'guid': self._guid,
            'modified': self.modified,
            'description': self.description,
            'level': self.level,
            'inherit': self.inherit,
            'tau': str(self.tau),
            'default_rate': self.default_rate,
            'default_deviation': self.default_deviation,
            'default_volatility': str(self.default_volatility),
            'lower_rate': self.lower_rate,
            'higher_rate': self.higher_rate,
            'outcomes': self.outcomes,
        }
        if self.idowner:
            simple['owner'] = serializer.addUser(self.owner)
        if self.idclub:
            simple['club'] = serializer.addClub(self.club)

        return simple


def interpolate_unrated(cache, ranking, glicko2, phantom_p, lower_rate, higher_rate):
    """Interpolate the rate of unrated players from the ranking."""

    unrated = []

    sumx = sumy = sumxy = sumx2 = phantoms = 0

    for x, competitor in enumerate(ranking, 1):
        # Do not consider withdrawn players when their only match was against the phantom
        if phantom_p(competitor) or competitor.idplayer1 not in cache:
            phantoms += 1
            continue

        if cache[competitor.idplayer1].is_default:
            unrated.append((x, competitor.idplayer1))
        else:
            y = cache[competitor.idplayer1].rate
            sumx += x
            sumy += y
            sumxy += x * y
            sumx2 += x**2

    nrated = len(ranking) - phantoms - len(unrated)
    if nrated < 2:
        # If there are less than 2 rated players, arbitrarily consider
        # two players, the first with 2600pt the other with 1600pt
        nrated = 2
        sumx = 1 + len(ranking) - phantoms
        sumy = lower_rate + higher_rate
        sumxy = higher_rate + (len(ranking) - phantoms) * lower_rate
        sumx2 = 1 + (len(ranking) - phantoms) ** 2

    den = nrated * sumx2 - sumx**2
    m = float(nrated * sumxy - sumx * sumy) / den
    q = float(sumy * sumx2 - sumx * sumxy) / den

    for x, idplayer in unrated:
        cache[idplayer].update(glicko2.create_rating(mu=int(x * m + q + 0.5)))
