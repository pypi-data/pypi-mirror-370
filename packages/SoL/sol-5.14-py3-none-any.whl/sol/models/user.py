# -*- coding: utf-8 -*-
# :Project:   SoL -- The User entity
# :Created:   mar 10 lug 2018 07:42:14 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict

from nacl import pwhash
from nacl.exceptions import InvalidkeyError
from pyramid.threadlocal import get_current_registry
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from typing_extensions import NotRequired  # 3.11

from ..i18n import ngettext
from ..i18n import translatable_string as _
from . import Base
from .domains import boolean_t
from .domains import email_t
from .domains import flag_t
from .domains import intid_t
from .domains import language_t
from .domains import name_t
from .domains import nationality_t
from .domains import password_t
from .domains import timestamp_t
from .errors import OperationAborted
from .rating import Rating
from .utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from .bio import Serializer
    from .championship import Championship
    from .club import Club
    from .player import Player
    from .tourney import Tourney


logger = logging.getLogger(__name__)


NULL_PASSWORD = b'*'
'The "empty" password marker.'


class SerializedUser(TypedDict):
    "A plain dictionary representing an exported :py:class:`.User`."

    created: datetime
    email: str
    firstname: str
    lastname: str
    ownersadmin: bool
    playersmanager: bool
    nationalliable: NotRequired[str]
    maxratinglevel: str
    state: str
    language: NotRequired[str]
    lastlogin: NotRequired[datetime]


