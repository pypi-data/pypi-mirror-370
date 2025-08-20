# -*- coding: utf-8 -*-
# :Project:   SoL -- Data controller
# :Created:   mer 15 ott 2008 08:25:21 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008-2010, 2013-2016, 2018-2024 Lele Gaifax
#

from __future__ import annotations

import logging

from metapensiero.sqlalchemy.proxy.filters import Operator
from metapensiero.sqlalchemy.proxy.filters import extract_filters
from metapensiero.sqlalchemy.proxy.pyramid import expose
from pyramid.view import view_config
from sqlalchemy import and_
from sqlalchemy import bindparam
from sqlalchemy import distinct
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import load_only

from ..i18n import countries_names
from ..i18n import language_name
from ..i18n import languages_names
from ..i18n import translatable_string as _
from ..i18n import translator
from ..models import Championship
from ..models import Club
from ..models import Competitor
from ..models import Match
from ..models import Player
from ..models import Rate
from ..models import Rating
from ..models import Tourney
from ..models import User
from ..models.club import clubusers as _clubusers_t
from . import unauthorized_for_guest

logger = logging.getLogger(__name__)

_championships_t = Championship.__table__
_clubs_t = Club.__table__
_competitors_t = Competitor.__table__
_matches_t = Match.__table__
_ratings_t = Rating.__table__
_tourneys_t = Tourney.__table__
_users_t = User.__table__


def add_owner(request, results):
    t = translator(request)

    if 'metadata' in results:
        fields = results['metadata']['fields']
        # The proxy may be called with "only_cols", so check for the presence of the 'idowner'
        # field
        for field in fields:
            if field['name'] == 'idowner':
                fields.append(
                    {
                        'label': t(_('Owner')),
                        'hint': t(
                            _(
                                'The user responsible for the record,'
                                ' who can modify or delete it.'
                            )
                        ),
                        'name': 'Owner',
                        'hidden': True,
                        'nullable': True,
                        'readonly': not request.session['is_ownersadmin'],
                        'sortable': False,
                        'lookup': dict(
                            url='/data/owners',
                            lookupField='idowner',
                            idField='iduser',
                            displayField='Fullname',
                        ),
                    }
                )
                break
    else:
        uids = set()
        s = request.dbsession
        no_owners = False
        for r in results['root']:
            try:
                idowner = r['idowner']
            except KeyError:
                # The proxy has been called with "only_cols", probably by a lookup combo
                no_owners = True
                break
            if idowner is not None:
                uids.add(idowner)

        if not no_owners:
            caption_by_userid = {
                u.iduser: u.caption(html=False)
                for u in s.query(User)
                .options(
                    load_only(
                        User.iduser,
                        User.firstname,
                        User.lastname,
                        User.email,
                        User.state,
                    )
                )
                .filter(User.iduser.in_(uids))
            }
            admin_email = request.registry.settings.get('sol.admin.email', '')
            if admin_email:
                admin_email = f' \N{E-MAIL SYMBOL} {admin_email}'
            caption_by_userid[None] = t(_('Administrator')) + admin_email
            for r in results['root']:
                r['Owner'] = caption_by_userid[r['idowner']]
    return results


def replace_ratings_description(request, results):
    if 'root' in results and results['root'] and 'idrating' in results['root'][0]:
        recs = results['root']
        t = translator(request)
        levels = {
            '1': _('International'),
            '2': _('National'),
            '3': _('Regional'),
            '4': _('Courtyard'),
        }
        rids = set()
        for rec in recs:
            if rec['idrating'] is not None:
                rids.add(rec['idrating'])
        q = (
            select(
                _ratings_t.c.idrating,
                _ratings_t.c.description,
                _ratings_t.c.level,
                _clubs_t.c.description.label('Club'),
            )
            .select_from(
                _ratings_t.outerjoin(_clubs_t, _ratings_t.c.idclub == _clubs_t.c.idclub)
            )
            .where(_ratings_t.c.idrating.in_(rids))
        )
        captions = {}
        t = translator(request)
        for rating in request.dbsession.execute(q):
            club = (' (%s)' % rating.Club) if rating.Club else ''
            captions[rating.idrating] = '%s-%s: %s%s' % (
                rating.level,
                t(levels[rating.level]),
                rating.description,
                club,
            )
        for rec in recs:
            if rec['idrating'] is not None:
                rec['Rating'] = captions[rec['idrating']]
    return results


