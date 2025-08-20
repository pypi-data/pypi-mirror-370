// -*- coding: utf-8 -*-
// :Project:   SoL -- Reset password window
// :Created:   lun 16 lug 2018 09:21:56 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2018 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('SoL.window.ResetPassword', {
    extend: 'Ext.Window',
    uses: 'Ext.form.Panel',

    title: _('Reset lost password'),
    titleAlign: 'center',
    width: 400,
    autoHeight: true,
    closable: false,
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

                url: '/auth/resetPassword',
                baseParams: {token: window.location.hash.substr(16)},
                items: me.getFormFields()
            }]
        });
        me.callParent();
    },

    buttons: ['->', {
        text: _("Change password"),
        type: "submit",
        formBind: true,
        handler: function(button) {
            var win = button.up('window'),
                panel = win.down('form'),
                form = panel.getForm();

            if(form.isValid()) {
                panel.getEl().mask(_("Changing password…"));

                form.submit({
                    success: function(f, a) {
                        Ext.Msg.show({
                            title: _('Password changed'),
                            msg: _('Your password has been successfully changed, you will be redirected to the authentication panel.'),
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            fn: function() {
                                win.close();
                                window.location.assign(a.result.location);
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

    defaultFocus: 'password',

    getFormFields: function() {
        return [{
            xtype: 'textfield',
            fieldLabel: _('New password'),
            name: 'password',
            allowBlank: false,
            inputType: 'password',
            minLength: 6,
            anchor: '100%',
            selectOnFocus: true
        }];
    }
});
