// -*- coding: utf-8 -*-
// :Project:   SoL -- Tourneys window
// :Created:   dom 19 ott 2008 01:35:43 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2021, 2023, 2024, 2025 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare window*/

Ext.define('SoL.module.Tourneys.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification'
    ],

    statics: {
        EDIT_TOURNEY_ACTION: 'edit_tourney',
        DOWNLOAD_TOURNEY_ACTION: 'download_tourney',
        REPLAY_TOURNEY_ACTION: 'duplicate_tourney',
        CREATE_KNOCKOUT_TOURNEY_ACTION: 'create_knockout_tourney',
        SHOW_TOURNEY_ACTION: 'show_tourney',
        SHOW_CHAMPIONSHIP_ACTION: 'show_championship',
        MANAGE_COMPETITORS_ACTION: 'manage_competitors',
        SHOW_LIT_PAGE_ACTION: 'show_lit',
        PRINT_BOARDLABELS_ACTION: 'print_boardlabels',
        PRINT_PLAYBILL_ACTION: 'print_playbill',
        PRINT_BLANK_BADGES: 'print_blank_badges'
    },

    initActions: function() {
        var me = this,
            ids = me.statics();

        me.callParent();

        me.editTourneyAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_TOURNEY_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected tourney.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditTourneyWindow(record);
            }
        }));

        me.showTourneyAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_TOURNEY_ACTION,
            text: _('Details'),
            tooltip: _('Show details of this tourney.'),
            iconCls: 'show-tourney-detail-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    module = me.module.app.getModule('tourney-win');

                module.createOrShowWindow(record);

                /* Since there is a chance that the tourney gets modified,
                 * close this window to avoid possible disalignments.
                 * This is the simplest thing to do to prevent any
                 * confusion to the user.
                 */

                var desktop = me.module.app.getDesktop(),
                    win = desktop.getWindow(me.module.id);

                if(win) {
                    win.destroy();
                }
            }
        }));

        me.showChampionshipAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CHAMPIONSHIP_ACTION,
            text: _('Championship'),
            tooltip: _('Show the championship this tourney belongs.'),
            iconCls: 'championships-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idchampionship = record.get('idchampionship'),
                    module = me.module.app.getModule('championships-win');
                module.createOrShowWindow('tourneys', idchampionship);
            }
        }));

        me.manageTourneyCompetitorsAction = me.addAction(new Ext.Action({
            itemId: ids.MANAGE_COMPETITORS_ACTION,
            text: _('Competitors'),
            tooltip: _("Manage tourney competitors, allowing player substitutions, even after prize-giving.<br>Use with <b>caution</b> only when you <i>know what you're doing</i>!"),
            iconCls: 'edit-user-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idtourney = record.get('idtourney'),
                    tourney = record.get('description'),
                    championship = record.get('Championship'),
                    hasrating = !!record.get('idrating'),
                    date = record.get('date'),
                    ppt = record.get('PlayersPerTeam'),
                    module = me.module.app.getModule('competitors-win');

                module.createOrShowWindow(idtourney, tourney, date, championship, ppt, hasrating);
            }
        }));

        me.duplicateTourneyAction = me.addAction(new Ext.Action({
            itemId: ids.REPLAY_TOURNEY_ACTION,
            text: _('Replay again'),
            tooltip: _('Duplicate selected tourney and its competitors on today.'),
            iconCls: 'replay-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.duplicateTourney(record);
            }
        }));

        me.createKnockoutTourneyAction = me.addAction(new Ext.Action({
            itemId: ids.CREATE_KNOCKOUT_TOURNEY_ACTION,
            text: _('Create knockout tourney'),
            tooltip: _('Create a knockout tourney from the selected one.'),
            iconCls: 'replay-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.createKnockoutTourney(record);
            }
        }));

        me.downloadTourneyAction = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEY_ACTION,
            text: _('Download'),
            tooltip: _('Download this tourney data.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idtourney = record.get('idtourney'),
                    url = '/bio/dump?idtourney=' + idtourney;

                window.open(url, "_blank");
            }
        }));

        me.showLitPageAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_LIT_PAGE_ACTION,
            text: _('Lit page'),
            tooltip: _('Show the corresponding Lit page.'),
            iconCls: 'lit-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    guid = record.get('guid'),
                    url = '/lit/tourney/' + guid;

                window.open(url, "_blank");
            }
        }));

        me.printBoardLabelsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_BOARDLABELS_ACTION,
            text: _('Board labels'),
            tooltip: _('Print board labels for this tourney, to allow self-insertion of matches results.'),
            iconCls: 'print-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.printBoardLabels(record);
            }
        }));

        me.printPlaybillAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_PLAYBILL_ACTION,
            text: _('Playbill'),
            tooltip: _('Print the tourney playbill with QRCode to reach its Lit page.'),

            iconCls: 'print-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idtourney = record.get('idtourney'),
                    url = '/pdf/playbill/' + idtourney;

                window.open(url, '_blank');
            }
        }));

        me.printBlankBadgesAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_BLANK_BADGES_ACTION,
            text: _('Blank badges'),
            tooltip: _('Print a sheet of blank player badges.'),

            iconCls: 'print-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    desktop = me.module.app.getDesktop();
                SoL.module.Tourneys.printBadges(desktop, record.get('idtourney'), true);
            }
        }));
    },

    attachActions: function() {
        var me = this,
            args = [];

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        if(me.component.noAddAndDelete) {
            args.push(0);
        } else {
            args.push(2);
            args.push(' ');
        }
        args.push(me.editTourneyAction,
                  me.showTourneyAction,
                  me.manageTourneyCompetitorsAction,
                  me.duplicateTourneyAction,
                  me.showChampionshipAction);

        tbar.add.apply(tbar, args);

        me.component.on({
            itemdblclick: function() {
                if(!me.editTourneyAction.isDisabled())
                    me.editTourneyAction.execute();
            }
        });

        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditTourneyWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this,
            disable = me.component.shouldDisableAction(act),
            statics = me.statics(),
            currentuser = me.module.app.user,
            record;

        if(!disable && !currentuser.is_admin) {
            if(act.itemId == statics.EDIT_TOURNEY_ACTION ||
               act.itemId == statics.MANAGE_COMPETITORS_ACTION) {
                record = me.component.getSelectionModel().getSelection()[0];

                if(record.get('idowner') !== null
                   && record.get('idowner') !== currentuser.user_id)
                    disable = true;
            }
        }
        if(!disable && act.itemId == statics.CREATE_KNOCKOUT_TOURNEY_ACTION) {
            record = me.component.getSelectionModel().getSelection()[0];

            if(!record.get('prized') || record.get('system') == 'knockout')
                disable = true;
        }

        return disable;
    },

    showEditTourneyWindow: function(record) {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win = desktop.getWindow('edit-tourney-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(800, 600),
            editors = metadata.editors({
                '*': { editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%') },
                description: { editor: { minLength: 6 } },
                Championship: {
                    editor: {
                        listeners: {
                            beforequery: function(queryPlan) {
                                var store = queryPlan.combo.store;
                                var idclub = me.module.idclub;

                                if(idclub) {
                                    store.addFilter({
                                        id: 'currentclub',
                                        property: 'idclub',
                                        value: idclub,
                                        operator: '='
                                    }, false);
                                }
                            },
                            select: function(combo, records) {
                                // Alter data directly, to avoid triggering data-changed
                                record.data['IDClub'] = records[0].get('idclub');
                            }
                        }
                    }
                },
                Rating: {
                    editor: {
                        // Force re-execution of the query, the championship (and
                        // thus the club id) may have changed
                        queryCaching: false,
                        listeners: {
                            beforequery: function(queryPlan) {
                                var store = queryPlan.combo.store;
                                var idclub = record.get('IDClub');

                                if(idclub) {
                                    store.addFilter({
                                        id: 'currentclub',
                                        property: 'idclub',
                                        value: "NULL," + idclub,
                                        operator: '='
                                    }, false);
                                }
                            }
                        }
                    }
                }
            }),
            form = Ext.create('MP.form.Panel', {
                autoScroll: true,
                fieldDefaults: {
                    labelWidth: 100,
                    margin: '15 10 0 10'
                },
                items: [{
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'container',
                        layout: 'anchor',
                        flex: 1,
                        items: [
                            editors.date,
                            editors.description,
                            editors.Championship,
                            editors.HostingClub,
                            editors.location,
                            editors.socialurl,
                            editors.system,
                            editors.matcheskind,
                            editors.finals,
                            editors.finalkind
                        ]
                    }, {
                        xtype: 'container',
                        layout: 'anchor',
                        flex: 1,
                        items: [
                            editors.duration,
                            editors.prealarm,
                            editors.couplings,
                            editors.delaytoppairing,
                            editors.delaycompatriotpairing,
                            editors.phantomscore,
                            editors.retirements,
                            editors.Rating,
                            editors.Owner
                        ]
                    }]
                }],
                buttons: [{
                    text: _('Cancel'),
                    handler: function() {
                        if(record.phantom) {
                            record.store.deleteRecord(record);
                        }
                        win.close();
                    }
                }, {
                    text: _('Confirm'),
                    formBind: true,
                    handler: function() {
                        if(form.isValid()) {
                            form.updateRecord(record);
                            win.close();
                            Ext.create("MP.window.Notification", {
                                position: 't',
                                width: 260,
                                title: _('Changes have been applied…'),
                                html: _('Your changes have been applied <strong>locally</strong>.<br/><br/>To make them permanent you must click on the <blink>Save</blink> button.'),
                                iconCls: 'info-icon'
                            }).show();
                        }
                    }
                }]
            });

        win = desktop.createWindow({
            id: 'edit-tourney-win',
            title: _('Edit tourney'),
            iconCls: me.module.iconCls,
            width: size.width,
            height: size.height,
            modal: true,
            items: form,
            closable: false,
            minimizable: false,
            maximizable: false,
            resizable: false,
            tools: [{
                type: 'help',
                tooltip: _('Show user manual section.'),
                callback: function() {
                    var whsize = desktop.getReasonableWindowSize(800, 640),
                        wh = Ext.create('SoL.window.Help', {
                            width: whsize.width,
                            height: whsize.height,
                            // TRANSLATORS: this is the URL of the manual page explaining
                            // tourneys insert/edit, do not change unless the manual is
                            // actually translated in the target language
                            help_url: _('/static/manual/en/tourneys.html#insert-and-edit'),
                            title: _('Help on tourney insert/edit')
                        });

                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        win.show();
    },

    duplicateTourney: function(record) {
        var me = this,
            idtourney = record.get('idtourney');

        Ext.Msg.confirm(
            _('Confirm tourney duplication'),
            _('The selected tourney, with its competitors but not the matches, will be replicated on the current day. Do you confirm?'),
            function(response) {
                if('yes' == response) {
                    Ext.create("MP.window.Notification", {
                        position: 'br',
                        html: _('Replicating selected tourney…'),
                        title: _('Please wait'),
                        iconCls: 'waiting-icon'
                    }).show();

                    Ext.Ajax.request({
                        url: '/tourney/replayToday',
                        params: { idtourney: idtourney },
                        success: function(result) {
                            var res = Ext.decode(result.responseText),
                                newid, store, prevOptions;
                            if(res && res.success) {
                                Ext.create("MP.window.Notification", {
                                    position: 'br',
                                    iconCls: 'done-icon',
                                    title: _('Done'),
                                    html: res.message
                                }).show();
                                newid = res.new_idtourney;
                                store = me.component.store;
                                prevOptions = Ext.apply({}, store.lastOptions);
                                store.reload({
                                    callback: function(records) {
                                        for(var i=0; i<records.length; i++) {
                                            if(records[i].getId() == newid) {
                                                me.showEditTourneyWindow(records[i]);
                                                break;
                                            }
                                        }
                                        store.lastOptions = prevOptions;
                                    }
                                });
                            } else {
                                Ext.create("MP.window.Notification", {
                                    position: 'br',
                                    iconCls: 'alert-icon',
                                    title: _('Error'),
                                    html: res
                                        ? res.message
                                        : _('Cannot decode JSON object')
                                }).show();
                            }
                        },
                        failure: function (result) {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                iconCls: 'alert-icon',
                                title: _('Error'),
                                html: result.statusText
                            }).show();
                        }
                    });
                }
            }
        );
    },

    createKnockoutTourney: function(record) {
        var me = this,
            win, form,
            winWidth = 215,
            winHeight = 110,
            top_players;

        var handler = function() {
            var frm = form.getForm();
            if(frm.isValid()) {
                var ncompetitors = frm.getFields().items[0].getValue();
                win.destroy();

                Ext.create("MP.window.Notification", {
                    position: 'br',
                    html: _('Creating knockout tourney…'),
                    title: _('Please wait'),
                    iconCls: 'waiting-icon'
                }).show();

                Ext.Ajax.request({
                    url: '/tourney/createKnockout',
                    params: {
                        idtourney: record.get('idtourney'),
                        ncompetitors: ncompetitors
                    },
                    success: function(result) {
                        var res = Ext.decode(result.responseText),
                            newid, store, prevOptions;
                        if(res && res.success) {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                iconCls: 'done-icon',
                                title: _('Done'),
                                html: res.message
                            }).show();
                            newid = res.new_idtourney;
                            store = me.component.store;
                            prevOptions = Ext.apply({}, store.lastOptions);
                            store.reload({
                                callback: function(records) {
                                    for(var i=0; i<records.length; i++) {
                                        if(records[i].getId() == newid) {
                                            me.showEditTourneyWindow(records[i]);
                                            break;
                                        }
                                    }
                                    store.lastOptions = prevOptions;
                                }
                            });
                        } else {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                iconCls: 'alert-icon',
                                title: _('Error'),
                                html: res
                                    ? res.message
                                    : _('Cannot decode JSON object')
                            }).show();
                        }
                    },
                    failure: function (result) {
                        Ext.create("MP.window.Notification", {
                            position: 'br',
                            iconCls: 'alert-icon',
                            title: _('Error'),
                            html: result.statusText
                        }).show();
                    }
                });
            }
        };

        var onKeyDown = function(field, event) {
            if (event.keyCode === event.RETURN || event.keyCode === 10) {
                handler();
            }
        };

        var onSpinUp = function(field) {
            var value = top_players,
                p2 = Math.trunc(Math.log2(value));
            value = Math.pow(2, p2 + 1);
            top_players = value;
            // the effect of the trigger is applied *after* we set the value
            field.setValue(value-1);
        };

        var onSpinDown = function(field) {
            var value = top_players,
                p2 = Math.trunc(Math.log2(value));
            value = Math.pow(2, p2 - 1);
            top_players = value;
            // the effect of the trigger is applied *after* we set the value
            field.setValue(value+1);
        };

        var validator = function(value) {
            value = parseInt(value, 10);
            var p2 = Math.log2(value);
            if(p2 > 0 && p2 != Math.trunc(p2)) {
                return _("Must be a power-of-two, i.e. 2, 4, 8, 16…");
            } else {
                top_players = value;
                return true;
            }
        };

        var ncompetitors = record.get('Competitors'),
            maxcompetitors = Math.pow(2, Math.trunc(Math.log2(ncompetitors)));

        top_players = Math.min(16, maxcompetitors);

        form = new Ext.form.Panel({
            frame: true,
            bodyPadding: '10 10 0',
            defaults: {
                labelWidth: 90,
                anchor: '100%'
            },
            items: [{
                xtype: 'numberfield',
                itemId: 'ncompetitors',
                allowBlank: false,
                allowDecimals: false,
                minValue: 2,
                maxValue: maxcompetitors,
                value: top_players,
                validator: validator,
                enableKeyEvents: true,
                fieldLabel: _('Top competitors'),
                listeners: {
                    keydown: onKeyDown,
                    spinup: onSpinUp,
                    spindown: onSpinDown
                }

            }],
            buttons: [{
                text: _('Cancel'),
                handler: function() {
                    win.destroy();
                }
            }, {
                text: _('Confirm'),
                formBind: true,
                handler: handler
            }]
        });

        win = me.module.app.getDesktop().createWindow({
            title: _('Create knockout tourney'),
            width: winWidth,
            height: winHeight,
            layout: 'fit',
            minimizable: false,
            maximizable: false,
            items: [form],
            defaultFocus: 'ncompetitors'
        });

        win.show();
    },

    printBoardLabels: function(record) {
        var me = this,
            idtourney = record.get('idtourney'),
            ncompetitors = record.get('Competitors'),
            url = '/pdf/boardlabels/' + idtourney,
            win, form,
            winWidth = 245,
            winHeight = 110;

        var handler = function() {
            var frm = form.getForm();
            if(frm.isValid()) {
                var flds = frm.getFields(),
                    nboards = flds.items[0].getValue();
                url += '?nboards=' + nboards;
                win.destroy();
                window.open(url, "_blank");
            }
        };

        var onKeyDown = function(field, event) {
            if (event.keyCode === event.RETURN || event.keyCode === 10) {
                handler();
            }
        };

        form = new Ext.form.Panel({
            frame: true,
            bodyPadding: '10 10 0',
            defaults: {
                labelWidth: 120,
                anchor: '100%'
            },
            items: [{
                xtype: 'numberfield',
                itemId: 'nboards',
                allowBlank: false,
                allowDecimals: false,
                minValue: 1,
                value: Math.trunc(ncompetitors / 2) || 1,
                enableKeyEvents: true,
                fieldLabel: _('Number of carromboards'),
                listeners: {
                    keydown: onKeyDown,
                    scope: me
                }
            }],
            buttons: [{
                text: _('Cancel'),
                handler: function() {
                    win.destroy();
                }
            }, {
                text: _('Confirm'),
                formBind: true,
                handler: handler
            }]
        });

        win = me.module.app.getDesktop().createWindow({
            title: _('Print carromboard labels'),
            width: winWidth,
            height: winHeight,
            layout: 'fit',
            minimizable: false,
            maximizable: false,
            items: [form],
            defaultFocus: 'nboards'
        });

        win.show();
    }
});


