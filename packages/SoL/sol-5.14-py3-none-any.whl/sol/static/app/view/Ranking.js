// -*- coding: utf-8 -*-
// :Project:   SoL -- Ranking panel of the tourney management
// :Created:   gio 20 nov 2008 18:24:44 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2015, 2018, 2020, 2024, 2025 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Ranking.Actions', {
    extend: 'MP.action.Plugin',
    uses: ['Ext.Action'],

    statics: {
        BY_NATIONALITY_ACTION: 'by_nationality',
        PRINT_RANKING_ACTION: 'print_ranking',
        PRINT_NATIONAL_RANKING_ACTION: 'print_national_ranking',
        PRINT_WOMEN_RANKING_ACTION: 'print_women_ranking',
        PRINT_UNDER_RANKING_ACTION: 'print_under_ranking',
        PRINT_OVER_RANKING_ACTION: 'print_over_ranking',
        PRINT_FINAL_BADGES_ACTION: 'print_final_badges',
        PRINT_FINAL_CARDS_ACTION: 'print_final_cards',
        PRIZE_GIVING_ACTION: 'prize_giving'
    },

    initActions: function() {
        var me = this,
            ids = me.statics(),
            tourney = me.module.tourney,
            tprized = tourney.prized;

        me.callParent();

        me.byNationalityAction = me.addAction(new Ext.Action({
            itemId: ids.BY_NATIONALITY_ACTION,
            text: _('By nationality'),
            tooltip: _("Toggle between normal ranking and grouped by competitor's nationality."),
            iconCls: 'toggle-by-nation-icon',
            handler: function() {
                me.component.toggleView(me.byNationalityAction);
            }
        }));

        me.printRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_RANKING_ACTION,
            text: _('Ranking'),
            tooltip: _('Print current ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn,
                    url = '/pdf/ranking/' + tourney.idtourney;
                if(turn) url += '?turn=' + turn;
                window.location.assign(url);
            }
        }));

        me.printNationalRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_NATIONAL_RANKING_ACTION,
            text: _('National ranking'),
            tooltip: _('Print current national ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn,
                    url = '/pdf/nationalranking/' + tourney.idtourney;
                if(turn) url += '?turn=' + turn;
                window.location.assign(url);
            }
        }));

        me.printWomenRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_WOMEN_RANKING_ACTION,
            text: _('Women ranking'),
            tooltip: _('Print women ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn,
                    url = '/pdf/womenranking/' + tourney.idtourney;
                if(turn) url += '?turn=' + turn;
                window.location.assign(url);
            }
        }));

        me.printUnderRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_UNDER_RANKING_ACTION,
            text: _('Junior ranking'),
            tooltip: _('Print junior ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn;
                me.component.printUnderOverRanking(turn, 'under');
            }
        }));

        me.printOverRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_OVER_RANKING_ACTION,
            text: _('Senior ranking'),
            tooltip: _('Print senior ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn;
                me.component.printUnderOverRanking(turn, 'over');
            }
        }));

        me.printFinalBadgesAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_FINAL_BADGES_ACTION,
            text: _('Badges'),
            tooltip: _('Print final badges with ranking and matches.'),
            iconCls: 'print-icon',
            hidden: !tprized,
            handler: function() {
                var url = '/pdf/badges/' + tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.printFinalCardsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_FINAL_CARDS_ACTION,
            text: _('Finals'),
            tooltip: _('Print 1st/2nd and 3rd/4th place finals scorecards.'),
            iconCls: 'print-icon',
            hidden: !tprized && tourney.finals === null,
            handler: function() {
                var url = '/pdf/scorecards/' + tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.prizegivingAction = this.addAction(new Ext.Action({
            itemId: ids.PRIZE_GIVING_ACTION,
            text: tprized ? _('Reset prizes') : _('Assign prizes'),
            hidden: tourney.readOnly,
            tooltip: tprized
                ? _('Reset assigned final prizes.')
                : _('Assign final prizes.'),
            iconCls: 'prize-giving-icon',
            handler: function() {
                Ext.Ajax.request({
                    url: tprized
                        ? '/tourney/resetPrizes'
                        : '/tourney/assignPrizes',
                    params: { idtourney: tourney.idtourney },
                    success: function (r) {
                        var res = Ext.decode(r.responseText);

                        if(!res) {
                            Ext.MessageBox.alert(
                                _("Communication error"),
                                _('Cannot decode JSON object'));
                        } else {
                            if(res.success) {
                                tourney.currentturn = res.currentturn;
                                tourney.rankedturn = res.rankedturn;
                                tourney.prized = tprized = res.prized;

                                me.component.store.reload();

                                if(tprized) {
                                    me.component.setWidth(500);
                                    me.prizegivingAction.setText(_('Reset prizes'));
                                    me.prizegivingAction.callEach(
                                        'setTooltip',
                                        [_('Reset assigned final prizes.')]);
                                } else {
                                    me.component.setWidth(me.component.initialConfig.width);
                                    me.prizegivingAction.setText(_('Assign prizes'));
                                    me.prizegivingAction.callEach(
                                        'setTooltip',
                                        [_('Assign final prizes.')]);
                                }
                            } else {
                                Ext.MessageBox.alert(_('Error'), res.message);
                            }
                        }
                    }
                });
        }}));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(0,
                 //me.byNationalityAction,
                 me.printFinalCardsAction,
                 me.printFinalBadgesAction,
                 me.printRankingAction,
                 {
                     text: _('Other…'),
                     iconCls: 'print-icon',
                     menu: {
                         items: [
                             me.printNationalRankingAction,
                             me.printWomenRankingAction,
                             me.printUnderRankingAction,
                             me.printOverRankingAction
                         ]
                     }
                 });

        if(!me.module.tourney.finals)
            me.component.addDocked({
                xtype: 'toolbar',
                dock: 'bottom',
                items: ['->', me.prizegivingAction]
            });
    }
});

