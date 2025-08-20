# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   mar 18 nov 2008 14:08:52 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008, 2010, 2013, 2014, 2018, 2022, 2024 Lele Gaifax
#

from __future__ import annotations

from translationstring import TranslationString


class OperationAborted(RuntimeError):
    "Exception raised on operation errors."

    def __str__(self):
        message = self.message
        if isinstance(message, TranslationString):  # pragma: no cover
            message = message.interpolate()
        return message

    @property
    def message(self):
        return self.args[0]


class LoadError(OperationAborted):
    "Exception raised on load operations."


class TourneyAlreadyExistsError(LoadError):
    "Exception raised trying to load an already existing tourney."

    def __init__(self, message, tourney):
        super().__init__(message)
        self.tourney = tourney


class UnauthorizedOperation(OperationAborted):
    "Exception raised trying to modify a record not owned."


class InvalidUserArgument(OperationAborted):
    "The operation is not valid, due to bad user arguments."
