# -*- coding: utf-8 -*-
# :Project:   SoL -- Autentication views
# :Created:   lun 15 apr 2013 16:48:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013-2016, 2018-2020, 2022, 2023, 2024 Lele Gaifax
#

from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from os.path import isdir
from socket import gethostbyaddr

import transaction
from itsdangerous import BadData
from itsdangerous import BadTimeSignature
from itsdangerous import TimestampSigner
from pyramid.csrf import check_csrf_token
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPGone
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.settings import asbool
from pyramid.view import view_config
from pyramid_mailer.message import Message
from sqlalchemy.exc import NoResultFound

from ..i18n import translatable_string as _
from ..i18n import translator
from ..models import User
from ..models import bio
from ..models.user import NULL_PASSWORD
from ..models.user import naive_current_uct_timestamp
from . import get_request_logger

logger = logging.getLogger(__name__)


NO_SUCH_USER = _('The inserted user and password, or one of the two, are wrong!')
INVALID_CREDENTIALS = _('Invalid credentials')
RESERVED_EMAIL = _('Invalid email address')
INVALID_EMAIL = _('Please use a different email address')
MANDATORY_FIELD = _('Mandatory field')
MISSING_FIELDS = _('Missing fields')
FULL_NAME = _('{first_name} {last_name}')
ADMINISTRATOR = _('Administrator')
ANONYMOUS = _('Anonymous')
INVALID_OLD_PASSWORD = _('Invalid old password')
OLD_PASSWORD_DOES_NOT_MATCH = _('Old password does not match')
INTERNAL_ERROR = _('Internal error occurred, please contact the administrator')


@subscriber(NewRequest)
def check_authorized_request(
    event,
    authorized_paths={
        '/',
        '/auth/login',
        '/auth/lostPassword',
        '/auth/resetPassword',
        '/auth/signin',
        '/catalog',
        '/data/languages',
        '/extjs-l10n',
        '/favicon.ico',
        '/robots.txt',
    },
):
    """Assert the request is authorized.

    This function gets hooked at the Pyramid's ``NewRequest`` event,
    so it will be executed at the start of each new request.

    If the user has been authenticated, or if she is requesting a
    static resource or one of the authentication views, then nothing
    happens. Otherwise an HTTPUnauthorized exception is raised.
    """

    request = event.request

    # Authenticated user?
    session = request.session
    if 'user_id' in session:
        request.dbsession.info['ignore_privacy'] = True
        return

    request.dbsession.info['ignore_privacy'] = False

    rpath = request.path

    # Anonymous authorized path or static resource?
    sw = rpath.startswith
    if rpath in authorized_paths or sw(('/static/', '/desktop/')):
        return
    if request.method in ('GET', 'HEAD') and (
        sw(('/bio/', '/lit/', '/pdf/', '/svg/', '/tourney/countdown', '/xlsx/'))
        or rpath == '/lit'
    ):
        return
    if request.method == 'POST' and sw(('/lit/match', '/lit/training_match/')):
        return
    # This is to fetch the countdown elapsed time
    if request.method == 'PUT' and sw('/lit/match'):
        return
    if sw('/scripts') and asbool(request.registry.settings.get('desktop.debug', False)):
        return

    get_request_logger(request, logger).error(
        'Unauthorized access to %s (%s)', request.path, request.method
    )

    raise HTTPUnauthorized(_('You must re-authenticate yourself'))


ADMIN_ONLY_MODULES = OrderedDict((('users', dict(classname='SoL.module.Users')),))


