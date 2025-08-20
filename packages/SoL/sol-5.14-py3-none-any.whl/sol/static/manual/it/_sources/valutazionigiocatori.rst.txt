.. -*- coding: utf-8 -*-
.. :Project:   SoL
.. :Created:   dom 19 gen 2014 09:28:50 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2014 Lele Gaifax
..

.. _valutazioni giocatori:

Valutazioni dei giocatori
-------------------------

.. index::
   pair: Giocatori; Valutazioni

Ogni :ref:`valutazione <gestione valutazioni glicko>` produce una serie di valutazioni per ogni
singolo giocatore coinvolto nei tornei associati, una per ogni torneo. La più recente
valutazione di ogni giocatore forma appunto una sorta di classifica che riesce a misurare la
forza reciproca dei vari giocatori, anche quando questi non si sono mai incontrati
direttamente.

.. figure:: valutazionigiocatori.png
   :figclass: float-right

   Valutazioni giocatori

Questo permette di avere una base non casuale per generare gli abbinamenti nei tornei
successivi. Come sotto prodotto statistico è possibile ottenere l'andamento nel tempo della
*forza* dei giocatori, in forma di grafico.


Voci del menu
~~~~~~~~~~~~~

.. figure:: grafico.png
   :figclass: float-left

   Grafico valutazioni

:guilabel:`Grafico`
  Mostra un grafico sull'andamento storico delle valutazioni dei
  giocatori selezionati

:guilabel:`Stampa`
  Genera un documento PDF stampabile con la classifica delle
  valutazioni dei giocatori
