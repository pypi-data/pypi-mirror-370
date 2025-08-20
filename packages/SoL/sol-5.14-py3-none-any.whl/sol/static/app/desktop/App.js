// -*- coding: utf-8 -*-
// :Project:   SoL -- Specialized MP Desktop
// :Created:   lun 16 lug 2018 07:29:27 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2018, 2020, 2021, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('SoL.desktop.App', {
    extend: 'MP.desktop.App',

    uses: [
        'SoL.window.ChangeLanguage',
        'SoL.window.ChangePassword'
    ],

    desktopConfig: {
        wallpaper: '/static/images/wallpapers/sol5.png',
        wallpaperStyle: 'center'
    },

    getStartConfig: function () {
        var me = this,
            config = me.callParent();

        config.height = (me.user.is_admin || me.user.user_id === null) ? 185 : 260;
        return config;
    },

    getToolConfig: function() {
        var me = this,
            config = me.callParent(),
            upload_module = me.getModule('upload-win');

        config.items.unshift({
            text: _('Scorecards'),
            tooltip: _('Print one sheet of blank scorecards.'),
            iconCls: 'print-icon',
            handler: function() {
                var url = '/pdf/scorecards/blank';
                window.location.assign(url);
            }
        }, '-', {
            text: _('Manual'),
            tooltip: _('Show user manual.'),
            iconCls: 'help-icon',
            handler: function() {
                // TRANSLATORS: this is the URL of the user manual
                window.open(_('/static/manual/en/index.html'), "_blank");
            }
        }, {
            text: _('Rules'),
            tooltip: _('Carrom playing rules.'),
            iconCls: 'info-icon',
            handler: function() {
                // TRANSLATORS: this is the URL of the carrom rules chapter in
                // the user manual
                window.open(_('/static/manual/en/rules.html'), "_blank");
            }
        }, !me.user.is_admin ? {
            text: _('Donate'),
            tooltip: _('Support SoL development through a donation.'),
            iconCls: 'money-euro-icon',
            handler: function() {
                // TRANSLATORS: this is the URL of the support chapter in
                // the user manual
                window.open(_('/static/manual/en/development.html#donations'), "_blank");
            }
        } : null, !me.user.is_admin ? {
            text: _('Issues'),
            tooltip: _('Propose enhancements or report issues.'),
            iconCls: 'bug-link-icon',
            handler: function() {
                window.open('https://gitlab.com/metapensiero/SoL/-/issues', "_blank");
            }
        } : null, '-');

        if(!me.user.is_admin && me.user.user_id !== null) {
            config.items.splice(config.items.length-1, 0, {
                text: _('Password'),
                tooltip: _('Change your account password.'),
                iconCls: 'edit-pwd-icon',
                handler: function() {
                    Ext.create('SoL.window.ChangePassword', {}).show();
                }
            });
            config.items.splice(config.items.length-1, 0, {
                text: _('Language'),
                tooltip: _('Change your account UI language.'),
                iconCls: 'comment-icon',
                handler: function() {
                    Ext.create('SoL.window.ChangeLanguage', {
                        currentLanguage: me.user.ui_language
                    }).show();
                }
            });
        }

        if(upload_module) {
            config.items.unshift({
                iconCls: upload_module.iconCls,
                text: _('Upload'),
                tooltip: upload_module.getLauncherTooltip(),
                handler: upload_module.createOrShowWindow,
                scope: upload_module
            });
        }

        return config;
    }
});
