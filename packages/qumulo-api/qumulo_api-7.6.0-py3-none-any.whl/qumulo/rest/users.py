# Copyright (c) 2012 Qumulo, Inc.
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


from typing import Optional, Union

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def list_users(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/users/'

    return conninfo.send_request(method, uri)


@request.request
def add_user(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    name: object,
    primary_group: object,
    password: object,
    uid: Optional[object] = None,
    home_directory: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/users/'

    home_directory = str(home_directory) if home_directory is not None else None
    user_info = {
        'name': str(name),
        'primary_group': str(primary_group),
        'uid': '' if uid is None else str(uid),
        'password': str(password),
        'home_directory': home_directory,
    }

    return conninfo.send_request(method, uri, body=user_info)


@request.request
def list_user(
    conninfo: request.Connection, _credentials: Optional[Credentials], user_id: Union[int, str]
) -> request.RestResponse:
    user_id = int(user_id)

    method = 'GET'
    uri = '/v1/users/%d' % user_id

    return conninfo.send_request(method, uri)


@request.request
def modify_user(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    user_id: Union[int, str],
    name: object,
    primary_group: object,
    uid: object,
    home_directory: Optional[object] = None,
    password: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    user_id = int(user_id)
    if_match = if_match if if_match is None else str(if_match)

    method = 'PUT'
    uri = '/v1/users/%d' % user_id

    home_directory = str(home_directory) if home_directory is not None else None
    password = str(password) if password is not None else None
    user_info = {
        'id': str(user_id),
        'name': str(name),
        'primary_group': str(primary_group),
        'uid': '' if uid is None else str(uid),
        'home_directory': home_directory,
        'password': password,
    }

    return conninfo.send_request(method, uri, body=user_info, if_match=if_match)


@request.request
def delete_user(
    conninfo: request.Connection, _credentials: Optional[Credentials], user_id: Union[int, str]
) -> request.RestResponse:
    user_id = int(user_id)

    method = 'DELETE'
    uri = '/v1/users/%d' % user_id

    return conninfo.send_request(method, uri)


@request.request
def list_groups_for_user(
    conninfo: request.Connection, _credentials: Optional[Credentials], user_id: Union[int, str]
) -> request.RestResponse:
    user_id = int(user_id)

    method = 'GET'
    uri = '/v1/users/%d/groups/' % user_id

    return conninfo.send_request(method, uri)


@request.request
def set_user_password(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    user_id: Union[int, str],
    new_password: str,
) -> request.RestResponse:
    user_id = int(user_id)
    new_password = str(new_password)

    method = 'POST'
    uri = '/v1/users/%d/setpassword' % user_id
    body = {'new_password': new_password}

    return conninfo.send_request(method, uri, body=body)


# Given either an auth_id or a username, return all the information about the
# user.
# TODO This should be a REST call, but is not yet.  Return a user_id from a
# string that contains either the id or a name.
@request.request
def get_user_id(
    conninfo: request.Connection, credentials: Optional[Credentials], value: Union[int, str]
) -> request.RestResponse:
    # First, try to parse as an integer
    try:
        return request.RestResponse(int(value), 'etag')
    except ValueError:
        pass

    # Second, look up the user by name
    username = str(value)

    data, etag = list_users(conninfo, credentials)
    for user in data:
        if user['name'] == username:
            return request.RestResponse(int(user['id']), etag)

    raise ValueError('Unable to convert "%s" to a user id' % username)