@view_config(route_name='clubs', renderer='json')
@expose(
    select(
        _clubs_t,
        select(func.count(_championships_t.c.idchampionship))
        .where(_championships_t.c.idclub == _clubs_t.c.idclub)
        .scalar_subquery()
        .label('Championships'),
        select(_ratings_t.c.description)
        .where(_ratings_t.c.idrating == _clubs_t.c.idrating)
        .scalar_subquery()
        .label('Rating'),
    ),
    metadata=dict(
        description=dict(flex=1, vtype='nonempty'),
        emblem=dict(hidden=True, width=130),
        nationality=dict(width=120),
        prizes=dict(hidden=True, width=180),
        couplings=dict(hidden=True, width=180),
        siteurl=dict(hidden=True, width=250, vtype='url'),
        email=dict(hidden=True, vtype='email'),
        isfederation=dict(nullable=True),
        Championships=dict(
            label=_('Championships'),
            hint=_('Number of championships organized by the club.'),
            width=40,
            readonly=True,
            sortable=False,
        ),
        Rating=dict(
            label=_('Rating'),
            hint=_("Rating this club's championships will use by default, if any."),
            hidden=True,
            nullable=True,
            lookup=dict(
                url='/data/ratingsLookup',
                idField='idrating',
                displayField='description',
            ),
        ),
    ),
)
def clubs():
    request, args = yield

    if 'filter_by_idowner' in args:
        # If user is not the admin, then give him just the clubs he owns OR those
        # explicitly associated with him

        if request.session['is_guest']:
            conditions = (_clubs_t.c.idclub == None,)
            results = yield args, conditions
        elif not request.session['is_admin']:
            from ..models.club import clubusers

            idowner = args.pop('filter_by_idowner')
            cu_t = clubusers.alias('cu')
            conditions = (
                or_(
                    _clubs_t.c.idowner == idowner,
                    exists().where(
                        and_(
                            cu_t.c.idclub == _clubs_t.c.idclub, cu_t.c.iduser == idowner
                        )
                    ),
                ),
            )
            results = yield args, conditions
        else:
            results = yield args
    else:
        results = yield args

    replace_ratings_description(request, results)
    yield add_owner(request, results)


@view_config(route_name='clubs_lookup', renderer='json')
@expose(
    select(_clubs_t.c.idclub, _clubs_t.c.description, _clubs_t.c.nationality).order_by(
        _clubs_t.c.nationality, _clubs_t.c.description
    )
)
def clubsLookup():
    request, args = yield

    # If user is not the admin, then give him just the clubs he owns OR those
    # explicitly associated with him

    if request.session['is_guest']:
        conditions = (_clubs_t.c.idclub == None,)
        results = yield args, conditions
    elif (
        not request.session['is_admin']
        and request.session['is_nationalliable'] != 'wrl'
    ):
        from ..models.club import clubusers

        cu_t = clubusers.alias('cu')
        if request.session['is_nationalliable']:
            conditions = (
                or_(
                    _clubs_t.c.idowner == request.session['user_id'],
                    _clubs_t.c.nationality == request.session['is_nationalliable'],
                    exists().where(
                        and_(
                            cu_t.c.idclub == _clubs_t.c.idclub,
                            cu_t.c.iduser == request.session['user_id'],
                        )
                    ),
                ),
            )
        else:
            conditions = (
                or_(
                    _clubs_t.c.idowner == request.session['user_id'],
                    exists().where(
                        and_(
                            cu_t.c.idclub == _clubs_t.c.idclub,
                            cu_t.c.iduser == request.session['user_id'],
                        )
                    ),
                ),
            )
        results = yield args, conditions
    else:
        results = yield args
    yield results


@view_config(route_name='club_users', renderer='json')
@unauthorized_for_guest
@expose(
    select(
        _users_t.c.iduser,
        _users_t.c.lastname,
        _users_t.c.firstname,
        _users_t.c.email,
        exists(
            select(1)
            .where(_clubusers_t.c.idclub == bindparam('idclub'))
            .where(_clubusers_t.c.iduser == _users_t.c.iduser)
        ).label('associated'),
    )
    .where(_users_t.c.state == 'C')
    .where(
        _users_t.c.iduser
        != (
            select(_clubs_t.c.idowner)
            .where(_clubs_t.c.idclub == bindparam('idclub'))
            .scalar_subquery()
        )
    ),
    metadata=dict(
        email=dict(flex=1, readonly=True),
        lastname=dict(flex=1, readonly=True),
        firstname=dict(flex=1, readonly=True),
        associated=dict(
            label=_('Associated'),
            hint=_('Whether the user is associated with the club.'),
            type='boolean',
        ),
    ),
)
def clubUsers():
    request, args = yield
    bindparams = args.setdefault('params', {})
    bindparams['idclub'] = int(args.pop('idclub', 0))
    result = yield args
    yield result


