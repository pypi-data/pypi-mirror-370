// -*- coding: utf-8 -*-
// :Project:   SoL -- Authentication form controller
// :Created:   lun 15 apr 2013 11:33:59 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2013, 2014, 2018 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare __password_reset__*/
/*jsl:declare __signin__*/
/*jsl:declare window*/

Ext.define('SoL.controller.Login', {
    extend: 'MP.controller.Login',
    uses: [
        'SoL.desktop.App',
        'SoL.window.Login',
        'SoL.window.LostPassword',
        'SoL.window.Signin'
    ],

    applicationClass: 'SoL.desktop.App',

    init: function() {
        var me = this;

        me.callParent(arguments);

        me.control({
            'loginwindow button[action=signin]': {
                click: me.signin
            },
            'loginwindow button[action=lostpassword]': {
                click: me.lostPassword
            }
        });
    },

    _doCreateUserDesktop: function(user) {
        var me = this;
        var app = MP.controller.Login.prototype.createUserDesktop.call(me, user);

        app.on('ready', function() {
            Ext.Ajax.request({
                url: '/data/countries',
                success: function(response) {
                    var result = Ext.decode(response.responseText);
                    var root = result.root;
                    var c, cd = {};

                    for(var i=0, l=result.count; i<l; i++) {
                        c = root[i];
                        cd[c.code] = c.name;
                    }
                    SoL.form.field.FlagsCombo.countries = cd;
                }
            });
        });
    },

    createUserDesktop: function(user) {
        var me = this;
        var reload = user.reload_l10n;

        delete user.reload_l10n;

        // Maybe reload the l10n catalogs, to match logged user prefs

        if(reload) {
            Ext.Loader.loadScript({
                url: '/catalog',
                onLoad: function() {
                    Ext.Loader.loadScript({
                        url: '/extjs-l10n',
                        onLoad: function() {
                            me._doCreateUserDesktop(user);
                        }
                    });
                }
            });
        } else {
            me._doCreateUserDesktop(user);
        }
    },

    signin: function(button) {
        if(__signin__) {
            Ext.create('SoL.window.Signin', {}).show();
        }
    },

    lostPassword: function(button) {
        if(__password_reset__) {
            Ext.create('SoL.window.LostPassword', {}).show();
        }
    }
});
