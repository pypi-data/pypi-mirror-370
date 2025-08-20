## -*- coding: utf-8 -*-
## :Project:   SoL -- List of players associated with a club
## :Created:   lun 20 giu 2016 21:19:29 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2016, 2018 Lele Gaifax
##

<%inherit file="base.mako" />

<%def name="title()">
  ${_('Players directory')}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
  if entity.emblem:
      parent.club_emblem(url="/lit/emblem/%s" % entity.emblem,
      href=entity.siteurl,
      title=entity.description)
  %>
</%def>

<%def name="header()">
  ${parent.header()}
  <h2 class="title centered">
    <a href="${request.route_path('lit_club', guid=entity.guid) | n}">${entity.description}</a>
  </h2>
</%def>

<div class="ui centered cards">
  % for letter, plist in players:
    <div class="card">
      <div class="content">
        <div class="header">« ${letter} »</div>
        % for player in plist:
          <p>
            <a href="${request.route_path('lit_player', guid=player.guid)}">${player.caption(False)}</a>
          </p>
        % endfor
      </div>
    </div>
  % endfor
</div>
