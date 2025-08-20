## -*- coding: utf-8 -*-
## :Project:   SoL
## :Created:   mer 16 lug 2014 12:19:04 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2014, 2016, 2018 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="title()">
  ${_('Players directory')}
</%def>

## Body

<div class="ui centered cards">
  % for letter, countsbycountry in index:
    <div class="card">
      <div class="content">
        <div class="header">« ${letter} »</div>
        % for count in countsbycountry:
          <p>
            <a href="${request.route_path('lit_players_list', country=count['code'], _query={'letter':letter})}">
              % if count['code']:
                <img src="/static/images/flags/${count['code']}.png" />
              % endif
              ${count['country']}: ${count['count']} ${ngettext('player', 'players', count['count'])}
            </a>
          </p>
        % endfor
      </div>
    </div>
  % endfor
</div>
