// -*- coding: utf-8 -*-
// :Project:   SoL -- Sign in window
// :Created:   lun 16 lug 2018 07:59:55 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2018, 2020, 2022 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare __csrf_token__*/

Ext.define('SoL.window.Signin', {
    extend: 'Ext.Window',
    uses: 'Ext.form.Panel',

    title: _('Complete the form to request a new account'),
    titleAlign: 'center',
    width: 400,
    autoHeight: true,
    closable: true,
    resizable: false,
    draggable: false,
    layout: 'fit',
    border: false,
    modal: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [{
                xtype: 'form',
                plain: true,
                frame: true,
                border: 0,
                bodyPadding: 5,

                url: '/auth/signin',

                items: me.getFormFields()
            }]
        });
        me.callParent();
    },

    buttons: ['->', {
        text: _("Register"),
        type: "submit",
        formBind: true,
        handler: function(button) {
            var win = button.up('window'),
                panel = win.down('form'),
                form = panel.getForm();

            if(form.isValid()) {
                panel.getEl().mask(_("Registration…"));

                form.submit({
                    headers: {'X-CSRF-Token': __csrf_token__},
                    success: function(f, a) {
                        Ext.Msg.show({
                            title: _('Registration succeeded'),
                            msg: _('An email has been sent to the given address, you should receive it shortly: please check your inbox and follow the link within two days to confirm the account.'),
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

    defaultFocus: 'email',

    getFormFields: function() {
        var flds = ['code', 'name'],
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
                }
            });
        lstore.implicitModel = true;

        return [{
            itemId: 'email',
            xtype: 'textfield',
            fieldLabel: _('Email'),
            name: 'email',
            allowBlank: false,
            anchor: '100%',
            selectOnFocus: true,
            vtype: 'email'
        }, {
            xtype: 'textfield',
            fieldLabel: _('Password'),
            name: 'password',
            allowBlank: false,
            inputType: 'password',
            minLength: 6,
            anchor: '100%',
            selectOnFocus: true
        }, {
            xtype: 'textfield',
            fieldLabel: _('First name'),
            name: 'firstname',
            allowBlank: false,
            anchor: '100%',
            selectOnFocus: true
        }, {
            xtype: 'textfield',
            fieldLabel: _('Last name'),
            name: 'lastname',
            allowBlank: false,
            anchor: '100%',
            selectOnFocus: true
        }, {
            xtype: 'combo',
            fieldLabel: _('Language'),
            name: 'language',
            store: lstore,
            valueField: 'code',
            displayField: 'name',
            loadingText: _('Loading…'),
            typeAhead: true,
            forceSelection: true,
            allowBlank: true,
            anchor: '100%',
            minChars: 0
        }, {
            xtype: 'container',
            height: 'auto',
            margin: '20 15 5 15',
            style: {
                textAlign: 'center'
            },
            html: _('By registering, you <strong>agree</strong> with the <a href="/static/manual/en/privacy.html" target="_blank">SoL privacy policy</a>.')
        }];
    }
});
