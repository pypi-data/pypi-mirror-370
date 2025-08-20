## -*- coding: utf-8 -*-
## :Project:   SoL -- Countdown page
## :Created:   mer 27 apr 2016 10:21:52 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2016, 2020, 2023, 2024 Lele Gaifax
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
          soundManager.createSound('tictac','/static/sounds/tictac.ogg');
          soundManager.createSound('start','/static/sounds/start.ogg');
          soundManager.createSound('prealarm','/static/sounds/prealarm.ogg');
          soundManager.createSound('stop','/static/sounds/stop.ogg');
        }
      });
    </script>

    <!-- Prevent accidental close/stop -->
    <script>
      addEventListener("beforeunload", function (e) {
        if(countdown.updateInterval && countdown.isOwner) {
          e.preventDefault();
          return e.returnValue = "${_('Closing the page will NOT stop the countdown.')}";
        }
      });
    </script>
  </head>

  <body onload=
        "countdown = new Countdown('c1', ${duration}, ${prealarm}, ${elapsed or 'false'}, ${'true' if isowner else 'false'});
         countdown.confirmRestart = '${_('Do you really want to restart the countdown?')}';
         countdown.confirmClose = '${_('Do you really want to stop the countdown?')}';
         countdown.notifyStart = '${notifystart}';
         countdown.draw();">
    <div>
      <!-- soundManager appends "hidden" Flash to the first DIV on the page. -->
    </div>

    <h2 id="title" class="centered">
      ${_('Playing %s round') % currentturn}:&nbsp;
      ${ngettext('%d minute', '%d minutes', duration) % duration}
      % if prealarm:
        ,&nbsp;
        ${ngettext('%d minute of prealarm', '%d minutes of prealarm', prealarm) % prealarm}
      % endif
    </h2>

    <div class="centered">
      <canvas id="c1">
      </canvas>
    </div>

    <div class="invisible">
      <img id="scr" src="/static/images/wallpapers/scr.png">
    </div>

    <div class="centered" onclick="countdown.close();">
      <img id="stop-sign" class="invisible" src="/static/images/stop.jpg">
    </div>

    <div id="buttons" class="centered hint">
      % if isowner:
        % if starttime:

          <button type="button" onclick="countdown.start();">
            ${_('Restart the countdown')}
          </button>

        % else:

          <button type="button" onclick="countdown.start();">
            ${_('(Re)start the countdown immediately')}
          </button>
          ${_('or')}
          <button type="button" onclick="countdown.start(15);">
            ${_('do it in 15 seconds')}
          </button>
          ${_('or')}
          <button type="button" onclick="countdown.start(60);">
            ${_('in 60 seconds')}
          </button>

        % endif
        &nbsp;
        <button type="button" onclick="countdown.close();">
        ${_('Interrupt and close')}
      </button>
      % endif
    </div>
  </body>
</html>
