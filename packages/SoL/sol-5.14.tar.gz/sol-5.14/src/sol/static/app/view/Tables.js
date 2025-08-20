// -*- coding: utf-8 -*-
// :Project:   SoL -- Carromboards panel of the tourney management
// :Created:   gio 20 nov 2008 18:26:21 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013, 2014, 2016, 2023, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Tables.Actions', {
    extend: 'MP.action.SaveAndReset',
    uses: ['Ext.Action'],

    attachActions: function() {
        var me = this;

        me.callParent();

        var panel = me.component.up('panel'),
            tbar = panel.child('#ttoolbar');

        tbar.add(0, '->',
                 me.saveAction,
                 me.restoreAction);

        if(!panel.module.tourney.prized) {
            var store = me.component.store;

            store.on('update', function(s, r, action) {
                //jsl:unused s
                //jsl:unused r
                if(action=='edit') {
                    me.saveAction.setDisabled(false);
                    me.restoreAction.setDisabled(false);
                }
            });
            store.on('load', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
            });
            store.on('reject', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
            });
        }
    }
});


Ext.define('SoL.view.Tables', {
    extend: 'Ext.view.View',
    requires: [
        'SoL.view.Tables.Actions'
    ],

    alias: 'widget.carromboards-dataview',

    autoHeight: true,
    autoScroll: true,
    ddGroup: 'competitor',
    deferEmptyText: false,
    emptyText: _('Only new round pairings can be manually adjusted.'),
    itemSelector: 'div.carromboard',
    singleSelect: true,

    tpl: [
        '<tpl for=".">',
        '  <div class="carromboard{dirtyCls}" id="match_{idcompetitor1}" mid="{idmatch}">',
        '    <span class="competitor" id="c_1_{idcompetitor1}">',
        '      {competitor1FullName}',
        '    </span>',
        '    <div class="carromboard-number">',
        '      <label for="mboard_{idmatch}">{boardNo}</label>',
        '      <input type="number" name="mboard_{idmatch}" min="1" value="{board}">',
        '    </div>',
        '    <span class="competitor" id="c_2_{idcompetitor2}">',
        '      {competitor2FullName}',
        '    </span>',
        '  </div>',
        '</tpl>',
        '<div class="x-clear"></div>'
    ],

    statics: {
        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this,
                dataURL = '/tourney/current_matches',
                dataview = {
                    saveChangesURL: '/bio/saveChanges',
                    xtype: 'carromboards-dataview',
                    id: 'carromboards-view',
                    listeners: {
                        destroy: function(v) {
                            v.dragZone.destroy();
                        },

                        render: function(v) {
                            v.dragZone = new Ext.dd.DragZone(v.getEl(), {
                                ddGroup: 'competitor',

                                getDragData: function(e) {
                                    var player = e.getTarget('span.competitor', 10, true);
                                    if (player) {
                                        var container = player.parent();
                                        var idmatch = parseInt(container.dom.attributes.mid.nodeValue, 10);
                                        var match = v.store.getById(idmatch);
                                        var xy = player.getXY();
                                        var sourceEl = player.dom;
                                        var d = sourceEl.cloneNode(true);
                                        d.id = Ext.id();
                                        return {
                                            sourceEl: sourceEl,
                                            sourceMatch: match,
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
                        }
                    },
                    plugins: [ Ext.create('SoL.view.Tables.Actions') ]
                },
                cfg = config.Tables = {
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'top',
                        itemId: 'ttoolbar',
                        enableOverflow: true
                    }],
                    hidden: config.tourney.readOnly,
                    items: [ dataview ],
                    layout: 'fit',
                    title: _('Current round pairings'),
                    titleCollapse: false,
                    floatable: false,
                    xtype: 'panel',
                    toggleCollapse: function(event) {
                        var me = this, res;
                        if(me.collapsed || me.floatedFromCollapse) {
                            me.toggled_with_altkey = event && event.altKey;
                            res = me.expand();
                            delete me.toggled_with_altkey;
                        } else
                            res = me.collapse();
                        return res;
                    }
                };

            MP.data.MetaData.fetch(dataURL, me, function(metadata) {
                var overrides = {},
                    model;

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
                    pageSize: 999
                });
                dataview.store.implicitModel = true;

                callback(cfg);
            });
        }
    },

    initEvents: function() {
        var me = this;

        me.callParent(arguments);

        me.ownerCt.on('beforeexpand', function() {
            var tourney = me.ownerCt.module.tourney;

            // If we are at the first turn, OR the user ALT-clicked the toggle tool
            // and we are on a new round
            if((tourney.currentturn == 1 && tourney.rankedturn === 0)
               || (me.up().toggled_with_altkey &&
                   (tourney.currentturn - 1) === tourney.rankedturn)) {
                me.setHeight(275);
                if(!me.competitorDrop) {
                    me.competitorDrop = new SoL.view.Tables.CompetitorDrop(me);
                }
                me.store.load();
            } else {
                me.setHeight(80);
                me.store.removeAll();
            }
        });

        me.on('refresh', function() {
            var nboards = me.store.count();

            Ext.select('div.carromboard input').each(function(el) {
                var mid = parseInt(el.parent('div.carromboard').getAttribute('mid'), 10);

                el.dom.setAttribute('max', nboards.toString());
                el.on('change', function(e, input) {
                    var newv = input.valueAsNumber,
                        oldv = parseInt(input.getAttribute('value'), 10),
                        thisMatch = me.store.getById(mid),
                        currInputs = Ext.select('div.carromboard input');

                    currInputs.each(function(otherEl) {
                        if(otherEl.dom !== input
                           && parseInt(otherEl.dom.getAttribute('value'), 10) == newv) {
                            var otherMid = parseInt(otherEl
                                                    .parent('div.carromboard')
                                                    .getAttribute('mid'), 10),
                                otherMatch = me.store.getById(otherMid);
                            otherMatch.set('board', oldv);
                            return false;
                        }
                        return true;
                    });
                    thisMatch.set('board', newv);
                });
            });
        });
    },

    prepareData: function(data, index, record) {
        var me = this,
            dirty = me.store.classifyRecord(record);

        me.callParent(data, index, record);

        data.dirtyCls = dirty === '' ? '' : ' '+dirty;
        data.boardNo = _('Carromboard #');
        return data;
    },

    commitChanges: function(callback, scope) {
        var me = this;

        me.store.commitChanges('/bio/saveChanges',
                               me.store.proxy.reader.idProperty,
                               function() {
                                   me.ownerCt.module.reloadMatches();
                                   if(callback) {
                                       callback();
                                   }
                               }, scope);
    },

    resetChanges: function() {
        var me = this;

        me.store.rejectChanges();
        me.refresh();
    }
});


