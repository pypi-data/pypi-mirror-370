// -*- coding: utf-8 -*-
// :Project:   SoL -- Club's users window
// :Created:   sab 18 gen 2020, 11:44:25
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2020, 2021 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/

Ext.define('SoL.module.ClubUsers', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'Ext.grid.column.CheckColumn',
        'SoL.window.Help'
    ],

    id: 'clubusers-win',
    iconCls: 'users-icon',
    launcherText: null,
    launcherTooltip: function() {
        return _('<b>Club\'s users</b><br />Basic club-users association management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        noAddAndDelete: true,
        clicksToEdit: 1,
        dataURL: '/data/clubUsers',
        sorters: [{ property: 'associated', direction: 'DESC' },
                  { property: 'lastname', direction: 'ASC' },
                  { property: 'firstname', direction: 'ASC' }],
        stripeRows: true
    },

    getConfig: function(callback) {
        var me = this,
            cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {},
                    fields = metadata.fields(overrides);

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, true),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(idclub, club) {
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

                config = Ext.apply({
                    extraParams: { idclub: idclub },
                    saveChangesURL: config.dataURL + '?idclub=' + idclub
                }, config);

                win = desktop.createWindow({
                    id: me.id,
                    title: Ext.String.format(_('Users associated with club {0}'), club),
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
                                // club/user management, do not change unless the manual is
                                // actually translated in the target language
                                help_url: _('/static/manual/en/clubusers.html'),
                                title: _('Help on club\'s users management')
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
            }
        );
    }
});
