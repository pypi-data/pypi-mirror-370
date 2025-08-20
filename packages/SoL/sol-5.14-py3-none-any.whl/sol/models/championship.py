# -*- coding: utf-8 -*-
# :Project:   SoL -- The Championship entity
# :Created:   gio 27 nov 2008 13:53:28 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018, 2020, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import gettext
from ..i18n import translatable_string as _
from . import Base
from . import GloballyUnique
from .domains import boolean_t
from .domains import code_t
from .domains import description_t
from .domains import intid_t
from .domains import smallint_t
from .errors import OperationAborted
from .utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from .club import Club
    from .rating import Rating
    from .tourney import Tourney
    from .user import User


logger = logging.getLogger(__name__)


class SerializedChampionship(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Championship`."

    guid: str
    modified: datetime
    club: int
    description: str
    prizes: str
    couplings: str
    skipworstprizes: int
    playersperteam: int
    rating: NotRequired[int]
    owner: NotRequired[int]
    closed: NotRequired[bool]
    previous: NotRequired[int]
    trainingboards: NotRequired[int]


class Championship(GloballyUnique, Base):
    """A series of tournaments organized by the same club."""

    __tablename__ = 'championships'
    'Related table'

    @declared_attr.directive
    def __table_args__(cls) -> tuple[Any, ...]:
        return GloballyUnique.__table_args__(cls) + (
            Index('%s_uk' % cls.__tablename__, 'description', 'idclub', unique=True),
        )

    ## Columns

    idchampionship: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idchampionship', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Championship ID'),
            hint=_('Unique ID of the championship.'),
        ),
    )
    """Primary key."""

    idprevious: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('championships.idchampionship', name='fk_championship_previous'),
        nullable=True,
        info=dict(
            label=_('Previous championship ID'),
            hint=_('ID of the previous championship.'),
        ),
    )
    """Previous championship's ID."""

    idclub: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('clubs.idclub', name='fk_championship_club'),
        nullable=False,
        info=dict(
            label=_('Club ID'),
            hint=_('ID of the club the championship is organized by.'),
        ),
    )
    """Organizer :py:class:`club <.Club>`'s ID."""

    idrating: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey(
            'ratings.idrating', name='fk_championship_rating', ondelete='SET NULL'
        ),
        nullable=True,
        info=dict(
            label=_('Rating ID'),
            hint=_('ID of the default rating used by tourneys in this championship.'),
        ),
    )
    """Possible :py:class:`rating <.Rating>` ID, used as default value
    for the corresponding field when creating a new tourney."""

    idowner: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey('users.iduser', name='fk_championship_owner', ondelete='SET NULL'),
        nullable=True,
        info=dict(
            label=_('Owner ID'),
            hint=_('ID of the user that is responsible for this record.'),
        ),
    )
    """ID of the :py:class:`user <.User>` that is responsible for this record."""

    description: Mapped[str] = mapped_column(
        description_t,
        nullable=False,
        info=dict(
            label=_('Description'),
            hint=_('Description of the championship.'),
        ),
    )
    """Description of the championship."""

    prizes: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='fixed',
        info=dict(
            label=_('Prizes'),
            hint=_('Method used to assign final prizes.'),
            dictionary=dict(
                asis=_('Simple tourneys, no special prizes'),
                fixed=_('Fixed prizes: 18,16,14,13…'),
                fixed40=_('Fixed prizes: 1000,900,800,750…'),
                millesimal=_('Classic millesimal prizes'),
                centesimal=_('Centesimal prizes'),
            ),
        ),
    )
    """Kind of prize-giving.

    This is used to determine which method will be used to assign
    final prizes. It may be:

    `asis`
      means that the final prize is a plain integer number, monotonically decreasing down to 1
      starting from num-of-competitors: this is meant to give the chance of swapping
      competitors positions after tournament's final rounds, the `final prize` column won't
      even show up in the final ranking printout;

    `fixed`
      means the usual way, that is 18 points to the winner, 16 to the second, 14 to the third,
      13 to the fourth, …, 1 point to the 16th, 0 points after that;

    `fixed40`
      similar to `fixed`, but applied to best fourty scores starting from 1000:

        1. 1000
        2. 900
        3. 800
        4. 750
        5. 700
        6. 650
        7. 600
        8. 550
        9. 500
        10. 450
        11. 400
        12. 375
        13. 350
        14. 325
        15. 300
        16. 275
        17. 250
        18. 225
        19. 200
        20. 175
        21. 150
        22. 140
        23. 130
        24. 120
        25. 110
        26. 100
        27. 90
        28. 80
        29. 70
        30. 60
        31. 50
        32. 40
        33. 35
        34. 30
        35. 25
        36. 20
        37. 15
        38. 10
        39. 5
        40. 1

    `millesimal`
      is the classic method, that distributes a multiple of 1000/num-of-competitors;

    `centesimal`
      assigns 100 to the first ranked competitor, 1 to the last, linear interpolation
      to the other competitors.
    """

    skipworstprizes: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(
            label=_('Skip'),
            hint=_(
                'Number of worst results to skip in computing'
                ' the final ranking of the championship.'
            ),
            min=0,
            max=5,
        ),
    )
    """Number of worst results to skip in computing the ranking."""

    playersperteam: Mapped[int] = mapped_column(
        smallint_t,
        nullable=False,
        default=1,
        info=dict(
            label=_('Players'),
            hint=_('Number of players in each team, 1 for singles, 2 for doubles.'),
            min=1,
            max=4,
        ),
    )
    """Number of players per team."""

    closed: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Closed'),
            hint=_(
                'Should be activated once the championship'
                ' has been completed and no other'
                ' tourney can be associated with it.'
            ),
        ),
    )
    """Whether the championships is closed, and its ranking finalized."""

    couplings: Mapped[str | None] = mapped_column(
        code_t,
        nullable=True,
        default='serial',
        info=dict(
            label=_('Pairings'),
            hint=_('Default method used to pair competitors at each round.'),
            dictionary=dict(
                serial=_('Ranking order'),
                dazed=_('Cross ranking order'),
                staggered=_('Staggered ranking order'),
            ),
        ),
    )
    """Kind of pairing method used to build next round, used as default value
    for the corresponding field when creating a new tourney."""

    trainingboards: Mapped[int | None] = mapped_column(
        smallint_t,
        nullable=True,
        info=dict(
            label=_('Number of boards'),
            hint=_(
                'If set, it is the number of boards to play in a “Corona Carrom”'
                ' or online tourneys. Leave this blank for normal championships.'
            ),
            min=0,
            max=8,
        ),
    )
    """When specified, this is the number of boards that players must complete in a
    “Corona Carrom” tourney.
    """

    ## Relations

    club: Mapped[Club] = relationship('Club', back_populates='championships')
    """The :py:class:`club <.Championship>` that organize this championship."""

    next: Mapped[Championship] = relationship(
        'Championship',
        uselist=False,
        back_populates='previous',
        remote_side='Championship.idprevious',
        post_update=True,
    )
    """Next championship."""

    owner: Mapped[User] = relationship('User', back_populates='owned_championships')
    'The :py:class:`owner <.User>` of this record, `admin` when ``None``.'

    previous: Mapped[Championship] = relationship(
        'Championship',
        uselist=False,
        back_populates='next',
        remote_side='Championship.idchampionship',
        post_update=True,
    )
    """Previous championship."""

    rating: Mapped[Rating] = relationship('Rating', back_populates='championships')
    """The default :py:class:`rating <.Rating>` used by this championship."""

    tourneys: Mapped[list[Tourney]] = relationship(
        'Tourney',
        back_populates='championship',
        cascade='all, delete-orphan',
        order_by='Tourney.date',
    )
    """:py:class:`Tourneys <.Tourney>` in this championship."""

    @classmethod
    def check_insert(
        cls, session: Session, fields: dict[str, Any], user_id: str | int
    ) -> None:
        "Check description validity"

        from .club import Club
        from .club import clubusers

        try:
            desc = normalize(fields['description'])
        except KeyError:
            raise OperationAborted(
                _('For a new championship the "description" field is mandatory')
            )

        if not desc:
            raise OperationAborted(
                _('For a new championship the "description" field is mandatory')
            )

        if 'idclub' not in fields:
            raise OperationAborted(
                _('For a new championship you must select an existing club')
            )

        if user_id != 'admin':
            clubs = Club.__table__
            if not session.scalar(
                select(1).where(
                    exists()
                    .where(clubs.c.idclub == fields['idclub'])
                    .where(clubs.c.idowner == user_id)
                    | exists()
                    .where(clubusers.c.idclub == fields['idclub'])
                    .where(clubusers.c.iduser == user_id)
                )
            ):
                raise OperationAborted(
                    _(
                        'You are not allowed to add a championship to the'
                        ' selected club'
                    )
                )

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Check description validity"

        if 'description' in fields:
            desc = normalize(fields['description'])
            if not desc:
                raise OperationAborted(
                    _('The "description" field of a championship cannot be empty')
                )

    def caption(self, html=None, localized=True):
        return gettext(
            '$championship of $club',
            just_subst=not localized,
            mapping=dict(
                championship=self.description, club=self.club.caption(html, localized)
            ),
        )

    def ranking(self, limit=None, onlywomen=False):
        """Summarize the championship, collecting final prizes of the players.

        :param limit: the earliest date to consider
        :type limit: either ``None`` or a date instance
        :param onlywomen: whether only women should be considered
        :type onlywomen: a boolean
        :rtype: a tuple of two slots

        For each tuple of players collect the earned prize in each tourney of the championship,
        or zero if the players did not participate to a given event.

        `limit` and `onlywomen` are used by the general rankings, to consider only last year
        tourneys and to produce women ranking respectively.

        Results in a tuple of two items, the first being a list of three slots tuples,
        respectively the date, the description and the guid of a tourney, the second a list of
        tuples, sorted by total prize: each tuple contains five items, a tuple of players,
        their total prize, a list of their prizes sorted by date of event, the number of prizes
        and finally either `None` or a list of skipped prizes.
        """

        dates = []
        allprizes = {}
        for t in self.tourneys:
            if t.prized and (limit is None or t.date >= limit):
                prizes = t.championship.prizes
                dates.append((t.date, t.description, t.guid))
                for c in t.competitors:
                    if not onlywomen or c.player1.sex == 'F':
                        players = (c.player1, c.player2, c.player3, c.player4)
                        prizes = allprizes.setdefault(players, {})
                        prize = c.points if prizes == 'asis' else c.prize
                        prizes[(t.date, t.description)] = prize
        dates.sort()

        championship = []
        for players in allprizes:
            prizes = allprizes[players]
            nprizes = len(prizes)
            for date, desc, g in dates:
                if (date, desc) not in prizes:  # pragma: no cover
                    prizes[(date, desc)] = 0
            championship.append(
                (players, [prizes[(date, desc)] for date, desc, g in dates], nprizes)
            )

        totalprizes = []
        for players, prizes, nprizes in championship:
            swp = self.skipworstprizes
            if swp and limit is None and nprizes > swp:
                pts = prizes[:]
                pts.sort()
                skipped = pts[:swp]
                pts = pts[swp:]
            else:
                pts = prizes
                skipped = None
            totalprizes.append((players, sum(pts), prizes, nprizes, skipped))

        return dates, sorted(
            totalprizes,
            key=lambda i: (
                # Order by total points, number of tourneys, lastname, firstname
                -i[1],
                -i[3],
                [p and (p.lastname, p.firstname) for p in i[0]],
            ),
        )

    def serialize(self, serializer) -> SerializedChampionship:
        """Reduce a single championship to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this championship
        """

        simple: SerializedChampionship = {
            'guid': self.guid,
            'modified': self.modified,
            'club': serializer.addClub(self.club),
            'description': self.description,
            'prizes': self.prizes,
            'couplings': self.couplings or self.__class__.couplings.default.arg,
            'skipworstprizes': self.skipworstprizes,
            'playersperteam': self.playersperteam,
        }
        if self.idrating:
            simple['rating'] = serializer.addRating(self.rating)
        if self.idowner:
            simple['owner'] = serializer.addUser(self.owner)
        if self.closed:
            simple['closed'] = self.closed
        if self.previous:
            simple['previous'] = serializer.addChampionship(self.previous)
        if self.trainingboards:
            simple['trainingboards'] = self.trainingboards

        return simple
