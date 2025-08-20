// -*- coding: utf-8 -*-
// :Project:   SoL -- Competitors panel of tourney management
// :Created:   gio 20 nov 2008 18:22:40 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2016, 2018, 2024, 2025 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare console*/
/*jsl:declare ngettext*/
/*jsl:declare window*/

Ext.define('SoL.view.Competitors.Actions', {
    extend: 'MP.action.SaveAndReset',
    uses: ['Ext.Action'],

    statics: {
        ADD_COMPETITOR_ACTION: 'add_competitor',
        PRINT_COMPETITORS_ACTION: 'print_competitors',
        PRINT_BADGES_ACTION: 'print_badges'
    },

    initActions: function() {
        var me = this,
            ids = me.statics(),
            tourney = me.module.tourney;

        me.callParent();

        me.addCompetitorAction = me.addAction(new Ext.Action({
            itemId: ids.ADD_COMPETITOR_ACTION,
            text: _('Add…'),
            tooltip: _('Show selectable players.'),
            iconCls: 'add-user-icon',
            disabled: tourney.readOnly || tourney.prized
                || ((tourney.system !== 'swiss' || tourney.system !== 'roundrobin')
                    && tourney.currentturn > 0),
            hidden: tourney.readOnly || tourney.prized
                || ((tourney.system !== 'swiss' || tourney.system !== 'roundrobin')
                    && tourney.currentturn > 0),
            scope: me.component,
            handler: me.component.showOtherPlayers
        }));

        me.printCompetitorsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_COMPETITORS_ACTION,
            text: _('Competitors'),
            tooltip: _('Print current list of participants.'),
            iconCls: 'print-icon',
            handler: function() {
                var url = '/pdf/participants/' + tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.printBadgesAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_BADGES_ACTION,
            text: _('Badges'),
            tooltip: _('Print participant badges.'),
            iconCls: 'print-icon',
            hidden: tourney.readOnly,
            handler: function() {
                var desktop = me.module.app.getDesktop();
                SoL.module.Tourneys.printBadges(desktop, tourney.idtourney, false);
            }
        }));
    },

    attachActions: function() {
        var me = this,
            tourney = me.module.tourney;

        me.callParent();

        var panel = me.component.up('panel'),
            tbar = panel.child('#ttoolbar');

        if(!tourney.readOnly) {
            tbar.add(0, me.addCompetitorAction, ' ',
                     me.printBadgesAction,
                     me.printCompetitorsAction, '->',
                     me.saveAction,
                     me.restoreAction);
        } else {
            tbar.add(0, me.printBadgesAction,
                     me.printCompetitorsAction);
        }

        if(!me.module.tourney.prized && !me.module.tourney.readOnly) {
            var store = me.component.store;

            store.on('update', function(s, r, action) {
                //jsl:unused s
                //jsl:unused r
                if(action=='edit') {
                    me.saveAction.setDisabled(false);
                    me.restoreAction.setDisabled(false);

                    // Show the save action
                    panel.setWidth(420);
                }
            });
            store.on('load', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
                panel.setWidth(panel.initialConfig.width);
            });
            store.on('reject', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
                panel.setWidth(panel.initialConfig.width);
            });
        }
    }
});


