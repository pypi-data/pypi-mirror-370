.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   mer 25 dic 2013 12:22:28 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2013, 2014, 2016 Lele Gaifax
..

Other windows
=============

.. _countdown:

.. figure:: countdown.png
   :figclass: float-right

   The countdown window.

Countdown
---------

This page shows a simple *countdown* widget that at determined states emits different *alarms*
(using SoundManager_): it's driven by the values :guilabel:`duration` and :guilabel:`prealarm`
of :ref:`tourney <tourneys management>`.

The countdown may be started (or restarted again) with the first button; alternatively you can
use the second button that will start the countdown after 15 seconds, so you can reach your own
table in time.

Close the countdown window or click on the third button when done: to prevent accidental
close, it asks for an explicit confirmation.

.. hint:: Given that the start time is sent back to SoL and stored in the database, should the
          computer be restarted for any reason, the countdown will be restored from the same
          instant.

          This allows also to open multiple instances of the countdown, possibly from different
          computers, for example when you would like to show the same countdown in a different
          room. Of course in this case the countdown must be started on one single host, while
          on the others it will sufficient to show the new one **after** the countdown has been
          started.

.. _soundmanager: http://schillmania.com/projects/soundmanager2/


.. _upload:

.. figure:: upload.png
   :figclass: float-right

   The upload window.

Upload
------

This very simple window allows the upload of whole tourneys data, as exported by another
instance of SoL. The new data won't clobber existing information though, only missing fields
will be updated of any existing entity.

Anybody can upload ``.sol`` (or ``.sol.gz``, the compressed version) archives. All
authenticated users but `guest` can upload ``.zip`` files with tourneys data, players emblems
and clubs portraits.

.. topic:: Exporting data

   Tourneys data can be exported with the :guilabel:`download` button on :ref:`tourneys
   <tourneys management>` and :ref:`championships <championships management>` windows: they are
   (possibly compressed) simple text files, in YAML__ format, which may be reloaded on another
   SoL instance or archived for security purposes. The archive created in this way contains all
   the specified tourneys as well as the data pertaining to all involved players, clubs and
   championships. It does **not** contain neither the emblems nor the portraits pictures.

   There is another way to export the whole database, that is *all* tourneys and *all* players
   (also those who never played) **and all** the referenced images. By visiting the URL::

     http://localhost:6996/bio/backup

   SoL will give you a ``ZIP`` archive containing all the above, that can be uploaded into
   another instance of SoL, effectively copying/updating almost all the information and related
   images stored on the source. This is clearly a much bigger archive that the one created with
   the method above, and should be used only migrating the whole database to a newer version of
   SoL, or when you want copy all the images at once.

__ http://www.yaml.org/
