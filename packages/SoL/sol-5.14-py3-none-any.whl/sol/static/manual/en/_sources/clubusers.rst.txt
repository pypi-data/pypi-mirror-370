.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   dom 19 gen 2020, 09:16:03
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2020 Lele Gaifax
..

.. _club-users association management:

Club's users association management
-----------------------------------

.. index::
   triple: Clubs; Users; Associations

In SoL 4, an user may create new *championships*, *ratings* and *tournaments* related to the
clubs he owns (that usually means the ones created by him). In some cases, in particular for
*federations*, it may be desirable to permit that to other users as well.

By right clicking on a particular row of the :ref:`clubs management` table, the owner of the
club (or the administrator) will find a :guilabel:`Users` action that opens the following
window:

.. figure:: clubusers.png

   Club's users management

It lists all :ref:`confirmed <users status>` users, with a *checkbox* next to each one that
tells whether the user is currently associated with the club or not: as said, only the checked
ones will be able to create, say, a new tournament linked to the club.