MODULES = OrderedDict(
    (
        ('upload', dict(classname='SoL.module.Upload')),
        (
            'clubs',
            dict(
                classname='SoL.module.Clubs',
                quickstart=dict(
                    name=_('Clubs'), iconCls='clubs-icon', moduleId='clubs-win'
                ),
            ),
        ),
        ('clubusers', dict(classname='SoL.module.ClubUsers')),
        (
            'championships',
            dict(
                classname='SoL.module.Championships',
                quickstart=dict(
                    name=_('Championships'),
                    iconCls='championships-icon',
                    moduleId='championships-win',
                ),
            ),
        ),
        (
            'tourneys',
            dict(
                classname='SoL.module.Tourneys',
                quickstart=dict(
                    name=_('Tourneys'), iconCls='tourneys-icon', moduleId='tourneys-win'
                ),
            ),
        ),
        ('tourney', dict(classname='SoL.module.Tourney')),
        ('players', dict(classname='SoL.module.Players')),
        ('ratings', dict(classname='SoL.module.Ratings')),
        ('competitors', dict(classname='SoL.module.Competitors')),
        ('ratedplayers', dict(classname='SoL.module.RatedPlayers')),
        (
            'myclubs',
            dict(
                classname='SoL.module.MyClubs',
                shortcut=dict(
                    name=_('My clubs'),
                    iconCls='clubs-shortcut-icon',
                    moduleId='my-clubs-win',
                ),
            ),
        ),
        (
            'mychampionships',
            dict(
                classname='SoL.module.MyChampionships',
                shortcut=dict(
                    name=_('My championships'),
                    iconCls='championships-shortcut-icon',
                    moduleId='my-championships-win',
                ),
            ),
        ),
        (
            'mytourneys',
            dict(
                classname='SoL.module.MyTourneys',
                shortcut=dict(
                    name=_('My tourneys'),
                    iconCls='tourneys-shortcut-icon',
                    moduleId='my-tourneys-win',
                ),
            ),
        ),
        (
            'myplayers',
            dict(
                classname='SoL.module.MyPlayers',
                shortcut=dict(
                    name=_('My players'),
                    iconCls='players-shortcut-icon',
                    moduleId='my-players-win',
                ),
            ),
        ),
        (
            'myratings',
            dict(
                classname='SoL.module.MyRatings',
                shortcut=dict(
                    name=_('My ratings'),
                    iconCls='ratings-shortcut-icon',
                    moduleId='my-ratings-win',
                ),
            ),
        ),
    )
)


def perform_backup(request):
    "Perform a database backup at login/logout."

    settings = request.registry.settings
    bckdir = settings.get('sol.backups_dir', None)
    if bckdir and isdir(bckdir):
        pdir = settings['sol.portraits_dir']
        edir = settings['sol.emblems_dir']

        with transaction.manager:
            bio.backup(
                request.dbsession,
                pdir,
                edir,
                bckdir,
                serialization_format='json',
                native_when_possible=True,
            )


