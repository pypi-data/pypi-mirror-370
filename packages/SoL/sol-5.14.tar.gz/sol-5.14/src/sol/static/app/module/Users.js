// -*- coding: utf-8 -*-
// :Project:   SoL -- Users window
// :Created:   mar 10 lug 2018 17:47:33 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2018-2021, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/

Ext.define('SoL.module.Users.AssignOwnership', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification'
    ],

    statics: {
        ASSIGN_OWNERSHIP_ACTION: 'assign_ownership'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.assignOwnershipAction = me.addAction(new Ext.Action({
            itemId: ids.ASSIGN_OWNERSHIP_ACTION,
            text: _('Assign'),
            tooltip: _('Assign ownership of selected records.'),
            iconCls: 'owner-icon',
            disabled: true,
            needsSelectedRow: true,
            handler: function() {
                me.assignOwnership();
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        if(me.module.app.user.is_admin || me.module.app.user.is_ownersadmin) {
            var tbar = me.component.child('#ttoolbar');

            tbar.add(tbar.items.length-3, me.assignOwnershipAction);
        }
    },

    assignOwnership: function() {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win,
            winWidth = 390,
            winHeight = 110,
            model = Ext.define('MP.data.ImplicitModel-'+Ext.id(), {
                extend: 'Ext.data.Model',
                fields: ['iduser', 'Fullname'],
                idProperty: 'iduser'
            }),
            lstore = Ext.create('Ext.data.Store', {
                model: model,
                pageSize: 999,
                autoLoad: false,
                remoteFilter: true,
                proxy: {
                    type: 'ajax',
                    url: '/data/owners',
                    filterParam: 'filters',
                    reader: {
                        type: 'json',
                        root: 'root',
                        idProperty: 'iduser'
                    }
                }
            });

        lstore.implicitModel = true;

        var form = new Ext.form.Panel({
            frame: true,
            bodyPadding: '10 10 0',
            defaults: {
                labelWidth: 90,
                anchor: '100%'
            },
            items: [{
                xtype: 'combo',
                store: lstore,
                valueField: 'iduser',
                displayField: 'Fullname',
                buttonText: _('Browse'),
                emptyText: _('Select responsible'),
                allowBlank: false,
                triggerAction: 'all',
                typeAhead: true,
                forceSelection: true,
                fieldLabel: _('Owner')
            }],
            buttons: [{
                text: _('Cancel'),
                handler: function() {
                    win.destroy();
                }
            }, {
                text: _('Confirm'),
                formBind: true,
                handler: function() {
                    var frm = form.getForm();
                    if(frm.isValid()) {
                        var combo = frm.getFields().getAt(0),
                            sels = me.component.getSelectionModel().getSelection();
                        Ext.each(sels, function(record) {
                            record.set('idowner', combo.value);
                            record.set('Owner', combo.getRawValue());
                        });
                        win.destroy();
                    }
                }
            }]
        });

        win = desktop.createWindow({
            id: me.id,
            title: _('Assign ownership'),
            iconCls: 'upload-icon',
            width: winWidth,
            height: winHeight,
            layout: 'fit',
            minimizable: false,
            maximizable: false,
            modal: true,
            items: [form]
        });

        win.show();
    }
});


Ext.define('SoL.module.Users.Actions', {
    extend: 'MP.action.StoreAware',

    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification',
        'SoL.module.Players',
        'SoL.window.Help'
    ],

    statics: {
        EDIT_USER_ACTION: 'edit_user',
        SHOW_OWNED_CLUBS: 'show_owned_clubs',
        SHOW_OWNED_CHAMPIONSHIPS: 'show_owned_championships',
        SHOW_OWNED_PLAYERS: 'show_owned_players',
        SHOW_OWNED_RATINGS: 'show_owned_ratings',
        SHOW_OWNED_TOURNEYS: 'show_owned_tourneys'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editUser = me.addAction(new Ext.Action({
            itemId: ids.EDIT_USER_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected user.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditUserWindow(record);
            }
        }));

        me.showOwnedClubs = me.addAction(new Ext.Action({
            itemId: ids.SHOW_OWNED_CLUBS,
            text: _('Clubs'),
            tooltip: _('Show clubs owned by the selected user.'),
            iconCls: 'clubs-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    iduser = record.get('iduser'),
                    user = SoL.module.Players.full_name(record),
                    module = me.module.app.getModule('clubs-win');
                module.createOrShowWindow('users', iduser, user);
            }
        }));

        me.showOwnedChampionships = me.addAction(new Ext.Action({
            itemId: ids.SHOW_OWNED_CHAMPIONSHIPS,
            text: _('Championships'),
            tooltip: _('Show championships owned by the selected user.'),
            iconCls: 'championships-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    iduser = record.get('iduser'),
                    user = SoL.module.Players.full_name(record),
                    module = me.module.app.getModule('championships-win');
                module.createOrShowWindow('users', iduser, user);
            }
        }));

        me.showOwnedPlayers = me.addAction(new Ext.Action({
            itemId: ids.SHOW_OWNED_PLAYERS,
            text: _('Players'),
            tooltip: _('Show players owned by the selected user.'),
            iconCls: 'players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    iduser = record.get('iduser'),
                    user = SoL.module.Players.full_name(record),
                    module = me.module.app.getModule('players-win');
                module.createOrShowWindow('users', iduser, user);
            }
        }));

        me.showOwnedRatings = me.addAction(new Ext.Action({
            itemId: ids.SHOW_OWNED_RATINGS,
            text: _('Ratings'),
            tooltip: _('Show ratings owned by the selected user.'),
            iconCls: 'ratings-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    iduser = record.get('iduser'),
                    user = SoL.module.Players.full_name(record),
                    module = me.module.app.getModule('ratings-win');
                module.createOrShowWindow('users', iduser, user);
            }
        }));

        me.showOwnedTourneys = me.addAction(new Ext.Action({
            itemId: ids.SHOW_OWNED_TOURNEYS,
            text: _('Tourneys'),
            tooltip: _('Show tourneys owned by the selected user.'),
            iconCls: 'tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    iduser = record.get('iduser'),
                    user = SoL.module.Players.full_name(record),
                    module = me.module.app.getModule('tourneys-win');
                module.createOrShowWindow('users', iduser, user);
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editUser,
                 me.showOwnedClubs,
                 me.showOwnedChampionships,
                 me.showOwnedPlayers,
                 me.showOwnedRatings,
                 me.showOwnedTourneys);

        me.component.on({
            itemdblclick: function() {
                if(!me.editUser.isDisabled())
                    me.editUser.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditUserWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this,
            disable = me.component.shouldDisableAction(act),
            statics = me.statics(),
            currentuser = me.module.app.user;

        if(!disable) {
            switch(act.itemId) {
                case statics.EDIT_USER_ACTION:
                    if(!currentuser.is_admin)
                        disable = true;
                    break;

                default:
                    break;
            }
        }

        return disable;
    },

    showEditUserWindow: function(record) {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win = desktop.getWindow('edit-user-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(600, 560),
            editors = metadata.editors({
                '*': {
                    editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
                },
                Language: { editor: { queryMode: 'local' }},
                nationalliable: { editor: { xtype: 'flagscombo' } },
                password: { editor: { minLength: 6 }}
            }),
            form = Ext.create('MP.form.Panel', {
                autoScroll: true,
                fieldDefaults: {
                    labelWidth: 100,
                    margin: '15 10 0 10'
                },
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    minHeight: 245,
                    flex: 1,
                    items: [
                        editors.email,
                        editors.password,
                        editors.firstname,
                        editors.lastname,
                        editors.Language,
                        editors.nationalliable,
                        editors.ownersadmin,
                        editors.playersmanager,
                        editors.maxratinglevel,
                        editors.state
                    ]
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
            id: 'edit-user-win',
            title: _('Edit user'),
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
                            // TRANSLATORS: this is the URL of the manual page explaining users
                            // insert/edit, do not change unless the manual is actually
                            // translated in the target language
                            help_url: _('/static/manual/en/users.html#insert-and-edit'),
                            title: _('Help on user insert/edit')
                        });

                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        win.show();
    }
});


Ext.define('SoL.module.Users', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Users.Actions',
        'SoL.window.Help'
    ],

    id: 'users-win',
    iconCls: 'users-icon',
    launcherText: function() {
        return _('Users');
    },
    launcherTooltip: function() {
        return _('<b>Users</b><br />Basic users management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/users',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['lastname', 'firstname'],
        stripeRows: true,
        selModel: {
            mode: 'MULTI'
        },
        newRecordData: {
            state: 'C'
        }
    },

    getConfig: function(callback) {
        var me = this,
            cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    nationalliable: {
                        renderer: SoL.form.field.FlagsCombo.renderer,
                        filter: { type: 'combo', xtype: 'flagscombo', noOperatorPlugin: true,
                                  editable: true },
                        editor: { xtype: 'flagscombo' }
                    }
                };
                var fields = metadata.fields(overrides);

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Users.Actions',
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

    createOrShowWindow: function(iduser) {
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
                var size = desktop.getReasonableWindowSize(780, 421, "C");

                win = desktop.createWindow({
                    id: me.id,
                    title: me.windowTitle || me.getLauncherText(),
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
                                // users management, do not change unless the manual is
                                // actually translated in the target language
                                help_url: _('/static/manual/en/users.html'),
                                title: _('Help on users management')
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
            var disable = !currentuser.is_admin;
            return disable;
        } else {
            return true;
        }
    }
});
