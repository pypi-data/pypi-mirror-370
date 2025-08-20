## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mer 17 dic 2008 02:16:28 CET
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2008-2010, 2013, 2014, 2016, 2018-2020, 2022, 2023, 2024 Lele Gaifax
##

<%inherit file="base.mako" />

<%
from operator import attrgetter
%>

<%def name="title()">
  ${_('SoL Lit')}
</%def>

## Body

<table class="ui compact unstackable definition table">
  <tbody>
    <tr>
      <td class="right aligned">${_('Clubs')}</td>
      <td>
        ${nclubs}
        (${ngettext('%d country', '%d countries', nccountries) % nccountries})
      </td>
    </tr>
    <tr>
      <td class="right aligned">${_('Federations')}</td>
      <td>${nfederations}</td>
    </tr>
    <tr>
      <td class="right aligned">${_('Championships')}</td>
      <td>${nchampionships}</td>
    </tr>
    <tr>
      <td class="right aligned">${_('Tourneys')}</td>
      <td>
        ${ntourneys}
        (<a href="${request.route_path('lit_latest', _query=dict(n=20))|n}">${_('latest 20')}</a>)
      </td>
    </tr>
    <tr>
      <td class="right aligned">${_('Players')}</td>
      <td>
        <a href="${request.route_path('lit_players')}">${nplayers}</a>
      </td>
    </tr>
    <tr>
      <td class="right aligned">${_('Ratings')}</td>
      <td>${nratings}</td>
    </tr>
  </tbody>
</table>

<div class="ui centered cards">
  % for country, code in sorted(bycountry):
    <% nc, nf, np = bycountry[(country, code)] %>
    <div class="${'red ' if nf else ''}card">
      <div class="content">
        % if code:
          <img class="right floated mini ui image" src="/static/images/flags/${code}.png"
               alt="${code} flag"/>
        % endif
        <div class="header">
          <a href="${request.route_path('lit_country', country=code)|n}">
            ${country}
          </a>
        </div>
      </div>
      <%
      nstats = 0
      if nc:
          nstats += 1
      if np:
          nstats += 1
      %>
      % if nstats:
        <% nstats_class = ['one', 'two'][nstats - 1] %>
        <div class="extra content">
          <div class="ui mini ${nstats_class} statistics">
            % if nc:
              <div class="statistic">
                <div class="value">
                  ${nc}
                </div>
                <div class="label">
                  ${ngettext('club', 'clubs', nc)}
                </div>
              </div>
            % endif
            % if np:
              <div class="statistic">
                <div class="value">
                  ${np}
                </div>
                <div class="label">
                  ${ngettext('player', 'players', np)}
                </div>
              </div>
            % endif
          </div>
        </div>
      % endif
    </div>
  % endfor
</div>