@view_config(route_name='login', renderer='json', request_method='POST')
def auth_user(request):
    from pyramid.i18n import make_localizer
    from pyramid.interfaces import ILocalizer
    from pyramid.interfaces import ITranslationDirectories

    from sol.i18n import available_languages

    t = translator(request)

    data = request.params

    username = data.get('username', None)
    password = data.get('password', None)

    ipaddress = request.client_addr
    try:
        host = gethostbyaddr(ipaddress)
    except Exception:
        hostname = 'unknown host'
    else:  # pragma: nocover
        hostname = host[0]

    logger.debug('Login attempt by "%s" from %s (%s)', username, ipaddress, hostname)

    if username and password:
        settings = request.registry.settings

        adminuser = settings.get('sol.admin.user')
        adminpwd = settings.get('sol.admin.password')
        guestuser = settings.get('sol.guest.user')
        guestpwd = settings.get('sol.guest.password')

        is_admin = False
        is_nationalliable = False
        is_ownersadmin = False
        is_playersmanager = False
        is_guest = False
        user_id = None
        ui_language = None
        maxratinglevel = None

        if adminuser and username == adminuser:
            if password == adminpwd:
                is_admin = is_nationalliable = is_ownersadmin = is_playersmanager = True
                maxratinglevel = '1'
                fullname = t(ADMINISTRATOR)
            else:
                logger.warning(
                    'Login attempt by "%s" from %s (%s) with wrong password',
                    username,
                    ipaddress,
                    hostname,
                )
                return {
                    'success': False,
                    'message': t(NO_SUCH_USER),
                    'errors': {
                        'username': t(INVALID_CREDENTIALS),
                        'password': t(INVALID_CREDENTIALS),
                    },
                }
        elif guestuser and username == guestuser:
            if password == guestpwd:
                is_guest = True
                maxratinglevel = '3'
                fullname = t(ANONYMOUS)
            else:
                logger.warning(
                    'Login attempt by "%s" from %s (%s) with wrong password',
                    username,
                    ipaddress,
                    hostname,
                )
                return {
                    'success': False,
                    'message': t(NO_SUCH_USER),
                    'errors': {
                        'username': t(INVALID_CREDENTIALS),
                        'password': t(INVALID_CREDENTIALS),
                    },
                }
        else:
            sasess = request.dbsession
            user = (
                sasess.query(User)
                .filter(User.email == username, User.password != NULL_PASSWORD)
                .one_or_none()
            )
            if user is None or user.state != 'C' or not user.check_password(password):
                if user is not None and user.state != 'C':  # pragma: no cover
                    logger.warning(
                        'Login attempt by not yet confirmed user "%s" from %s (%s)',
                        username,
                        ipaddress,
                        hostname,
                    )
                else:
                    logger.warning(
                        'Login attempt by "%s" from %s (%s) with wrong credentials',
                        username,
                        ipaddress,
                        hostname,
                    )

                return {
                    'success': False,
                    'message': t(NO_SUCH_USER),
                    'errors': {
                        'username': t(INVALID_CREDENTIALS),
                        'password': t(INVALID_CREDENTIALS),
                    },
                }
            else:
                user_id = user.iduser
                is_nationalliable = user.nationalliable
                is_ownersadmin = user.ownersadmin
                is_playersmanager = user.playersmanager
                first_name = user.firstname
                last_name = user.lastname
                if (
                    user.language
                    and user.language.replace('_', '-') in available_languages
                ):
                    ui_language = user.language
                maxratinglevel = user.maxratinglevel

                if first_name and last_name:
                    fullname = t(FULL_NAME).format(
                        first_name=first_name, last_name=last_name
                    )
                else:  # pragma: nocover
                    fullname = username
                user.lastlogin = naive_current_uct_timestamp()

        s = request.session
        s['user_id'] = user_id
        s['user_name'] = username
        s['is_admin'] = is_admin
        s['is_nationalliable'] = is_nationalliable
        s['is_ownersadmin'] = is_ownersadmin
        s['is_playersmanager'] = is_playersmanager
        s['is_guest'] = is_guest
        s['ui_language'] = ui_language

        def translate_name(cfg):
            copy = dict(cfg)
            copy['name'] = t(copy['name'])
            return copy

        if ui_language:
            req_language = request.accept_language.lookup(
                available_languages, default='en-GB'
            )
            reload_l10n = ui_language != req_language

            if reload_l10n:
                # Reset the Pyramid request localizer to use the preferred language
                registry = request.registry
                localizer = registry.queryUtility(ILocalizer, name=ui_language)

                if localizer is None:
                    tdirs = registry.queryUtility(ITranslationDirectories, default=[])
                    localizer = make_localizer(ui_language, tdirs)
                    registry.registerUtility(localizer, ILocalizer, name=ui_language)

                request.localizer = localizer
        else:
            reload_l10n = False

        modules = [
            MODULES[m]['classname'] for m in MODULES if not is_guest or m != 'upload'
        ]
        if is_admin:
            modules += [ADMIN_ONLY_MODULES[m]['classname'] for m in ADMIN_ONLY_MODULES]
        result = {
            'success': True,
            'fullname': fullname,
            'is_admin': is_admin,
            'is_nationalliable': is_nationalliable,
            'is_ownersadmin': is_ownersadmin,
            'is_playersmanager': is_playersmanager,
            'user_id': user_id,
            'maxratinglevel': maxratinglevel,
            'reload_l10n': reload_l10n,
            'ui_language': ui_language,
            'modules': modules,
            'shortcuts': []
            if is_guest
            else [
                translate_name(sc)
                for sc in [
                    MODULES[m]['shortcut'] for m in MODULES if 'shortcut' in MODULES[m]
                ]
            ],
            'quickstart': [
                translate_name(qs)
                for qs in [
                    MODULES[m]['quickstart']
                    for m in MODULES
                    if 'quickstart' in MODULES[m]
                ]
            ],
        }

        get_request_logger(request, logger).info('New session for %s', fullname)

        if (
            (user_id or is_admin)  # not for guest users
            and settings.get('desktop.version') != 'test'
        ):  # pragma: no check
            request.add_finished_callback(perform_backup)

        return result
    else:  # pragma: no cover
        errors = {}
        if not username:
            errors['username'] = t(MANDATORY_FIELD)
        if not password:
            errors['password'] = t(MANDATORY_FIELD)
        return {'success': False, 'message': t(MISSING_FIELDS), 'errors': errors}