@view_config(route_name='club_users', request_method='POST', renderer='json')
@unauthorized_for_guest
def saveClubUsers(request):
    from metapensiero.sqlalchemy.proxy.json import JSON
    from sqlalchemy.exc import DBAPIError

    from ..models.bio import changes_logger
    from ..models.utils import njoin
    from . import get_request_logger

    t = translator(request)
    rlogger = get_request_logger(request, logger)
    params = request.params
    idclub = int(params['idclub'])
    mr = JSON.decode(params['modified_records'])

    sess = request.dbsession
    club = sess.get(Club, idclub)
    if club is None:
        rlogger.warning('Club %d does not exist', idclub)
        return dict(success=False, message=t(_('Specified club does not exist!')))
    elif (
        not request.session['is_admin']
        and request.session.get('user_id') != club.idowner
    ):
        rlogger.warning('Attempt to change not owned club %r', club)
        return dict(success=False, message=t(_('Unauthorized attempt to change club!')))

    users = club.users
    if users:
        before = njoin(
            (f'{u.lastname} {u.firstname} <{u.email}>' for u in users), localized=False
        )
    else:
        before = 'none'
    add_uids = set()
    del_uids = set()
    for key, data in mr:
        if key != 'iduser':  # pragma: no cover
            return dict(success=False, message=t(_('Invalid data!')))
        iduser = data.get('iduser')
        if iduser is None:  # pragma: no cover
            return dict(success=False, message=t(_('Invalid data!')))
        associated = data.get('associated')
        if associated is None:  # pragma: no cover
            return dict(success=False, message=t(_('Invalid data!')))
        if associated:
            add_uids.add(iduser)
        else:
            del_uids.add(iduser)

    if add_uids or del_uids:
        if del_uids:
            club.users = [u for u in users if u.iduser not in del_uids]
        if add_uids:
            for uid in add_uids:
                user = sess.get(User, uid)
                if user is None:
                    return dict(
                        success=False, message=t(_('Specified user does not exist!'))
                    )
                users.append(user)

    success = False
    try:
        sess.flush()
        success = True
        message = 'Ok'
        if users:
            after = njoin(
                (f'{u.lastname} {u.firstname} <{u.email}>' for u in club.users),
                localized=False,
            )
        else:  # pragma: no cover
            after = 'none'
        get_request_logger(request, changes_logger).info(
            'Updated %r: changed associated users from %s to %s', club, before, after
        )
        rlogger.info('Changes to %r successfully committed', club)
    except DBAPIError as e:  # pragma: no cover
        rlogger.error('Could not save changes: %s', e)
        message = t(_('Error occurred while saving changes!'))
        message += '<br/>'
        message += t(_('Please inform the admin or consult the application log.'))
    except Exception as e:  # pragma: no cover
        rlogger.critical('Could not save changes: %s', e, exc_info=True)
        message = t(_('Internal error!'))
        message += '<br/>'
        message += t(_('Please inform the admin or consult the application log.'))

    return dict(success=success, message=message)


_federations_t = _clubs_t.alias()


@view_config(route_name='federations', renderer='json')
@expose(
    select(
        _federations_t.c.idclub,
        _federations_t.c.description,
        _federations_t.c.nationality,
    ).where(_federations_t.c.isfederation == True)
)
def federations(request, results):
    return results


_players_t = Player.__table__.alias('p')
_countplayed = (
    select(func.count(_tourneys_t.c.idtourney))
    .where(
        and_(
            or_(
                bindparam('played4club') == None,
                _championships_t.c.idclub == bindparam('played4club'),
            ),
            or_(
                _competitors_t.c.idplayer1 == _players_t.c.idplayer,
                _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                _competitors_t.c.idplayer4 == _players_t.c.idplayer,
            ),
        )
    )
    .select_from(_competitors_t.join(_tourneys_t).join(_championships_t))
)
_firstplayed = (
    select(func.min(_tourneys_t.c.date))
    .where(
        and_(
            or_(
                bindparam('played4club') == None,
                _championships_t.c.idclub == bindparam('played4club'),
            ),
            or_(
                _competitors_t.c.idplayer1 == _players_t.c.idplayer,
                _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                _competitors_t.c.idplayer4 == _players_t.c.idplayer,
            ),
        )
    )
    .select_from(_competitors_t.join(_tourneys_t).join(_championships_t))
)
_lastplayed = (
    select(func.max(_tourneys_t.c.date))
    .where(
        and_(
            or_(
                bindparam('played4club') == None,
                _championships_t.c.idclub == bindparam('played4club'),
            ),
            or_(
                _competitors_t.c.idplayer1 == _players_t.c.idplayer,
                _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                _competitors_t.c.idplayer4 == _players_t.c.idplayer,
            ),
        )
    )
    .select_from(_competitors_t.join(_tourneys_t).join(_championships_t))
)
_players_metadata = dict(
    firstname=dict(flex=1, vtype='nonempty'),
    lastname=dict(flex=1, vtype='nonempty'),
    nickname=dict(hidden=True, nullable=True),
    password=dict(hidden=True, password=True, width=40, nullable=True),
    sex=dict(hidden=True, width=80),
    nationality=dict(width=120),
    language=dict(hidden=True, width=120),
    citizenship=dict(hidden=True, nullable=True),
    agreedprivacy=dict(hidden=True),
    birthdate=dict(hidden=True),
    email=dict(hidden=True, vtype='email'),
    portrait=dict(hidden=True, width=130),
    ownersadmin=dict(hidden=True, nullable=True),
    playersmanager=dict(hidden=True, nullable=True),
    Club=dict(
        label=_('Club'),
        hint=_('The club this player is affiliated with.'),
        flex=1,
        nullable=True,
        lookup=dict(
            url='/data/clubsLookup',
            idField='idclub',
            displayField='description',
            otherFields='nationality',
            pageSize=12,
            innerTpl=(
                '<div class="sol-flags-icon sol-flag-{nationality}"'
                ' data-qtip="'
                '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                '">{description}'
                '</div>'
            ),
        ),
    ),
    Federation=dict(
        label=_('Federation'),
        hint=_('The federation this player is associated with.'),
        hidden=True,
        nullable=True,
        lookup=dict(
            url='/data/federations?sort_by_description=ASC',
            idField='idclub',
            lookupField='idfederation',
            displayField='description',
            otherFields='nationality',
            innerTpl=(
                '<div class="sol-flags-icon sol-flag-{nationality}"'
                ' data-qtip="'
                '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                '">{description}'
                '</div>'
            ),
        ),
    ),
    CountPlayed=dict(
        label=_('Tourneys'),
        hint=_('Number of played tourneys.'),
        hidden=True,
        readonly=True,
    ),
    FirstPlayed=dict(
        label=_('First tourney'),
        hint=_('Oldest participation.'),
        hidden=True,
        readonly=True,
    ),
    LastPlayed=dict(
        label=_('Last tourney'),
        hint=_('Most recent participation.'),
        hidden=True,
        readonly=True,
    ),
)