Ext.define('SoL.view.Competitors.PlayersActions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'SoL.module.Tourneys'
    ],

    statics: {
        INSERT_PLAYERS_ACTION: 'insert_players',
        TOGGLE_SHOW_ALL_PLAYERS_ACTION: 'show_all_players'
    },

    initActions: function() {
        var me = this,
            ids = me.statics();

        me.callParent();

        me.insertPlayersAction = me.addAction(new Ext.Action({
            itemId: ids.INSERT_PLAYERS_ACTION,
            text: _('Insert selected players'),
            tooltip: _('Subscribe selected players to the tourney if not already present.'),
            iconCls: 'add-group-icon',
            disabled: true,
            needsSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                me.insertSelectedPlayers();
            }
        }));

        me.toggleShowAllPlayersAction = me.addAction(new Ext.Action({
            itemId: ids.TOGGLE_SHOW_ALL_PLAYERS_ACTION,
            text: _('Show all players'),
            tooltip: _('Toggle between all players or only active ones, whose participated to at least a tourney organized by the current club in the last year.'),
            iconCls: 'magnify-icon',
            handler: function() {
                me.toggleShowAllPlayers();
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.addDocked({
            xtype: 'toolbar',
            dock: 'bottom',
            ui: 'footer',
            layout: {
                pack: 'end'
            }
        })[0];

        tbar.add(me.insertPlayersAction, me.toggleShowAllPlayersAction);
        me.toggleShowAllPlayers(true);
    },

    toggleShowAllPlayers: function(setup) {
        var me = this,
            component = me.component,
            store = component.store,
            tourney = me.competitors.ownerCt.module.tourney,
            win = component.up();

        if(!component.orig_dataURL)
            component.orig_dataURL = component.dataURL;

        if(setup || !me.show_active_players) {
            me.toggleShowAllPlayersAction.setText(_('Show all players'));
            me.show_active_players = true;

            var today = new Date(),
                oneyearago = new Date(today.getFullYear()-1,
                                      today.getMonth(),
                                      today.getDate());

            store.proxy.url = Ext.String.urlAppend(component.orig_dataURL,
                                                   'played4club=' + tourney.IDClub);

            store.stickyFilter({
                id: 'lastplayed',
                property: 'LastPlayed',
                value: SoL.module.Tourneys.dateToISO(oneyearago),
                operator: ">="
            });

            win.setTitle(Ext.String.format(_("Players of last year's “{0}” tourneys"),
                                           tourney.Club));
        } else {
            me.toggleShowAllPlayersAction.setText(_('Show only active players'));
            me.show_active_players = false;
            store.proxy.url = component.orig_dataURL;
            store.stickyFilters.removeAtKey('lastplayed');
            store.filters.removeAtKey('lastplayed');
            store.load();
            win.setTitle(_('All players'));
        }
    },

    insertSelectedPlayers: function() {
        var me = this,
            grid = me.component,
            sels = grid.getSelectionModel().getSelection(),
            competitor,
            nplayers = 0,
            tourney = me.competitors.ownerCt.module.tourney,
            idtourney = tourney.idtourney,
            playersperteam = tourney.PlayersPerTeam,
            deststore = me.competitors.store,
            ids = me.player_ids;

        Ext.each(sels, function(record) {
            var idplayer = record.get('idplayer');
            var present = false;

            deststore.each(function(comp) {
                if(idplayer == comp.get('idplayer1') ||
                   idplayer == comp.get('idplayer2') ||
                   idplayer == comp.get('idplayer3') ||
                   idplayer == comp.get('idplayer4')) {
                    present = true;
                    return false;
                } else {
                    return true;
                }

            });

            if(!present) {
                if(nplayers === 0) {
                    competitor = deststore.add({
                        retired: false,
                        player1Nationality: record.get('nationality')
                    })[0];
                    competitor.set('idtourney', idtourney);
                    competitor.set('player1FirstName',
                                   record.get('firstname'));
                    competitor.set('player1LastName',
                                   record.get('lastname'));
                    competitor.set('player1Sex', record.get('sex'));
                }
                nplayers++;
                competitor.set('idplayer'+nplayers, idplayer);
                competitor.set('player'+nplayers+'FullName',
                               SoL.module.Players.full_name(record));
                if(nplayers == playersperteam) {
                    nplayers = 0;
                }
                ids.push(idplayer);
            }
        });

        // Refresh the DataView
        deststore.sort();
        me.competitors.refresh();

        // Reload remaining players
        grid.store.stickyFilter({
            id: 'ids',
            property: 'idplayer',
            value: ids.join(','),
            operator: '<>'
        });

        Ext.each(grid.plugins, function(p) {
            if(p.ptype == 'filterbar') {
                var field = p.fields.get('firstname');
                if (field) {
                    field.selectText();
                    field.focus(false, 200);
                }
                return false;
            }
            return true;
        });
    }
});


Ext.define('SoL.view.Competitors', {
    extend: 'Ext.view.View',
    requires: [
        'Ext.tip.ToolTip',
        'SoL.view.Competitors.Actions'
    ],

    alias: 'widget.competitors-dataview',

    autoScroll: true,
    tpl: [
        '<ul>',
        '<tpl for=".">',
        '<li class="competitor{dirtyCls} {Icon}"',
        '    id="competitor_{idplayer1}"',
        '    cid="{cid}">',
        // First player
        '<span class="player" id="player_{idplayer1}">',
        '{player1FullName}',
        '</span>',
        // Second player
        '<tpl if="idplayer2">',
        '<tpl if="idplayer3">, <tpl else> ' + _('and') + ' </tpl>',
        '<span class="player" id="player_{idplayer2}">',
        '{player2FullName}',
        '</span>',
        '</tpl>',
        // Third player
        '<tpl if="idplayer3">',
        '<tpl if="idplayer4">, <tpl else> ' + _('and') + ' </tpl>',
        '<span class="player" id="player_{idplayer3}">',
        '{player3FullName}',
        '</span>',
        '</tpl>',
        // Fourth player
        '<tpl if="idplayer4"> ' + _('and') + ' ',
        '<span class="player" id="player_{idplayer4}">',
        '{player4FullName}',
        '</span>',
        '</tpl>',
        '<tpl if="rate">',
        '<span class="rate"> ({rate})</span>',
        '</tpl>',
        // First player nationality
        '<span class="sol-flags-icon sol-flag-{player1Nationality}',
        ' competitor-flag" data-qtip="{player1Country}"></span>',
        '</li>',
        '</tpl>',
        '</ul>',
        '<div class="x-clear"></div>'
    ],
    itemSelector: 'li.competitor',

    statics: {
        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this,
                dataURL = '/tourney/competitors',
                dataview = {
                    xtype: 'competitors-dataview',
                    id: 'competitors-view',
                    plugins: [
                        Ext.create('SoL.view.Competitors.Actions', {
                            module: me
                        })
                    ]
                };

            if(config.tourney.PlayersPerTeam > 1 &&
               !config.tourney.prized &&
               !config.tourney.readOnly) {
                dataview.listeners = {
                    destroy: function(v) {
                        v.dragZone.destroy();
                    },

                    render: function(v) {
                        v.dragZone = new Ext.dd.DragZone(v.getEl(), {
                            ddGroup: 'player',

                            getDragData: function(e) {
                                var player = e.getTarget('span.player', 10, true);
                                if (player) {
                                    var container = player.parent(),
                                        cid = container.dom.attributes.cid.nodeValue,
                                        idcompetitor = parseInt(cid, 10),
                                        competitor,
                                        xy = player.getXY(),
                                        sourceEl = player.dom,
                                        d = sourceEl.cloneNode(true);

                                    d.id = Ext.id();
                                    if(isNaN(idcompetitor)) {
                                        // the node contains a phantom record
                                        competitor = v.store.data.findBy(function(r) {
                                            return r.id === cid;
                                        });
                                    } else {
                                        competitor = v.store.getById(idcompetitor);
                                    }
                                    return {
                                        sourceEl: sourceEl,
                                        sourceCompetitor: competitor,
                                        repairXY: xy,
                                        ddel: d
                                    };
                                } else {
                                    return null;
                                }
                            },

                            getRepairXY: function() {
                                return this.dragData.repairXY;
                            }
                        });

                        if(config.tourney.currentturn === 0) {
                            Ext.create('SoL.view.Competitors.PlayerDrop', v);
                        }
                    }
                };
            }

            if(config.tourney.PlayersPerTeam == 1 && !config.tourney.prized) {
                dataview.listeners = {
                    render: function(v) {
                        if(config.tourney.currentturn === 0) {
                            Ext.create('SoL.view.Competitors.PlayerDrop', v);
                        }
                    }
                };
            }

            var cfg = config.Competitors = {
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'top',
                    itemId: 'ttoolbar',
                    enableOverflow: true
                }],
                items: [dataview],
                layout: 'fit',
                title: _('Competitors'),
                xtype: 'panel'
            };

            MP.data.MetaData.fetch(dataURL, me, function(metadata) {
                var model,
                    overrides = {
                        rate: {
                            sendback: false
                        }
                    };

                model = Ext.define('MP.data.ImplicitModel-' + Ext.id(), {
                    extend: 'Ext.data.Model',
                    fields: metadata.fields(overrides),
                    idProperty: metadata.primary_key
                });

                dataview.store = Ext.create('MP.data.Store', {
                    model: model,
                    proxy: {
                        type: 'ajax',
                        url: dataURL,
                        reader: {
                            type: 'json',
                            idProperty: metadata.primary_key,
                            totalProperty: metadata.count_slot,
                            successProperty: metadata.success_slot,
                            root: metadata.root_slot
                        }
                    },
                    autoDestroy: true,
                    remoteSort: false,
                    sorters: ['player1LastName', 'player1FirstName'],
                    pageSize: 999,
                    listeners: {
                        beforeload: function(store, operation) {
                            // remove the sorters, we do local sort...
                            // silly ExtJS 4.2.1!
                            operation.sorters = undefined;
                        }
                    }
                });
                dataview.store.implicitModel = true;

                callback(cfg);
            });
        }
    },

    initEvents: function() {
        var me = this,
            tourney = me.ownerCt.module.tourney;

        if(!tourney.prized && !tourney.readOnly) {
            Ext.create('Ext.tip.ToolTip', {
                target: me.el,
                html: _('Double click to withdraw this competitor.'),
                delegate: 'span.player',
                trackMouse: true
            });
            me.on({
                itemdblclick: function(view, competitor) {
                    var prized = tourney.prized;

                    if(prized) {
                        return;
                    }

                    var players = [],
                        he = competitor.get('player1Sex') == 'M' ? _('he') : _('she');

                    for(var i=1; i <= 4; i++) {
                        var fn = competitor.get('player' + i + 'FullName');
                        if(fn) {
                            players.push(fn);
                        }
                    }

                    Ext.Msg.confirm(
                        _('Confirm competitor withdraw'),
                        Ext.String.format(
                            // TRANSLATORS: {0} is the name of the player, or the
                            // list of the names of the players in the team; {1}
                            // is the singular “she” or “he” pronoun
                            ngettext("Do you confirm the withdraw of {0}?<br/>Doing so {1} won't play further matches!",
                                     "Do you confirm the withdraw of {0}?<br/>Doing so they won't play further matches!",
                                     players.length),
                            Ext.toSentence(players, _('and')), he),
                        function(response) {
                            if('yes' == response) {
                                if(me.ownerCt.module.tourney.currentturn === 0) {
                                    view.store.deleteRecord(competitor);
                                } else {
                                    competitor.set('retired', true);
                                }
                                view.refresh();
                            }
                        });
                }
            });
        }
    },

    prepareData: function(data, index, record) {
        var me = this,
            tourney = me.ownerCt.module.tourney,
            ppt = tourney.PlayersPerTeam,
            dirty;

        me.callParent(data, index, record);

        if(record.data.retired) {
            dirty = 'retired-competitor';
        } else {
            dirty = me.store.classifyRecord(record, null, null, me.store);
        }
        if(ppt > 1) {
            var nplayers = 1;

            if(record.get('idplayer2')) {
                nplayers++;
                if(record.get('idplayer3')) {
                    nplayers++;
                    if(record.get('idplayer4')) {
                        nplayers++;
                    }
                }
            }
            if(nplayers != ppt) {
                data.Icon = 'group-error-icon';
            } else {
                data.Icon = 'group-icon';
            }
        } else {
            data.Icon = record.data.player1Sex == 'F'
                ? 'fuser-icon' : 'user-icon';
        }
        data.dirtyCls = dirty==='' ? '' : ' '+dirty;
        data.cid = record.data.idcompetitor || record.id;
        return data;
    },

    showOtherPlayers: function() {
        var me = this,
            otheractions,
            module = me.ownerCt.module.app.getModule('players-win'),
            idp, ids = [];

        me.store.each(function(comp) {
            ids.push(comp.get('idplayer1'));
            if((idp=comp.get('idplayer2'))) {
                ids.push(idp);
                if((idp=comp.get('idplayer3'))) {
                    ids.push(idp);
                    if((idp=comp.get('idplayer4'))) {
                        ids.push(idp);
                    }
                }
            }
        });

        otheractions = Ext.create('SoL.view.Competitors.PlayersActions', {
            competitors: me,
            player_ids: ids
        });
        module.createOrShowWindow('competitors', ids, otheractions);
    },

    commitChanges: function(callback, scope) {
        var me = this;

        me.store.commitChanges('/bio/saveChanges',
                               me.store.proxy.reader.idProperty,
                               callback, scope);
    },

    resetChanges: function() {
        var me = this;

        me.store.rejectChanges();
        me.refresh();
    }
});