@view_config(route_name='logout', renderer='json')
def logout(request):
    if request.session['user_id'] or request.session['is_admin']:  # not for guest users
        request.add_finished_callback(perform_backup)

    get_request_logger(request, logger).info('Session terminated')

    request.session.invalidate()

    return {'success': True, 'message': 'Goodbye'}


CONFIRM_MESSAGE = _("""\
Hello {firstname},

you received this message because somebody, possibly you, requested a new
account on the SoL instance at {hostname}.

If it was not you, sorry for the inconvenience: just ignore this email,
and the request won't be fulfilled and eventually trashed.

Otherwise, you have two days starting from now to visit the following link
and complete the registration form:

  {confirm_url}

Best regards and happy carromming!
""")


@view_config(route_name='signin', renderer='json', request_method='POST')
def create_new_user(request):
    settings = request.registry.settings

    if not asbool(settings.get('sol.enable_signin')):  # pragma: nocover
        raise HTTPBadRequest()

    check_csrf_token(request)

    t = translator(request)

    data = request.params

    email = data.get('email', None)
    if email:
        email = email.strip()
    firstname = data.get('firstname', None)
    if firstname:
        firstname = firstname.strip()
    lastname = data.get('lastname', None)
    if lastname:
        lastname = lastname.strip()
    password = data.get('password', None)
    language = data.get('language', None) or None

    ipaddress = request.client_addr
    try:
        host = gethostbyaddr(ipaddress)
    except Exception:
        hostname = 'unknown host'
    else:  # pragma: nocover
        hostname = host[0]

    logger.debug('Sign in attempt by "%s" from %s (%s)', email, ipaddress, hostname)

    if email and firstname and lastname and password:
        adminuser = settings.get('sol.admin.user')
        adminemail = settings.get('sol.admin.email')
        guestuser = settings.get('sol.guest.user')

        if (adminuser and email == adminuser) or (guestuser and email == guestuser):
            logger.warning(
                'Sign in attempt for reserved user "%s" from %s (%s)',
                email,
                ipaddress,
                hostname,
            )
            return {
                'success': False,
                'message': t(RESERVED_EMAIL),
                'errors': {'email': t(INVALID_EMAIL)},
            }

        sasess = request.dbsession
        user = sasess.query(User).filter(User.email == email).one_or_none()

        if user is not None:
            logger.warning(
                'Sign in attempt for already existing user "%s" from %s (%s)',
                email,
                ipaddress,
                hostname,
            )
            return {
                'success': False,
                'message': t(RESERVED_EMAIL),
                'errors': {'email': t(INVALID_EMAIL)},
            }

        user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=password,
            language=language,
        )
        sasess.add(user)
        sasess.flush()

        s = TimestampSigner(settings['sol.signer_secret_key'])
        signed_id = s.sign(str(user.iduser)).decode('ascii')
        confirm_url = request.route_url('signin', _query={'confirm': signed_id})
        body = t(CONFIRM_MESSAGE).format(
            firstname=firstname,
            hostname=request.route_url('app'),
            confirm_url=confirm_url,
        )
        message = Message(
            subject=t(_('Confirm your SoL account')),
            recipients=[email],
            bcc=[adminemail] if adminemail else None,
            body=body,
        )

        logger.info(
            'Accepted new account request "%s" from %s (%s)', email, ipaddress, hostname
        )

        try:
            request.mailer.send(message)
        except Exception:  # pragma: no cover
            logger.exception('Could not send activation link email to %s', email)
            return {'success': False, 'message': t(INTERNAL_ERROR)}

        logger.debug(
            'Sent email to %s with the activation link: %s', email, confirm_url
        )

        return {'success': True, 'message': t(_('Email sent!'))}
    else:  # pragma: no cover
        errors = {}
        if not email:
            errors['email'] = t(MANDATORY_FIELD)
        if not firstname:
            errors['firstname'] = t(MANDATORY_FIELD)
        if not lastname:
            errors['lastname'] = t(MANDATORY_FIELD)
        if not password:
            errors['password'] = t(MANDATORY_FIELD)
        return {'success': False, 'message': t(MISSING_FIELDS), 'errors': errors}


