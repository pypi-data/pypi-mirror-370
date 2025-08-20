## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   sab 13 dic 2008 16:34:51 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2008-2010, 2013, 2014, 2016, 2018-2025 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from sol.i18n import ordinal
from sol.i18n import ordinalp
from sol.models.utils import njoin
if entity.championship.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="head()">
  ${parent.head()}
  <script>
    window.onload = function() {
      let $auto_scroll_cb = $('#enable-auto-scroll');

      if(window.innerHeight < document.body.scrollHeight) {
        let scrollInterval;

        function startAutoScroll() {
          const intervalBetweenScrolls = 90,
                pixelsToScroll = 6,
                changeDirectionSleep = 1000;
          let scrollBy = pixelsToScroll,
              previousYOffset = null;

          scrollInterval = setInterval(function() {
            // When last run did not change the page offset, assume we reached
            // the top/bottom of the page, wait a bit and change scroll direction
            if(scrollBy !== 0 && previousYOffset === window.pageYOffset) {
              let oldScrollBy = scrollBy;

              scrollBy = 0;
              setTimeout(function() {
                scrollBy = -oldScrollBy;
                // Arbitrary change, just to avoid re-entering this case at next execution
                previousYOffset -= pixelsToScroll;
              }, changeDirectionSleep);
            }

            previousYOffset = window.pageYOffset;
            if(scrollBy)
              window.scrollBy({top: scrollBy, behavior: 'smooth'});
          }, intervalBetweenScrolls);

          // Stop scrolling on any user interaction
          ['mousedown', 'keydown', 'touchstart', 'wheel'].forEach(event => {
            window.addEventListener(event, stopAutoScroll, { once: true });
          });
        }

        function stopAutoScroll() {
          if (scrollInterval) {
            clearInterval(scrollInterval);
            scrollInterval = null;
          }
          $auto_scroll_cb.checkbox('uncheck');
        }

        $auto_scroll_cb.checkbox({
          onChecked: async function() { await startAutoScroll(); },
          onUnchecked: function() { stopAutoScroll(); }
        });
      }
      else
        $auto_scroll_cb.hide();
    }
  </script>
</%def>

<%def name="header()">
  ${self.logo()}
  <h1 class="title centered">
    % if not (turn is match is player is None):
      <a href="${request.route_path('lit_tourney', guid=entity.guid) | n}">
    % endif
    ${self.title()}
    % if not (turn is match is player is None):
      </a>
    % endif
  </h1>
  ${self.club_emblem()}
</%def>

<%def name="fui_css()">
  ${parent.fui_css()}
  <link rel="stylesheet" type="text/css" href="/static/css/fomantic-ui-button.css" />
  % if len(entity.competitors) > 30:
    <link rel="stylesheet" type="text/css" href="/static/css/fomantic-ui-checkbox.css" />
    <script src="/static/jquery-3.7.1.min.js"></script>
    <script src="/static/fomantic-ui-checkbox.js"></script>
  % endif
  % if entity.system == 'knockout':
    <script src="/static/bracketry.min.js"></script>
  % endif
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.championship.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.championship.club.emblem,
                            href=entity.championship.club.siteurl,
                            title=entity.championship.club.description)
  %>
</%def>


## Body