@view_config(route_name='players', renderer='json')
@expose(
    select(
        _players_t,
        _clubs_t.c.description.label('Club'),
        _federations_t.c.description.label('Federation'),
        _countplayed.scalar_subquery().label('CountPlayed'),
        _firstplayed.scalar_subquery().label('FirstPlayed'),
        _lastplayed.scalar_subquery().label('LastPlayed'),
    ).select_from(
        _players_t.outerjoin(
            _clubs_t, _clubs_t.c.idclub == _players_t.c.idclub
        ).outerjoin(
            _federations_t, _federations_t.c.idclub == _players_t.c.idfederation
        )
    ),
    metadata=_players_metadata,
)
def players():
    request, args = yield

    bindparams = args.setdefault('params', {})

    played_for_club_id = args.get('played4club', None)
    if played_for_club_id is not None:
        bindparams['played4club'] = int(played_for_club_id)
    else:
        bindparams['played4club'] = None

    if 'metadata' in args:
        results = yield args
        t = translator(request)
        results['metadata']['fields'].append(
            {
                'label': t(_('Language')),
                'hint': t(
                    _(
                        'The preferred language of the player, used to send email messages.'
                    )
                ),
                'name': 'Language',
                'hidden': True,
                'nullable': True,
                'lookup': dict(
                    url='/data/languages',
                    remoteFilter=False,
                    lookupField='language',
                    idField='code',
                    displayField='name',
                ),
            }
        )
    else:
        if played_for_club_id is not None:
            conditions = (
                exists().where(
                    and_(
                        _tourneys_t.c.idchampionship
                        == _championships_t.c.idchampionship,
                        _championships_t.c.idclub == int(played_for_club_id),
                        _tourneys_t.c.idtourney == _competitors_t.c.idtourney,
                        or_(
                            _competitors_t.c.idplayer1 == _players_t.c.idplayer,
                            _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                            _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                            _competitors_t.c.idplayer4 == _players_t.c.idplayer,
                        ),
                    )
                ),
            )
            results = yield args, conditions
        else:
            # If there is a single filter on either the first name or the last name transform
            # it in an expression that checks for the presence of the search term in either one
            # of those fields
            if 'filter' in args:
                # Save it, as extract_filter() removes them from the dictionary
                old_args = dict(args)
                filters = extract_filters(args)
                if (
                    len(filters) == 1
                    and filters[0].property in {'firstname', 'lastname'}
                    and filters[0].operator == Operator.CONTAINS
                ):
                    op = filters[0].operator
                    value = filters[0].value
                    conditions = or_(
                        op.filter(_players_t.c.firstname, value),
                        op.filter(_players_t.c.lastname, value),
                    )
                    results = yield args, (conditions,)
                else:
                    results = yield old_args
            else:
                results = yield args
        for r in results['root']:
            code = r['language']
            if code:
                r['Language'] = language_name(code)
    yield add_owner(request, results)


_pdup_t = _players_t.alias('pdup')


@view_config(route_name='players', renderer='json', request_param='dups')
@expose(
    select(
        _players_t,
        _clubs_t.c.description.label('Club'),
        _countplayed.scalar_subquery().label('CountPlayed'),
        _firstplayed.scalar_subquery().label('FirstPlayed'),
        _lastplayed.scalar_subquery().label('LastPlayed'),
    )
    .select_from(
        _players_t.outerjoin(_clubs_t, _clubs_t.c.idclub == _players_t.c.idclub)
    )
    .where(
        exists().where(
            and_(
                _players_t.c.idplayer != _pdup_t.c.idplayer,
                or_(
                    _players_t.c.sex == None,
                    _pdup_t.c.sex == None,
                    _players_t.c.sex == _pdup_t.c.sex,
                ),
                or_(
                    and_(
                        func.soundex(_players_t.c.firstname)
                        == func.soundex(_pdup_t.c.firstname),
                        func.soundex(_players_t.c.lastname)
                        == func.soundex(_pdup_t.c.lastname),
                    ),
                    and_(
                        func.soundex(_players_t.c.firstname)
                        == func.soundex(_pdup_t.c.lastname),
                        func.soundex(_players_t.c.lastname)
                        == func.soundex(_pdup_t.c.firstname),
                    ),
                ),
            )
        )
    ),
    metadata=_players_metadata,
)
def duplicatedPlayers():
    request, args = yield

    bindparams = args.setdefault('params', {})

    played_for_club_id = args.get('played4club', None)
    if played_for_club_id is not None:  # pragma: no cover
        bindparams['played4club'] = int(played_for_club_id)
    else:
        bindparams['played4club'] = None

    results = yield args

    yield add_owner(request, results)


