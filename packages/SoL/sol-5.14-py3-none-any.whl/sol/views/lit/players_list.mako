## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mer 16 lug 2014 13:20:13 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2018, 2019, 2023 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="title()">
  ${_('Players directory')}
</%def>

<table class="ui compact unstackable definition table">
  <tbody>
    <tr>
      <td class="right aligned">${_('Country')}</td>
      <td>
        % if code:
          <img src="/static/images/flags/${code}.png" />
        % endif
        ${country}
      </td>
    </tr>
    % if letter:
      <tr>
        <td class="right aligned">${_('Letter')}</td>
        <td>«${letter}»</td>
      </tr>
    % endif
  </tbody>
</table>

% if letter:
  <div class="ui centered card">
    <div class="content">
      % for player in players:
        <p>
          <a href="${request.route_path('lit_player', guid=player.guid)}">
            ${player.caption(False)}
          </a>
        </p>
      % endfor
    </div>
  </div>
% else:
    <%
    byletter = {}
    for player in players:
        lst = byletter.setdefault(player.lastname[0], [])
        lst.append(player)
    %>

  <div class="ui centered cards">
    % for fnletter in sorted(byletter):
      <div class="card">
        <div class="content">
          <div class="header">« ${fnletter} »</div>
          % for player in byletter[fnletter]:
            <p>
              <a href="${request.route_path('lit_player', guid=player.guid)}">
                ${player.caption(False)}
              </a>
            </p>
          % endfor
        </div>
      </div>
    % endfor
  </div>
% endif