<details class="centered">
  <summary><i class="dropdown icon"></i>${_('Details')}</summary>
  <div>
    <table class="ui compact unstackable definition table">
      <tbody>
        <tr>
          <td class="right aligned">${_('Date')}</td>
          <td>${entity.date.strftime(_('%m-%d-%Y'))}</td>
        </tr>
        <tr>
          <td class="right aligned">${_('Championship')}</td>
          <td>
            <a href="${request.route_path('lit_championship', guid=entity.championship.guid) | n}">
              ${entity.championship.description}
            </a>
          </td>
        </tr>
        <tr>
          <td class="right aligned">${_('Club')}</td>
          <td>
            <a href="${request.route_path('lit_club', guid=entity.championship.club.guid) | n}">
              ${entity.championship.club.description}
            </a>
          </td>
        </tr>
        % if entity.hosting_club and entity.hosting_club != entity.championship.club:
          <tr>
            <td class="right aligned">${_('Hosted by')}</td>
            <td>
              <a href="${request.route_path('lit_club', guid=entity.hosting_club.guid) | n}">
                ${entity.hosting_club.description}
              </a>
            </td>
          </tr>
        % endif
        % if entity.location:
          <tr>
            <td class="right aligned">${_('Location')}</td>
            <td>${entity.location}</td>
          </tr>
        % endif
        % if entity.socialurl:
          <tr>
            <td class="right aligned">${_('Social site')}</td>
            <td><a href="${entity.socialurl}" target="_blank">${entity.socialurl}</a></td>
          </tr>
        % endif
        <tr>
          <td class="right aligned">${_('Duration')}</td>
          <td>${ngettext('%d minute', '%d minutes', entity.duration) % entity.duration}</td>
        </tr>
        <tr>
          <% system = entity.__class__.__table__.c.system.info['dictionary'][entity.system] %>
          <td class="right aligned">${_('System')}</td>
          <td>${_(system)}</td>
        </tr>
        % if entity.system == 'knockout':
        <tr>
          <% matcheskind = entity.__class__.__table__.c.matcheskind.info['dictionary'][entity.matcheskind] %>
          <td class="right aligned">${_('Kind of matches')}</td>
          <td>${_(matcheskind)}</td>
        </tr>
        % endif
        <tr>
          <% cmethod = entity.__class__.__table__.c.couplings.info['dictionary'][entity.couplings] %>
          <td class="right aligned">${_('Coupling method')}</td>
          <td>${_(cmethod)}</td>
        </tr>
        % if entity.delaytoppairing:
          <tr>
            <td class="right aligned">${_('Delay top players pairing')}</td>
            <td>${ngettext('%d turn', '%d turns', entity.delaytoppairing) % entity.delaytoppairing}</td>
          </tr>
        % endif
        <tr>
          <td class="right aligned">${_('Delay compatriots pairing')}</td>
          <td>${ngettext('%d turn', '%d turns', entity.delaycompatriotpairing) % entity.delaycompatriotpairing}</td>
        </tr>
        % if entity.finals:
          <tr>
            <td class="right aligned">${ngettext('Final', 'Finals', entity.finals)}</td>
            <td>
              <% firstfinalturn = entity.firstFinalTurn %>
              % if firstfinalturn:
                <a href="${request.route_path('lit_tourney', guid=entity.guid, _query=dict(turn=firstfinalturn))}">
              % endif
              ${_('1st/2nd place') if entity.finals==1 else _('1st/2nd place and 3rd/4th place')},
              ${_('Single game') if entity.finalkind == 'simple' else _('Best of three games')}
              % if entity.finalturns:
                </a>
              % endif
            </td>
          </tr>
        % endif
        <tr>
          <% pmethod = entity.championship.__class__.__table__.c.prizes.info['dictionary'][entity.championship.prizes] %>
          <td class="right aligned">${_('Prize-giving method')}</td>
          <td>${_(pmethod)}</td>
        </tr>
        % if entity.rating:
          <tr>
            <td class="right aligned">${_('Rating')}</td>
            <td>
              <a href="${request.route_path('lit_rating', guid=entity.rating.guid) | n}">
                ${entity.rating.description}
              </a>
            </td>
          </tr>
        % endif
        % if turn is None:
          <tr>
            <td class="right aligned">${_('Players')}</td>
            <td>${len(entity.ranking)}</td>
          </tr>
        % endif
      </tbody>
    </table>
  </div>
</details>

% if len(entity.competitors) > 30:
  <div class="centered">
    <div id="enable-auto-scroll" class="ui toggle checkbox">
      <input type="checkbox">
      <label>${_('Enable auto-scroll')}</label>
    </div>
  </div>
% endif

<table class="ui compact unstackable definition table">
  <tbody>
    % if entity.currentturn:
      <tr>
        <td class="right aligned">${_('Rounds')}</td>
        <td>
          <div class="ui mini wrapping spaced compact buttons">
            % for i in range(1,entity.currentturn+1):
              <% href = request.route_path('lit_tourney', guid=entity.guid, _query=dict(turn=i)) %>
              <a class="ui${' black' if turn==i else ''} button" href="${href|n}">
                ${i}
              </a>
            % endfor
          </div>
          <div class="ui mini compact buttons">
            <a class="ui button" href="${request.route_path('pdf_results', id=entity.guid, _query=dict(turn='all')) | n}">
              pdf
            </a>
            <div class="or" data-text="⇣"></div>
            <a class="ui button" href="${request.route_path('xlsx_tourney', id=entity.guid) | n}">
              xlsx
            </a>
          </div>
        </td>
      </tr>
    % endif
    % if not entity.prized and entity.countdownstarted:
      <tr>
        <td class="right aligned">${_('Currently playing %s round') % ordinal(entity.currentturn)}</td>
        <td>
          <a href="${request.route_path('countdown', _query={'idtourney': entity.idtourney}) | n}" target="_blank">
            ${_('Show countdown')}
          </a>
        </td>
      </tr>
    % endif
  </tbody>