@view_config(route_name='owners', renderer='json')
@unauthorized_for_guest
@expose(
    select(
        _users_t.c.iduser, _users_t.c.email, _users_t.c.lastname, _users_t.c.firstname
    ).where(and_(_users_t.c.state == 'C'))
)
def owners(request, results):
    from operator import itemgetter

    t = translator(request)
    if 'metadata' in results:
        results['metadata']['fields'] = [
            f for f in results['metadata']['fields'] if f['name'] == 'iduser'
        ]
        results['metadata']['fields'].append(
            {
                'label': t(_('Owner')),
                'hint': t(_('The fullname of the responsible user.')),
                'name': 'Fullname',
            }
        )
    else:
        owners = results['root']
        for owner in owners:
            email = owner.pop('email')
            firstname = owner.pop('firstname')
            lastname = owner.pop('lastname')
            owner['Fullname'] = f'{lastname} {firstname} \N{E-MAIL SYMBOL} {email}'
        admin_email = request.registry.settings.get('sol.admin.email', '')
        if admin_email:
            admin_email = f' \N{E-MAIL SYMBOL} {admin_email}'
        owners.append(
            {
                'iduser': None,
                'Fullname': t(_('Administrator')) + admin_email,
            }
        )
        owners.sort(key=itemgetter('Fullname'))
        results['count'] = results['count'] + 1
    return results


@view_config(route_name='users', renderer='json')
@unauthorized_for_guest
@expose(
    select(
        _users_t.c.iduser,
        _users_t.c.email,
        _users_t.c.lastname,
        _users_t.c.firstname,
        _users_t.c.created,
        _users_t.c.lastlogin,
        _users_t.c.password,
        _users_t.c.language,
        _users_t.c.nationalliable,
        _users_t.c.ownersadmin,
        _users_t.c.playersmanager,
        _users_t.c.maxratinglevel,
        _users_t.c.state,
    ),
    metadata=dict(
        email=dict(flex=1, vtype='email'),
        firstname=dict(flex=1, vtype='nonempty'),
        lastname=dict(flex=1, vtype='nonempty'),
        password=dict(hidden=True, password=True, width=40),
        language=dict(hidden=True, width=120),
        created=dict(hidden=True, width=140),
        lastlogin=dict(hidden=True, width=140),
        nationalliable=dict(hidden=True, width=120),
        ownersadmin=dict(hidden=True, nullable=True),
        playersmanager=dict(hidden=True, nullable=True),
        maxratinglevel=dict(hidden=True),
    ),
)
def users():
    request, args = yield

    t = translator(request)

    if 'metadata' in args:
        results = yield args
        results['metadata']['fields'].append(
            {
                'label': t(_('Language')),
                'hint': t(
                    _(
                        'The preferred language of the user, used to send email messages'
                        ' and for the user interface when he logs in.'
                    )
                ),
                'name': 'Language',
                'hidden': True,
                'nullable': True,
                'lookup': dict(
                    url='/data/languages',
                    remoteFilter=False,
                    lookupField='language',
                    idField='code',
                    displayField='name',
                ),
            }
        )
    else:
        # If there is a single filter on either the first name, the last name or the email
        # transform it in an expression that checks for the presence of the search term in
        # either one of those fields
        if 'filter' in args:
            # Save it, as extract_filter() removes them from the dictionary
            old_args = dict(args)
            filters = extract_filters(args)
            if (
                len(filters) == 1
                and filters[0].property in {'email', 'firstname', 'lastname'}
                and filters[0].operator == Operator.CONTAINS
            ):
                op = filters[0].operator
                value = filters[0].value
                conditions = or_(
                    op.filter(_users_t.c.email, value),
                    op.filter(_users_t.c.firstname, value),
                    op.filter(_users_t.c.lastname, value),
                )
                results = yield args, (conditions,)
            else:
                results = yield old_args
        else:
            results = yield args

        for r in results['root']:
            r['password'] = '*' * 6
            code = r['language']
            if code:
                r['Language'] = language_name(code)
    yield results


_pchampionships_t = _championships_t.alias()


