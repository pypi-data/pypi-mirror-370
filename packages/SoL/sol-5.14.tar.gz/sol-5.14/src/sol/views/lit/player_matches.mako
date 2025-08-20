## -*- coding: utf-8 -*-
## :Project:   SoL -- Player's matches
## :Created:   sab 08 nov 2014 09:16:28 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2018-2020, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${_('Singles matches played by %s') % entity.caption(html=False)}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
  if entity.idclub is not None and entity.club.emblem:
      parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
      href=entity.club.siteurl,
      title=entity.club.description)
  %>
</%def>

## Body

<%
opponents = entity.opponents()
%>

% if entity.acceptedDiscernibility() and entity.portrait:
  <img class="centered portrait" src="/lit/portrait/${entity.portrait}" />
% endif

<table class="ui compact unstackable definition table">
  <tbody>
    <tr>
      <td class="right aligned">${_('First name')}</td>
      <td>${entity.firstname if entity.acceptedDiscernibility() else entity.obfuscatedFirstname}</td>
    </tr>
    <tr>
      <td class="right aligned">${_('Last name')}</td>
      <td>${entity.lastname if entity.acceptedDiscernibility() else entity.obfuscatedLastname}</td>
    </tr>
    % if not entity.shouldOmitNickName():
      <tr>
        <td class="right aligned">${_('Nickname')}</td>
        <td>${entity.nickname if entity.acceptedDiscernibility() else entity.obfuscatedNickname}</td>
      </tr>
    % endif
    % if entity.acceptedDiscernibility() and entity.sex:
      <tr>
        <% sex = entity.__class__.__table__.c.sex.info['dictionary'][entity.sex] %>
        <td class="right aligned">${_('Gender')}</td>
        <td>${_(sex)}</td>
      </tr>
    % endif
    % if entity.acceptedDiscernibility() and entity.nationality:
      <tr>
        <td class="right aligned">${_('Country')}</td>
        <td>
          <img src="/static/images/flags/${entity.nationality}.png" />
          ${entity.country}
          % if entity.citizenship:
            (${_('citizenship')})
          % endif
        </td>
      </tr>
    % endif
    % if entity.club and entity.federation and entity.club is entity.federation:
      <tr>
        <td class="right aligned">${_('Associated and federated with')}</td>
        <td>
          <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">
            ${entity.club.description}
          </a>
        </td>
      </tr>
    % else:
      % if entity.club:
        <tr>
          <td class="right aligned">${_('Associated to')}</td>
          <td>
            <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">
              ${entity.club.description}
            </a>
          </td>
        </tr>
      % endif
      % if entity.federation:
        <tr>
          <td class="right aligned">${_('Federated with')}</td>
          <td>
            <a href="${request.route_path('lit_club', guid=entity.federation.guid) | n}">
              ${entity.federation.description}
            </a>
          </td>
        </tr>
      % endif
    % endif
    % if opponents:
      <tr>
        <td class="right aligned">${_('Direct matches')}</td>
        <%
        wins, losts, ties, singles = entity.matchesSummary()
        done = wins + losts + ties
        msgs = []
        if wins:
            wp = ' (%d%%)' % (100 * wins // done)
            msgs.append((ngettext('%d won', '%d won', wins) % wins) + wp)
            if losts:
                lp = ' (%d%%)' % (100 * losts // done)
                msgs.append((ngettext('%d lost', '%d lost', losts) % losts + lp))
                if ties:
                    tp = ' (%d%%)' % (100 * ties // done)
                    msgs.append((ngettext('%d tied', '%d tied', ties) % ties) + tp)
        %>
        <td>${njoin(msgs)}</td>
      </tr>
    % endif
  </tbody>
</table>

<%def name="opponents_header()">
  <thead>
    <tr>
      <th class="center aligned player-header" rowspan="2">${_('Opponent')}</th>
      <th class="center aligned event-header" colspan="7">${_('Matches')}</th>
      <th class="center aligned event-header" colspan="3">${_('Coins')}</th>
    </tr>
    <tr>
      <th class="center aligned sortedby total-header">${_('Number')}</th>
      <th class="center aligned event-header winner">${_('Won')}</th>
      <th class="center aligned event-header winner">%</th>
      <th class="center aligned event-header">${_('Lost')}</th>
      <th class="center aligned event-header">%</th>
      <th class="center aligned event-header">${_('Tied')}</th>
      <th class="center aligned event-header">%</th>
      <th class="center aligned event-header">+</th>
      <th class="center aligned event-header">-</th>
      <th class="center aligned event-header">${_('Diff')}</th>
    </tr>
  </thead>
</%def>

<%def name="opponents_body()">
  <tbody>
    % for i, row in enumerate(opponents, 1):
      ${opponents_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="opponents_row(index, row)">
  <tr>
    <td class="player">
      ${'<a href="%s">%s</a>' % (request.route_path('lit_player_opponent', guid=entity.guid, opponent=row[0].guid), escape(row[0].caption(html=False))) | n}
    </td>
    <% done = row[1] + row[2] + row[3] %>
    <td class="right aligned sortedby event">${done}</td>
    <td class="right aligned event winner">${row[1]}</td>
      <td class="right aligned event winner">${100 * row[1] // done}%</td>
      <td class="right aligned event">${row[2]}</td>
      <td class="right aligned event">${100 * row[2] // done}%</td>
      <td class="right aligned event">${row[3]}</td>
      <td class="right aligned event">${100 * row[3] // done}%</td>
      <td class="right aligned event">${row[4]}</td>
      <td class="right aligned event">${row[5]}</td>
      <td class="right aligned event">${row[4] - row[5]}</td>
    </tr>
</%def>

% if opponents:
<table class="ui striped compact unstackable table ranking">
  <caption>${_('Opponents')}</caption>
  ${opponents_header()}
  ${opponents_body()}
</table>
% endif
