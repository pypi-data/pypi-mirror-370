# Copyright (c) 2016 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


import time

from typing import Mapping, Optional, Sequence

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.identity_util import Identity


@request.request
def login(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    username: object,
    password: object,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/session/login'

    login_info = {'username': str(username), 'password': str(password)}
    resp = conninfo.send_request(method, uri, body=login_info)

    # Authorization uses deltas in time, so we store this systems unix epoch as the issue date.
    # That way time deltas can be computed locally. Server uses its own time deltas so the clocks
    # must tick at the same rate.
    resp.data['issue'] = int(time.time())
    return resp


@request.request
def start_saml_login(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('POST', '/v1/session/start-saml-login')


@request.request
def retrieve_saml_login(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    saml_login_id: str,
    verification_code: str,
) -> request.RestResponse:
    body = {'login_id': saml_login_id, 'verification_code': verification_code}
    return conninfo.send_request('POST', '/v1/session/retrieve-saml-login', body=body)


@request.request
def change_password(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    old_password: object,
    new_password: object,
) -> request.RestResponse:
    'Unlike SetUserPassword, acts implicitly on logged in user'

    method = 'POST'
    uri = '/v1/session/change-password'
    body = {'old_password': str(old_password), 'new_password': str(new_password)}

    return conninfo.send_request(method, uri, body=body)


@request.request
def who_am_i(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    'Same as GET on user/<current_id>'

    return conninfo.send_request('GET', '/v1/session/who-am-i')


@request.request
def my_roles(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('GET', '/v1/session/roles')


@request.request
def get_identity_attributes(
    conninfo: request.Connection, _credentials: Optional[Credentials], auth_id: object
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return conninfo.send_request(method, uri)


@request.request
def set_identity_attributes(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    auth_id: object,
    attributes: Mapping[str, object],
) -> request.RestResponse:
    method = 'PUT'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return conninfo.send_request(method, uri, body=attributes)


@request.request
def delete_identity_attributes(
    conninfo: request.Connection, _credentials: Optional[Credentials], auth_id: object
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return conninfo.send_request(method, uri)


@request.request
def user_defined_mappings_set(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    mappings: Mapping[str, object],
) -> request.RestResponse:
    method = 'PUT'
    uri = '/v1/auth/user-defined-mappings/'

    return conninfo.send_request(method, uri, body=mappings)


@request.request
def user_defined_mappings_get(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/auth/user-defined-mappings/'

    return conninfo.send_request(method, uri)


@request.request
def clear_cache(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('POST', '/v1/auth/clear-cache')


@request.request
def find_identity(
    conninfo: request.Connection, _credentials: Optional[Credentials], **attrs: object
) -> request.RestResponse:
    """
    Obtain a fully-populated api_identity object. At least one argument other
    than @p domain must be specified. If multiple are specified, they must
    represent the same identity.
    @p domain The domain the identity is in.  LOCAL_DOMAIN, WORLD_DOMAIN,
        POSIX_USER_DOMAIN, POSIX_GROUP_DOMAIN, or AD_DOMAIN.
    @p auth_id The identifier used internally by qsfs.
    @p uid A posix UID
    @p gid A posix GID
    @p sid A SID.
    @p name A name of a cluster-local, AD, or LDAP user.  May be an unqualified
        login name, qualified with netbios name (e.g. DOMAIN\\user), a
        universal principal name (e.g. user@domain.example.com), or an LDAP
        distinguished name (e.g CN=John Doe,OU=users,DC=example,DC=com).
    """
    return conninfo.send_request('POST', '/v1/identity/find', body=attrs)


# User types that can be returned by expand_identity
ID_TYPE_USER = 'USER'
ID_TYPE_GROUP = 'GROUP'
ID_TYPE_UNKNOWN = 'UNKNOWN'


@request.request
def expand_identity(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    _id: Identity,
    aux_equivalent_ids: Optional[Sequence[Identity]] = None,
    aux_group_ids: Optional[Sequence[Identity]] = None,
) -> request.RestResponse:
    """
    Find the type, all equivalent identities, and the full (recursive) group
    membership of the given identity.
    @p _id The ID to expand, an instance of qumulo.lib.identity_util.Identity
    @p aux_equivalent_ids An optional list of Identity that should be considered
            equivalent to @p _id for the purpose of this expansion.
    @p aux_group_ids An optional list of Identity that are groups that @p _id
            should be considered a member of for the purpose of this expansion.
    """
    req = {'id': _id.dictionary()}
    if aux_equivalent_ids:
        req['equivalent_ids'] = [i.dictionary() for i in aux_equivalent_ids]
    if aux_group_ids:
        req['group_ids'] = [i.dictionary() for i in aux_group_ids]
    return conninfo.send_request('POST', '/v1/identity/expand', body=req)