@view_config(route_name='championships', renderer='json')
@expose(
    select(
        _championships_t,
        _clubs_t.c.description.label('Club'),
        select(_pchampionships_t.c.description)
        .where(_pchampionships_t.c.idchampionship == _championships_t.c.idprevious)
        .scalar_subquery()
        .label('Previous'),
        select(_ratings_t.c.description)
        .where(_ratings_t.c.idrating == _championships_t.c.idrating)
        .scalar_subquery()
        .label('Rating'),
        select(func.count(_tourneys_t.c.idtourney))
        .where(_tourneys_t.c.idchampionship == _championships_t.c.idchampionship)
        .scalar_subquery()
        .label('Tourneys'),
    ).select_from(_championships_t.join(_clubs_t)),
    metadata=dict(
        description=dict(flex=1, vtype='nonempty'),
        prizes=dict(hidden=True, width=180),
        couplings=dict(hidden=True, width=180),
        skipworstprizes=dict(hidden=True),
        playersperteam=dict(hidden=True),
        closed=dict(hidden=True, nullable=True),
        trainingboards=dict(hidden=True),
        Club=dict(
            label=_('Club'),
            hint=_('Club that organizes the tourneys of the championship.'),
            flex=1,
            lookup=dict(
                url='/data/clubsLookup',
                idField='idclub',
                displayField='description',
                otherFields='nationality',
                pageSize=12,
                innerTpl=(
                    '<div class="sol-flags-icon sol-flag-{nationality}"'
                    ' data-qtip="'
                    '{[ SoL.form.field.FlagsCombo.countries'
                    '[values.nationality] ]}">{description}'
                    '</div>'
                ),
            ),
        ),
        Previous=dict(
            label=_('Previous championship'),
            hint=_('Previous championship.'),
            hidden=True,
            nullable=True,
            lookup=dict(
                url='/data/championships?only_cols=idchampionship,description'
                '&sort_by_description=ASC&filter_by_closed=true',
                idField='idchampionship',
                lookupField='idprevious',
                displayField='description',
            ),
        ),
        Rating=dict(
            label=_('Rating'),
            hint=_("Rating this championship's tourneys will use by default, if any."),
            hidden=True,
            nullable=True,
            lookup=dict(
                url='/data/ratingsLookup',
                idField='idrating',
                displayField='description',
            ),
        ),
        Tourneys=dict(
            label=_('Tourneys'),
            hint=_('Number of tourneys in the championship.'),
            width=40,
            readonly=True,
            sortable=False,
        ),
    ),
)
def championships(request, results):
    replace_ratings_description(request, results)
    return add_owner(request, results)


@view_config(route_name='championships_lookup', renderer='json')
@expose(
    select(
        _championships_t.c.idchampionship,
        _championships_t.c.description,
        _clubs_t.c.description.label('Club'),
    )
    .select_from(_championships_t.join(_clubs_t))
    .order_by(_clubs_t.c.description, _championships_t.c.description)
    .where(~_championships_t.c.closed)
)
def championshipsLookup():
    request, args = yield

    # If user is not the admin, then give him just the championships he owns OR those
    # explicitly associated with him

    if request.session['is_guest']:
        conditions = (_championships_t.c.idchampionship == None,)
        results = yield args, conditions
    elif not request.session['is_admin']:
        from ..models.club import clubusers

        cu_t = clubusers.alias('cu')
        conditions = (
            or_(
                _championships_t.c.idowner == request.session['user_id'],
                _clubs_t.c.idowner == request.session['user_id'],
                exists().where(
                    and_(
                        cu_t.c.idclub == _clubs_t.c.idclub,
                        cu_t.c.iduser == request.session['user_id'],
                    )
                ),
            ),
        )
        results = yield args, conditions
    else:
        results = yield args
    yield results


