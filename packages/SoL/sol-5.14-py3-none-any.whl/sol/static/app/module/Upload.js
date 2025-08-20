// -*- coding: utf-8 -*-
// :Project:   SoL -- Upload tourneys data or club emblems
// :Created:   ven 17 ott 2008 11:38:21 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2008-2010, 2013-2016 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/

Ext.define('SoL.module.Upload', {
    extend: 'MP.desktop.Module',
    requires: [
        'Ext.form.Panel',
        'Ext.form.field.File'
    ],
    uses: ['MP.window.Notification'],

    id: 'upload-win',
    iconCls: 'upload-icon',
    launcherText: null,
    launcherTooltip: function() {
        return _('<b>Upload</b><br />Upload tourneys data.');
    },

    uploadURL: "/bio/upload",

    createOrShowWindow: function() {
        var me = this,
            desktop = me.app.getDesktop(),
            win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var winWidth = 315,
            winHeight = 110,
            form = new Ext.form.Panel({
                frame: true,
                bodyPadding: '10 10 0',
                defaults: {
                    labelWidth: 50,
                    anchor: '100%'
                },
                items: [{
                    xtype: 'fileuploadfield',
                    buttonText: _('Browse'),
                    emptyText: _('Select archive'),
                    allowBlank: false,
                    blankText: _('This field is required'),
                    fieldLabel: _('File'),
                    name: 'archive',
                    buttonCfg: {
                        text: '',
                        iconCls: 'upload-browse-icon'
                    },
                    listeners: {
                        afterrender: function(fld) {
                            var el = fld.fileInputEl.dom;
                            el.setAttribute('accept', 'application/zip,application/gzip');
                        }
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
                    handler: function() {
                        if(form.getForm().isValid()) {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                html: _('Uploading…'),
                                title: _('Please wait'),
                                iconCls: 'waiting-icon'
                            }).show();
                            form.getForm().submit({
                                url: me.uploadURL,
                                waitMsg: _('Uploading…'),
                                success: function(fp, o) {
                                    //jsl:unused fp
                                    if(o.result.success) {
                                        Ext.create("MP.window.Notification", {
                                            position: 'br',
                                            html: o.result.message,
                                            title: _('Done'),
                                            iconCls: 'done-icon'
                                        }).show();
                                    } else {
                                        Ext.create("MP.window.Notification", {
                                            position: 'br',
                                            html: o.result.message,
                                            title: _('Error'),
                                            iconCls: 'alert-icon'
                                        }).show();
                                    }
                                },
                                failure: function(fp, o) {
                                    //jsl:unused fp
                                    Ext.create("MP.window.Notification", {
                                        position: 'br',
                                        html: _("Couldn't upload selected file:")
                                            + "<br/>" + o.result.message,
                                        title: _('Error'),
                                        iconCls: 'alert-icon'
                                    }).show();
                                }
                            });
                        }
                    }
                }]
            });

        win = desktop.createWindow({
            id: me.id,
            title: _('Upload'),
            iconCls: 'upload-icon',
            width: winWidth,
            height: winHeight,
            layout: 'fit',
            minimizable: false,
            maximizable: false,
            taskbuttonTooltip: me.getLauncherTooltip(),
            items: [form]
        });

        win.show();
    }
});
