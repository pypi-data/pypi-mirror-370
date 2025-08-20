## -*- coding: utf-8 -*-
## :Project:   SoL -- Pre countdown page
## :Created:   lun 02 mag 2016 09:00:56 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2016, 2024 Lele Gaifax
##

<!DOCTYPE html>

<html>
  <head>
    <title>${_('SoL Countdown')}</title>

    <meta charset="utf-8">

    <link rel="stylesheet" type="text/css" href="/static/css/countdown.css">
    <script src="/static/clock/countdown.js"></script>
    <script src="/static/clock/soundmanager2.js"></script>

    <!-- Sounds initialization -->
    <script>
     soundManager.setup({
         url: '/static/clock/', // directory where SM2 .SWFs live
         debugMode: false,
         onready: function() {
             soundManager.createSound('prealarm','/static/sounds/prealarm.ogg');
             soundManager.createSound('stop','/static/sounds/stop.ogg');
         }
     });
    </script>
  </head>

  <body onload=
        "countdown = new PreCountdown('c1', ${duration}, ${prealarm});
        countdown.draw();
        countdown.start();">
    <div>
      <!-- soundManager appends "hidden" Flash to the first DIV on the page. -->
    </div>

    <h2 id="title" class="centered">
      ${_('Preparing %s round') % nextturn}
    </h2>

    <div class="centered">
      <canvas id="c1">
      </canvas>
    </div>

    <div class="centered" onclick="countdown.close();">
      <img id="stop-sign" class="invisible" src="/static/images/takeplace.jpg">
    </div>

    <div id="buttons" class="centered hint">
      <button type="button" onclick="countdown.addMinutes(1);">
        ${_('Add one more minute')}
      </button>
      &nbsp;
      <button type="button" onclick="countdown.addMinutes(5);">
        ${_('Add five more minutes')}
      </button>
      &nbsp;
      <button type="button" onclick="countdown.close();">
        ${_('Interrupt and close')}
      </button>
    </div>
  </body>
</html>
