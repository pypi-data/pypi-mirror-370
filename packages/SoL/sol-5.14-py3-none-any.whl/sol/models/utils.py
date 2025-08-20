# -*- coding: utf-8 -*-
# :Project:   SoL -- Utilities
# :Created:   mar 30 set 2008 15:21:56 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013, 2014, 2016, 2018, 2020, 2022-2024 Lele Gaifax
#

"""
Simple helper functions.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any

from . import Base

logger = logging.getLogger(__name__)


def asunicode(s: Any) -> str | None:
    """Force a string to be a unicode instance.

    :param s: any value
    :rtype: str

    If `s` is not already an unicode string, it is assumed to be a ``utf-8`` bytes string, and
    thus decoded to unicode and returned. Otherwise `s` is returned as is::

      >>> assert asunicode(None) is None
      >>> assert not isinstance(asunicode(b'ascii'), bytes)
    """

    if s is None:
        return None
    elif isinstance(s, bytes):
        return s.decode('utf-8')
    else:
        return str(s)


def normalize(s: str | None, title: bool | None = None) -> str | None:
    """Normalize the case of a string, removing spurious spaces.

    :param s: a string
    :param title: if `True` always titleize the string, if `False`
                  never do that, if `None` (default) only when the
                  input string is all lower case or all upper case
    :rtype: unicode

    ::

      >>> assert normalize(None) is None
      >>> print(normalize('lele gaifax'))
      Lele Gaifax
      >>> print(normalize('LELE'))
      Lele
      >>> print(normalize('LeLe', title=False))
      LeLe
    """

    if s is None:
        return None

    n = ' '.join(s.strip().split())
    if title is not False and (title is True or n == n.upper() or n == n.lower()):
        n = n.title()
    return n


def njoin(
    elts: Sequence[Any] | Generator[Any, None, None],
    stringify: Callable[[Any], str | None] = asunicode,
    localized: bool = True,
) -> str:
    """Given a sequence of items, concatenate them in a nice way.

    :param elts: a sequence of elements
    :param stringify: the stringification function applied to all elements,
                      by default coerced to `unicode`
    :param localized: a boolean flag to disable the translation of the final 'and'
    :rtype: unicode

    If `elts` is empty returns an empty unicode string; if it contains
    a single element, returns the stringified element; otherwise
    returns a unicode string composed by all but the last elements
    stringified and joined by a comma, followed by the localized
    version of `and` followed by the last element stringified::

      >>> print(njoin([1,2,3]))
      1, 2 and 3
      >>> print(njoin([1,2]))
      1 and 2
      >>> print(njoin([1]))
      1
      >>> assert njoin([]) == ''
      >>> print(njoin([1,2], stringify=lambda x: str(x*10)))
      10 and 20

    Note that *falsey* elements are skipped::

      >>> print(njoin(['first', None, False, '', 'last']))
      first and last

    but ``0`` (*zero*) isn't considered a *falsey* value::

      >>> print(njoin([1,0,2]))
      1, 0 and 2
    """

    from ..i18n import gettext

    elts = [stringify(e) for e in elts if e or (e == 0 and e is not False)]
    if not elts:
        return ''
    elif len(elts) == 1:
        return elts[0]
    else:
        last = elts[-1]
        if localized:
            # TRANSLATORS: this is the final "conjunction" used when joining multiple
            # statements, for example "x, y and z".
            and_ = ' %s ' % gettext('and')
        else:
            and_ = ' and '
        return ', '.join(elts[:-1]) + and_ + last


def entity_from_primary_key(pkname: str) -> Base:
    """Given the name of a primary key, return the mapped entity.

    :param pkname: the name of a primary key
    :rtype: a mapped class
    """

    for m in Base.registry.mappers:
        if len(m.primary_key) == 1 and m.primary_key[0].name == pkname:
            return m.class_
    raise ValueError('Unknown PK: %s' % pkname)


def table_from_primary_key(pkname: str):
    """Given the name of a primary key, return the related table.

    :param pkname: the name of a primary key
    :rtype: a SQLAlchemy table
    """

    from . import Base

    for t in Base.metadata.sorted_tables:
        if len(t.primary_key.columns) == 1 and pkname in t.primary_key.columns:
            return t
    raise ValueError('Unknown PK: %s' % pkname)


def changes_summary(changes: Mapping[str, tuple[Any, Any]]) -> str:
    """Format a set of changes into a nice string.

    :param changes: a mapping of field names to ``(oldvalue, newvalue)`` tuples
    :rtype: a string

      >>> print(changes_summary(dict(a=(None, 1))))
      changed a to 1
      >>> print(changes_summary(dict(a=(False, True))))
      changed a from False to True
      >>> print(changes_summary(dict(a=(0,1), b=('foo','bar'))))
      changed a from 0 to 1 and b from "foo" to "bar"
      >>> print(changes_summary(dict(a=(0,1), b=(None,'bar'), c=(True,None))))
      changed a from 0 to 1, b to "bar" and c from True to None
    """

    summary = []
    for field in sorted(changes):
        oldvalue, newvalue = changes[field]

        if oldvalue is None or oldvalue == '':
            oldvalue = False
        else:
            if isinstance(oldvalue, str):
                oldvalue = '"%s"' % oldvalue
            else:
                oldvalue = str(oldvalue)

        if isinstance(newvalue, str):
            newvalue = '"%s"' % newvalue
        else:
            newvalue = str(newvalue)

        if oldvalue is False:
            summary.append(f'{field} to {newvalue}')
        else:
            summary.append(f'{field} from {oldvalue} to {newvalue}')

    return 'changed ' + njoin(summary, localized=False)
