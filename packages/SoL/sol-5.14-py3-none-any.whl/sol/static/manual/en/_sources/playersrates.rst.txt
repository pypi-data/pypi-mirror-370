.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   mar 04 mar 2014 19:31:21 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2014, 2016, 2018 Lele Gaifax
..

.. _players rates:

Players rates
-------------

.. index::
   pair: Players; Rates

Each :ref:`rating <glicko ratings management>` produces a series of rates for each player, one
for each tourney associated with that rating he participates to. The most recent rate of each
player compose a ranking that *weight* the mutual strength, even when the players did not meet
each other directly.

This ranking allows the generation of non-random pairing in the subsequent tourneys. As a
statistical byproduct it is possible to obtain the trend in time of the strength of the
players, as a graphical chart.

Menu actions
~~~~~~~~~~~~

:guilabel:`Chart`
  Shows a graphical chart of the historic trend of the rates of the selected players

:guilabel:`Print`
  Generate a PDF document with the ranking of the players rates
