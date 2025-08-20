# -*- coding: utf-8 -*-
# :Project:   SoL -- Data domains
# :Created:   mar 09 apr 2013 10:31:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013, 2014, 2016, 2018, 2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean
from sqlalchemy import CHAR
from sqlalchemy import Date as _Date
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode
from sqlalchemy import VARCHAR
from sqlalchemy.types import TypeDecorator


class Date(TypeDecorator):
    impl = _Date
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            value = value.date()
        return value


class Description(TypeDecorator):
    impl = Unicode
    cache_ok = True

    def process_bind_param(self, value, dialect):
        from .utils import asunicode
        from .utils import normalize

        return normalize(asunicode(value))


class Name(TypeDecorator):
    impl = Unicode
    cache_ok = True

    def process_bind_param(self, value, dialect):
        from .utils import asunicode
        from .utils import normalize

        return normalize(asunicode(value), True)


class NickName(TypeDecorator):
    impl = Unicode
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.strip()
        else:
            value = ''
        return value


class EMail(TypeDecorator):
    impl = Unicode
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.strip()
        else:
            value = ''
        return value


class PreciseDecimalNumber(TypeDecorator):
    """A decimal number with a fixed precision stored as an integer"""

    impl = Integer
    precisionfactor = 10**0

    def process_bind_param(self, value, dialect):
        if value is None:  # pragma: nocover
            return None

        if not isinstance(value, Decimal):
            value = Decimal(value)

        return int(value * self.precisionfactor)

    def process_result_value(self, value, dialect):
        if value is None:  # pragma: nocover
            return None
        else:
            return Decimal(value) / self.precisionfactor


class Prize(PreciseDecimalNumber):
    cache_ok = True
    precisionfactor = 10**2


class Volatility(PreciseDecimalNumber):
    cache_ok = True
    precisionfactor = 10**5


boolean_t = Boolean()
'A boolean value, either True or False'

code_t = VARCHAR(10)
'A string code'

date_t = Date()
'A date'

timestamp_t = DateTime()
'A date stamp'

description_t = Description(50)
'A fifty characters long description'

email_t = EMail(50, collation='NOCASE')
'An email address'

filename_t = Unicode(40)
'A file name'

flag_t = CHAR(1)
'A single character used as some sort of flag'

guid_t = CHAR(32)
'A globally unique id'

int_t = Integer()
'An integer value'

intid_t = Integer()
'An integer value, commonly used as the primary key'

language_t = CHAR(5)
'A ISO 639-1 language code, possibly country specific'

name_t = Name(50)
'A fifty characters long name'

nationality_t = CHAR(3)
'A ISO 3166 country code'

nickname_t = NickName(15)
'A short string used for nicknames'

password_t = VARCHAR(128)
'A password hash'

prize_t = Prize()
'A number with two decimal digits, but stored as an integer'

smallint_t = SmallInteger()
'A small integer number'

url_t = VARCHAR(128)
'A web URL'

volatility_t = Volatility()
'A number with five decimal digits, but stored as an integer'
