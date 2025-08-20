## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   sab 13 dic 2008 16:32:24 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2008-2010, 2013, 2014, 2016, 2018-2020, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${entity.caption(html=False)}
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

% if entity.acceptedDiscernibility() and entity.portrait:
<img class="centered portrait" src="/lit/portrait/${entity.portrait}" />
% endif

<%
participations = [p for p in entity.participations() if p.tourney.prized]
team_events = any(c.idplayer2 is not None for c in participations)
%>

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
        <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
      </td>
    </tr>
  % else:
  % if entity.club:
    <tr>
      <td class="right aligned">${_('Associated to')}</td>
      <td>
        <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
      </td>
    </tr>
  % endif
  % if entity.federation:
    <tr>
      <td class="right aligned">${_('Federated with')}</td>
      <td>
        <a href="${request.route_path('lit_club', guid=entity.federation.guid) | n}">${entity.federation.description}</a>
      </td>
    </tr>
  % endif
  % endif
  % if participations:
    <tr>
      <td class="right aligned">${_('Tourneys')}</td>
      <td>
        <%
        gold = silver = bronze = 0
        for p in participations:
            if p.rank == 1:
                gold += 1
            elif p.rank == 2:
                silver += 1
            elif p.rank == 3:
                bronze += 1
        if gold or silver or bronze:
            details = []
            if gold:
                details.append('<span class="winner">%s</span>' %
                               escape(ngettext('%d gold medal', '%d gold medals', gold) % gold))
            if silver:
                details.append(escape(ngettext('%d silver medal', '%d silver medals', silver) % silver))
            if bronze:
                details.append(escape(ngettext('%d bronze medal', '%d bronze medals', bronze) % bronze))
            details = ' (' + njoin(details) + ')'
        else:
            details = ''
        %>
        ${len(participations)}${details | n}
      </td>
    </tr>
    <tr>
      <td class="right aligned">${_('Matches')}</td>
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
      <td>
        ${njoin(msgs)}
        % if singles:
          ,
          <a href="${request.route_path('lit_player_matches', guid=entity.guid)}">
            ${ngettext('%d single', '%d singles', singles) % singles}
          </a>
        % endif
      </td>
    </tr>
  % endif
  </tbody>
</table>

<%def name="partecipations_header()">
  <thead>
    <tr>
      <th class="center aligned rank-header">#</th>
      <th class="center aligned tourney-header">${_('Tourney')}</th>
      <th class="center aligned championship-header">${_('Championship')}</th>
      <th class="center aligned sortedby date-header">${_('Date')}</th>
      % if team_events:
      <th class="center aligned player-header">${_('In team with')}</th>
      % endif
      <th class="center aligned event-header">${_('Pts')}</th>
      <th class="center aligned event-header">${_('Bch')}</th>
      <th class="center aligned center aligned event-header">${_('Net')}</th>
      <th class="center aligned total-header">${_('Prize')}</th>
      <th class="center aligned total-header">${_('Rank')}</th>
    </tr>
  </thead>
</%def>

<%def name="partecipations_body()">
  <tbody>
    <% prevs = None %>
    % for i, row in enumerate(participations, 1):
    ${partecipations_row(i, row, row.tourney.championship is prevs)}
    <% prevs = row.tourney.championship %>
    % endfor
  </tbody>
</%def>

<%def name="partecipations_row(index, row, samechampionship)">
    <tr class="${'winner' if row.rank==1 else ''}">
      <td class="right aligned index">${index}</td>
      <td class="center aligned tourney">
        <a href="${request.route_path('lit_tourney', guid=row.tourney.guid) | n}">${row.tourney.description}</a>
      </td>
      <td class="center aligned championship">
        <a href="${request.route_path('lit_championship', guid=row.tourney.championship.guid) | n}" title="${samechampionship and _('Idem') or row.tourney.championship.club.description}">
          ${samechampionship and '...' or row.tourney.championship.description}
        </a>
      </td>
      <td class="center aligned sortedby date">${row.tourney.date.strftime(_('%m-%d-%Y'))}</td>
      % if team_events:
      <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'idplayer%d'%i) not in (None, entity.idplayer)] %>
      <td class="center aligned player">
        ${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}
      </td>
      % endif
      <td class="right aligned event">${row.points}</td>
      <td class="right aligned event">${row.bucholz}</td>
      <td class="right aligned event">${row.netscore}</td>
      <td class="right aligned total">${format_prize(row.prize)}</td>
      <td class="right aligned total">${row.rank}</td>
    </tr>
</%def>

% if participations:
<table class="ui striped compact unstackable table ranking">
  <caption>${_('Tourneys results')}</caption>
  ${partecipations_header()}
  ${partecipations_body()}
</table>
% endif