Ext.define('SoL.view.Competitors.PlayerDrop', {
    extend: 'Ext.dd.DropTarget',
    uses: ['MP.window.Notification'],

    group: 'player',
    dropAllowedRemove : "x-dd-drop-ok-del",
    dropAllowedAdd : "x-dd-drop-ok-add",

    constructor: function(view) {
        var me = this;

        me.callParent([view.el, {}]);
        me.store = view.store;
        me.dataview = view;
        me.tourney = view.ownerCt.module.tourney;
        me.playersperteam = me.tourney.PlayersPerTeam;
    },

    isAnyPlayerAlreadyPresent: function(sels) {
        var me = this,
            present = false;

        function is_present(comp, id) {
            if(id == comp.get("idplayer1") ||
               id == comp.get("idplayer2") ||
               id == comp.get("idplayer3") ||
               id == comp.get("idplayer4")) {
                present = true;
                return false;
            } else
                return null;
        }

        for(var i=0; !present && i<sels.length; i++) {
            var id = sels[i].get("idplayer");
            me.store.each(function(comp) { return is_present(comp, id); });
        }

        return present;
    },

    notifyEnter: function(source, e, data) {
        var me = this,
            r;

        //<debug>
        console.debug('Checking droppability...');
        //</debug>

        if((r=me.notifyOver(source, e, data)) != me.dropNotAllowed) {
            me.callParent(source, e, data);
            return r;
        } else {
            return me.dropNotAllowed;
        }
    },

    notifyOver: function(source, e, data) {
        //jsl:unused source
        var me = this,
            target = me.playersperteam == 1 ? null : e.getTarget('.competitor'),
            idplayer1, index, comp, nplayers;

        if(me.tourney.readOnly) {
            //<debug>
            console.debug('Not allowed, readonly tourney');
            //</debug>
            return me.dropNotAllowed;
        }
        if(me.playersperteam==1 && target) {
            //<debug>
            console.debug('Not allowed, this is a single');
            //</debug>
            return me.dropNotAllowed;
        }

        var sels = data.records;
        if(sels) {
            // we are coming from the Players window
            if(me.isAnyPlayerAlreadyPresent(sels)) {
                //<debug>
                console.debug('Not allowed, player(s) already present');
                //</debug>
                return me.dropNotAllowed;
            }
            if(target) {
                idplayer1 = parseInt(target.id.split('_')[1], 10);
                index = me.store.find('idplayer1', idplayer1);
                comp = me.store.getAt(index);
                nplayers = 1;

                if(comp.get("idplayer2")) {
                    nplayers++;
                    if(comp.get("idplayer3")) {
                        nplayers++;
                        if(comp.get("idplayer4")) {
                            nplayers++;
                        }
                    }
                }
                //<debug>
                if(nplayers < me.playersperteam)
                    console.debug('New team player, allowed!');
                else
                    console.debug('Team is complete, not allowed!');
                //</debug>

                return ((nplayers < me.playersperteam)
                        ? me.dropAllowedAdd
                        : me.dropNotAllowed);
            } else {
                //<debug>
                console.debug('New competitor, allowed!');
                //</debug>
                return me.dropAllowedAdd;
            }
        } else {
            // we are reordering players

            if(target && data.sourceEl == target.firstChild) {
                return me.dropNotAllowed;
            } else {
                if(target) {
                    idplayer1 = parseInt(target.id.split('_')[1], 10);
                    index = me.store.find('idplayer1', idplayer1);
                    comp = me.store.getAt(index);
                    nplayers = 1;

                    if(comp.get("idplayer2")) {
                        nplayers++;
                        if(comp.get("idplayer3")) {
                            nplayers++;
                            if(comp.get("idplayer4")) {
                                nplayers++;
                            }
                        }
                    }
                    //<debug>
                    if(nplayers < me.playersperteam)
                        console.debug('Allowing player move to other team');
                    else
                        console.debug('Team is complete, cannot accept player move');
                    //</debug>
                    return ((nplayers < me.playersperteam)
                            ? me.dropAllowedAdd
                            : me.dropNotAllowed);
                } else {
                    //<debug>
                    console.debug('Allowing player deletion');
                    //</debug>
                    return me.dropAllowedRemove;
                }
            }
        }
    },

    notifyDrop : function(source, e, data) {
        //jsl:unused source
        var me = this,
            target = me.playersperteam == 1 ? null : e.getTarget('.competitor'),
            full_name = SoL.module.Players.full_name,
            idplayer, idplayer1, index, comp, nplayers, spos, others, sc, i, idp;

        if(me.tourney.readOnly) {
            //<debug>
            console.debug('Not allowed, readonly tourney');
            //</debug>
            return false;
        }
        if(me.playersperteam==1 && target) {
            //<debug>
            console.debug('Not allowed, this is a single');
            //</debug>
            return false;
        }

        var sels = data.records;

        if(sels) {
            // we are coming from the Players window
            if(me.isAnyPlayerAlreadyPresent(sels)) {
                return false;
            }

            if(target) {
                idplayer1 = parseInt(target.id.split('_')[1], 10);
                index = me.store.find('idplayer1', idplayer1);
                comp = me.store.getAt(index);
                nplayers = 1;

                if(comp.get('idplayer2')) {
                    nplayers++;
                    if(comp.get('idplayer3')) {
                        nplayers++;
                        if(comp.get('idplayer4')) {
                            nplayers++;
                        }
                    }
                }
                if((nplayers + sels.length) <= me.playersperteam) {
                    Ext.each(sels, function(r) {
                        nplayers++;
                        if(nplayers == 1) {
                            comp.set('player1Nationality', r.get('nationality'));
                            comp.set('player1FirstName', r.get('firstname'));
                            comp.set('player1LastName', r.get('lastname'));
                            comp.set('player1Sex', r.get('sex'));
                        }
                        comp.set('idplayer'+nplayers, r.get('idplayer'));
                        comp.set('player'+nplayers+'FullName', full_name(r));
                    }, me);
                } else {
                    return false;
                }
            } else {
                nplayers = 0;

                Ext.each(sels, function(r) {
                    if(nplayers === 0) {
                        comp = me.store.add({
                            retired: false,
                            player1Nationality: r.get('nationality')
                        })[0];
                        comp.set('idtourney', me.tourney.idtourney);
                        comp.set('player1FirstName', r.get('firstname'));
                        comp.set('player1LastName', r.get('lastname'));
                        comp.set('player1Sex', r.get('sex'));
                    }
                    nplayers++;
                    comp.set('idplayer'+nplayers, r.get('idplayer'));
                    comp.set('player'+nplayers+'FullName', full_name(r));
                    if(nplayers == me.playersperteam) {
                        nplayers = 0;
                    }
                });
            }

            var ids = [];
            me.store.each(function(r) {
                for(var j=0; j<4; j++) {
                    idp = r.get('idplayer' + j);
                    if(idp && idp !== '') {
                        ids.push(idp);
                    }
                }
            });

            // Reload remaining players
            sels[0].store.stickyFilter({
                id: 'ids',
                property: 'idplayer',
                value: ids.join(','),
                operator: '<>'
            });
        } else {
            // we are reordering players
            if(!target) {
                idplayer = parseInt(data.sourceEl.id.split('_')[1], 10);
                others = true;
                sc = data.sourceCompetitor;

                if(!sc) {
                    return false;
                }
                if(sc.get("idplayer1") == idplayer) {
                    spos = 1;
                    if(!(idp=sc.get("idplayer2")) || idp === '') {
                        others = false;
                    }
                } else if(sc.get("idplayer2") == idplayer) {
                    spos = 2;
                } else if(sc.get("idplayer3") == idplayer) {
                    spos = 3;
                } else {
                    spos = 4;
                }
                if(spos==1 && !others) {
                    me.store.deleteRecord(sc);
                } else {
                    for(i=spos; i<4; i++) {
                        sc.set('idplayer'+i, sc.get('idplayer'+(i+1)));
                        sc.set('player'+i+'FullName',
                               sc.get('player'+(i+1)+'FullName'));
                    }
                    sc.set('idplayer4', null);
                    sc.set('player4FullName', null);
                }
            } else {
                idplayer1 = parseInt(target.id.split('_')[1], 10);

                if(!data.sourceCompetitor) {
                    return false;
                }
                if(idplayer1 == data.sourceCompetitor.get("idplayer1")) {
                    return false;
                }

                index = me.store.find('idplayer1', idplayer1);
                comp = me.store.getAt(index);
                nplayers = 1;

                if(comp.get("idplayer2")) {
                    nplayers++;
                    if(comp.get("idplayer3")) {
                        nplayers++;
                        if(comp.get("idplayer4")) {
                            nplayers++;
                        }
                    }
                }
                if(nplayers < me.playersperteam) {
                    idplayer = parseInt(data.sourceEl.id.split('_')[1], 10);
                    var fnplayer;
                    sc = data.sourceCompetitor;

                    others = true;
                    if(sc.get("idplayer1") == idplayer) {
                        spos = 1;
                        if(!sc.get("idplayer2") || sc.get("idplayer2") === '') {
                            others = false;
                        }
                    } else if(sc.get("idplayer2") == idplayer) {
                        spos = 2;
                    } else if(sc.get("idplayer3") == idplayer) {
                        spos = 3;
                    } else {
                        spos = 4;
                    }
                    fnplayer = sc.get('player' + spos + 'FullName');
                    if(spos==1 && !others) {
                        me.store.deleteRecord(sc);
                    } else {
                        for(i=spos; i<4; i++) {
                            sc.set('idplayer'+i, sc.get('idplayer'+(i+1)));
                            sc.set('player'+i+'FullName',
                                   sc.get('player'+(i+1)+'FullName'));
                        }
                        sc.set('idplayer4', null);
                        sc.set('player4FullName', null);
                    }
                    nplayers++;
                    comp.set('idplayer'+nplayers, idplayer);
                    comp.set('player'+nplayers+'FullName', fnplayer);
                }
            }
        }

        me.dataview.store.sort();
        me.dataview.refresh();
        return true;
    }
});
