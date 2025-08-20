## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   gio 06 nov 2014 19:12:19 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2018-2020, 2022, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="header()">
    ${self.logo()}
    <h1 class="title centered">
      <a href="${request.route_path('lit_player', guid=entity.guid)}">
        ${entity.caption(html=False)}
      </a>
      ${_('vs')}
      <a href="${request.route_path('lit_player', guid=opponent.guid)}">
        ${opponent.caption(html=False)}
      </a>
    </h1>
</%def>

<%def name="title()">
  ${_('Matches between %s and %s') % (entity.caption(html=False), opponent.caption(html=False))}
</%def>

<%
matches = entity.opponentMatches(opponent)
nmatches = len(matches)
ewon = sum(1 for m in matches
           if (m.competitor1.player1 is entity and m.score1 > m.score2)
           or (m.competitor2.player1 is entity and m.score1 < m.score2))
owon = sum(1 for m in matches
           if (m.competitor1.player1 is opponent and m.score1 > m.score2)
           or (m.competitor2.player1 is opponent and m.score1 < m.score2))
tied = sum(1 for m in matches if m.score1 == m.score2)
%>

<table class="ui compact unstackable definition table">
  <tbody>
    <tr>
      <td class="right aligned">${_('Matches')}</td>
      <td>${nmatches}</td>
    </tr>
    % if nmatches:
      <tr>
        <td class="right aligned">${_('Won by %s') % entity.caption(html=False)}</td>
        <td>${ewon} ${'(%d%%)' % (100 * ewon // nmatches)}</td>
      </tr>
      <tr>
        <td class="right aligned">${_('Won by %s') % opponent.caption(html=False)}</td>
        <td>${owon} ${'(%d%%)' % (100 * owon // nmatches)}</td>
      </tr>
      <tr>
        <td class="right aligned">${_('Tied')}</td>
        <td>${tied} ${'(%d%%)' % (100 * tied // nmatches)}</td>
      </tr>
    % endif
  </tbody>
</table>

<%def name="matches_header()">
  <thead>
    <tr>
      <th class="center aligned rank-header" rowspan="2">#</th>
      <th class="center aligned tourney-header" rowspan="2">${_('Tourney')}</th>
      <th class="center aligned championship-header" rowspan="2">${_('Championship')}</th>
      <th class="center aligned date-header" rowspan="2">${_('Date')}</th>
      <th class="center aligned event-header" rowspan="2">${_('Round')}</th>
      <th class="center aligned event-header" colspan="2">${_('Scores')}</th>
    </tr>
    <tr>
      <th class="center aligned event-header">${entity.caption(html=False)}</th>
      <th class="center aligned event-header">${opponent.caption(html=False)}</th>
    </tr>
  </thead>
</%def>

<%def name="matches_body()">
  <tbody>
    <% prevs = None %>
    % for i, row in enumerate(matches, 1):
    ${matches_row(i, row, row.tourney.championship is prevs)}
    <% prevs = row.tourney.championship %>
    % endfor
  </tbody>
</%def>

<%def name="matches_row(index, row, samechampionship)">
  <tr>
    <td class="right aligned index">${index}</td>
    <td class="center aligned tourney">
      <a href="${request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(turn=row.turn))}">
        ${row.tourney.description}
      </a>
    </td>
    <td class="center aligned championship">
      <a href="${request.route_path('lit_championship', guid=row.tourney.championship.guid) | n}" title="${samechampionship and _('Idem') or row.tourney.championship.club.description}">
          ${samechampionship and '...' or row.tourney.championship.description}
      </a>
    </td>
    <td class="center aligned date">${row.tourney.date.strftime(_('%m-%d-%Y'))}</td>
    <td class="right aligned event">${row.turn}</td>
    % if row.competitor1.player1 is entity:
      <td class="right aligned event${' winner' if row.score1>row.score2 else ''}">${row.score1}</td>
      <td class="right aligned event${' winner' if row.score1<row.score2 else ''}">${row.score2}</td>
    % else:
      <td class="right aligned event${' winner' if row.score1<row.score2 else ''}">${row.score2}</td>
      <td class="right aligned event${' winner' if row.score1>row.score2 else ''}">${row.score1}</td>
    % endif
  </tr>
</%def>

<table class="ui striped compact unstackable table ranking">
  <caption>
    ${_('Matches results')}
  </caption>
  ${matches_header()}
  ${matches_body()}
</table>
