// -*- coding: utf-8 -*-
// :Project:   SoL --
// :Created:   ven 19 apr 2013 19:48:07 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2013, 2014 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare SoL*/

Ext.define('SoL.form.field.FlagsCombo', {
    extend:'Ext.form.field.ComboBox',
    alias:'widget.flagscombo',
    requires: ['Ext.data.ArrayStore'],

    valueField: 'code',
    displayField: 'name',
    triggerAction: 'all',
    queryMode: 'local',
    typeAhead: true,
    forceSelection: true,
    minChars: 0,

    statics: {
        renderer: function(value) {
            var country = SoL.form.field.FlagsCombo.countries[value];
            if(country) {
                return '<div class="sol-flags-icon'
                    + ' sol-flag-' + value + '">'
                    + country + '</div>';
            } else {
                return value;
            }
        }
    },

    initComponent: function() {
        var me = this;
        var array = [];

        delete me.maxLength;

        me.tpl = new Ext.XTemplate(
            '<tpl for=".">',
            '<div class="x-boundlist-item sol-flags-icon',
            ' sol-flag-{code}">{name}</div></tpl>'
            );

        var countries = SoL.form.field.FlagsCombo.countries;
        for(var code in countries) {
            array.push([code, countries[code]]);
        }

        me.store = new Ext.data.ArrayStore({
            fields: ['code', 'name'],
            data: array,
            sorters: [{
                property: 'name'
            }]
        });

        // call parent initComponent
        me.callParent();
    },

    onRender: function() {
        var me = this;

        // call parent onRender
        me.callParent(arguments);

        // adjust styles
        me.triggerWrap.el.applyStyles({position: 'relative'});
        me.el.down('input.x-form-field').addCls('sol-flags-icon');

        // add div for icon
        me.icon = Ext.core.DomHelper.append(
            me.el.down('td.x-form-trigger-input-cell'), {
                tag: 'div', style:'position:absolute; top:3px; left:3px;'
            });
    },

    setIconCls: function() {
        var me = this;

        if(me.rendered) {
            var value = me.getValue();
            if (value) {
                var country = SoL.form.field.FlagsCombo.countries[value];
                if (country) {
                    me.icon.className = 'sol-flags-icon sol-flag-' + value;
                } else {
                    me.icon.className = '';
                }
            } else {
                me.icon.className = '';
            }
        } else {
            me.on('render', me.setIconCls, me, { single: true } );
        }
    },

    setValue: function(value, doSelect) {
        var me = this;

        me.callParent([value, doSelect]);
        me.setIconCls();
    }
});
