// -*- coding: utf-8 -*-
// :Project:   SoL -- Rated players window
// :Created:   dom 15 dic 2013 18:08:06 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2013, 2014, 2016, 2018, 2021, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare window*/

Ext.define('SoL.module.RatedPlayers.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action'
    ],

    statics: {
        SHOW_RANKING_ACTION: 'show_ranking'
    },

    initActions: function() {
        var me = this,
            ids = me.statics();

        me.callParent();

        me.showRanking = me.addAction(new Ext.Action({
            itemId: ids.SHOW_RANKING_ACTION,
            text: _('Print'),
            tooltip: _('Print this rating ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var idrating = me.module.idrating,
                    url = '/pdf/ratingranking/' + idrating;
                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');
        tbar.add(2, ' ', me.showRanking);
    }
});

Ext.define('SoL.module.RatedPlayers', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.RatedPlayers.Actions',
        'SoL.window.Help'
    ],

    id: 'rated-players-win',
    iconCls: 'rated-players-icon',
    launcherText: null,
    launcherTooltip: function() {
        return _('Players rates.');
    },

    config: {
        xtype: 'basic-grid',
        pageSize: 14,
        readOnly: true,
        dataURL: '/data/ratedPlayers',
        sorters: [{ property: 'rate', direction: 'DESC' }],
        stripeRows: true
    },

    getConfig: function(callback) {
        var me = this,
            cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer
                    }
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
                        Ext.create('SoL.module.RatedPlayers.Actions', {
                            module: me
                        })
                    ]
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(idrating, rating) {
        var me = this,
            config = me.config,
            desktop = me.app.getDesktop(),
            win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.idrating = idrating;

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(690, 421, "SE");

                config = Ext.apply({
                    stickyFilters: [{
                        property: 'idrating',
                        value: idrating,
                        operator: '='
                    }]
                }, config);

                win = desktop.createWindow({
                    id: me.id,
                    title: Ext.String.format(
                        // TRANSLATORS: {0} is the description of the rating
                        _('Players in rating “{0}”'), rating),
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
                                    // explaining players rates management, do not change
                                    // unless the manual is actually translated in the target
                                    // language
                                    help_url: _('/static/manual/en/playersrates.html'),
                                    title: _('Help on rated players window')
                                });

                            wh.show();
                        }
                    }]
                });

                // Fetch the first page of records, and when done show
                // the window
                win.child('basic-grid').store.load({
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
