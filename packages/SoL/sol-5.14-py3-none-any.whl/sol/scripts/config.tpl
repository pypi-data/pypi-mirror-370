# -*- mode: conf; coding: utf-8 -*-
# SoL production configuration

[app:main]
use = egg:sol

####################
# Desktop settings #
####################

desktop.title = SoL
desktop.debug = false
desktop.domain = sol-client

available_languages = it en_GB en_US

mako.directories = sol:views

pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en
pyramid.includes =
    pyramid_tm
    pyramid_mailer
    metapensiero.sqlalchemy.proxy.pyramid

session.secret = {secret}
# Sessions maximum age in seconds, None means unlimited
session.timeout = None
session.reissue_time = None

##############################
# Database kind and location #
##############################

sqlalchemy.url = sqlite:///{datadir}/SoL.sqlite

######################
# SoL Authentication #
######################

sol.admin.user = {admin}
sol.admin.password = {password}
sol.admin.email = someone@example.com

# Uncomment to enable guest user
#sol.guest.user = guest
#sol.guest.password = guest

# Set to "true" to enable following functionalities...
sol.enable_signin = false
sol.enable_password_reset = false
sol.signer_secret_key = {signer_secret_key}

##############################
# Persistent stuff locations #
##############################

# Directories containing players portraits and clubs emblems
sol.portraits_dir = {datadir}/portraits
sol.emblems_dir = {datadir}/emblems

# Directory used for automatic backups, "None" to disable
sol.backups_dir = {datadir}/backups

# Crypted key for backups: if set (to a 32-bytes hex string), backups will be crypted
# sol.backup_secret_key =

#################
# Outgoing mail #
#################

# Consult https://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/#configuration
# to setup outgoing mail
#mail.host = localhost
#mail.port = 25
#mail.default_sender = no-reply@metapensiero.it

###########
# Alembic #
###########

# Path to migration scripts
script_location = {alembicdir}

# Template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# Max length of characters to apply to the
# "slug" field
#truncate_slug_length = 40

# Set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 6996

#########################
# Logging configuration #
#########################

[loggers]
keys = root, sol, sqlalchemy, changes, auth

[handlers]
keys = file, changes, auth

[formatters]
keys = generic, changes

[logger_root]
level = WARN
handlers = file

[logger_sol]
level = WARN
handlers =
qualname = sol

[logger_changes]
level = INFO
handlers = changes
qualname = sol.models.bio.changes
propagate = 0

[logger_auth]
level = INFO
handlers = auth
qualname = sol.views.auth
propagate = 0

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)

[handler_file]
class = handlers.RotatingFileHandler
args = ('{datadir}/sol.log', 'a', 1000000, 5, 'utf-8')
level = NOTSET
formatter = generic

[handler_changes]
class = handlers.RotatingFileHandler
args = ('{datadir}/changes.log', 'a', 1000000, 5, 'utf-8')
level = NOTSET
formatter = changes

[handler_auth]
class = handlers.RotatingFileHandler
args = ('{datadir}/auth.log', 'a', 1000000, 5, 'utf-8')
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s

[formatter_changes]
format = %(asctime)s %(message)s