REGISTRATION_MESSAGE = _("""\
Hello again,

this to confirm that your registration has been successfully completed: you
can now access your own account at

  {login_url}

and start using SoL.

Use this email address as the “username” and provide the same password you
specified in the request.

Please consult the online documentation at

  {manual_url}

in particular the section about players management at

  {players_mgmt_url}

If you need help, or would like to register players not already present
in the database, either send an email to the administrator at the following
address

  {admin_email}

or subscribe to the very low traffic "SoL users" mailing list and ask there

  https://groups.google.com/g/sol-users

Best regards and happy carromming!
""")


@view_config(route_name='signin', request_method='GET')
def confirm_new_user(request):
    settings = request.registry.settings

    if not asbool(settings.get('sol.enable_signin')):  # pragma: nocover
        raise HTTPBadRequest()

    signed_id = request.params.get('confirm')
    if signed_id is not None:
        s = TimestampSigner(settings['sol.signer_secret_key'])
        max_age = 60 * 60 * 24 * 2  # in seconds, two days
        try:
            id = s.unsign(signed_id, max_age=max_age)
        except BadTimeSignature as e:
            logger.info('New user confirm token %r expired: %s', signed_id, e)
            raise HTTPGone()
        except BadData:
            raise HTTPBadRequest()
        else:
            id = int(id.decode('ascii'))
    else:
        raise HTTPBadRequest()

    sasess = request.dbsession
    user = sasess.get(User, id)

    if user is None or user.state != 'R':
        logger.warning(
            'New user confirm token %r is valid, but account is already'
            ' confirmed or has been deleted',
            signed_id,
        )
        raise HTTPGone()

    user.state = 'C'
    sasess.flush()

    t = translator(request)

    login_url = request.route_url('app')
    # TRANSLATORS: this is the route to the user's manual, leave it UNCHANGED
    # if the manual is NOT translated in your language!
    user_manual_path = t(_('sol:static/manual/en/index.html'))
    manual_url = request.static_url(user_manual_path)
    # TRANSLATORS: this is the anchor to the players manager section in the
    # users.html chapter, leave it UNCHANGED if the manual is NOT translated
    # in your language!
    players_mgmt_anchor = t(_('players-manager'))
    # TRANSLATORS: this is the route to the players manager section in the
    # user's manual, leave it UNCHANGED if the manual is NOT translated in
    # your language!
    players_mgmt_path = t(_('sol:static/manual/en/users.html'))
    players_mgmt_url = request.static_url(
        players_mgmt_path, _anchor=players_mgmt_anchor
    )
    admin_email = request.registry.settings.get(
        'sol.admin.email', 'lele@metapensiero.it'
    )
    body = t(REGISTRATION_MESSAGE).format(
        login_url=login_url,
        manual_url=manual_url,
        players_mgmt_url=players_mgmt_url,
        admin_email=admin_email,
    )
    message = Message(
        subject=t(_('Your new SoL account has been activated')),
        recipients=[user.email],
        body=body,
    )

    logger.info('New user account "%s" has been confirmed', user.email)

    try:
        request.mailer.send(message)
    except Exception:  # pragma: no cover
        logger.exception('Could not send confirmation email to %s', user.email)
        return {'success': False, 'message': t(INTERNAL_ERROR)}

    logger.debug('Sent confirmation email to %s', user.email)

    return HTTPFound(location=login_url)


