// -*- coding: utf-8 -*-
// :Project:   SoL -- Clubs window
// :Created:   mer 15 ott 2008 09:09:47 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2016, 2018, 2020, 2021, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/
/*jsl:declare FileReader*/

Ext.define('SoL.module.Clubs.Actions', {
    extend: 'MP.action.StoreAware',

    uses: [
        'Ext.Action',
        'Ext.form.field.File',
        'MP.form.Panel',
        'MP.window.Notification',
        'SoL.window.Help'
    ],

    statics: {
        EDIT_CLUB_ACTION: 'edit_club',
        DOWNLOAD_TOURNEYS_ACTION: 'download_tourneys',
        SHOW_CHAMPIONSHIPS_ACTION: 'show_championships',
        SHOW_MEMBERS_ACTION: 'show_members',
        SHOW_ASSOCIATES_ACTION: 'show_associates',
        SHOW_HOSTED_TOURNEYS_ACTION: 'show_hosted_tourneys',
        SHOW_USERS_ACTION: 'show_users',
        SHOW_LIT_PAGE_ACTION: 'show_lit'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editClub = me.addAction(new Ext.Action({
            itemId: ids.EDIT_CLUB_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected club.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditClubWindow(record);
            }
        }));

        me.showChampionships = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CHAMPIONSHIPS_ACTION,
            text: _('Championships'),
            tooltip: _('Show championships organized by this club.'),
            iconCls: 'championships-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    club = record.get('description'),
                    prizes = record.get('prizes'),
                    couplings = record.get('couplings'),
                    idrating = record.get('idrating'),
                    rating = record.get('Rating'),
                    module = me.module.app.getModule('championships-win');
                module.createOrShowWindow('clubs', idclub, club, prizes, couplings,
                                          idrating, rating);
            }
        }));

        me.showMembers = me.addAction(new Ext.Action({
            itemId: ids.SHOW_MEMBERS_ACTION,
            text: _('Members'),
            tooltip: _('Show players members of this club.'),
            iconCls: 'players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    club = record.get('description'),
                    module = me.module.app.getModule('players-win');
                module.createOrShowWindow('clubs', idclub, club);
            }
        }));

        me.showAssociates = me.addAction(new Ext.Action({
            itemId: ids.SHOW_ASSOCIATES_ACTION,
            text: _('Associates'),
            tooltip: _('Show players associated with this federation.'),
            iconCls: 'players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    club = record.get('description'),
                    module = me.module.app.getModule('players-win');
                module.createOrShowWindow('clubs', idclub, club, true);
            }
        }));

        me.downloadTourneys = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEYS_ACTION,
            text: _('Download'),
            tooltip: _('Download data of all the tourneys in every championship organized by this club.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    url = '/bio/dump?idclub=' + idclub;
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
                    url = '/lit/club/' + guid;
                window.open(url, "_blank");
            }
        }));

        var show_users = new Ext.Action({
            itemId: ids.SHOW_USERS_ACTION,
            text: _('Users'),
            tooltip: _('Show users associated to this club.'),
            iconCls: 'users-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    club = record.get('description'),
                    module = me.module.app.getModule('clubusers-win');
                module.createOrShowWindow(idclub, club);
            }
        });
        show_users.isDisabled = function() {
            var record = me.component.getSelectionModel().getSelection()[0],
                currentuser = me.module.app.user;
            return (!currentuser.is_admin
                    && record.get('idowner') !== null
                    && record.get('idowner') !== currentuser.user_id);
        };
        me.showUsers = me.addAction(show_users);

        me.showHostedTourneys = me.addAction(new Ext.Action({
            itemId: ids.SHOW_HOSTED_TOURNEYS_ACTION,
            text: _('Tourneys'),
            tooltip: _('Show tourneys hosted by this club.'),
            iconCls: 'tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0],
                    idclub = record.get('idclub'),
                    club = record.get('description'),
                    module = me.module.app.getModule('tourneys-win');
                module.createOrShowWindow('clubs', idclub, club);
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editClub,
                 me.showChampionships,
                 me.showHostedTourneys, {
                     text: _('Players'),
                     iconCls: 'players-icon',
                     menu: { items: [me.showMembers,
                                     me.showAssociates] }
                 },
                 me.downloadTourneys);

        me.component.on({
            itemdblclick: function() {
                if(!me.editClub.isDisabled())
                    me.editClub.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditClubWindow(record);
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
                case statics.EDIT_CLUB_ACTION:
                case statics.SHOW_USERS_ACTION:
                    if(!currentuser.is_admin
                       && record.get('idowner') !== null
                       && record.get('idowner') !== currentuser.user_id
                       && (Ext.isEmpty(currentuser.is_nationalliable)
                           || record.get('nationality') !== currentuser.is_nationalliable))
                        disable = true;
                    break;

                case statics.SHOW_ASSOCIATES_ACTION:
                    if(!record.get('isfederation'))
                        disable = true;
                    break;

                default:
                    break;
            }
        }

        return disable;
    },

    readImageAsDataURL: function(event, elt, form) {
        var file = elt.files[0];

        if(file.type.split('/')[0] == 'image') {
            var reader = new FileReader();

            form._emblem = file.name;

            reader.onload = function(e) {
                var img = e.target.result;
                // Multiply by 1.33, because here we have a data URI, in
                // base 64
                if(img.length > (512000 * 1.33)) {
                    Ext.MessageBox.alert(_('Error'),
                                         _('Image too big, max 512k allowed'));
                    form._emblem = null;
                } else {
                    form.down('image').setSrc(img);
                }
            };

            reader.onerror = function() {
                Ext.MessageBox.alert(_('Error'),
                                     _('Sorry, could not read image file')
                                     + ': ' + reader.error);
                form._emblem = null;
            };

            reader.readAsDataURL(file);
        } else {
            Ext.MessageBox.alert(_('Error'),
                                 _('Only image files allowed'));
        }
    },

    deleteImage: function(form) {
        form._emblem = '';
        form.down('image').setSrc('');
    },

    showEditClubWindow: function(record) {
        var me = this,
            desktop = me.module.app.getDesktop(),
            win = desktop.getWindow('edit-club-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata,
            size = desktop.getReasonableWindowSize(1000, 310),
            editors = metadata.editors({
                '*': { editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%') },
                description: { editor: { minLength: 6 } },
                nationality: { editor: { xtype: 'flagscombo' } },
                Rating: {
                    editor: {
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
                    labelWidth: 100,
                    margin: '15 10 0 10'
                },
                items: [{
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'container',
                        layout: 'anchor',
                        minHeight: 245,
                        flex: 1,
                        items: [
                            editors.description,
                            editors.siteurl,
                            editors.email,
                            editors.nationality,
                            editors.Rating
                        ]
                    }, {
                        xtype: 'container',
                        layout: 'anchor',
                        minHeight: 245,
                        flex: 1,
                        items: [
                            editors.isfederation,
                            editors.couplings,
                            editors.prizes,
                            editors.Owner
                        ]
                    }, {
                        xtype: 'container',
                        style: 'text-align: center;',
                        minHeight: 245,
                        width: 170,
                        items: [{
                            xtype: 'image',
                            margin: '10 10 0 10',
                            border: 1,
                            style: {
                                maxWidth: '150px',
                                maxHeight: '150px',
                                borderColor: 'lightgray',
                                borderStyle: 'solid'
                            }
                        }, {
                            xtype: 'filefield',
                            name: 'emblem',
                            fieldLabel: '',
                            labelWidth: 0,
                            buttonOnly: true,
                            buttonText: _('Change emblem…'),
                            style: 'text-align: center;',
                            listeners: {
                                afterrender: function(fld) {
                                    var el = fld.fileInputEl.dom;
                                    el.setAttribute('accept', 'image/*');
                                },
                                el: {
                                    change: {
                                        fn: function(event, elt) {
                                            if(elt.files.length)
                                                me.readImageAsDataURL(event, elt, form);
                                        }
                                    }
                                }
                            }
                        }, {
                            xtype: 'button',
                            text: _('Delete emblem'),
                            handler: function() {
                                me.deleteImage(form);
                            }
                        }]
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
                            if(form._emblem !== undefined) {
                                record.set('emblem', form._emblem);
                                // Force the field as modified: the image name may be the same, but
                                // its content may be different. The backend needs the file name
                                // for logging purposes.
                                record.modified['emblem'] = '';
                                record.set('image', form.down('image').src);
                            }
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
            id: 'edit-club-win',
            title: _('Edit club'),
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
                            // TRANSLATORS: this is the URL of the manual page explaining clubs
                            // insert/edit, do not change unless the manual is actually
                            // translated in the target language
                            help_url: _('/static/manual/en/clubs.html#insert-and-edit'),
                            title: _('Help on club insert/edit')
                        });

                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        if(!Ext.isEmpty(record.get('emblem')) || !Ext.isEmpty(record.get('image'))) {
            var emblem = form.down('image');

            if(!Ext.isEmpty(record.get('image'))) {
                emblem.setSrc(record.get('image'));
            } else {
                emblem.setSrc('/lit/emblem/' + record.get('emblem'));
            }
        }

        win.show();
    }
});


Ext.define('SoL.module.Clubs', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Clubs.Actions',
        'SoL.module.ClubUsers',
        'SoL.module.Users',
        'SoL.form.field.FlagsCombo',
        'SoL.window.Help'
    ],

    id: 'clubs-win',
    iconCls: 'clubs-icon',
    launcherText: function() {
        return _('Clubs');
    },
    launcherTooltip: function() {
        return _('<b>Clubs</b><br />Basic clubs management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/clubs',
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
                    Owner: { filter: false },
                    nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer,
                        filter: { type: 'combo', xtype: 'flagscombo', noOperatorPlugin: true,
                                  editable: true },
                        editor: { xtype: 'flagscombo' }
                    }},
                    fields = metadata.fields(overrides);

                fields.push({
                    name: 'image',
                    type: 'string',
                    sendBackToServer: true
                });

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Clubs.Actions',
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
                var size = desktop.getReasonableWindowSize(770, 447, "NW"),
                    filteredOn = '';

                if(caller == 'championships') {
                    config = Ext.apply({
                        filters: [{
                            property: 'idclub',
                            value: id,
                            operator: '='
                        }]
                    }, config);
                } else if(caller == 'users') {
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
                                // clubs management, do not change unless the manual is
                                // actually translated in the target language
                                help_url: _('/static/manual/en/clubs.html'),
                                title: _('Help on clubs management')
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

                if(record.get('Championships') > 0 ||
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


Ext.define('SoL.module.MyClubs', {
    extend: 'SoL.module.Clubs',

    id: 'my-clubs-win',
    iconCls: 'clubs-icon',
    launcherText: null, // don't show an entry in the start menu

    init: function() {
        var me = this,
            user = me.app.user;

        if(!me.config.orig_dataURL) me.config.orig_dataURL = me.config.dataURL;
        me.config.dataURL = Ext.String.urlAppend(me.config.orig_dataURL,
                                                 'filter_by_idowner=' + (user.is_admin
                                                                         ? 'NULL'
                                                                         : user.user_id));
        me.windowTitle = Ext.String.format(_('Clubs managed by {0}'), user.fullname);
        me.callParent();
    }
});