Ext.define('SoL.view.Ranking', {
    extend: 'MP.grid.Panel',
    uses: ['SoL.view.Matches'],

    // requires: [
    //     'Ext.grid.feature.GroupingSummary'
    // ],

    alias: 'widget.ranking-grid',

    clicksToEdit: 1,

    statics: {
        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this,
                ordinal = SoL.view.Matches.ordinal,
                cfg = config.Ranking = {
                    dataURL: '/tourney/ranking',
                    header: true,
                    layout: 'fit',
                    noAddAndDelete: true,
                    noBottomToolbar: true,
                    noFilterbar: true,
                    pageSize: 999,
                    plugins: [
                        Ext.create('SoL.view.Ranking.Actions', {
                            module: me
                        })
                    ],
                    remoteSort: false,
                    saveChangesURL: '/bio/saveChanges',
                    title: (config.tourney.rankedturn === 0
                            ? _('Ranking')
                            : (config.tourney.prized
                               ? _('Final ranking')
                               : Ext.String.format(
                                   _('Ranking after {0} round'),
                                   ordinal(config.tourney.rankedturn)))),
                    xtype: 'ranking-grid'
                };

            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    prize: { hidden: !config.tourney.prized,
                             editor: { hideTrigger: true }
                           },
                    bucholz: { hidden: (config.tourney.system === 'knockout'
                                        || config.tourney.system === 'roundrobin'
                                        || config.tourney.couplings === 'all') },
                    netscore: { hidden: config.tourney.system === 'knockout' }
                };

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot
                });
                callback(cfg);
            });
        }
    },

    initEvents: function() {
        var me = this,
            module = me.module,
            tourney = module.tourney,
            ordinal = SoL.view.Matches.ordinal,
            normal_sorters = [
                { property: 'prize', direction: 'DESC' },
                { property: 'points', direction: 'DESC' },
                { property: 'bucholz', direction: 'DESC' },
                { property: 'netscore', direction: 'DESC' },
                { property: 'totscore', direction: 'DESC' },
                { property: 'position', direction: 'ASC' },
                { property: 'rate', direction: 'DESC' },
                { property: 'description', direction: 'ASC' }
            ],
            newturn_sorters = [
                { property: 'prize', direction: 'DESC' },
                { property: 'points', direction: 'DESC' },
                { property: 'bucholz', direction: 'DESC' },
                { property: 'position', direction: 'ASC' },
                { property: 'rate', direction: 'DESC' },
                { property: 'netscore', direction: 'DESC' },
                { property: 'totscore', direction: 'DESC' },
                { property: 'description', direction: 'ASC' }
            ],
            ko_and_rr_sorters = [
                { property: 'prize', direction: 'DESC' },
                { property: 'points', direction: 'DESC' },
                { property: 'position', direction: 'ASC' },
                { property: 'rate', direction: 'DESC' },
                { property: 'description', direction: 'ASC' }
            ],
            ko_and_rr_newturn_sorters = [
                { property: 'position', direction: 'ASC' },
                { property: 'rate', direction: 'DESC' },
                { property: 'description', direction: 'ASC' }
            ];

        me.callParent();

        me.on('itemdblclick', module.togglePlayerDetail, module);
        me.on('beforeedit', function() {
            return !tourney.readOnly && tourney.prized;
        });
        me.store.on('load', function(store) {
            var pcol = me.getColumnByName('prize'),
                turn = me.store.proxy.extraParams.turn;

            if(tourney.prized && !turn) {
                pcol.show();
            } else {
                pcol.hide();
            }

            if(turn) {
                if(turn <= tourney.rankedturn) {
                    // Reflect the actual ordering used to compute the next turn,
                    // see Tourney._makeNextTurn()
                    me.setTitle(Ext.String.format(_('Ranking used to compute {0} round'),
                                                  ordinal(turn+1)));
                    if(tourney.system === 'swiss')
                        newturn_sorters = store.sort(newturn_sorters);
                    else {
                        ko_and_rr_newturn_sorters = store.sort(ko_and_rr_newturn_sorters);
                        me.getColumnByName('rank').hide();
                        me.getColumnByName('points').hide();
                        me.getColumnByName('position').show();
                        if(tourney.Rating)
                            me.getColumnByName('rate').show();
                    }
                } else {
                    me.setTitle(Ext.String.format(_('Ranking after {0} round'),
                                                  ordinal(turn)));
                    if(tourney.system === 'swiss')
                        normal_sorters = store.sort(normal_sorters);
                    else {
                        ko_and_rr_sorters = store.sort(ko_and_rr_sorters);
                        me.getColumnByName('rank').hide();
                        me.getColumnByName('points').hide();
                        me.getColumnByName('position').show();
                        if(tourney.Rating)
                            me.getColumnByName('rate').show();
                    }
                }
            } else {
                me.setTitle((tourney.rankedturn === 0
                             ? _('Ranking')
                             : (tourney.prized
                                ? _('Final ranking')
                                : Ext.String.format(
                                    _('Ranking after {0} round'),
                                    ordinal(tourney.rankedturn)))));
                if(tourney.system == 'swiss')
                    normal_sorters = store.sort(normal_sorters);
                else {
                    ko_and_rr_sorters = store.sort(ko_and_rr_sorters);
                    me.getColumnByName('rank').show();
                    me.getColumnByName('points').show();
                    me.getColumnByName('position').hide();
                    if(tourney.Rating)
                        me.getColumnByName('rate').hide();
                }
            }
        });

        Ext.tip.QuickTipManager.register({
            target: me.getView().getId(),
            text: _('Double click on a player to view his matches.'),
            width: 200,
            dismissDelay: 3000
        });
    },

    toggleView: function(action) {
        var me = this,
            view = me.view,
            feature = view.getFeature('bynationgrouping');

        if(feature.disabled) {
            feature.enable();
            action.setText(_('By nationality'));
        } else {
            feature.disable();
            action.setText(_('Normal'));
        }
    },

    printUnderOverRanking: function(turn, under_or_over) {
        var me = this,
            tourney = me.module.tourney,
            url = '/pdf/' + under_or_over + 'ranking/' + tourney.idtourney,
            win, form,
            winWidth = 215,
            winHeight = 110;

        var handler = function() {
            var frm = form.getForm();
            if(frm.isValid()) {
                var age = frm.getFields().items[0].getValue();
                url += '?age=' + age;
                if(turn)
                    url += '&turn=' + turn;
                win.destroy();
                window.location.assign(url);
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
                labelWidth: 50,
                anchor: '100%'
            },
            items: [{
                xtype: 'numberfield',
                itemId: 'age',
                increment: 3,
                allowBlank: false,
                minValue: 5,
                maxValue: 99,
                value: under_or_over == 'under' ? 18 : 60,
                enableKeyEvents: true,
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
            title: under_or_over == 'under' ? _('Maximum age') : _('Minimum age'),
            width: winWidth,
            height: winHeight,
            layout: 'fit',
            minimizable: false,
            maximizable: false,
            items: [form],
            defaultFocus: 'age'
        });

        win.show();
    }
});
