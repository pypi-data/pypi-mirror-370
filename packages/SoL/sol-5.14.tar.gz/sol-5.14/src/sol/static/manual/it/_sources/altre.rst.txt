.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   mer 25 dic 2013 12:20:17 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2013, 2014, 2016 Lele Gaifax
..

Altre finestre
==============

.. _countdown:

.. figure:: countdown.png
   :figclass: float-right

   Conto alla rovescia.

Conto alla rovescia
-------------------

Questa pagina mostra un semplice *conto alla rovescia* che emette degli *allarmi* in
determinati momenti (utilizzando SoundManager_): la durata è determinata dai valori impostati
in :guilabel:`durata` e :guilabel:`preavviso` sul :ref:`torneo <gestione tornei>`.

Il *conto alla rovescia* può essere attivato usando il primo pulsante in basso; un altro modo
di farlo è usando il secondo pulsante che farà partire il tempo dopo 15 secondi, dando così
modo all'operatore di raggiungere il proprio tavolo di gioco.

Chiudere la finestra con il conto alla rovescia (o usa il terzo pulsante in basso) per
annullare l'allarme: per prevenire chiusure accidentali, viene richiesta una conferma
esplicita.

.. hint:: Dal momento che l'istante di attivazione del conto alla rovescia viene inviato a SoL
          e memorizzato nel database, se per qualsiasi ragione il computer dovesse essere fatto
          ripartire il conto alla rovescia verrà ripristinato dal medesimo istante.

          Questo consente inoltre di mostrare più pagine con il conteggio, anche su computer
          diversi, ad esempio quando si desideri mostrare lo stesso conto alla rovescia in
          stanze diverse.  Ovviamente in questo caso il conto alla rovescia deve essere fatto
          partire da una sola postazione, mentre sulle altre basterà richiedere la nuova
          visualizzazione **dopo** aver fatto partire il conto alla rovescia.

.. _soundmanager: http://schillmania.com/projects/soundmanager2/
.. _caricamento:

.. figure:: caricamento.png
   :figclass: float-right

   Caricamento dati torneo.

Caricamento
-----------

Con questa semplice finestra è possibile caricare i dati di un intero torneo, provenienti da
un'altra istanza di SoL. I nuovi dati non sovrascriveranno quelli esistenti, delle entità
preesistenti verranno aggiornati solo i dati mancanti.

Chiunque può caricare archivi ``.sol`` (o la versione compressa ``.sol.gz``). Gli utenti
autenticati, tranne l'utente `guest`, possono caricare anche archivi ``.zip`` con i dati dei
tornei insieme ai ritratti dei giocatori e agli stemmi dei club.

.. topic:: Esportazione dei dati

   I dati dei tornei possono essere estratti con il pulsante :guilabel:`Scarica` nelle gestioni
   dei :ref:`tornei <gestione tornei>` e dei :ref:`campionati <gestione campionati>`: si tratta
   di file di testo, in formato YAML__ (eventualmente compresso), che possono essere ricaricati
   in un'altra istanza di SoL, piuttosto che archiviati per sicurezza. L'archivio creato in
   questo modo contiene tutti i tornei specificati così come i dati relativi a tutti i
   giocatori, club e campionati coinvolti. **Non** contiene nessuna immagine, né ritratti né
   stemmi.

   Un altro modo consente di esportare l'intero database, cioè *tutti* i tornei e *tutti* i
   giocatori (indipendentemente se abbiano partecipato a un torneo o meno) **e tutte** le
   immagini associate. Visitando l'indirizzo::

     http://localhost:6996/bio/backup

   si otterrà un archivio ``ZIP`` contenente tutto quanto, che potrà essere caricato in
   un'altra installazione di SoL, copiando/aggiornando così praticamente tutte le informazioni
   memorizzate e le relative immagini. Chiaramente l'archivio prodotto in questo modo avrà
   dimensioni molto maggiori del precedente: questo metodo è raccomandato solo per migrare
   l'intero database a una nuova versione di SoL, oppure qualora si desideri copiare tutte le
   immagini in un colpo solo.

__ http://www.yaml.org/
