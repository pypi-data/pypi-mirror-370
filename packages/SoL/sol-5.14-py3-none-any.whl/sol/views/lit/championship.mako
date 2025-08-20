## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   sab 13 dic 2008 16:34:14 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2008-2010, 2013, 2014, 2016, 2018-2020, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
if entity.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
  if entity.club.emblem:
      parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
      href=entity.club.siteurl,
      title=entity.club.description)
  %>
</%def>

<%def name="table_header(dates)">
  <thead>
    <tr>
      <th class="center aligned rank-header">#</th>
      <th class="center aligned player-header">${subject}</th>
      % for date, description, guid in dates:
        <th class="center aligned event-header">
          <a href="${request.route_path('lit_tourney', guid=guid) | n}" title="${description}">
            ${date.strftime(_('%m-%d-%y'))}
          </a>
        </th>
      % endfor
      <th class="center aligned sortedby total-header">${_('Total')}</th>
    </tr>
  </thead>
</%def>

<%def name="table_body(ranking)">
  <tbody>
    % for i, row in enumerate(ranking, 1):
      ${table_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="table_row(rank, row)">
  <tr>
    <td class="right aligned rank">${rank}</td>
    <td class="center aligned player">
      ${njoin(row[0], stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}
    </td>
    % for s in row[2]:
      <%
      if row[4] and s in row[4]:
          eventclass = 'skipped-event'
          row[4].remove(s)
      else:
          eventclass = 'event'
      %>
      <td class="right aligned ${eventclass}">${format_prize(s) if s else ''}</td>
    % endfor
    <td class="right aligned sortedby total">${format_prize(row[1])}</td>
  </tr>
</%def>

## Body

<details class="centered">
  <summary>
    <i class="dropdown icon"></i>${_('Details')}
  </summary>
  <div>
    <table class="ui compact unstackable definition table">
      <tbody>
        <tr>
          <td class="right aligned">${_('Club')}</td>
          <td>
            <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">
              ${entity.club.description}
            </a>
          </td>
        </tr>

        <tr>
          <td class="right aligned">${_('Players per team')}</td>
          <td>${entity.playersperteam}</td>
        </tr>

        <tr>
          <% pmethod = entity.__class__.__table__.c.prizes.info['dictionary'][entity.prizes] %>
          <td class="right aligned">${_('Prize-giving method')}</td>
          <td>${_(pmethod)}</td>
        </tr>

        % if entity.skipworstprizes:
          <tr>
            <td class="right aligned">${_('Skip worst prizes')}</td>
            <td>${entity.skipworstprizes}</td>
          </tr>
        % endif

        % if entity.trainingboards:
          <tr>
            <td class="right aligned">${_('Training boards')}</td>
            <td>${entity.trainingboards}</td>
          </tr>
        % endif

        % if entity.previous:
          <tr>
            <td class="right aligned">${_('Previous championship')}</td>
            <td>
              <a href="${request.route_path('lit_championship', guid=entity.previous.guid) | n}">
                ${entity.previous.description}
              </a>
            </td>
          </tr>
        % endif
        % if entity.next:
          <tr>
            <td class="right aligned">${_('Next championship')}</td>
            <td>
              <a href="${request.route_path('lit_championship', guid=entity.next.guid) | n}">
                ${entity.next.description}
              </a>
            </td>
          </tr>
        % endif
      </tbody>
    </table>
  </div>
</details>

<% dates, ranking = entity.ranking() %>
<table class="ui striped compact unstackable table ranking">
  <caption>${_('Championship ranking')} (<a href="${request.route_path('pdf_championshipranking', id=entity.guid) | n}">pdf</a>) </caption>
  ${table_header(dates)}
  ${table_body(ranking)}
</table>
