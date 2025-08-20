// -*- coding: utf-8 -*-
// :Project:   SoL -- The ratings window
// :Created:   gio 05 dic 2013 20:31:44 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2016, 2018, 2020, 2021, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/

Ext.define('SoL.module.Ratings.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification',
        'SoL.window.Help'
    ],

    statics: {
        EDIT_RATING_ACTION: 'edit_rating',
        RECOMPUTE_RATING_ACTION: 'recompute_rating',
        DOWNLOAD_TOURNEYS_ACTION: 'download_tourneys',
        SHOW_TOURNEYS_ACTION: 'show_tourneys',
        SHOW_PLAYERS_ACTION: 'show_players',
        SHOW_RANKING_ACTION: 'show_ranking',
        SHOW_LIT_PAGE_ACTION: 'show_lit'
    },

    initActions: function() {
        var me = this,
            ids = me.statics();

        me.callParent();

        me.editRating = me.addAction(new Ext.Action({
            itemId: ids.EDIT_RATING_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected rating.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditRatingWindow(record);
            }
        }));

        me.showTourneys = me.addAction(new Ext.Action({
            itemId: ids.SHOW_TOURNEYS_ACTION,
            text: _('Tourneys'),
            tooltip: _('Show tourneys related to the selected rating.'),
            iconCls: 'show-tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idrating = record.get('idrating'),
                    rating = record.get('description'),
                    module = me.module.app.getModule('tourneys-win');

                module.createOrShowWindow('ratings', idrating, rating);
            }
        }));

        me.showPlayers = me.addAction(new Ext.Action({
            itemId: ids.SHOW_PLAYERS_ACTION,
            text: _('Players'),
            tooltip: _('Show rated players in the selected rating.'),
            iconCls: 'rated-players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idrating = record.get('idrating'),
                    rating = record.get('description'),
                    module = me.module.app.getModule('rated-players-win');

                module.createOrShowWindow(idrating, rating);
            }
        }));

        me.recomputeRating = me.addAction(new Ext.Action({
            itemId: ids.RECOMPUTE_RATING_ACTION,
            text: _('Recompute'),
            tooltip: _('Recompute the selected rating from scratch.'),
            iconCls: 'recompute-rating-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idrating = record.get('idrating');

                Ext.create("MP.window.Notification", {
                    position: 'br',
                    html: _('Recomputing…'),
                    title: _('Please wait'),
                    iconCls: 'waiting-icon'
                }).show();

                Ext.Ajax.request({
                    url: '/bio/recomputeRating',
                    params: { idrating: idrating },
                    success: function(response) {
                        var result = Ext.decode(response.responseText);

                        if(result.success) {
                            var store = me.component.store;

                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                html: result.message,
                                title: _('Done'),
                                iconCls: 'done-icon'
                            }).show();

                            store.loadPage(store.currentPage);
                        } else {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                html: result.message,
                                title: _('Error'),
                                iconCls: 'alert-icon'
                            }).show();
                        }
                    },
                    failure: function(response) {
                        Ext.create("MP.window.Notification", {
                            position: 'br',
                            html: response.responseText,
                            title: _('Error'),
                            iconCls: 'alert-icon'
                        }).show();
                    }
                });
            }
        }));

        me.downloadTourneys = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEYS_ACTION,
            text: _('Download'),
            tooltip: _('Download all tourneys related to this rating.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idrating = record.get('idrating'),
                    url = '/bio/dump?idrating=' + idrating;

                window.open(url, "_blank");
            }
        }));

        me.showRatingRanking = me.addAction(new Ext.Action({
            itemId: ids.SHOW_RANKING_ACTION,
            text: _('Ranking'),
            tooltip: _('Print this rating ranking.'),
            iconCls: 'print-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idrating = record.get('idrating'),
                    url = '/pdf/ratingranking/' + idrating;

                window.open(url, "_blank");
            }
        }));

        me.showLitPage = me.addAction(new Ext.Action({
            itemId: ids.SHOW_LIT_PAGE_ACTION,
            text: _('Lit page'),
            tooltip: _('Show the corresponding Lit page.'),
            iconCls: 'lit-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    guid = record.get('guid'),
                    url = '/lit/rating/' + guid;

                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editRating,
                 me.showTourneys,
                 me.showPlayers,
                 me.recomputeRating,
                 me.downloadTourneys,
                 me.showRatingRanking
        );

        me.component.on({
            itemdblclick: function() {
                if(!me.editRating.isDisabled())
                    me.editRating.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditRatingWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this,
            disable = me.component.shouldDisableAction(act),
            statics = me.statics(),
            currentuser = me.module.app.user;

        if(!disable) {
            var record = me.component.getSelectionModel().getSelection()[0];

            switch(act.itemId) {
                case statics.RECOMPUTE_RATING_ACTION:
                case statics.SHOW_TOURNEYS_ACTION:
                    // Disable pointless actions on historical ratings
                    if(record.get('level') == '0')
                        disable = true;
                    break;

                case statics.EDIT_RATING_ACTION:
                    // Disable pointless actions on historical ratings
                    if(record.get('level') == '0')
                        disable = true;
                    else if(!currentuser.is_admin
                            && record.get('idowner') !== null
                            && record.get('idowner') !== currentuser.user_id)
                        disable = true;
                    break;

                default:
                    break;
            }
        }
        return disable;
    },

    showEditRatingWindow: function(record) {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win = desktop.getWindow('edit-rating-win'),
            currentuser = me.module.app.user,
            canchange = currentuser.is_admin,
            maxratinglevel = parseInt(currentuser.maxratinglevel, 10) || 1;

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(800, 440),
            editors = metadata.editors({
                '*': { editor: MP.form.Panel.getDefaultEditorSettingsFunction() },
                tau: { editor: { disabled: !canchange } },
                default_rate: { editor: { disabled: !canchange } },
                default_deviation: { editor: { disabled: !canchange } },
                default_volatility: { editor: { disabled: !canchange } },
                lower_rate: { editor: { disabled: !canchange } },
                higher_rate: { editor: { disabled: !canchange } },
                outcomes: { editor: { disabled: !canchange } }
            });

        // Remove the levels higher than the maximum visible to the user
        editors.level.store = editors.level.store.filter(
            function(v) { return parseInt(v[0], 10) >= maxratinglevel; });

        var form = Ext.create('MP.form.Panel', {
            autoScroll: true,
            fieldDefaults: {
                labelWidth: 150,
                margin: '15 0 0 20'
            },
            items: [{
                xtype: 'container',
                layout: 'hbox',
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    flex: 1,
                    items: [
                        editors.description,
                        editors.level,
                        editors.inherit,
                        editors.tau,
                        editors.default_rate,
                        editors.default_deviation
                    ]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    flex: 1,
                    items: [
                        editors.default_volatility,
                        editors.outcomes,
                        editors.lower_rate,
                        editors.higher_rate,
                        editors.Club,
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
            id: 'edit-rating-win',
            title: _('Edit rating'),
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
                            // ratings insert/edit, do not change unless the manual is actually
                            // translated in the target language
                            help_url: _('/static/manual/en/ratings.html#insert-and-edit'),
                            title: _('Help on ratings insert/edit')
                        });

                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        win.show();
    }
});


Ext.define('SoL.module.Ratings', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Ratings.Actions',
        'SoL.module.Users',
        'SoL.window.Help'
    ],

    id: 'ratings-win',
    iconCls: 'ratings-icon',
    launcherText: function() {
        return _('Ratings');
    },
    launcherTooltip: function() {
        return _('<b>Ratings</b><br />Basic ratings management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/ratings',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['description'],
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
                        Ext.create('SoL.module.Ratings.Actions',
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

    createOrShowWindow: function(caller, id, description) {
        var me = this,
            config = me.config,
            desktop = me.app.getDesktop(),
            win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(850, 421, "S"),
                    filteredOn = '';

                me.config.newRecordData = {
                    tau: 0.5,
                    default_rate: 1500,
                    default_deviation: 350,
                    default_volatility: 0.06
                };

                if(caller == 'users') {
                    filteredOn = ' (' + Ext.String.format(
                        // TRANSLATORS: this is the explanation on the window title when the
                        // filter is a user
                        _('owned by {0}'), description) + ')';
                    config = Ext.apply({
                        filters: [{
                            property: 'idowner',
                            value: id,
                            operator: '='
                        }]
                    }, config);
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
                                // ratings management, do not change unless the manual is
                                // actually translated in the target language
                                help_url: _('/static/manual/en/ratings.html'),
                                title: _('Help on ratings management')
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

                if(record.get('Tourneys') > 0 ||
                   (!currentuser.is_admin
                    && record.get('idowner') !== null
                    && currentuser.user_id !== record.get('idowner'))) {
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


Ext.define('SoL.module.MyRatings', {
    extend: 'SoL.module.Ratings',

    id: 'my-ratings-win',
    iconCls: 'ratings-icon',
    launcherText: null, // don't show an entry in the start menu

    init: function() {
        var me = this,
            user = me.app.user;

        if(!me.config.orig_dataURL) me.config.orig_dataURL = me.config.dataURL;
        me.config.dataURL = Ext.String.urlAppend(me.config.orig_dataURL,
                                                 'filter_by_idowner=' + (user.is_admin
                                                                         ? 'NULL'
                                                                         : user.user_id));
        me.windowTitle = Ext.String.format(_('Ratings managed by {0}'), user.fullname);
        me.callParent();
    }
});