@view_config(route_name='tourneys', renderer='json')
@expose(
    select(
        _tourneys_t,
        _championships_t.c.description.label('Championship'),
        _championships_t.c.idclub.label('IDClub'),
        _championships_t.c.trainingboards.label('TrainingBoards'),
        select(_clubs_t.c.description)
        .where(_clubs_t.c.idclub == _championships_t.c.idclub)
        .scalar_subquery()
        .label('Club'),
        select(_clubs_t.c.description)
        .where(_clubs_t.c.idclub == _tourneys_t.c.idhostingclub)
        .scalar_subquery()
        .label('HostingClub'),
        _championships_t.c.playersperteam.label('PlayersPerTeam'),
        _championships_t.c.prizes.label('Prizes'),
        select(_ratings_t.c.description)
        .where(_ratings_t.c.idrating == _tourneys_t.c.idrating)
        .scalar_subquery()
        .label('Rating'),
        select(func.count(_competitors_t.c.idcompetitor))
        .where(_competitors_t.c.idtourney == _tourneys_t.c.idtourney)
        .scalar_subquery()
        .label('Competitors'),
        select(func.max(_matches_t.c.turn))
        .where(_matches_t.c.idtourney == _tourneys_t.c.idtourney)
        .scalar_subquery()
        .label('GeneratedTurns'),
    ).select_from(_tourneys_t.join(_championships_t)),
    metadata=dict(
        countdownstarted=False,
        couplings=dict(hidden=True, width=180),
        currentturn=dict(hidden=True, readonly=True),
        delaycompatriotpairing=dict(hidden=True),
        delaytoppairing=dict(hidden=True),
        description=dict(flex=3, vtype='nonempty'),
        duration=dict(hidden=True),
        finalkind=dict(hidden=True, nullable=True),
        finals=dict(hidden=True),
        finalturns=dict(hidden=True),
        location=dict(flex=2),
        matcheskind=dict(hidden=True),
        phantomscore=dict(hidden=True),
        prealarm=dict(hidden=True),
        prized=dict(hidden=True),
        rankedturn=dict(hidden=True, readonly=True),
        retirements=dict(hidden=True),
        socialurl=dict(hidden=True, width=250, vtype='url'),
        system=dict(hidden=True),
        Championship=dict(
            label=_('Championship'),
            hint=_('Championship this tourney belongs to.'),
            flex=3,
            lookup=dict(
                url='/data/championshipsLookup',
                idField='idchampionship',
                displayField='description',
                otherFields='Club',
                innerTpl=('<div>{description}&nbsp;<small>({Club})</small></div>'),
            ),
        ),
        Club=dict(
            label=_('Club'),
            hint=_('Club this tourney is organized by.'),
            flex=3,
            readonly=True,
            # This is effective only for filtering purposes
            lookup=dict(
                url='/data/clubsLookup',
                idField='idclub',
                displayField='description',
                otherFields='nationality',
                pageSize=12,
                innerTpl=(
                    '<div class="sol-flags-icon sol-flag-{nationality}"'
                    ' data-qtip="'
                    '{[ SoL.form.field.FlagsCombo.countries'
                    '[values.nationality] ]}">{description}'
                    '</div>'
                ),
            ),
        ),
        Competitors=dict(
            label=_('Competitors'),
            hint=_('Number of competitors.'),
            width=40,
            readonly=True,
            sortable=False,
        ),
        GeneratedTurns=dict(
            label=_('Turns'),
            hint=_('Number of turns that has been generated so far.'),
            width=40,
            readonly=True,
            sortable=False,
            hidden=True,
        ),
        HostingClub=dict(
            label=_('Hosted by'),
            hint=_(
                'Club that hosts this tourney, when different from the one'
                ' that organizes the championship.'
            ),
            hidden=True,
            nullable=True,
            lookup=dict(
                url='/data/clubsLookup',
                idField='idclub',
                lookupField='idhostingclub',
                displayField='description',
                otherFields='nationality',
                pageSize=12,
                innerTpl=(
                    '<div class="sol-flags-icon sol-flag-{nationality}"'
                    ' data-qtip="'
                    '{[ SoL.form.field.FlagsCombo.countries'
                    '[values.nationality] ]}'
                    '">{description}'
                    '</div>'
                ),
            ),
        ),
        IDClub=dict(
            label=_championships_t.c.idclub.info['label'],
            hint=_('ID of the club this tourney is organized by.'),
            hidden=True,
        ),
        PlayersPerTeam=dict(
            label=_championships_t.c.playersperteam.info['label'],
            hint=_championships_t.c.playersperteam.info['hint'],
            width=40,
            readonly=True,
            hidden=True,
        ),
        Prizes=dict(
            hidden=True,
            label=_championships_t.c.prizes.info['label'],
            hint=_championships_t.c.prizes.info['hint'],
        ),
        Rating=dict(
            label=_('Rating'),
            hint=_('Rating this tourney will use and update, if any.'),
            hidden=True,
            nullable=True,
            lookup=dict(
                url='/data/ratingsLookup',
                idField='idrating',
                displayField='description',
            ),
        ),
        TrainingBoards=dict(
            hidden=True,
            label=_championships_t.c.trainingboards.info['label'],
            hint=_championships_t.c.trainingboards.info['hint'],
            readonly=True,
            sortable=False,
        ),
    ),
)
def tourneys():
    request, params = yield
    if 'idplayer' in params:
        idplayer = int(params.pop('idplayer'))
        condition = exists().where(
            and_(
                _competitors_t.c.idtourney == _tourneys_t.c.idtourney,
                or_(
                    _competitors_t.c.idplayer1 == idplayer,
                    _competitors_t.c.idplayer2 == idplayer,
                    _competitors_t.c.idplayer3 == idplayer,
                    _competitors_t.c.idplayer4 == idplayer,
                ),
            )
        )
        results = yield params, (condition,)
    else:
        results = yield params
    replace_ratings_description(request, results)
    yield add_owner(request, results)


@view_config(route_name='countries', renderer='json')
def countries(request):
    names = countries_names(request=request)
    return dict(count=len(names), message='Ok', root=names, success=True)


@view_config(route_name='languages', renderer='json')
def languages(request):
    from operator import itemgetter

    result = languages_names(request=request)
    return dict(
        count=len(result),
        message='Ok',
        root=sorted(result, key=itemgetter('name')),
        success=True,
    )


_rates_t = Rate.__table__


