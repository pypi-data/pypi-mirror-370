# -*- coding: utf-8 -*-
# :Project:   SoL -- Track players merges
# :Created:   sab 21 dic 2013 13:12:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ..i18n import translatable_string as _
from . import Base
from . import GloballyUnique
from .domains import intid_t
from .domains import name_t
from .domains import nickname_t

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player


logger = logging.getLogger(__name__)


class MergedPlayer(GloballyUnique, Base):
    """A player who has been merged into another."""

    __tablename__ = 'mergedplayers'
    'Related table.'

    @declared_attr.directive
    def __table_args__(cls):
        return GloballyUnique.__table_args__(cls) + (
            Index('%s_names' % cls.__tablename__, 'lastname', 'firstname', 'nickname'),
            Index('%s_idplayer' % cls.__tablename__, 'idplayer'),
        )

    ## Columns

    idmergedplayer: Mapped[int] = mapped_column(
        intid_t,
        Sequence('gen_idmergedplayer', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(
            label=_('Merge ID'),
            hint=_('Unique ID of the merged player.'),
        ),
    )
    """Primary key."""

    firstname: Mapped[str] = mapped_column(
        name_t,
        nullable=False,
        default='',
        info=dict(
            label=_('First name'),
            hint=_('First name of the player.'),
        ),
    )
    """Player's first name."""

    lastname: Mapped[str] = mapped_column(
        name_t,
        nullable=False,
        default='',
        info=dict(
            label=_('Last name'),
            hint=_('Last name of the player.'),
        ),
    )
    """Player's last name."""

    nickname: Mapped[str] = mapped_column(
        nickname_t,
        nullable=False,
        default='',
        info=dict(
            label=_('Nickname'),
            hint=_('Nickname of the player, for login and to disambiguate homonyms.'),
        ),
    )
    """Player's nickname, used also for login purposes."""

    idplayer: Mapped[int] = mapped_column(
        intid_t,
        ForeignKey('players.idplayer', name='fk_mergedplayer_player'),
        nullable=False,
        info=dict(
            label=_('Player ID'),
            hint=_('ID of the target player.'),
        ),
    )
    """Target :py:class:`player <.Player>`'s ID."""

    ## Relations

    player: Mapped[Player] = relationship('Player', back_populates='merged')
    """The :py:class:`player <.Player>` this has been merged into."""

    ## Methods

    def caption(self, html=None, localized=True):
        "Description of the player, made up concatenating his names."

        if self.lastname:
            oldname = f'{self.lastname} {self.firstname}'
        else:  # pragma: nocover
            oldname = self.guid

        newname = self.player.caption(html, localized=localized)
        return f'{oldname} -> {newname}'

    description = property(caption)
