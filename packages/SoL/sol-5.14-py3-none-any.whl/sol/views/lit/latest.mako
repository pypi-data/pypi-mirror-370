## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   dom 13 lug 2014 10:08:55 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2018, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${ngettext('Latest %d tournament', 'Latest %d tournaments', n) % n}
</%def>

<%def name="table_header()">
  <thead>
    <tr>
      <th class="center aligned rank-header">#</th>
      <th class="center aligned tourney-header">${_('Tournament')}</th>
      <th class="center aligned date-header">${_('Date')}</th>
      <th class="center aligned event-header">${_('Location')}</th>
      <th class="center aligned championship-header">${_('Club')}</th>
      <th class="center aligned championship-header">${_('Championship')}</th>
      <th class="center aligned player-header">${_('Winner')}</th>
    </tr>
  </thead>
</%def>

<%def name="table_body()">
  <tbody>
    % for i, row in enumerate(tourneys, 1):
    ${table_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="table_row(rank, row)">
  <tr>
    <td class="right aligned rank">${rank}</td>
    <td class="center aligned tourney">
      <a href="${request.route_path('lit_tourney', guid=row.guid) | n}">
        ${row.description}
      </a>
    </td>
    <td class="center aligned date sortedby">${row.date.strftime(_('%m-%d-%y'))}</td>
    <td>${row.location}</td>
    <td class="center aligned championship">
      <a href="${request.route_path('lit_club', guid=row.championship.club.guid) | n}">
        ${row.championship.club.description}
      </a>
    </td>
    <td class="center aligned championship">
      <a href="${request.route_path('lit_championship', guid=row.championship.guid) | n}">
        ${row.championship.description}
      </a>
    </td>
    <%
    ranking = row.ranking
    if ranking:
        winner = ranking[0]
        players = [getattr(winner, 'player%d'%i) for i in range(1,5) if getattr(winner, 'player%d'%i) is not None]
    else:
        players = []
    %>
    <td class="center aligned player winner">
      ${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}
    </td>
  </tr>
</%def>

<table class="ui striped compact unstackable table ranking">
  ${table_header()}
  ${table_body()}
</table>
