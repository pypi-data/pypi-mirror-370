# Copyright (c) 2017 Qumulo, Inc.
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


from typing import Dict, Optional, Sequence

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def settings_set_v2(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    bind_uri: object,
    base_distinguished_names: Sequence[str],
    use_ldap: Optional[bool] = False,
    user: Optional[object] = None,
    password: Optional[object] = None,
    encrypt_connection: Optional[bool] = None,
    ldap_schema: Optional[str] = None,
    ldap_schema_description: Optional[str] = None,
) -> request.RestResponse:
    method = 'PUT'
    uri = '/v2/ldap/settings'

    settings = {
        'use_ldap': use_ldap,
        'bind_uri': str(bind_uri),
        'base_distinguished_names': str(base_distinguished_names),
    }
    if user is not None:
        settings['user'] = str(user)
    if password is not None:
        settings['password'] = str(password)
    if encrypt_connection is not None:
        settings['encrypt_connection'] = encrypt_connection
    if ldap_schema is not None:
        settings['ldap_schema'] = str(ldap_schema)
    if ldap_schema_description is not None:
        settings['ldap_schema_description'] = ldap_schema_description

    return conninfo.send_request(method, uri, body=settings)


@request.request
def settings_get_v2(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/ldap/settings'

    return conninfo.send_request(method, uri)


@request.request
def settings_update_v2(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    bind_uri: Optional[str] = None,
    base_distinguished_names: Optional[Sequence[str]] = None,
    use_ldap: Optional[bool] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    encrypt_connection: Optional[bool] = None,
    ldap_schema: Optional[str] = None,
    ldap_schema_description: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v2/ldap/settings'

    settings: Dict[str, object] = {}

    if bind_uri != None:  # noqa: E711
        settings['bind_uri'] = bind_uri
    if base_distinguished_names != None:  # noqa: E711
        settings['base_distinguished_names'] = base_distinguished_names
    if ldap_schema != None:  # noqa: E711
        settings['ldap_schema'] = ldap_schema
    if ldap_schema_description != None:  # noqa: E711
        settings['ldap_schema_description'] = ldap_schema_description
    if user != None:  # noqa: E711
        settings['user'] = user
    if password != None:  # noqa: E711
        settings['password'] = password
    if use_ldap != None:  # noqa: E711
        settings['use_ldap'] = use_ldap
    if encrypt_connection != None:  # noqa: E711
        settings['encrypt_connection'] = encrypt_connection

    return conninfo.send_request(method, uri, body=settings)


@request.request
def status_get(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/ldap/status'

    return conninfo.send_request(method, uri)


@request.request
def uid_number_to_login_name_get(
    conninfo: request.Connection, _credentials: Optional[Credentials], uid_number: object
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/ldap/uid-number/' + str(uid_number) + '/login-name'

    return conninfo.send_request(method, uri)


@request.request
def login_name_to_gid_numbers_get(
    conninfo: request.Connection, _credentials: Optional[Credentials], login_name: object
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/ldap/login-name/' + str(login_name) + '/gid-numbers'

    return conninfo.send_request(method, uri)


@request.request
def login_name_to_uid_numbers_get(
    conninfo: request.Connection, _credentials: Optional[Credentials], uid: object
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/ldap/login-name/' + str(uid) + '/uid-numbers'

    return conninfo.send_request(method, uri)
