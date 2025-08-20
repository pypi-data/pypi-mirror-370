// -*- coding: utf-8 -*-
// :Project:   SoL -- Reset password window
// :Created:   lun 16 lug 2018 08:20:24 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2018 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare __csrf_token__*/

Ext.define('SoL.window.LostPassword', {
    extend: 'Ext.Window',
    uses: 'Ext.form.Panel',

    title: _('Lost password'),
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

                url: '/auth/lostPassword',

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
                panel.getEl().mask(_("Requesting password reset…"));

                form.submit({
                    headers: {'X-CSRF-Token': __csrf_token__},
                    success: function(f, a) {
                        Ext.Msg.show({
                            title: _('Request succeeded'),
                            msg: _('An email has been sent to the given address, you should receive it shortly: please check your inbox and follow the link within two days to renew your password.'),
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
        return [{
            itemId: 'email',
            xtype: 'textfield',
            fieldLabel: _('Email'),
            name: 'email',
            allowBlank: false,
            anchor: '100%',
            selectOnFocus: true,
            vtype: 'email'
        }];
    }
});
