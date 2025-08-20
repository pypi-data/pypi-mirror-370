# -*- coding: utf-8 -*-
# :Project:   SoL -- Auth views tests
# :Created:   gio 12 lug 2018 10:22:16 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018-2020, 2022, 2024 Lele Gaifax
#

import re

import pytest

from itsdangerous import TimestampSigner
from pyramid_mailer import get_mailer
from webtest.app import AppError

from sol.models import User


def test_no_input(app):
    payload = {}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is False
    assert result['message'] == 'Missing fields'
    assert set(result['errors']) == {'username', 'password'}


def test_admin(app):
    payload = {'username': 'admin', 'password': 'admin'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is True
    assert result['fullname'] == 'Administrator'
    assert result['is_admin'] is True
    assert result['is_ownersadmin'] is True
    assert result['is_playersmanager'] is True


def test_admin_bad_password(app):
    payload = {'username': 'admin', 'password': 'badpassword'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert set(result['errors']) == {'username', 'password'}


def test_guest(app):
    payload = {'username': 'guest', 'password': 'guest'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is True
    assert result['fullname'] == 'Anonymous'
    assert result['is_admin'] is False
    assert result['is_ownersadmin'] is False
    assert result['is_playersmanager'] is False


def test_guest_bad_password(app):
    payload = {'username': 'guest', 'password': 'badpassword'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert set(result['errors']) == {'username', 'password'}


def test_lele(app):
    payload = {'username': 'lele@metapensiero.it', 'password': 'lelegaifax'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is True
    assert result['fullname'] == 'Lele Gaifax'
    assert result['is_admin'] is False
    assert result['is_ownersadmin'] is False
    assert result['is_playersmanager'] is True


def test_lele_bad_password(app):
    payload = {'username': 'lele@metapensiero.it', 'password': 'badpassword'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert set(result['errors']) == {'username', 'password'}


def test_unknown(app):
    payload = {'username': 'nobody', 'password': 'anypassword'}
    response = app.post_route(payload, 'login')
    result = response.json

    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert set(result['errors']) == {'username', 'password'}


def test_signin_no_csrf_token(app):
    payload = {}
    with pytest.raises(AppError) as e:
        app.post_route(payload, 'signin')
    assert '400 Bad CSRF Token' in str(e.value)


def test_signin_no_input(anonymous_user):
    payload = {'csrf_token': anonymous_user.csrf_token}
    response = anonymous_user.post_route(payload, 'signin')
    result = response.json

    assert result['success'] is False
    assert result['message'] == 'Missing fields'
    assert set(result['errors']) == {'email', 'firstname', 'lastname', 'password'}


@pytest.mark.parametrize('email', ('admin', 'guest', 'lele@metapensiero.it'))
def test_signin_reserved_email(anonymous_user, email):
    payload = {
        'email': email,
        'firstname': 'foo',
        'lastname': 'bar',
        'password': '123456',
        'csrf_token': anonymous_user.csrf_token,
    }
    response = anonymous_user.post_route(payload, 'signin')
    result = response.json

    assert result['success'] is False
    assert result['message'] == 'Invalid email address'
    assert set(result['errors']) == {'email'}


def test_signin(anonymous_user, session):
    payload = {
        'email': 'lele@example.com',
        'firstname': 'Lele',
        'lastname': 'Gaifax',
        'password': '123456',
        'csrf_token': anonymous_user.csrf_token,
    }
    response = anonymous_user.post_route(payload, 'signin')
    result = response.json

    assert result['success'] is True
    assert result['message'] == 'Email sent!'

    user = session.query(User).filter_by(email='lele@example.com').one()
    assert user.firstname == 'Lele'
    assert user.lastname == 'Gaifax'
    assert user.state == 'R'

    registry = anonymous_user.app.registry
    mailer = get_mailer(registry)
    outbox = mailer.outbox
    assert len(outbox) == 1

    sentmail = outbox[0]
    assert sentmail.subject == 'Confirm your SoL account'
    assert 'lele@example.com' in sentmail.send_to
    assert 'test@example.com' in sentmail.send_to
    assert 'Hello Lele' in sentmail.body

    match = re.search(r'signin\?confirm=(.*)', sentmail.body)
    assert match is not None

    token = match.group(1)
    response = anonymous_user.get_route('signin', _query={'confirm': token})
    assert response.status_code == 302
    assert response.location == 'http://localhost/'

    session.expunge_all()
    user = session.query(User).filter_by(email='lele@example.com').one()
    assert user.firstname == 'Lele'
    assert user.lastname == 'Gaifax'
    assert user.state == 'C'

    assert len(outbox) == 2
    sentmail = outbox[1]
    assert sentmail.subject == 'Your new SoL account has been activated'
    assert 'lele@example.com' in sentmail.send_to
    assert 'Hello again' in sentmail.body

    # Retrying should give an error
    with pytest.raises(AppError) as e:
        anonymous_user.get_route('signin', _query={'confirm': token})
    assert '410 Gone' in str(e.value)


def test_signin_no_token(app):
    with pytest.raises(AppError):
        app.get_route('signin')


def test_signin_bad_token(app):
    with pytest.raises(AppError):
        app.get_route('signin', _query={'confirm': 'foo'})


def test_signin_expired_token(app):
    s = TimestampSigner(app.app.registry.settings['sol.signer_secret_key'])
    s.get_timestamp = lambda: 200000000
    token = s.sign('1').decode('ascii')
    with pytest.raises(AppError) as e:
        app.get_route('signin', _query={'confirm': token})
    assert '410 Gone' in str(e.value)


def test_signin_bad_user_id(app):
    s = TimestampSigner(app.app.registry.settings['sol.signer_secret_key'])
    token = s.sign('0').decode('ascii')
    with pytest.raises(AppError) as e:
        app.get_route('signin', _query={'confirm': token})
    assert '410 Gone' in str(e.value)


def test_change_password_anonymous(app):
    with pytest.raises(AppError) as e:
        app.post_route({}, 'change_password')
    assert '401 Unauthorized' in str(e.value)


def test_change_password_admin(admin_user):
    with pytest.raises(AppError) as e:
        admin_user.post_route({}, 'change_password')
    assert '400 Bad Request' in str(e.value)


def test_change_password_guest(guest_user):
    with pytest.raises(AppError) as e:
        guest_user.post_route({}, 'change_password')
    assert '400 Bad Request' in str(e.value)


def test_change_password(app, lele_user):
    payload = {'oldpassword': 'badpwd', 'newpassword': 'newpwd'}
    response = lele_user.post_route(payload, 'change_password')
    result = response.json
    assert result['success'] is False
    assert result['errors']['oldpassword']

    payload = {'oldpassword': 'lelegaifax', 'newpassword': 'lelegaifax'}
    response = lele_user.post_route(payload, 'change_password')
    result = response.json
    assert result['success'] is True

    payload = {'oldpassword': 'lelegaifax', 'newpassword': 'ßŧ¶æñŋ€'}
    response = lele_user.post_route(payload, 'change_password')
    result = response.json
    assert result['success'] is True

    payload = {'username': 'lele@metapensiero.it', 'password': 'lelegaifax'}
    response = app.post_route(payload, 'login')
    result = response.json
    assert result['success'] is False

    payload = {'username': 'lele@metapensiero.it', 'password': 'ßŧ¶æñŋ€'}
    response = app.post_route(payload, 'login')
    result = response.json
    assert result['success'] is True

    payload = {'oldpassword': 'ßŧ¶æñŋ€', 'newpassword': 'lelegaifax'}
    response = lele_user.post_route(payload, 'change_password')
    result = response.json
    assert result['success'] is True


def test_lost_password_no_csrf_token(app):
    payload = {}
    with pytest.raises(AppError) as e:
        app.post_route(payload, 'lost_password')
    assert '400 Bad CSRF Token' in str(e.value)


def test_lost_password_no_input(anonymous_user):
    payload = {'csrf_token': anonymous_user.csrf_token}
    response = anonymous_user.post_route(payload, 'lost_password')
    result = response.json

    assert result['success'] is False
    assert result['message'] == 'Missing fields'
    assert tuple(result['errors'].keys()) == ('email',)


def test_lost_password_unknown_user(anonymous_user):
    payload = {'email': 'no_such@user.com', 'csrf_token': anonymous_user.csrf_token}
    response = anonymous_user.post_route(payload, 'lost_password')
    result = response.json

    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert tuple(result['errors'].keys()) == ('email',)


def test_reset_password_no_input(anonymous_user):
    payload = {'csrf_token': anonymous_user.csrf_token}
    with pytest.raises(AppError) as e:
        anonymous_user.post_route(payload, 'reset_password')
    assert '400 Bad Request' in str(e.value)


def test_reset_password_bad_token(app):
    with pytest.raises(AppError) as e:
        app.post_route({'token': 'foo', 'password': 'bar'}, 'reset_password')
    assert '400 Bad Request' in str(e.value)


@pytest.mark.parametrize('email', ('admin', 'guest'))
def test_lost_password_reserved_email(anonymous_user, email):
    payload = {'email': email, 'csrf_token': anonymous_user.csrf_token}
    response = anonymous_user.post_route(payload, 'lost_password')
    result = response.json

    assert result['success'] is False
    assert result['message'] == 'Invalid email address'
    assert tuple(result['errors'].keys()) == ('email',)


def test_lost_password_suspended_user(anonymous_user, user_suspended):
    payload = {'email': user_suspended.email, 'csrf_token': anonymous_user.csrf_token}
    response = anonymous_user.post_route(payload, 'lost_password')
    result = response.json
    assert result['success'] is False
    assert (
        result['message']
        == 'The inserted user and password, or one of the two, are wrong!'
    )
    assert tuple(result['errors'].keys()) == ('email',)


def test_reset_password_expired_token(anonymous_user):
    s = TimestampSigner(anonymous_user.app.registry.settings['sol.signer_secret_key'])
    s.get_timestamp = lambda: 200000000
    token = s.sign('1').decode('ascii')
    with pytest.raises(AppError) as e:
        anonymous_user.post_route(
            {'token': token, 'password': '123123'}, 'reset_password'
        )
    assert '410 Gone' in str(e.value)


def test_reset_password(anonymous_user, session):
    payload = {
        'email': 'lele@metapensiero.it',
        'password': '123456',
        'csrf_token': anonymous_user.csrf_token,
    }
    response = anonymous_user.post_route(payload, 'lost_password')
    result = response.json

    assert result['success'] is True
    assert result['message'] == 'Email sent!'

    registry = anonymous_user.app.registry
    mailer = get_mailer(registry)
    outbox = mailer.outbox
    assert len(outbox) == 1

    sentmail = outbox[0]
    assert sentmail.subject == 'Confirm password reset for your SoL account'
    assert 'lele@metapensiero.it' in sentmail.send_to
    assert 'Hello Lele' in sentmail.body

    match = re.search(r'reset_password=(.*)', sentmail.body)
    assert match is not None

    user = None
    payload = {'token': match.group(1), 'password': '123234'}
    try:
        response = anonymous_user.post_route(payload, 'reset_password')
        result = response.json
        assert result['success'] is True
        assert result['location'] == 'http://localhost/'

        session.expunge_all()
        user = session.query(User).filter_by(email='lele@metapensiero.it').one()
        assert user.check_password('123234') is True
    finally:
        if user is not None:
            user.password = 'lelegaifax'
            session.commit()

    # Retrying should give an error
    with pytest.raises(AppError) as e:
        anonymous_user.post_route(payload, 'reset_password')
    assert '400 Bad Request' in str(e.value)


def test_change_language(session, lele_user):
    payload = {'language': 'unknown'}
    with pytest.raises(AppError) as e:
        lele_user.post_route(payload, 'change_language')
    assert '400 Bad Request' in str(e.value)

    payload = {'language': ''}
    response = lele_user.post_route(payload, 'change_language')
    result = response.json
    assert result['success'] is True
    session.expunge_all()
    user = session.query(User).filter_by(email='lele@metapensiero.it').one()
    assert user.language is None

    payload = {'language': 'it'}
    response = lele_user.post_route(payload, 'change_language')
    result = response.json
    assert result['success'] is True
    session.expunge_all()
    user = session.query(User).filter_by(email='lele@metapensiero.it').one()
    assert user.language == 'it'
