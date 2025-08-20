// -*- coding: utf-8 -*-
// :Project:   SoL -- Application entry point
// :Created:   ven 19 apr 2013, 19:02:33
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2013, 2018, 2020 Lele Gaifax
//

/*jsl:declare Ext*/

Ext.Loader.setPath({
    MP: '/desktop/js'
});

Ext.application({
    name: 'SoL',
    appFolder: '/static/app',
    controllers: [
        'Login'
    ],

    launch: function() {
        var hash = window.location.hash;

        // Fix an issue with form fields tooltips width on recent Firefoxes
        // Taken from https://stackoverflow.com/a/16220208
        Ext.override(Ext.tip.QuickTip, {
            helperElId: 'ext-quicktips-tip-helper',
            initComponent: function() {
                var me = this;

                me.target = me.target || Ext.getDoc();
                me.targets = me.targets || {};
                me.callParent();

                // new stuff
                me.on('move', function() {
                    var offset = me.hasCls('x-tip-form-invalid') ? 35 : 12,
                        helperEl = Ext.fly(me.helperElId) || Ext.fly(
                            Ext.DomHelper.createDom({
                                tag: 'div',
                                id: me.helperElId,
                                style: {
                                    position: 'absolute',
                                    left: '-1000px',
                                    top: '-1000px',
                                    'font-size': '12px',
                                    'font-family': 'tahoma, arial, verdana, sans-serif'
                                }
                            }, Ext.getBody())
                        );

                    if(me.html && (me.html !== helperEl.getHTML()
                                   || me.getWidth() !== (helperEl.dom.clientWidth + offset))) {
                        helperEl.update(me.html);
                        me.setWidth(Ext.Number.constrain(helperEl.dom.clientWidth + offset,
                                                         me.minWidth, me.maxWidth));
                    }
                }, this);
            }
        });

        // Fix a similar issue, also on modern Firefoxes, where the tooltip attached to
        // grids are not resized accordingly to the width of their text.
        // Taken from https://www.sencha.com/forum/showthread.php\
        // ?260106-Tooltips-on-forms-and-grid-are-not-resizing-to-the-size-of-the-text&p=976013&viewfull=1#post976013
        Ext.override(Ext.dom.Element, {
            getWidth: function(contentWidth, preciseWidth) {
                var me = this,
                    dom = me.dom,
                    hidden = me.isStyle('display', 'none'),
                    rect, width, floating;

                if (hidden) {
                    return 0;
                }

                // Gecko will in some cases report an offsetWidth that is actually less than
                // the width of the text contents, because it measures fonts with sub-pixel
                // precision but rounds the calculated value down. Using getBoundingClientRect
                // instead of offsetWidth allows us to get the precise subpixel measurements so
                // we can force them to always be rounded up. See
                // https://bugzilla.mozilla.org/show_bug.cgi?id=458617 Rounding up ensures that
                // the width includes the full width of the text contents.
                if (Ext.supports.BoundingClientRect) {
                    rect = dom.getBoundingClientRect();
                    // IE9 is the only browser that supports getBoundingClientRect() and
                    // uses a filter to rotate the element vertically.  When a filter
                    // is used to rotate the element, the getHeight/getWidth functions
                    // are not inverted (see setVertical).
                    width = (me.vertical && !Ext.isIE9 && !Ext.supports.RotatedBoundingClientRect) ?
                        (rect.bottom - rect.top) : (rect.right - rect.left);
                    width = preciseWidth ? width : Math.ceil(width);
                } else {
                    width = dom.offsetWidth;
                }

                // IE9/10 Direct2D dimension rounding bug:
                // https://sencha.jira.com/browse/EXTJSIV-603 there is no need make adjustments
                // for this bug when the element is vertically rotated because the width of a
                // vertical element is its rotated height
                if (Ext.supports.Direct2DBug && !me.vertical) {
                    // get the fractional portion of the sub-pixel precision width of the
                    // element's text contents
                    floating = me.adjustDirect2DDimension('width');
                    if (preciseWidth) {
                        width += floating;
                    }
                    // IE9 also measures fonts with sub-pixel precision, but unlike Gecko,
                    // instead of rounding the offsetWidth down, it rounds to the nearest
                    // integer. This means that in order to ensure that the width includes the
                    // full width of the text contents we need to increment the width by 1 only
                    // if the fractional portion is less than 0.5
                    else if (floating > 0 && floating < 0.5) {
                        width++;
                    }
                }

                if (contentWidth) {
                    width -= me.getBorderWidth("lr") + me.getPadding("lr");
                }

                return (width < 0) ? 0 : width;
            }
        });

        Ext.BLANK_IMAGE_URL = '/static/images/s.gif';
        if(hash && hash.substr(1, 15) == 'reset_password=') {
            Ext.create('SoL.window.ResetPassword', {}).show();
        } else {
            Ext.create('SoL.window.Login', {}).show();
        }
    }
});
