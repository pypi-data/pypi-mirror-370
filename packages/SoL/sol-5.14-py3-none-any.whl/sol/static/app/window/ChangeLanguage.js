// -*- coding: utf-8 -*-
// :Project:   SoL -- Change UI language window
// :Created:   dom 9 feb 2020, 14:38:32
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2020 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('SoL.window.ChangeLanguage', {
    extend: 'Ext.Window',
    uses: 'Ext.form.Panel',

    title: _('Change your account UI language'),
    titleAlign: 'center',
    width: 400,
    autoHeight: true,
    closable: true,
    resizable: false,
    draggable: false,
    layout: 'fit',
    border: false,
    modal: true,
    currentLanguage: null,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [{
                xtype: 'form',
                plain: true,
                frame: true,
                border: 0,
                bodyPadding: 5,

                url: '/auth/changeLanguage',
                fieldDefaults: {
                    labelWidth: 150
                },
                items: me.getFormFields()
            }]
        });
        me.callParent();
    },

    buttons: ['->', {
        text: _("Confirm"),
        type: "submit",
        formBind: true,
        handler: function(button) {
            var win = button.up('window'),
                panel = win.down('form'),
                form = panel.getForm();

            if(form.isValid()) {
                panel.getEl().mask(_("Changing UI language…"));

                form.submit({
                    success: function(f, a) {
                        Ext.Msg.show({
                            title: _('Change succeeded'),
                            msg: _('Your account UI language has been successfully updated, it will be used at your next login.'),
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            fn: function() {
                                win.close();
                            }
                        });
                    },

                    failure: function(f, a) {
                        f.owner.el.unmask();
                        Ext.Msg.alert(_('Error'),
                                      a.result
                                      ? a.result.message
                                      : _('No response from the server'));
                        if(a.result && a.result.errors) {
                            form.markInvalid(a.result.errors);
                        }
                    }
                });
            }
        }
    }],

    getFormFields: function() {
        var me = this,
            flds = ['code', 'name'],
            displayField = 'name',
            model = Ext.define('MP.data.ImplicitModel-'+Ext.id(), {
                extend: 'Ext.data.Model',
                fields: flds,
                idProperty: 'code'
            }),
            lstore = Ext.create('Ext.data.Store', {
                model: model,
                autoLoad: true,
                proxy: {
                    type: 'ajax',
                    url: '/data/languages',
                    reader: {
                        type: 'json',
                        root: 'root',
                        idProperty: 'code',
                        totalProperty: 'count'
                    }
                },
                listeners: {
                    load: function() {
                        var f;
                        if(me.currentLanguage) {
                            f = me.down('form').form.getFields().get(1);
                            f.suspendEvents();
                            f.setValue(me.currentLanguage);
                            f.resumeEvents();
                        } else {
                            f = me.down('form').form.getFields().get(0);
                            f.suspendEvents();
                            f.setValue(true);
                            f.resumeEvents();
                        }
                    }
                }
            });
        lstore.implicitModel = true;

        return [{
            xtype: 'checkbox',
            fieldLabel: _('Use browser setting'),
            name: 'use_browser_setting',
            listeners: {
                change: function(cb, value) {
                    var f = me.down('form').form.getFields().get(1);
                    f.suspendEvents();
                    f.setValue(value ? null : me.currentLanguage);
                    f.resumeEvents();
                }
            }
        }, {
            xtype: 'combo',
            fieldLabel: _('Language'),
            name: 'language',
            store: lstore,
            valueField: 'code',
            displayField: 'name',
            loadingText: _('Loading…'),
            selectOnFocus: true,
            allowBlank: true,
            anchor: '100%',
            listeners: {
                select: function(c, value) {
                    var f = me.down('form').form.getFields().get(0);
                    f.suspendEvents();
                    f.setValue(!value);
                    f.resumeEvents();
                }
            }
        }, {
            xtype: 'container',
            height: 'auto',
            margin: '20 15 5 15',
            style: {
                textAlign: 'center'
            },
            html: [
                _('If you change this setting, it will be applied at your <b>next</b> login.')
            ].join('')
        }];
    }
});