</table>

## When we aren't focused on a particular turn/player/board, show the ranking

% if turn is None and match is None and player is None:

<%def name="ranking_header()">
  <thead>
    <tr>
      <th class="center aligned rank-header">#</th>
      <th class="player-header">${subject}</th>
      % if entity.rankedturn:
        <th class="center aligned event-header">${_('Pts')}</th>
        % if entity.system != 'knockout':
          % if entity.system != 'roundrobin':
            <th class="center aligned event-header">${_('Bch')}</th>
          % endif
        <th class="center aligned event-header">${_('Net')}</th>
        % endif
      % endif
      % if entity.prized and entity.championship.prizes != 'asis':
        <th class="center aligned sortedby total-header">${_('Prize')}</th>
      % endif
    </tr>
  </thead>
</%def>

<%def name="ranking_body(ranking)">
  <tbody>
    % for i, row in enumerate(ranking, 1):
      ${ranking_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="ranking_row(rank, row)">
  <tr>
    <td class="right aligned rank">${rank}</td>
    <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'player%d'%i) is not None] %>
    <td class="player">
      ${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (
        request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}
    </td>
    % if entity.rankedturn:
      <td class="right aligned event">${row.points}</td>
      % if entity.system != 'knockout':
        % if entity.system != 'roundrobin':
          <td class="right aligned event">${row.bucholz}</td>
        % endif
      <td class="right aligned event">${row.netscore}</td>
      % endif
    % endif
    % if entity.prized and entity.championship.prizes != 'asis':
      <td class="right aligned sortedby total">${format_prize(row.prize)}</td>
    % endif
  </tr>
</%def>

<% ranking = entity.ranking %>
<table class="ui striped compact unstackable table ranking">
  <caption>
    % if entity.prized or entity.date <= today:
      ${_('Ranking')} (<a href="${request.route_path('pdf_tourneyranking', id=entity.guid) | n}">pdf</a>)
    % endif
  </caption>
  ${ranking_header()}
  ${ranking_body(ranking)}
</table>

% if entity.system == 'knockout':
  <div id="brackets" class="centered">
  </div>
  <script>
   const bracket = Bracketry.createBracket(
     JSON.parse('${bracketry | n}'),
     document.querySelector('#brackets'),
     { getNationalityHTML: (player) => `<img src="/static/images/flags/${'${player.nationality}'}.png">` }
   );
   bracket.setBaseRoundIndex(${entity.rankedturn}-1);
  </script>
% endif

## When focused on a particular match, show its boards

% elif turn is not None and match is not None:

<%def name="training_boards_header()">
  <thead>
    <tr>
      <th class="center aligned competitor1${' winner' if match.score1>match.score2 else ''}"
          width="45%">
        <%
        ctor = match.competitor1
        players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
        %>
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
          request.route_path('lit_tourney', guid=match.tourney.guid, _query=dict(player=p.guid)),
          escape(_('Show matches played by %s') % p.caption(html=False)),
          escape(p.caption(html=False)))) | n}
      </th>
      <th width="10%"></th>
      % if match.idcompetitor2:
        <%
        ctor = match.competitor2
        players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
        %>
        <th class="center aligned competitor2${' winner' if match.score1<match.score2 else ''}"
            width="45%">
          ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=match.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
        </th>
      % else:
        <th class="center aligned phantom" colspan="4">${_('Phantom')}</th>
      % endif
    </tr>
    % if match.boards:
    <tr>
      <th class="center aligned scores-header">${_('Errors')}</th>
      <th class="center aligned round-number-header">#</th>
      <th class="center aligned scores-header">${_('Errors')}</th>
    </tr>
    % endif
  </thead>
</%def>

<%def name="training_boards_body()">
  <%
  incomplete = match.score1 is None or match.score2 is None or match.score1 == match.score2 == 0
  %>
  <tbody>
    % for i, row in enumerate(match.boards, 1):
      ${training_boards_row(i, row, incomplete)}
    % endfor
    % if match.score1 is not None and match.score2 is not None:
    <tr class="${'partial-score' if incomplete else ''}">
      <td class="center aligned${' winner' if match.score1>match.score2 else ''}">
        ${match.score2}
      </td>
      <td></td>
      <td class="center aligned${' winner' if match.score1<match.score2 else ''}">
        ${match.score1}
      </td>
    </tr>
    % endif
  </tbody>