Ext.define('SoL.view.Tables.CompetitorDrop', {
    extend: 'Ext.dd.DropTarget',
    uses: ['MP.window.Notification'],

    group: 'competitor',

    constructor: function(view) {
        var me = this;

        me.callParent([view.el, {}]);
        me.store = view.store;
        me.dataview = view;
        me.tourney = view.ownerCt.module.tourney;
    },

    notifyEnter: function(source, e, data) {
        var me = this,
            r;

        if((r=me.notifyOver(source, e, data)) != me.dropNotAllowed) {
            me.callParent(source, e, data);
            return r;
        } else {
            return me.dropNotAllowed;
        }
    },

    notifyOver: function(source, e, data) {
        //jsl:unused source

        var target = e.getTarget('.competitor', 10, true);

        if(!target) {
            return this.dropNotAllowed;
        }

        var tcontainer = target.parent(),
            targetId = parseInt(tcontainer.dom.attributes.mid.nodeValue, 10),
            targetMatch = this.store.getById(targetId),
            targetOpps, ids, scomp, idscomp, oscomp, tcomp, idtcomp, otcomp, osOpps;

        ids = String(data.sourceEl.id).split('_');
        scomp = parseInt(ids[1], 10);
        idscomp = parseInt(ids[2], 10);

        ids = String(target.id).split('_');
        tcomp = parseInt(ids[1], 10);
        idtcomp = parseInt(ids[2], 10);

        // Check if the source competitor already met the competitor on the other side of the
        // target carromboard, or if the source's opponent already met the target competitor:
        // in such case, the swap would be invalid
        oscomp = scomp == 1 ? 2 : 1;
        osOpps = data.sourceMatch.get('competitor'+oscomp+'Opponents');
        otcomp = tcomp == 1 ? 2 : 1;
        targetOpps = targetMatch.get('competitor'+otcomp+'Opponents');

        return ((target
                 && idscomp != idtcomp // targetId != data.sourceMatch.get("idmatch")
                 && targetOpps.indexOf(idscomp) < 0
                 && osOpps.indexOf(idtcomp) < 0)
                ? this.dropAllowed : this.dropNotAllowed);
    },

    notifyDrop : function(source, e, data) {
        //jsl:unused source

        var me = this,
            target = e.getTarget('.competitor', 10, true);

        if(!target || me.notifyOver(source, e, data) == me.dropNotAllowed) {
            return false;
        }

        var tcontainer = target.parent(),
            targetId = parseInt(tcontainer.dom.attributes.mid.nodeValue, 10),
            targetMatch = this.store.getById(targetId),
            sourceMatch = data.sourceMatch,
            ids, scomp, idscomp, tcomp, idtcomp, sfullname, sopps;

        ids = String(data.sourceEl.id).split('_');
        scomp = parseInt(ids[1], 10);
        idscomp = parseInt(ids[2], 10);

        ids = String(target.id).split('_');
        tcomp = parseInt(ids[1], 10);
        idtcomp = parseInt(ids[2], 10);

        sfullname = sourceMatch.get('competitor'+scomp+'FullName');
        sopps = sourceMatch.get('competitor'+scomp+'Opponents');

        if(scomp == 1 && !idtcomp) {
            sourceMatch.set('idcompetitor1',
                            sourceMatch.get('idcompetitor2'));
            sourceMatch.set('competitor1FullName',
                            sourceMatch.get('competitor2FullName'));
            sourceMatch.set('competitor1Opponents',
                            sourceMatch.get('competitor2Opponents'));
            sourceMatch.set('idcompetitor2', null);
            sourceMatch.set('competitor2FullName',
                            targetMatch.get('competitor'+tcomp+'FullName'));
            sourceMatch.set('competitor2Opponents', "");
        } else {
            sourceMatch.set('idcompetitor'+scomp, idtcomp);
            sourceMatch.set('competitor'+scomp+'FullName',
                            targetMatch.get('competitor'+tcomp+'FullName'));
            sourceMatch.set('competitor'+scomp+'Opponents',
                            targetMatch.get('competitor'+tcomp+'Opponents'));
        }

        if(!sourceMatch.get('idcompetitor2')) {
            if(!sourceMatch.get('score1')) {
                sourceMatch.set('score1', targetMatch.get('score1'));
            }
        }

        if(tcomp == 1 && !idscomp) {
            targetMatch.set('idcompetitor1',
                            targetMatch.get('idcompetitor2'));
            targetMatch.set('competitor1FullName',
                            targetMatch.get('competitor2FullName'));
            targetMatch.set('competitor1Opponents',
                            targetMatch.get('competitor2Opponents'));
            targetMatch.set('idcompetitor2', null);
            targetMatch.set('competitor2FullName', sfullname);
            targetMatch.set('competitor2Opponents', sopps);
        } else {
            targetMatch.set('idcompetitor'+tcomp, idscomp);
            targetMatch.set('competitor'+tcomp+'FullName', sfullname);
            targetMatch.set('competitor'+tcomp+'Opponents', sopps);
        }

        if(!targetMatch.get('idcompetitor2')) {
            if(!targetMatch.get('score1')) {
                targetMatch.set('score1', sourceMatch.get('score1'));
            }
        }

        if(sourceMatch.get('idcompetitor2')) {
            sourceMatch.set('score1', 0);
        }

        if(targetMatch.get('idcompetitor2')) {
            targetMatch.set('score1', 0);
        }

        this.dataview.refresh();
        return true;
    }
});