Ext.define('SoL.module.Tourneys', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Tourneys.Actions',
        'SoL.module.Users',
        'SoL.window.Help'
    ],

    statics: {
        dateToISO: function(date) {
            var year = '' + date.getFullYear(),
                month = '' + (date.getMonth() + 1),
                day = '' + date.getDate();
            if(month.length < 2) {
                month = '0' + month;
            }
            if(day.length < 2) {
                day = '0' + day;
            }
            return year + '-' + month + '-' + day;
        },

        printBadges: function(desktop, idtourney, blank) {
            var me = this,
                url = '/pdf/badges/' + idtourney + '?',
                win, form,
                winWidth = 380,
                winHeight = 180;

            if(blank) {
                url += 'blank&';
            }

            var handler = function() {
                var frm = form.getForm();
                if(frm.isValid()) {
                    var flds = frm.getFields();
                    url += Ext.Object.toQueryString({
                        alt_championship: flds.items[0].getValue(),
                        alt_date: flds.items[1].getValue(),
                        alt_tourney: flds.items[2].getValue(),
                    });
                    win.destroy();
                    window.open(url, "_blank");
                }
            };

            form = new Ext.form.Panel({
                frame: true,
                bodyPadding: '10 10 0',
                defaults: {
                    labelWidth: 100,
                    anchor: '100%'
                },
                items: [{
                    xtype: 'textfield',
                    itemId: 'alt_championship',
                    allowBlank: true,
                    fieldLabel: _('Championship'),
                    emptyText: _('Alternative championship description')
                }, {
                    xtype: 'textfield',
                    itemId: 'alt_date',
                    allowBlank: true,
                    fieldLabel: _('Date'),
                    emptyText: _('Alternative date value')
                }, {
                    xtype: 'textfield',
                    itemId: 'alt_tourney',
                    allowBlank: true,
                    fieldLabel: _('Tourney'),
                    emptyText: _('Alternative tourney description')
                }],
                buttons: [{
                    text: _('Cancel'),
                    handler: function() {
                        win.destroy();
                    }
                }, {
                    text: _('Confirm'),
                    formBind: true,
                    handler: handler
                }]
            });

            win = desktop.createWindow({
                title: blank ? _('Print blank badges') : _('Print participant badges'),
                width: winWidth,
                height: winHeight,
                layout: 'fit',
                minimizable: false,
                maximizable: false,
                items: [form],
                defaultFocus: 'alt_championship'
            });

            win.show();
        }
    },

    id: 'tourneys-win',
    iconCls: 'tourneys-icon',
    launcherText: function() {
        return _('Tourneys');
    },
    launcherTooltip: function() {
        return _('<b>Tourneys</b><br />Basic tourneys management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/tourneys',
        saveChangesURL: '/bio/saveChanges',
        sorters: [{property: 'date', direction: 'DESC'}],
        stripeRows: true,
        selModel: {
            mode: 'MULTI'
        }
    },

    getConfig: function(callback) {
        var me = this,
            cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    Owner: { filter: false }
                };

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Tourneys.Actions',
                                   { module: me }),
                        Ext.create('SoL.module.Users.AssignOwnership',
                                   { module: me })
                    ]
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(caller, id, description, idclub, club, couplings, closed,
                          idrating, rating) {
        var me = this,
            config = me.config,
            desktop = me.app.getDesktop(),
            win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.idclub = idclub;

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(920, 421, "NE"),
                    filteredOn;

                if(club) {
                    filteredOn = ' (' + Ext.String.format(
                        // TRANSLATORS: this is the explanation on the window title when the
                        // filter is a championship, with its club
                        _('in championship {0}, organized by {1}'),
                        description, club) + ')';
                } else if(description) {
                    var explanation;

                    switch(caller) {
                        case 'championships':
                            // TRANSLATORS: this is the explanation on the window title when
                            // the filter is a championship
                            explanation = _('in championship');
                            break;

                        case 'clubs':
                            // TRANSLATORS: this is the explanation on the window title when
                            // the filter is a club
                            explanation = _('hosted by');
                            break;

                        case 'players':
                            // TRANSLATORS: this is the explanation on the window title when
                            // the filter is a player
                            explanation = _('played by');
                            break;

                        case 'ratings':
                            // TRANSLATORS: this is the explanation on the window title when
                            // the filter is a rating
                            explanation = _('related with');
                            break;

                        case 'users':
                            // TRANSLATORS: this is the explanation on the window title when
                            // the filter is a user
                            explanation = _('owned by');
                            break;

                        default:
                            explanation = '';
                            break;
                    }
                    if(explanation !== '') {
                        explanation += ' ';
                    }
                    filteredOn = ' (' + explanation + description + ')';
                } else {
                    filteredOn = '';
                }

                config = Ext.apply({
                    newRecordData: {
                        date: new Date(),
                        currentturn: 0,
                        rankedturn: 0,
                        prized: false,
                        duration: 45,
                        prealarm: 5,
                        phantomscore: 25,
                        finals: 0,
                        delaytoppairing: 1,
                        delaycompatriotpairing: 0,
                        couplings: couplings || 'serial',
                        retirements: 'none',
                        system: 'swiss',
                        matcheskind: 'simple'
                    },
                    filters: [{
                        property: 'date',
                        value: SoL.module.Tourneys.dateToISO(new Date()),
                        operator: '<='
                    }]
                }, config);

                if(caller == 'championships') {
                    Ext.apply(config.newRecordData, {
                        idchampionship: id,
                        Championship: description,
                        idrating: idrating,
                        Rating: rating
                    });

                    Ext.apply(config, {
                        noAddAndDelete: closed,
                        stickyFilters: [{
                            property: 'idchampionship',
                            value: id,
                            operator: '='
                        }]
                    });
                } else if(caller == 'ratings') {
                    Ext.apply(config.newRecordData, {
                        idrating: id,
                        Rating: description
                    });

                    Ext.apply(config, {
                        stickyFilters: [{
                            property: 'idrating',
                            value: id,
                            operator: '='
                        }]
                    });
                } else if(caller == 'players') {
                    Ext.apply(config, {
                        noAddAndDelete: true,
                        extraParams: { idplayer: id }
                    });
                } else if(caller == 'users') {
                    Ext.apply(config, {
                        stickyFilters: [{
                            property: 'idowner',
                            value: id,
                            operator: '='
                        }]
                    });
                } else if(caller == 'clubs') {
                    Ext.apply(config, {
                        stickyFilters: [{
                            property: 'idhostingclub',
                            value: id,
                            operator: '='
                        }]
                    });
                }

                win = desktop.createWindow({
                    id: me.id,
                    title: (me.windowTitle || me.getLauncherText()) + filteredOn,
                    taskbuttonTooltip: me.getLauncherTooltip(),
                    iconCls: me.iconCls,
                    items: [config],
                    x: size.x,
                    y: size.y,
                    width: size.width,
                    height: size.height,
                    tools: [{
                        type: 'help',
                        tooltip: _('Show user manual section.'),
                        callback: function() {
                            var whsize = desktop.getReasonableWindowSize(800, 640);
                            var wh = Ext.create('SoL.window.Help', {
                                width: whsize.width,
                                height: whsize.height,
                                // TRANSLATORS: this is the URL of the manual page explaining
                                // tourneys management, do not change unless the manual is
                                // actually translated in the target language
                                help_url: _('/static/manual/en/tourneys.html'),
                                title: _('Help on tourneys management')
                            });
                            wh.show();
                        }
                    }]
                });

                var grid = win.child('editable-grid');

                // Fetch the first page of records, and when done show
                // the window
                grid.store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });

                var da = grid.findActionById('delete');
                if(da)
                    da.shouldBeDisabled = me.shouldDisableDeleteAction.bind(grid);
            }
        );
    },

    shouldDisableDeleteAction: function() {
        var grid = this,
            sm = grid.getSelectionModel(),
            currentuser = grid.up().up().app.user;

        if(sm.getCount() > 0) {
            var selrecs = sm.getSelection(),
                disable = false;

            for(var i=selrecs.length-1; i>=0; i--) {
                var record = selrecs[i];

                if(!currentuser.is_admin
                   && record.get('idowner') !== null
                   && currentuser.user_id !== record.get('idowner')) {
                    disable = true;
                    break;
                }
            }
            return disable;
        } else {
            return true;
        }
    }
});


Ext.define('SoL.module.MyTourneys', {
    extend: 'SoL.module.Tourneys',

    id: 'my-tourneys-win',
    iconCls: 'tourneys-icon',
    launcherText: null, // don't show an entry in the start menu

    init: function() {
        var me = this,
            user = me.app.user;

        if(!me.config.orig_dataURL) me.config.orig_dataURL = me.config.dataURL;
        me.config.dataURL = Ext.String.urlAppend(me.config.orig_dataURL,
                                                 'filter_by_idowner=' + (user.is_admin
                                                                         ? 'NULL'
                                                                         : user.user_id));
        me.windowTitle = Ext.String.format(_('Tourneys managed by {0}'), user.fullname);
        me.callParent();
    }
});