@view_config(route_name='ratings', renderer='json')
@expose(
    select(
        _ratings_t,
        select(_clubs_t.c.description)
        .where(_clubs_t.c.idclub == _ratings_t.c.idclub)
        .scalar_subquery()
        .label('Club'),
        select(func.count(_tourneys_t.c.idtourney))
        .where(_tourneys_t.c.idrating == _ratings_t.c.idrating)
        .scalar_subquery()
        .label('Tourneys'),
        select(func.count(distinct(_rates_t.c.idplayer)))
        .where(_rates_t.c.idrating == _ratings_t.c.idrating)
        .scalar_subquery()
        .label('Players'),
    ),
    metadata=dict(
        description=dict(flex=1, vtype='nonempty'),
        level=dict(width=180),
        inherit=dict(hidden=True, nullable=True),
        tau=dict(hidden=True, decimals=2, type='numeric'),
        default_rate=dict(hidden=True),
        default_deviation=dict(hidden=True),
        default_volatility=dict(hidden=True, decimals=5, type='numeric'),
        lower_rate=dict(hidden=True),
        higher_rate=dict(hidden=True),
        outcomes=dict(hidden=True, width=200),
        Club=dict(
            label=_('Club'),
            hint=_('Club this rating is restricted to.'),
            flex=1,
            nullable=True,
            lookup=dict(
                url='/data/clubsLookup',
                idField='idclub',
                displayField='description',
                otherFields='nationality',
                pageSize=12,
                innerTpl=(
                    '<div class="sol-flags-icon sol-flag-{nationality}"'
                    ' data-qtip="'
                    '{[ SoL.form.field.FlagsCombo.countries'
                    '[values.nationality] ]}">{description}'
                    '</div>'
                ),
            ),
        ),
        Tourneys=dict(
            label=_('Tourneys'),
            hint=_('Number of tourneys using this rating.'),
            width=80,
            readonly=True,
            sortable=False,
        ),
        Players=dict(
            label=_('Players'),
            hint=_('Number of rated players in this rating.'),
            width=80,
            readonly=True,
            sortable=False,
        ),
    ),
)
def ratings(request, results):
    return add_owner(request, results)


@view_config(route_name='ratings_lookup', renderer='json')
@expose(
    select(
        _ratings_t.c.idrating,
        _ratings_t.c.description,
        _ratings_t.c.level,
        _clubs_t.c.description.label('Club'),
    )
    .select_from(
        _ratings_t.outerjoin(_clubs_t, _clubs_t.c.idclub == _ratings_t.c.idclub)
    )
    .where(_ratings_t.c.level != '0')
    .where(_ratings_t.c.description != 'Glicko Base Rating (admin only!)')
    .order_by(_ratings_t.c.level, _ratings_t.c.description)
)
def ratingsLookup():
    request, args = yield

    # admin can obviously see all the ratings, guest only the lowest level, normal users cannot
    # see ratings higher than their maxratinglevel
    if request.session['is_admin']:
        results = yield args
    else:
        if request.session['is_guest']:
            rating_filter = _ratings_t.c.level == '4'
        else:
            rating_filter = _ratings_t.c.level >= (
                select(_users_t.c.maxratinglevel)
                .where(_users_t.c.iduser == request.session['user_id'])
                .scalar_subquery()
            )
        results = yield args, (rating_filter,)

    if 'metadata' not in results:
        ratings = results['root']
        t = translator(request)
        levels = {
            '1': _('International'),
            '2': _('National'),
            '3': _('Regional'),
            '4': _('Courtyard'),
        }
        for rating in ratings:
            club = (' (%s)' % rating['Club']) if rating['Club'] else ''
            rating['description'] = '%s-%s: %s%s' % (
                rating['level'],
                t(levels[rating['level']]),
                rating['description'],
                club,
            )
    yield results


_ratesc_t = _rates_t.alias()
_ratesl_t = _rates_t.alias()
_countrates = select(func.count(_ratesc_t.c.idrate)).where(
    and_(
        _ratesc_t.c.idrating == _rates_t.c.idrating,
        _ratesc_t.c.idplayer == _rates_t.c.idplayer,
    )
)
_lastrate = (
    select(func.max(_ratesl_t.c.date))
    .where(_ratesl_t.c.idrating == _rates_t.c.idrating)
    .where(_ratesl_t.c.idplayer == _rates_t.c.idplayer)
)
_rated_players_metadata = _players_metadata
_rated_players_metadata['CountRates'] = dict(
    label=_('Rates'),
    hint=_('Number of rates of the player.'),
    width=40,
)
_rated_players_metadata['volatility'] = dict(
    decimals=5,
    hidden=True,
    type='numeric',
)


@view_config(route_name='rated_players', renderer='json')
@expose(
    select(
        _players_t,
        _countrates.scalar_subquery().label('CountRates'),
        _rates_t.c.rate,
        _rates_t.c.deviation,
        _rates_t.c.volatility,
    )
    .select_from(_players_t.join(_rates_t))
    .where(_rates_t.c.date == _lastrate.scalar_subquery()),
    metadata=_rated_players_metadata,
)
def ratedPlayers(request, results):
    return results