RESET_MESSAGE = _("""\
Hello {firstname},

you received this message because somebody, possibly you, requested a
password reset of your account on the SoL instance at {hostname}.

If it was not you, sorry for the inconvenience: just ignore this email,
and the request won't be fulfilled and eventually trashed.

Otherwise, you have two days starting from now to visit the following
link to complete the procedure:

  {reset_password_url}

Best regards and happy carromming!
""")


@view_config(route_name='lost_password', renderer='json', request_method='POST')
def lost_password(request):
    settings = request.registry.settings

    if not asbool(settings.get('sol.enable_password_reset')):  # pragma: nocover
        raise HTTPBadRequest()

    check_csrf_token(request)

    t = translator(request)

    data = request.params

    email = data.get('email', None)
    if email:
        email = email.strip()

    ipaddress = request.client_addr
    try:
        host = gethostbyaddr(ipaddress)
    except Exception:
        hostname = 'unknown host'
    else:  # pragma: nocover
        hostname = host[0]

    logger.debug(
        'Password reset request by "%s" from %s (%s)', email, ipaddress, hostname
    )

    if email:
        adminuser = settings.get('sol.admin.user')
        guestuser = settings.get('sol.guest.user')

        if (adminuser and email == adminuser) or (guestuser and email == guestuser):
            logger.warning(
                'Password reset request for reserved user "%s" from %s (%s)',
                email,
                ipaddress,
                hostname,
            )
            return {
                'success': False,
                'message': t(RESERVED_EMAIL),
                'errors': {'email': t(INVALID_EMAIL)},
            }

        sasess = request.dbsession
        try:
            user = sasess.query(User).filter(User.email == email).one()
        except NoResultFound:
            logger.warning(
                'Password reset request for non existing user "%s" from %s (%s)',
                email,
                ipaddress,
                hostname,
            )
            return {
                'success': False,
                'message': t(NO_SUCH_USER),
                'errors': {'email': t(INVALID_EMAIL)},
            }
        else:
            if user.state not in ('C', 'R'):
                logger.warning(
                    'Password reset request for user "%s" in state "%s" from %s'
                    ' (%s)',
                    email,
                    user.state,
                    ipaddress,
                    hostname,
                )
                return {
                    'success': False,
                    'message': t(NO_SUCH_USER),
                    'errors': {'email': t(INVALID_EMAIL)},
                }

        s = TimestampSigner(settings['sol.signer_secret_key'])
        password = user._password
        # Should never happen, but just in case
        if isinstance(password, str):
            password = password.encode('utf-8')
        token = f'{user.iduser}-{hashlib.md5(password).hexdigest()}'
        signed_token = s.sign(token).decode('ascii')
        reset_password_url = request.route_url(
            'app', _anchor='reset_password=' + signed_token
        )
        body = t(RESET_MESSAGE).format(
            firstname=user.firstname,
            hostname=request.route_url('app'),
            reset_password_url=reset_password_url,
        )
        message = Message(
            subject=t(_('Confirm password reset for your SoL account')),
            recipients=[email],
            body=body,
        )

        logger.info(
            'Password reset request for "%s" accepted from %s (%s)',
            email,
            ipaddress,
            hostname,
        )

        try:
            request.mailer.send(message)
        except Exception:  # pragma: no cover
            logger.exception('Could not send reset password email to %s', email)
            return {'success': False, 'message': t(INTERNAL_ERROR)}

        logger.debug(
            'Sent email to %s with the password reset link: %s',
            email,
            reset_password_url,
        )

        return {'success': True, 'message': t(_('Email sent!'))}
    else:  # pragma: no cover
        return {
            'success': False,
            'message': t(MISSING_FIELDS),
            'errors': {'email': t(MANDATORY_FIELD)},
        }


