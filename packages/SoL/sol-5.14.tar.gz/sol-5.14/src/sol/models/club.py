# -*- coding: utf-8 -*-
# :Project:   SoL -- The Club entity
# :Created:   gio 27 nov 2008 13:49:40 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013, 2014, 2016, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy import Table
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import country_name
from ..i18n import translatable_string as _
from . import Base
from . import GloballyUnique
from .domains import boolean_t
from .domains import code_t
from .domains import description_t
from .domains import email_t
from .domains import filename_t
from .domains import intid_t
from .domains import nationality_t
from .domains import url_t
from .errors import OperationAborted
from .utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .championship import Championship
    from .player import Player
    from .rating import Rating
    from .tourney import Tourney
    from .user import User


logger = logging.getLogger(__name__)


clubusers = Table(
    'clubusers',
    Base.metadata,
    Column(
        'idclub',
        intid_t,
        ForeignKey('clubs.idclub', name='fk_clubuser_club', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        info=dict(
            label=_('Club ID'),
            hint=_('ID of the club.'),
        ),
    ),
    Column(
        'iduser',
        intid_t,
        ForeignKey('users.iduser', name='fk_clubuser_user', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        index=True,
        info=dict(
            label=_('User ID'),
            hint=_('ID of the user.'),
        ),
    ),
)


class SerializedClub(TypedDict):
    "A plain dictionary representing an exported :py:class:`.Club`."

    guid: str
    modified: datetime
    description: str
    prizes: str
    couplings: str
    rating: NotRequired[int]
    owner: NotRequired[int]
    emblem: NotRequired[str]
    nationality: NotRequired[str]
    siteurl: NotRequired[str]
    email: NotRequired[str]
    isfederation: NotRequired[bool]
    users: NotRequired[list[int]]


class Club(GloballyUnique, Base):
    """A club, which organizes championships of tourneys."""

    __tablename__ = 'clubs'
    'Related table'

    @declared_attr.directive
    def __table_args__(cls):
        return GloballyUnique.__table_args__(cls) + (
            Index('%s_uk' % cls.__tablename__, 'description', unique=True),
        )

    ## Columns

    idclub: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idclub', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Club ID'),
            hint=_('Unique ID of the club.'),
        ),
    )
    """Primary key."""

    idrating: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey(
            'ratings.idrating',
            use_alter=True,
            name='fk_club_rating',
            ondelete='SET NULL',
        ),
        nullable=True,
        info=dict(
            label=_('Rating ID'),
            hint=_(
                'ID of the default rating used by championships organized by this'
                ' club.'
            ),
        ),
    )
    """Possible :py:class:`rating <.Rating>` ID, used as default value
    for the corresponding field when creating a new championship."""

    idowner: Mapped[int | None] = mapped_column(
        intid_t,
        ForeignKey(
            'users.iduser', use_alter=True, name='fk_club_owner', ondelete='SET NULL'
        ),
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
        info=dict(label=_('Description'), hint=_('Description of the club.')),
    )
    """Description of the club."""

    emblem: Mapped[str | None] = mapped_column(
        filename_t,
        nullable=True,
        info=dict(
            label=_('Emblem'),
            hint=_('File name of the PNG, JPG or GIF logo of the club.'),
        ),
    )
    """Logo of the club, used on badges.

    This is just the filename, referencing a picture inside the
    ``sol.emblems_dir`` directory.
    """

    nationality: Mapped[str] = mapped_column(
        nationality_t,
        nullable=False,
        default='wrl',
        info=dict(label=_('Country'), hint=_('Nationality of the club.')),
    )
    """`ISO country code <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3>`_
    to compute national rankings."""

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
    for the corresponding field when creating a new championship."""

    prizes: Mapped[str] = mapped_column(
        code_t,
        nullable=False,
        default='fixed',
        info=dict(
            label=_('Prizes'),
            hint=_('Default method used to assign final prizes.'),
            dictionary=dict(
                asis=_('Simple tourneys, no special prizes'),
                fixed=_('Fixed prizes: 18,16,14,13…'),
                fixed40=_('Fixed prizes: 1000,900,800,750…'),
                millesimal=_('Classic millesimal prizes'),
            ),
        ),
    )
    """Kind of prize-giving, used as default value for the corresponding
    field when creating a new championship.

    This is used to determine which method will be used to assign
    final prizes. It may be:

    `asis`
      means that the final prize is the same as the competitor's points;

    `fixed`
      means the usual way, that is 18 points to the winner, 16 to the
      second, 14 to the third, 13 to the fourth, …, 1 point to the
      16th, 0 points after that;

    `fixed40`
      similar to `fixed`, but applied to best fourty scores starting
      from 1000:

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
      is the classic method, that distributes a multiple of
      1000/num-of-competitors."""

    siteurl: Mapped[str | None] = mapped_column(
        url_t,
        nullable=True,
        info=dict(
            label=_('Website'),
            hint=_('URL of the web site of the club.'),
        ),
    )
    """Web site URL."""

    email: Mapped[str | None] = mapped_column(
        email_t,
        nullable=True,
        info=dict(
            label=_('Email'),
            hint=_('Email address of the club.'),
        ),
    )
    """Email address of the club."""

    isfederation: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Federation'),
            hint=_('Whether the club is also a federation.'),
        ),
    )
    """Flag indicating whether the club is also a federation."""

    ## Relations

    associated_players: Mapped[list[Player]] = relationship(
        'Player',
        back_populates='club',
        primaryjoin='Player.idclub==Club.idclub',
        passive_updates=False,
    )
    """Players associated with this club."""

    championships: Mapped[list[Championship]] = relationship(
        'Championship',
        back_populates='club',
        cascade='all, delete-orphan',
        order_by='Championship.description',
    )
    """:py:class:`Championships <.Championship>` organized by this club."""

    federated_players: Mapped[list[Player]] = relationship(
        'Player',
        back_populates='federation',
        primaryjoin='Player.idfederation==Club.idclub',
        passive_updates=False,
    )
    """Players associated with this federation."""

    hosted_tourneys: Mapped[list[Tourney]] = relationship(
        'Tourney', back_populates='hosting_club'
    )
    """:py:class:`Tourneys <.Tourney> hosted by this club.`"""

    owner: Mapped[User | None] = relationship(
        'User', back_populates='owned_clubs', primaryjoin='Club.idowner==User.iduser'
    )
    """The :py:class:`owner <.User>` of this record, `admin` when ``None``."""

    rating: Mapped[Rating | None] = relationship(
        'Rating', foreign_keys=[idrating], post_update=True
    )
    """Default :py:class:`Ratings <.Rating>` used by this club's championships."""

    ratings: Mapped[list[Rating]] = relationship(
        'Rating', back_populates='club', primaryjoin='Rating.idclub == Club.idclub'
    )
    """:py:class:`Ratings <.Rating>` reserved for tourneys organized by this club."""

    users = relationship('User', secondary=clubusers)

    ## Methods

    @classmethod
    def check_insert(
        cls, session: Session, fields: dict[str, Any], user_id: str | int
    ) -> None:
        "Check description validity."

        try:
            desc = normalize(fields['description'])
        except KeyError:
            raise OperationAborted(
                _('For a new club the "description" field is mandatory')
            )
        if not desc:
            raise OperationAborted(
                _('For a new club the "description" field is mandatory')
            )

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Check description validity."

        if 'description' in fields:
            desc = normalize(fields['description'])
            if not desc:
                raise OperationAborted(
                    _('The "description" field of a club cannot be empty')
                )

    @property
    def country(self):
        "The name of the club's country."

        return country_name(self.nationality)

    def countChampionships(self):
        """Return the number of championships organized by this club."""

        from .championship import Championship

        sasess = object_session(self)
        assert sasess
        ct = Championship.__table__
        return sasess.scalar(
            select(func.count(ct.c.idchampionship)).where(ct.c.idclub == self.idclub)
        )

    def countPlayers(self):
        """Return the number of players associated to this club."""

        from .player import Player

        sasess = object_session(self)
        assert sasess
        pt = Player.__table__
        return sasess.scalar(
            select(func.count(pt.c.idplayer)).where(
                or_(pt.c.idclub == self.idclub, pt.c.idfederation == self.idclub)
            )
        )

    def serialize(self, serializer: Serializer) -> SerializedClub:
        """Reduce a single club to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this club
        """

        simple: SerializedClub = {
            'guid': self.guid,
            'modified': self.modified,
            'description': self.description,
            'prizes': self.prizes,
            'couplings': self.couplings or self.__class__.couplings.default.arg,
        }
        if self.idrating:
            simple['rating'] = serializer.addRating(self.rating)
        if self.idowner:
            simple['owner'] = serializer.addUser(self.owner)
        if self.emblem:
            simple['emblem'] = self.emblem
        if self.nationality:
            simple['nationality'] = self.nationality
        if self.siteurl:
            simple['siteurl'] = self.siteurl
        if self.email:
            simple['email'] = self.email
        if self.isfederation:
            simple['isfederation'] = self.isfederation
        if self.users:
            susers = simple['users'] = []
            for user in self.users:
                susers.append(serializer.addUser(user))

        return simple