</%def>

<%def name="training_boards_row(rank, row, incomplete)">
  <tr class="${'partial-score' if incomplete else ''}">
    <td class="center aligned${' winner' if row.score1>row.score2 else ''}">
      ${row.score1}
    </td>
    <td class="center aligned round-number">${rank}</td>
    <td class="center aligned${' winner' if row.score1<row.score2 else ''}">
      ${row.score2}
    </td>
  </tr>
</%def>

<%def name="boards_header()">
  <thead>
    <tr>
      <th class="center aligned competitor1${' winner' if match.score1>match.score2 else ''}"
          colspan="4" width="46%">
        <%
        ctor = match.competitor1
        players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
        %>
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
          request.route_path('lit_tourney', guid=match.tourney.guid, _query=dict(player=p.guid)),
          escape(_('Show matches played by %s') % p.caption(html=False)),
          escape(p.caption(html=False)))) | n}
      </th>
      <th></th>
      % if match.idcompetitor2:
        <%
        ctor = match.competitor2
        players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
        %>
        <th class="center aligned competitor2${' winner' if match.score1<match.score2 else ''}"
            colspan="4" width="46%">
          ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=match.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
        </th>
      % else:
        <th class="center aligned phantom" colspan="4" width="46%">${_('Phantom')}</th>
      % endif
    </tr>
    % if match.breaker or match.boards:
    <tr class="narrow-only">
      <th class="center aligned scores-header">${_('Pts')}</th>
      <th class="center aligned scores-header">${_('Sc')}</th>
      <th class="center aligned scores-header">${_('C')}</th>
      <th class="center aligned scores-header">${_('Q')}</th>
      <th class="center aligned round-number-header">#</th>
      <th class="center aligned scores-header">${_('Q')}</th>
      <th class="center aligned scores-header">${_('C')}</th>
      <th class="center aligned scores-header">${_('Sc')}</th>
      <th class="center aligned scores-header">${_('Pts')}</th>
    </tr>
    <tr class="wide-only">
      <th class="center aligned scores-header">${_('Points')}</th>
      <th class="center aligned scores-header">${_('Score')}</th>
      <th class="center aligned scores-header">${_('Coins')}</th>
      <th class="center aligned scores-header">${_('Queen')}</th>
      <th class="center aligned round-number-header">#</th>
      <th class="center aligned scores-header">${_('Queen')}</th>
      <th class="center aligned scores-header">${_('Coins')}</th>
      <th class="center aligned scores-header">${_('Score')}</th>
      <th class="center aligned scores-header">${_('Points')}</th>
    </tr>
    % endif
  </thead>
</%def>

<%def name="boards_body()">
  <tbody>
    % for i, row in enumerate(match.boards, 1):
      ${boards_row(i, row)}
    % endfor
  </tbody>
  <tfoot>
    % if match.score1 or match.score2:
    <tr>
      <td colspan="4" class="center aligned${' winner' if match.score1>match.score2 else ''}">
        ${match.score1}
      </td>
      <td></td>
      <td colspan="4" class="center aligned${' winner' if match.score1<match.score2 else ''}">
        ${match.score2}
      </td>
    </tr>
    % else:
    <tr class="partial-score">
      <td class="right aligned${' winner' if match.partial_score1>match.partial_score2 else ''}">
        ${match.partial_score1}
      </td>
      <td class="center aligned" colspan="7">
        ${_('Still playing...')}
      </td>
      <td class="right aligned${' winner' if match.partial_score1<match.partial_score2 else ''}">
        ${match.partial_score2}
      </td>
    </tr>
    % endif
  </tfoot>
</%def>

<%def name="boards_row(rank, row)">
  <tr>
    <td class="right aligned${' winner' if row.total_score1>row.total_score2 else ''}">
      ${row.total_score1}
    </td>
    <td class="right aligned${' winner' if row.score1>row.score2 else ''}">
      ${row.score1}
    </td>
    <td class="right aligned">${row.coins1 or ''}</td>
    <td class="center aligned">
      ${'✔' if row.queen == '1' else ''}
    </td>
    <td class="center aligned round-number">${rank}</td>
    <td class="center aligned">
      ${'✔' if row.queen == '2' else ''}
    </td>
    <td class="right aligned">${row.coins2 or ''}</td>
    <td class="right aligned${' winner' if row.score1<row.score2 else ''}">
      ${row.score2}
    </td>
    <td class="right aligned${' winner' if row.total_score1<row.total_score2 else ''}">
      ${row.total_score2}
    </td>
  </tr>