@view_config(route_name='reset_password', renderer='json', request_method='POST')
def reset_password(request):
    settings = request.registry.settings

    if not asbool(settings.get('sol.enable_password_reset')):  # pragma: nocover
        raise HTTPBadRequest()

    signed_token = request.params.get('token')
    password = request.params.get('password')

    if signed_token is not None and password is not None:
        s = TimestampSigner(settings['sol.signer_secret_key'])
        max_age = 60 * 60 * 24 * 2  # in seconds, two days
        try:
            token = s.unsign(signed_token, max_age=max_age)
        except BadTimeSignature as e:
            logger.warning('Password reset token %r expired: %s', signed_token, e)
            raise HTTPGone()
        except BadData:
            raise HTTPBadRequest()
        else:
            id, oldpwhash = token.decode('ascii').split('-', 1)
            id = int(id)
    else:
        raise HTTPBadRequest()

    sasess = request.dbsession
    user = sasess.get(User, id)

    if user is None:  # pragma: no cover
        logger.warning(
            'Password reset token %r is valid, but user has been deleted', id
        )
        raise HTTPGone()

    if user.state not in ('C', 'R'):  # pragma: no cover
        logger.warning(
            'Password reset for "%s" rejected, user state is "%s"',
            user.email,
            user.state,
        )
        raise HTTPBadRequest()

    oldpassword = user._password
    # Should never happen, but just in case
    if isinstance(oldpassword, str):
        oldpassword = oldpassword.encode('utf-8')
    if hashlib.md5(oldpassword).hexdigest() != oldpwhash:
        logger.warning(
            'Password reset for "%s" rejected, old password does not match', user.email
        )
        raise HTTPBadRequest()

    user.password = password
    user.state = 'C'
    sasess.flush()

    return {'success': True, 'location': request.route_url('app')}


@view_config(route_name='change_language', renderer='json', request_method='POST')
def change_language(request):
    from sol.i18n import available_languages

    user_id = request.session.get('user_id')
    language = request.params.get('language') or None
    if user_id is not None and (
        language is None or language.replace('_', '-') in available_languages
    ):
        sasess = request.dbsession
        user = sasess.get(User, user_id)
        user.language = language
        sasess.flush()

        logger.info('Language for "%s" set to "%s"', user.email, language)

        return {
            'success': True,
        }
    else:
        raise HTTPBadRequest()


@view_config(route_name='change_password', renderer='json', request_method='POST')
def change_password(request):
    user_id = request.session.get('user_id')
    oldpassword = request.params.get('oldpassword')
    newpassword = request.params.get('newpassword')

    if user_id is not None and oldpassword is not None and newpassword is not None:
        sasess = request.dbsession
        user = sasess.get(User, user_id)
        if user.check_password(oldpassword):
            user.password = newpassword
            sasess.flush()

            logger.info('Password reset for "%s" completed', user.email)

            return {
                'success': True,
            }
        else:
            t = translator(request)
            return {
                'success': False,
                'message': t(INVALID_OLD_PASSWORD),
                'errors': {'oldpassword': t(OLD_PASSWORD_DOES_NOT_MATCH)},
            }
    else:
        raise HTTPBadRequest()
