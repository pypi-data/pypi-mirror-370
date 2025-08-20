// -*- coding: utf-8 -*-
// :Project:   SoL -- Championships window
// :Created:   dom 19 ott 2008 00:26:20 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2018, 2020, 2021 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/

Ext.define('SoL.module.Championships.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification',
        'SoL.window.Help'
    ],

    statics: {
        EDIT_CHAMPIONSHIP_ACTION: 'edit_championship',
        DOWNLOAD_TOURNEYS_ACTION: 'download_tourneys',
        SHOW_TOURNEYS_ACTION: 'show_tourneys',
        SHOW_CLUB_ACTION: 'show_club',
        SHOW_RANKING_ACTION: 'show_ranking',
        SHOW_LIT_PAGE_ACTION: 'show_lit'
    },

    initActions: function() {
        var me = this,
            ids = me.statics();

        me.callParent();

        me.editChampionship = me.addAction(new Ext.Action({
            itemId: ids.EDIT_CHAMPIONSHIP_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected championship.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditChampionshipWindow(record);
            }
        }));

        me.showTourneys = me.addAction(new Ext.Action({
            itemId: ids.SHOW_TOURNEYS_ACTION,
            text: _('Tourneys'),
            tooltip: _('Show tourneys of this championship.'),
            iconCls: 'show-tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idchampionship = record.get('idchampionship'),
                    championship = record.get('description'),
                    couplings = record.get('couplings'),
                    idclub = record.get('idclub'),
                    club = record.get('Club'),
                    idrating = record.get('idrating'),
                    rating = record.get('Rating'),
                    closed = record.get('closed'),
                    module = me.module.app.getModule('tourneys-win');

                module.createOrShowWindow('championships', idchampionship, championship,
                                          idclub, club, couplings, closed, idrating, rating);
            }
        }));

        me.showClub = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CLUB_ACTION,
            text: _('Club'),
            tooltip: _('Show the club this championship belongs.'),
            iconCls: 'clubs-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    module = me.module.app.getModule('clubs-win');

                module.createOrShowWindow('championships', idclub);
            }
        }));

        me.downloadTourneys = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEYS_ACTION,
            text: _('Download'),
            tooltip: _('Download this whole championship of tourneys data.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idchampionship = record.get('idchampionship'),
                    url = '/bio/dump?idchampionship=' + idchampionship;

                window.open(url, "_blank");
            }
        }));

        me.showChampionshipRanking = me.addAction(new Ext.Action({
            itemId: ids.SHOW_RANKING_ACTION,
            text: _('Ranking'),
            tooltip: _('Print this championship ranking.'),
            iconCls: 'print-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idchampionship = record.get('idchampionship'),
                    url = '/pdf/championshipranking/' + idchampionship;

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
                    url = '/lit/championship/' + guid;

                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editChampionship,
                 me.showTourneys,
                 me.showClub,
                 me.downloadTourneys,
                 me.showChampionshipRanking);

        me.component.on({
            itemdblclick: function() {
                if(!me.editChampionship.isDisabled())
                    me.editChampionship.execute();
            }
        });

        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditChampionshipWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this,
            disable = me.component.shouldDisableAction(act),
            statics = me.statics(),
            currentuser = me.module.app.user;

        if(!disable && !currentuser.is_admin) {
            if(act.itemId == statics.EDIT_CHAMPIONSHIP_ACTION) {
                var record = me.component.getSelectionModel().getSelection()[0];

                if(record.get('idowner') !== null
                   && record.get('idowner') !== currentuser.user_id)
                    disable = true;
            }
        }

        return disable;
    },

    showEditChampionshipWindow: function(record) {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win = desktop.getWindow('edit-championship-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(800, 430),
            editors = metadata.editors({
                '*': { editor: MP.form.Panel.getDefaultEditorSettingsFunction() },
                description: { editor: { minLength: 6 } },
                Previous: {
                    editor: {
                        listeners: {
                            beforequery: function(queryPlan) {
                                var store = queryPlan.combo.store,
                                    clubf = form.getForm().findField(editors.Club.name),
                                    idclub;

                                if(!Ext.isEmpty(clubf.lastSelection)) {
                                    var iname = clubf.store.proxy.reader.idProperty,
                                        srec = clubf.lastSelection[0];

                                    idclub = srec.get(iname);
                                } else {
                                    idclub = record.get('idclub');
                                }
                                store.addFilter([{
                                    id: 'currentclub',
                                    property: 'idclub',
                                    value: idclub,
                                    operator: '='
                                }, {
                                    id: 'currentchampionship',
                                    property: 'idchampionship',
                                    value: record.get('idchampionship'),
                                    operator: '<>'
                                }], false);
                                delete queryPlan.combo.lastQuery;
                            }
                        }
                    }
                },
                Rating: {
                    editor: {
                        // Force re-execution of the query, the club id may have changed
                        queryCaching: false,
                        listeners: {
                            beforequery: function(queryPlan) {
                                var store = queryPlan.combo.store;
                                var idclub = record.get('idclub');

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
                    labelWidth: 150,
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
                            editors.description,
                            editors.Club,
                            editors.playersperteam,
                            editors.skipworstprizes,
                            editors.trainingboards
                        ]
                    }, {
                        xtype: 'container',
                        layout: 'anchor',
                        flex: 1,
                        items: [
                            editors.Rating,
                            editors.couplings,
                            editors.prizes,
                            editors.closed,
                            editors.Previous,
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
            id: 'edit-championship-win',
            title: _('Edit championship'),
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
                            // championship insert/edit, do not change unless the manual is
                            // actually translated in the target language
                            help_url: _('/static/manual/en/championships.html#insert-and-edit'),
                            title: _('Help on championship insert/edit')
                        });
                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        win.show();
    }
});


Ext.define('SoL.module.Championships', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Championships.Actions',
        'SoL.module.Users',
        'SoL.window.Help'
    ],

    id: 'championships-win',
    iconCls: 'championships-icon',
    launcherText: function() {
        return _('Championships');
    },
    launcherTooltip: function() {
        return _('<b>Championships</b><br />Basic championships management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/championships',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['closed', 'description'],
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
                        Ext.create('SoL.module.Championships.Actions',
                                   { module: me }),
                        Ext.create('SoL.module.Users.AssignOwnership',
                                   { module: me }),
                    ]
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(caller, id, description, prizes, couplings, idrating, rating) {
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
                var size = desktop.getReasonableWindowSize(740, 421, "SW"),
                    filteredOn = '';

                config = Ext.apply({
                    newRecordData: {
                        prizes: prizes || 'fixed',
                        couplings: couplings || 'serial',
                        skipworstprizes: 0,
                        playersperteam: 1,
                        closed: false
                    }
                }, config);

                if(caller == 'clubs') {
                    filteredOn = ' (' + Ext.String.format(
                        // TRANSLATORS: this is the explanation on the window title when the
                        // filter is a club
                        _('organized by {0}'), description) + ')';
                    config.newRecordData.idclub = id;
                    config.newRecordData.Club = description;
                    config.newRecordData.idrating = idrating;
                    config.newRecordData.Rating = rating;
                    config.stickyFilters = [{
                        property: 'idclub',
                        value: id,
                        operator: '='
                    }];
                } else if(caller == 'tourneys') {
                    config.filters = [{
                        property: 'idchampionship',
                        value: id,
                        operator: '='
                    }];
                } else if(caller == 'users') {
                    filteredOn = ' (' + Ext.String.format(
                        // TRANSLATORS: this is the explanation on the window title when the
                        // filter is a user
                        _('owned by {0}'), description) + ')';
                    config.filters = [{
                        property: 'idowner',
                        value: id,
                        operator: '='
                    }];
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
                            var whsize = desktop.getReasonableWindowSize(800, 640),
                                wh = Ext.create('SoL.window.Help', {
                                    width: whsize.width,
                                    height: whsize.height,
                                    // TRANSLATORS: this is the URL of the manual page
                                    // explaining championship management, do not change unless
                                    // the manual is actually translated in the target language
                                    help_url: _('/static/manual/en/championships.html'),
                                    title: _('Help on championships management')
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


Ext.define('SoL.module.MyChampionships', {
    extend: 'SoL.module.Championships',

    id: 'my-championships-win',
    iconCls: 'championships-icon',
    launcherText: null, // don't show an entry in the start menu

    init: function() {
        var me = this,
            user = me.app.user;

        if(!me.config.orig_dataURL) me.config.orig_dataURL = me.config.dataURL;
        me.config.dataURL = Ext.String.urlAppend(me.config.orig_dataURL,
                                                 'filter_by_idowner=' + (user.is_admin
                                                                         ? 'NULL'
                                                                         : user.user_id));
        me.windowTitle = Ext.String.format(_('Championships managed by {0}'), user.fullname);
        me.callParent();
    }
});