</%def>

<table class="ui compact unstackable table boards${'' if not match.breaker else ' breaker-%s' % match.breaker}">
  <caption>
    ${_('Round $round', mapping=dict(round=match.turn))},
    ${_('carromboard $num', mapping=dict(num=match.board))}
    <%
    completed = entity.prized or turn < entity.currentturn
    if not completed:
      completed = match.score1 or match.score2
    %>
    % if not completed:
      <button class="ui mini compact right floated button" onclick="history.go(0)">
        ${_('Refresh')}
      </button>
    % endif
  </caption>
  % if entity.championship.trainingboards:
  ${training_boards_header()}
  ${training_boards_body()}
  % else:
  ${boards_header()}
  ${boards_body()}
  % endif
</table>

## Otherwise display the matches details

% else:

<%def name="training_matches_header(matches)">
  <% tboards = entity.championship.trainingboards %>
  <thead>
    <tr>
      <th class="center aligned rank-header" rowspan="2">#</th>
      <th class="center aligned competitors-header" rowspan="2">
        ${_('Match')}
      </th>
      <th colspan="${(tboards + 1)}"
          class="center aligned scores-header">
        ${_('Errors')}
      </th>
      <th class="center aligned scores-header" rowspan="2">
        ${_('Score')}
      </th>
    </tr>
    <tr>
      % for i in range(1, tboards+1):
        <th class="center aligned scores-header">${_('board $board', mapping=dict(board=i))}</th>
      % endfor
      <th class="center aligned scores-header">${_('Average')}</th>
    </tr>
  </thead>
</%def>

<%def name="training_matches_body(matches)">
  <tbody>
    % for i, row in enumerate(matches, 1):
    ${training_matches_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="training_matches_row(rank, row)">
  <%
  boardcoins1 = all(b.coins1 is not None for b in row.boards)
  boardcoins2 = all(b.coins2 is not None for b in row.boards)
  tboards = entity.championship.trainingboards
  misses1 = sum(b.coins1 for b in row.boards) if boardcoins1 else None
  misses2 = sum(b.coins2 for b in row.boards) if boardcoins2 else None
  scored = tboards and row.boards and boardcoins1 and boardcoins2 or (
      (row.score1 != 0 or row.score2 != 0))
  %>
  <tr class="${'' if scored else ' partial-score'}">
    <td rowspan="2" class="right aligned rank">${rank}</td>
    <%
    ctor = row.competitor1
    players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
    %>
    <td class="center aligned competitor1${' winner' if row.score1>row.score2 else ''}">
      ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
          request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
          escape(_('Show matches played by %s') % p.caption(html=False)),
          escape(p.caption(html=False)))) | n}
    </td>
    % for tboard in row.boards:
      <td class="right aligned">
        ${tboard.coins1 if tboard.coins1 is not None else '—'}
      </td>
    % endfor
    % for i in range(tboards - len(row.boards)):
      <td class="right aligned">—</td>
    % endfor
    <td class="right aligned">
      ${format_decimal(misses1 / tboards, '#.00') if misses1 is not None else '—'}
    </td>
    <td rowspan="2" class="center aligned scores">
      % if row.boards:
      <a href="${request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(turn=row.turn, board=row.board))}">
      % endif
      <span class="score1${' winner' if row.score1 > row.score2 else ''}">
        ${row.score1}
      </span>
      /
      <span class="score2${' winner' if row.score1 < row.score2 else ''}">
        ${row.score2}
      </span>
      % if row.boards:
      </a>
      % endif
    </td>
  </tr>
  <tr class="${'' if scored else ' partial-score'}">
    % if row.idcompetitor2:
      <%
      ctor = row.competitor2
      players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
      %>
      <td class="center aligned competitor2${' winner' if row.score1<row.score2 else ''}">
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
      </td>
    % else:
      <td class="center aligned phantom">${_('Phantom')}</td>
    % endif
    % for tboard in row.boards:
      <td class="right aligned">
        ${tboard.coins2 if tboard.coins2 is not None else '—'}
      </td>
    % endfor
    % for i in range(tboards - len(row.boards)):
      <td class="right aligned">—</td>
    % endfor
    <td class="right aligned">
      ${format_decimal(misses2 / tboards, '#.00') if misses2 is not None else '—'}
    </td>
  </tr>
