.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   mer 25 dic 2013 12:20:58 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2013, 2014, 2018, 2020 Lele Gaifax
..

Basic entities
==============

All basic entities share a similar looking window, that shows fourteen *records* at a time in a
*grid*.

At the top there's a menu specific to the grid, where some items may be disabled, for example
when it is mandatory to have a selection to execute a particular action. In general, you can
find almost the same items in the contextual menu you get with a right click of the mouse on a
record in the grid.

At the bottom there's a *pagination toolbar* with which the complete *dataset* may be
browsed. The actual number of records shown in a single page can be changed: this makes the
selection of players to be registered to a tourney easier, for example.

.. hint:: You can maximize the vertical dimension of any window by double clicking on the title
          bar. Double clicking on the page size value will adjust the number to fit current
          window size.

.. figure:: columns.png
   :figclass: float-right

   Visible columns selection

The grid by default shows a minimal set of fields, possibly just one, the *description* of the
entity. Clicking on the columns title reorder the items on that particular field, toggling
between *ascending* and *descending* order.

On the right border of each column's title there is a button that brings a popup menu that
allows selection of the sort order of the column, or which columns are visible or not.

.. toctree::
   :maxdepth: 2

   filtering
   stdactions
   users
   players
   clubs
   clubusers
   championships
   tourneys
   ratings
   playersrates
