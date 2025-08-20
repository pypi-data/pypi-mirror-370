// -*- coding: utf-8 -*-
// :Project:   SoL --
// :Created:   lun 29 apr 2013 08:21:57 CEST
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2013, 2024 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Tourney', {
    requires: [
        'SoL.view.Competitors',
        'SoL.view.Matches',
        'SoL.view.Ranking',
        'SoL.view.Tables'
    ],

    statics: {
        configurators: function() {
            return [SoL.view.Competitors.getConfig,
                    SoL.view.Matches.getConfig,
                    SoL.view.Ranking.getConfig,
                    SoL.view.Tables.getConfig];
        }
    }
});