def naive_current_uct_timestamp():
    "Equivalent of deprecated ``datetime.utcnow()``."

    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """A single user of the system."""

    __tablename__ = 'users'
    'Related table.'

    @declared_attr.directive
    def __table_args__(cls):
        return (Index('%s_uk' % cls.__tablename__, 'email', unique=True),)

    ## Columns

    iduser: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_iduser', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('User ID'),
            hint=_('Unique ID of the user.'),
        ),
    )
    """Primary key."""

    created: Mapped[datetime] = mapped_column(
        timestamp_t,
        nullable=False,
        default=naive_current_uct_timestamp,
        info=dict(
            label=_('Created'),
            hint=_('Timestamp of record creation.'),
            type='date',
            timestamp=True,
        ),
    )
    """Timestamp of record creation."""

    email: Mapped[str] = mapped_column(
        email_t,
        nullable=False,
        info=dict(
            label=_('Email'),
            hint=_('Email address of the user, used also as login name.'),
        ),
    )
    """Email address of the user."""

    firstname: Mapped[str] = mapped_column(
        name_t,
        nullable=False,
        info=dict(
            label=_('First name'),
            hint=_('First name of the user.'),
        ),
    )
    """User's first name."""

    lastname: Mapped[str] = mapped_column(
        name_t,
        nullable=False,
        info=dict(
            label=_('Last name'),
            hint=_('Last name of the user.'),
        ),
    )
    """User's last name."""

    _password: Mapped[bytes] = mapped_column(
        password_t,
        name='password',
        nullable=False,
        default=NULL_PASSWORD,
        info=dict(
            label=_('Password'),
            hint=_('Login password of the user.'),
        ),
    )
    """Crypted password."""

    language: Mapped[str | None] = mapped_column(
        language_t,
        nullable=True,
        info=dict(
            label=_('Language'),
            hint=_('The code of the preferred language by the user.'),
        ),
    )
    """The `ISO code <http://en.wikipedia.org/wiki/ISO_639-1>`_ of the preferred
       language of the user."""

    ownersadmin: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Owners admin'),
            hint=_('Whether the user can change ownership of other items.'),
        ),
    )
    """Whether the user can change ownership of other items."""

    playersmanager: Mapped[bool] = mapped_column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(
            label=_('Players manager'),
            hint=_('Whether the user can add, edit and remove players.'),
        ),
    )
    """Whether the user can manage players."""

    nationalliable: Mapped[str] = mapped_column(
        nationality_t,
        nullable=True,
        info=dict(
            label=_('National liable'),
            hint=_(
                'Whether the user is allowed to edit players and clubs of a'
                ' particular country, even those owned by somebody else.'
            ),
        ),
    )
    """
    `ISO country code <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3>`_
    of the country the user is responsible for, and thus can edit players and
    clubs, even when owned by a different user.
    """

    maxratinglevel: Mapped[str] = mapped_column(
        flag_t,
        nullable=False,
        default='3',
        info=dict(
            label=_('Max rating level'),
            hint=_('The highest level of rating available to this user.'),
            dictionary={
                level: desc
                for level, desc in Rating.level.info['dictionary'].items()
                if level != '0'
            },
        ),
    )
    """The highest level of rating available to this user."""

    state: Mapped[str] = mapped_column(
        flag_t,
        nullable=False,
        default='R',
        info=dict(
            label=_('Status'),
            hint=_('The status of the user, only confirmed users can login.'),
            dictionary=dict(
                R=_('Registered'),
                C=_('Confirmed'),
                S=_('Suspended'),
            ),
        ),
    )
    """The status of the user: ``R`` means *registered*, ``C`` means *confirmed*,
       ``S`` means *suspended*."""

    lastlogin: Mapped[datetime | None] = mapped_column(
        timestamp_t,
        nullable=True,
        info=dict(
            label=_('Last login'),
            hint=_('Timestamp of the last successful login.'),
            type='date',
            timestamp=True,
        ),
    )
    """The timestamp of the last successful login, if any."""

    ## Relations

    owned_championships: Mapped[list[Championship]] = relationship(
        'Championship', back_populates='owner'
    )
    """List of owned :py:class:`championships <.Championship>`."""

    owned_clubs: Mapped[list[Club]] = relationship('Club', back_populates='owner')
    """List of owned :py:class:`clubs <.Club>`."""

    owned_players: Mapped[list[Player]] = relationship('Player', back_populates='owner')
    """List of owned :py:class:`players <.Player>`."""

    owned_ratings: Mapped[list[Rating]] = relationship('Rating', back_populates='owner')
    """List of owned :py:class:`ratings <.Rating>`."""

    owned_tourneys: Mapped[list[Tourney]] = relationship(
        'Tourney', back_populates='owner'
    )
    """List of owned :py:class:`tourneys <.Tourney>`."""

    ## Methods

    @classmethod
    def check_insert(
        cls, session: Session, fields: dict[str, Any], user_id: str | int
    ) -> None:
        "Prevent duplicated user."

        from pyramid.threadlocal import get_current_registry

        try:
            lname = normalize(fields['lastname'])
            fname = normalize(fields['firstname'])
            email = fields['email']
            if email:
                email = email.strip()
            password = fields['password']
            if password:
                password = password.strip()
        except KeyError:
            raise OperationAborted(
                _(
                    'For a new user "firstname", "lastname", "email" and'
                    ' "password" fields are mandatory'
                )
            )
        if not lname or not fname or not email or not password:
            raise OperationAborted(
                _(
                    'For a new user "firstname", "lastname", "email" and'
                    ' "password" fields are mandatory'
                )
            )

        settings = get_current_registry().settings
        if settings is None:  # unittests
            settings = {'sol.admin.user': 'admin', 'sol.guest.user': 'guest'}
        reservedemails = (
            settings.get('sol.admin.user'),
            settings.get('sol.guest.user'),
        )
        if email in reservedemails:
            raise OperationAborted(
                _(
                    '“$email” is reserved, please use a different email',
                    mapping=dict(email=email),
                )
            )

        try:
            q = select(User).where(User.email == email, User.password != NULL_PASSWORD)
            session.scalars(q).one()
        except NoResultFound:
            pass
        else:
            raise OperationAborted(
                _(
                    'The user “$email” already exists, please use a different email',
                    mapping=dict(email=email),
                )
            )

        if len(password) < 6:
            raise OperationAborted(_('Password is too weak, use a longer one'))

    def check_update(self, fields: dict[str, Any], user_id: str | int) -> None:
        "Perform any check before updating the instance."

        if 'lastname' in fields:
            lname = normalize(fields['lastname'])
            if not lname:
                raise OperationAborted(
                    _('The "lastname" field of a user cannot be empty')
                )

        if 'firstname' in fields:
            fname = normalize(fields['firstname'])
            if not fname:
                raise OperationAborted(
                    _('The "firstname" field of a user cannot be empty')
                )

        if 'password' in fields:
            password = fields['password']
            if password:
                password = password.strip()
                if password != NULL_PASSWORD and len(password) < 6:
                    raise OperationAborted(_('Password is too weak, use a longer one'))
            else:
                raise OperationAborted(_('Please provide a valid "password"'))

        if 'email' in fields:
            email = fields['email']
            if email:
                email = email.strip()
                if not email:
                    raise OperationAborted(_('Please provide a valid "email" address'))
            else:
                raise OperationAborted(_('Please provide a valid "email" address'))

            settings = get_current_registry().settings
            if settings is None:  # unittests
                settings = {'sol.admin.user': 'admin', 'sol.guest.user': 'guest'}
            reservedemails = (
                settings.get('sol.admin.user'),
                settings.get('sol.guest.user'),
            )
            if email in reservedemails:
                raise OperationAborted(
                    _(
                        '“$email” is reserved, please use a different email',
                        mapping=dict(email=email),
                    )
                )

            sasess = object_session(self)
            assert sasess

            try:
                q = select(User).where(
                    User.email == email,
                    User.password != NULL_PASSWORD,
                    User.iduser != self.iduser,
                )
                sasess.scalars(q).one()
            except NoResultFound:
                pass
            else:
                raise OperationAborted(
                    _(
                        'The user “$email” already exists, please use a different email',
                        mapping=dict(email=email),
                    )
                )

    def delete(self):
        "Prevent deletion if this user owns something."

        from . import Base

        sasess = object_session(self)
        assert sasess

        for table in Base.metadata.tables.values():
            if 'idowner' in table.c:
                q = select(func.count()).where(table.c.idowner == self.iduser)
                count = sasess.scalar(q)
                if count:
                    raise OperationAborted(
                        ngettext(
                            'Deletion not allowed: $user owns $count record in table "$table"!',
                            'Deletion not allowed: $user owns $count records in table "$table"!',
                            count,
                            mapping=dict(
                                user=self.caption(html=False),
                                table=table.name,
                                count=count,
                            ),
                        )
                    )

        super().delete()

    @hybrid_property
    def password(self) -> bytes | None:
        """Return the hashed password of the user."""

        password: bytes | None = self._password
        if password == NULL_PASSWORD:
            password = None
        return password

    @password.inplace.setter
    def _set_password(self, value: bytes | str | None) -> None:
        """Change the password of the user.

        :param value: the raw password, in clear
        """

        if value:
            value = value.strip()
            if value:
                if value != NULL_PASSWORD:
                    # Should never happen, but just in case
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    self._password = pwhash.str(value)
                else:
                    self._password = NULL_PASSWORD
            else:
                self._password = NULL_PASSWORD
        else:
            self._password = NULL_PASSWORD

    def check_password(self, raw_password: bytes | str) -> bool:
        """Check the password.

        :param raw_password: the raw password, in clear
        :rtype: boolean

        Return ``True`` if the `raw_password` matches the user's
        password, ``False`` otherwise.
        """

        if self.state == 'C' and raw_password:
            raw_password = raw_password.strip()
            if not raw_password:
                return False
            if isinstance(raw_password, str):
                raw_password = raw_password.encode('utf-8')
            password = self.password
            if password is not None:
                if isinstance(password, str):
                    password = password.encode('utf-8')
                try:
                    return pwhash.verify(password, raw_password)
                except InvalidkeyError:
                    return False

        return False

    def caption(self, html=None, localized=True):
        "Description of the user, made up concatenating his names."

        result = f'{self.lastname} {self.firstname}'
        if self.state == 'C':
            result += f' \N{E-MAIL SYMBOL} {self.email}'
        return result

    description = property(caption)

    def serialize(self, serializer: Serializer) -> SerializedUser:
        """Reduce a single user to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this user
        """

        simple: SerializedUser = {
            'created': self.created,
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'nationalliable': self.nationalliable,
            'ownersadmin': self.ownersadmin,
            'playersmanager': self.playersmanager,
            'maxratinglevel': self.maxratinglevel,
            'state': self.state,
        }
        if self.language:
            simple['language'] = self.language
        if self.lastlogin:
            simple['lastlogin'] = self.lastlogin

        return simple