</%def>

<%def name="matches_header(matches)">
  <thead>
    <tr>
      <th class="center aligned rank-header">#</th>
      <th class="center aligned competitors-header" colspan="3">
        ${_('Match')}
      </th>
      <th class="center aligned scores-header">
        ${_('Score')}
      </th>
    </tr>
  </thead>
</%def>

<%def name="matches_body(matches)">
  <tbody>
    % for i, row in enumerate(matches, 1):
    ${matches_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="matches_row(rank, row)">
  <%
  scored = row.score1 != 0 or row.score2 != 0
  score1 = row.score1 if scored else row.partial_score1
  score2 = row.score2 if scored else row.partial_score2
  %>
  <tr class="${'' if scored else 'partial-score'}">
    <td class="right aligned rank">${rank}</td>
    <%
    ctor = row.competitor1
    players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
    %>
    <td class="center aligned competitor1${' winner' if row.score1>row.score2 else ''}">
      ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
          request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
          escape(_('Show matches played by %s') % p.caption(html=False)),
          escape(p.caption(html=False)))) | n}
    </td>
    <td class="separator"></td>
    % if row.idcompetitor2:
      <%
      ctor = row.competitor2
      players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
      %>
      <td class="center aligned competitor2${' winner' if row.score1<row.score2 else ''}">
        ${njoin(players, stringify=lambda p: '<a href="%s" title="%s">%s</a>' % (
            request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(player=p.guid)),
            escape(_('Show matches played by %s') % p.caption(html=False)),
            escape(p.caption(html=False)))) | n}
      </td>
    % else:
      <td class="center aligned phantom">${_('Phantom')}</td>
    % endif
    <td class="center aligned scores">
      % if row.breaker or row.boards:
      <a href="${request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(turn=row.turn, board=row.board))}">
      % endif
      <span class="score1${' winner' if score1 > score2 else ''}">
        ${score1}
      </span>
      /
      <span class="score2${' winner' if score1 < score2 else ''}">
        ${score2}
      </span>
      % if row.breaker or row.boards:
      </a>
      % endif
    </td>
  </tr>
</%def>

<%
   if player:
       matches = [m for m in entity.matches
                  if (m.competitor1.player1.guid == player or
                      m.competitor1.player2 and m.competitor1.player2.guid == player or
                      m.competitor1.player3 and m.competitor1.player3.guid == player or
                      m.competitor1.player4 and m.competitor1.player4.guid == player or
                      (m.competitor2 and (m.competitor2.player1.guid == player or
                                          m.competitor2.player2 and m.competitor2.player2.guid == player or
                                          m.competitor2.player3 and m.competitor2.player3.guid == player or
                                          m.competitor2.player4 and m.competitor2.player4.guid == player)))]
       if matches:
           m0 = matches[0]
           if (m0.competitor1.player1.guid == player or
               m0.competitor1.player2 and m0.competitor1.player2.guid == player or
               m0.competitor1.player3 and m0.competitor1.player3.guid == player or
               m0.competitor1.player4 and m0.competitor1.player4.guid == player):
               cname = m0.competitor1.caption(html=False)
           else:
               cname = m0.competitor2.caption(html=False)
           caption = _('Matches played by %s') % (
               '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=player), escape(cname)))
       else:
           caption = _('No matches for this player')
   else:
       matches = [m for m in entity.matches if m.turn == turn]
       if matches:
           caption = (_('Results %s final round (%s)') if matches[0].final else _('Results %s round (%s)')) % (
               ordinalp(turn), '<a href="%s">pdf</a>' % (request.route_path('pdf_results', id=entity.guid,
                                                                  _query=dict(turn=turn))))
       else:
           caption = _('No matches for this round')
%>

<table class="ui${'' if entity.championship.trainingboards else ' striped'} compact unstackable table matches">
  <caption>
    ${caption | n}
    <%
    completed = entity.prized or turn is not None and turn < entity.currentturn
    if not completed:
      completed = all(m.score1 or m.score2 for m in entity.matches)
    %>
    % if not completed:
      <button class="ui mini compact right floated button" onclick="history.go(0)">
        ${_('Refresh')}
      </button>
    % endif
  </caption>
  % if entity.championship.trainingboards:
  ${training_matches_header(matches)}
  ${training_matches_body(matches)}
  % else:
  ${matches_header(matches)}
  ${matches_body(matches)}
  % endif
</table>

% endif
