## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mer 09 lug 2014 17:34:22 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2016, 2018-2020, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="title()">
  ${entity.caption(html=False)}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
  if entity.emblem:
      parent.club_emblem(url="/lit/emblem/%s" % entity.emblem,
                         href=entity.siteurl,
                         title=entity.description)
  %>
</%def>

<table class="ui compact unstackable definition table">
  <tbody>
  % if entity.nationality:
    <tr>
      <td class="right aligned">${_('Country')}</td>
      <td>
        <img src="/static/images/flags/${entity.nationality}.png" />
        ${entity.country}
      </td>
    </tr>
  % endif
  % if entity.siteurl:
    <tr>
      <td class="right aligned">${_('Federation web site') if entity.isfederation else _('Club web site')}</td>
      <td><a href="${entity.siteurl}" target="_blank">${entity.siteurl}</a></td>
    </tr>
  % endif
  % if len(championships):
    <tr>
      <td class="right aligned">${_('Championships')}</td>
      <td>${len(entity.championships)}</td>
    </tr>
  % endif
  % if len(entity.associated_players):
    <tr>
      <td class="right aligned">${_('Players')}</td>
      <td><a href="${request.route_path('lit_club_players', guid=entity.guid) | n}">${len(entity.associated_players)}</a></td>
    </tr>
  % endif
  % if entity.isfederation and len(entity.federated_players):
    <tr>
      <td class="right aligned">${_('Federated players')}</td>
      <td><a href="${request.route_path('lit_club_players', guid=entity.guid) | n}">${len(entity.federated_players)}</a></td>
    </tr>
  % endif
  </tbody>
</table>

<%
singles = []
doubles = []
teams = []

for championship in championships:
    pt = []
    for t in championship.tourneys:
        if t.prized:
            pt.append(t)
    nt = len(pt)
    if nt:
        new = (today - pt[-1].date).days < 21
        if championship.playersperteam == 1:
            singles.append((championship, nt, new))
        elif championship.playersperteam == 2:
            doubles.append((championship, nt, new))
        else:
            teams.append((championship, nt, new))
%>

% if singles:
  <div class="ui centered card">
    <div class="content">
      <div class="header">${_('Singles')}</div>
      % for championship,nt,new in singles:
        <p class="championship">
          <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">
            ${championship.description}
          </a>
          (${ngettext('%d tourney', '%d tourneys', nt) % nt})
          % if new:
            <img src="/static/images/new.png" />
          % endif
        </p>
      % endfor
    </div>
  </div>
% endif

% if doubles:
  <div class="ui centered card">
    <div class="content">
      <div class="header">${_('Doubles')}</div>
      % for championship,nt,new in doubles:
        <p class="championship">
          <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">
            ${championship.description}
          </a>
          (${ngettext('%d tourney', '%d tourneys', nt) % nt})
          % if new:
            <img src="/static/images/new.png" />
          % endif
        </p>
      % endfor
    </div>
  </div>
% endif

% if teams:
  <div class="ui centered card">
    <div class="content">
      <div class="header">${_('Teams')}</div>
      % for championship,nt,new in teams:
        <p class="championship">
          <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">
            ${championship.description}
          </a>
          (${ngettext('%d tourney', '%d tourneys', nt) % nt})
          % if new:
            <img src="/static/images/new.png" />
          % endif
        </p>
      % endfor
    </div>
  </div>
% endif

% if not singles and not doubles and not teams:
  <h4 class="centered">${_('No championships!')}</h4>
% endif
