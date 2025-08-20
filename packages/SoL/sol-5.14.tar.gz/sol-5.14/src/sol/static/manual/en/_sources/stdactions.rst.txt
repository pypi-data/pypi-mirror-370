.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   gio 30 gen 2014 09:19:03 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2014 Lele Gaifax
..

Insert, delete and modify
-------------------------

.. figure:: modify.png
   :figclass: float-right

   Editing a record

.. _standard actions:

To the left of the menu at the top there are the following buttons:

:guilabel:`Add new`
  Adds a new record, opening a `insertion window`.

:guilabel:`Delete`
  Removes the selected record

:guilabel:`Modify`
  Open a `modify window` on the selected record

The latter action is also triggered with a double click on any of the
records.

The actual edits happen in another window that shows only the fields
that may be changed: below the form there are two buttons,
:guilabel:`Cancel` and :guilabel:`Confirm` and the latter is active
only when the changes are correctly validated.

All these operations do **not** cause an immediate change in the
database: the grid shows edited records with a *yellow* background,
new ones in *green* and removed ones in *red*. A little red triangle
appears in the top left corner of edited fields. At this point the two
actions near the top right corner of the window, :guilabel:`Confirm`
and :guilabel:`Restore`, get enabled and respectively let you confirm
all the changes or to forget them, reloading records from the
database.

.. warning:: Reloading the grid, or moving to a different page with
             the navigation bar, will cancel all not yet confirmed
             changes made so far!
