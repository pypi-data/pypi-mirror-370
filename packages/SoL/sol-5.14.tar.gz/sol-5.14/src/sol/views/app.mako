## -*- coding: utf-8 -*
## :Project:   SoL -- Top level application page
## :Created:   sab 14 lug 2018 11:34:50 CEST
## :Author:    Lele Gaifax <lele@metapensiero.it>
## :License:   GNU General Public License version 3 or later
## :Copyright: © 2018, 2020, 2024 Lele Gaifax
##

<!DOCTYPE html>

<html lang="${locale}">
  <head>
    <link rel="icon" type="image/png" href="/static/favicon.png" />
    % if debug:
      <link rel="stylesheet" type="text/css"
            href="/desktop/extjs/resources/css/ext-all-debug.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/action.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/desktop.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/filterbar.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/grid.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/form.css" />
      <link rel="stylesheet" type="text/css"
            href="/desktop/css/upload.css" />
      <link rel="stylesheet" type="text/css"
            href="/static/css/app.css" />
    % else:
      <link rel="stylesheet" type="text/css"
            href="/static/all-styles.css?v=${app_version}" />
    % endif

    <script>
     __title__ = "${app_title}";
     __version__ = "${app_version}";
     __csrf_token__ = "${get_csrf_token()}";
     __signin__ = ${'true' if signin_enabled else 'false'};
     __password_reset__ = ${'true' if password_reset_enabled else 'false'};
     __admin_email__ = "${admin_email}";
    </script>

    <script src="/catalog"></script>

    % if debug:
      <script src="/desktop/extjs/ext-dev.js">
      </script>

      <script>
       Ext.Loader.setConfig({ enabled: true });
      </script>
    % else:
      <script src="/static/ext.js">
      </script>

      <script>
       Ext.Loader.setConfig({ enabled: false });
      </script>

      <script src="/static/all-classes.js?v=${app_version}">
      </script>
    % endif

    <script src="/static/app.js?v=${app_version}"></script>

    <script src="/extjs-l10n"></script>

    <title>${app_title} (${app_version})</title>
  </head>

  <body></body>
</html>
