## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mer 25 lug 2018 12:41:35 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2018-2020, 2023, 2024 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="title()">
  ${country}
</%def>

<%def name="club_emblem(url='', href='')">
  % if code:
    <div id="club_emblem">
      <img id="emblem" src="/static/images/flags/${code}.png" />
    </div>
  % endif
</%def>

## Body

<table class="ui compact unstackable definition table">
  <tbody>
    % if nclubs:
      <tr>
        <td class="right aligned">${_('Clubs')}</td>
        <td>
          ${nclubs}
        </td>
      </tr>
    % endif
    % if nfederations:
      <tr>
        <td class="right aligned">${_('Federations')}</td>
        <td>${nfederations}</td>
      </tr>
    % endif
    % if nplayers:
      <tr>
        <td class="right aligned">${_('Players')}</td>
        <td>
          <a href="${request.route_path('lit_players_list', country=code)}">
            ${nplayers}
          </a>
        </td>
      </tr>
    % endif
  </tbody>
</table>

% if nclubs:
  <div class="ui centered cards">
    % for club, guid, emblem, isfederation, nc, np in sorted(clubs):
      <div class="${'red ' if isfederation else ''}card">
        <div class="content">
          % if emblem:
            <img class="right floated tiny ui image" src="/lit/emblem/${emblem}"
                 alt="Club's emblem" />
          % endif
          <div class="header">
            <a href="${request.route_path('lit_club', guid=guid) | n}">${club}</a>
          </div>
          <div class="meta">
            % if nc:
              <span>${ngettext('%d championship', '%d championships', nc) % nc}</span>
            % endif
            % if np:
              <a href="${request.route_path('lit_club_players', guid=guid) | n}">
                ${ngettext('%d player', '%d players', np) % np}
              </a>
            % endif
          </div>
        </div>
      </div>
    % endfor
  </div>
% else:
  <h4 class="centered">${_('No clubs!')}</h4>
% endif
