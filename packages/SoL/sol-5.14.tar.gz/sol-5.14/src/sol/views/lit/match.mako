## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mar 28 apr 2020, 08:50:19
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2020-2025 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="header()">
  <div class="centered">
  <h1 class="title centered">
    <a href="${request.route_path('lit_tourney', guid=tourney.guid) | n}" target="_blank">
      ${tourney.description}
    </a>
  </h1>
  <h2 class="title centered">
    ${_('round $round', mapping=dict(round=currentturn))},
    ${_('carromboard $num', mapping=dict(num=match.board))}
  </h2>
  </div>
  <div id="countdown" class="invisible">
    <p></p>
    <img id="stop-sign" class="invisible" src="/static/images/stop.jpg">
  </div>
</%def>

<%def name="footer()">
</%def>

<%def name="title()">
  ${match.caption(html=False)}
</%def>

<%def name="fui_css()">
  ${parent.fui_css()}
  <link rel="stylesheet" type="text/css" href="/static/css/fomantic-ui-button.css" />
  <link rel="stylesheet" type="text/css" href="/static/css/fomantic-ui-form.css" />
  <link rel="stylesheet" type="text/css" href="/static/css/fomantic-ui-loader.css" />
  <link rel="stylesheet" type="text/css" href="/static/css/match.css?v=${version}" />
  <script src="/static/jquery-3.7.1.min.js"></script>
  <script src="/static/fomantic-ui-checkbox.js"></script>
  <script src="/static/match.js?v=${version}"></script>
  <script src="/static/NoSleep.min.js?v=${version}"></script>
  <script>
   $(document).ready(function() {
     new MatchScorecard(${100 if match.final else 9},
                        ${tourney.duration}, ${tourney.prealarm},
                        ${elapsed or 'false'})
     .init("${_('New board')}",
           "${_('Do you confirm that the match has ended and you verified the correctness of'
                ' the scores?')|n}",
           "${_('Neither player has reached 25 points and there is still time to play'
                ': do you confirm that you are really sure you want to stop the match'
                ' and send current scores, not playing further boards?')|n}");
   });
  </script>
</%def>

## Body

<dialog class="overlay" id="match-not-yet-started">
  <div class="text">
    ${_('Please wait, the match has not yet started')}
  </div>
</dialog>

<dialog class="overlay" id="wait-server-result">
  <div class="text">
    <div class="ui active centered inline loader"></div>
  </div>
</dialog>

<form class="ui center aligned form${' error' if error else ''}" method="POST">
  <input type="hidden" name="turn" value="${tourney.currentturn}">
  <input type="hidden" name="score1" value="${match.score1}">
  <input type="hidden" name="score2" value="${match.score2}">
  <table class="ui large unstackable celled compact table${'' if not match.breaker else ' breaker-%s' % match.breaker}">
    <thead>
      <tr>
        <% omit_nn = match.competitor1.caption(omit_nicknames=True) != match.competitor2.caption(omit_nicknames=True) %>
        <th class="center aligned" colspan="4" width="50%">
          <div class="breaker">
            <div class="ui radio checkbox" title="${_('Break')}">
              <input type="radio" name="breaker" value="1">
            </div>
            <br/>
          </div>
          <span>${match.competitor1.caption(omit_nicknames=omit_nn)|n}</span>
        </th>
        <th class="center aligned" colspan="4" width="50%">
          <div class="breaker">
            <div class="ui radio checkbox" title="${_('Break')}">
              <input type="radio" name="breaker" value="2">
            </div>
            <br/>
          </div>
          <span>${match.competitor2.caption(omit_nicknames=omit_nn)|n}</span>
        </th>
      </tr>
      <tr>
        <th class="center aligned">Score</th>
        <th class="center aligned">${_('Coins')}</th>
        <th class="center aligned collapsing">Q</th>
        <th class="center aligned collapsing" colspan="2">#</th>
        <th class="center aligned collapsing">Q</th>
        <th class="center aligned">${_('Coins')}</th>
        <th class="center aligned">Score</th>
      </tr>
    </thead>

    <tbody id="boards">
      % for board in match.boards:
        <%
        q1_checked = ' checked="checked"' if board.queen == '1' else ''
        q2_checked = ' checked="checked"' if board.queen == '2' else ''
        %>
        <tr id="board_${board.number}">
          <td class="center aligned" id="score_${board.number}_1"></td>
          <td class="center aligned">
            <input type="number" name="coins_${board.number}_1"
                   min="0" max="9"
                   value="${'' if board.coins1 is None else board.coins1}" />
          </td>
          <td class="collapsing">
            <div class="ui radio fitted checkbox center aligned" id="cb_queen_${board.number}_1">
              <input type="radio" name="queen_${board.number}" value="1"${q1_checked | n} />
            </div>
          </td>
          <td class="grey center aligned collapsing" colspan="2">${board.number}</td>
          <td class="collapsing">
            <div class="ui radio fitted checkbox center aligned" id="cb_queen_${board.number}_2">
              <input type="radio" name="queen_${board.number}" value="2"${q2_checked | n} />
            </div>
          </td>
          <td class="center aligned">
            <input type="number" name="coins_${board.number}_2"
                   min="0" max="9"
                   value="${'' if board.coins2 is None else board.coins2}" />
          </td>
          <td class="center aligned" id="score_${board.number}_2"></td>
        </tr>
      % endfor
    </tbody>
    <tfoot>
      <tr class="invisible">
        <td colspan="8" class="center aligned">
          <button id="reset_queen" class="ui tiny compact button" type="button">
            ${_('Reset queen')}
          </button>
        </td>
      </tr>
      <tr>
        <td class="center aligned" id="total_1"></td>
        <td colspan="6" class="center aligned">
          <div class="ui center aligned compact medium buttons">
            <button id="new_board_btn" class="ui primary${'' if match.breaker else ' disabled'} button" type="button">
              ${_('New board') if match.boards else _('Start game')}
            </button>
            <button id="end_match_btn" class="ui positive disabled button" name="end_match">
              ${_('End match')}
            </button>
          </div>
        </td>
        <td class="center aligned" id="total_2"></td>
      </tr>
      <tr>
        <td colspan="8" class="center aligned">
          <button id="enable_nosleep" class="ui fluid tiny compact button" type="button">
            ${_('Keep the display active')}
          </button>
          <button id="disable_nosleep" class="ui fluid tiny compact button invisible" type="button">
            ${_('Re-enable display dim and sleep')}
          </button>
        </td>
      </tr>
    </tfoot>
  </table>
</form>
