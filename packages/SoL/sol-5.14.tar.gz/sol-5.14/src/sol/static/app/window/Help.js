// -*- coding: utf-8 -*-
// :Project:   SoL -- Help modal iframe
// :Created:   mar 03 mag 2016 11:43:38 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2016 Lele Gaifax
//

//jsl:declare Ext


Ext.define('SoL.window.Help', {
    extend: 'Ext.window.Window',

    uses: ['SoL.component.IFrame'],

    layout: 'fit',
    width: 800,
    height: 640,
    maximizable: true,
    iconCls: 'help-icon',

    initComponent: function() {
        var me = this;

        me.items = [{
            xtype: 'iframe'
        }];

        me.callParent();
    },

    onShow: function() {
        var me = this;
        var iframe = me.items.getAt(0);

        this.callParent();

        iframe.load(me.help_url);
    }
});
