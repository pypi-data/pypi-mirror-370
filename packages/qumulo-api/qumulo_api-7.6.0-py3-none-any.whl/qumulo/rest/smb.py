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


from typing import Dict, Optional, Sequence

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.identity_util import EVERYONE_ID, GUEST_USER_ID
from qumulo.lib.uri import UriBuilder

# Permissions constants
NO_ACCESS = 'NONE'
READ_ACCESS = 'READ'
WRITE_ACCESS = 'WRITE'
CHANGE_PERMISSIONS_ACCESS = 'CHANGE_PERMISSIONS'
ALL_ACCESS = 'ALL'

ALLOWED_TYPE = 'ALLOWED'
DENIED_TYPE = 'DENIED'

ALLOW_ALL_USER_PERMISSIONS = [
    {'type': ALLOWED_TYPE, 'trustee': {'auth_id': EVERYONE_ID}, 'rights': [ALL_ACCESS]}
]
ALLOW_READ_ONLY_GUEST_PERMISSIONS = [
    {'type': ALLOWED_TYPE, 'trustee': {'auth_id': GUEST_USER_ID}, 'rights': [READ_ACCESS]}
]

# Compares equal to the default ACL which allows access to all hosts.
# Note that, at least in principle, there are other equivalent ACLs which are
# equivalent but which to not compare equal, although somebody would have to go
# out of their way to create them.
ALLOW_ALL_NETWORK_PERMISSIONS = [
    {
        'type': ALLOWED_TYPE,
        # empty == all:
        'address_ranges': [],
        # Equivalent to ALL_ACCESS, which gets normalized to this by the API:
        'rights': [READ_ACCESS, WRITE_ACCESS, CHANGE_PERMISSIONS_ACCESS],
    }
]

# This is equivalent to an empty ACL, but a bit nicer of a thing to set because
# it makes the meaning and intention explicit.
DENY_ALL_NETWORK_PERMISSIONS = [
    {
        'type': DENIED_TYPE,
        # empty == all:
        'address_ranges': [],
        'rights': [ALL_ACCESS],
    }
]


@request.request
def smb_list_shares(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    populate_trustee_names: bool = False,
) -> request.RestResponse:
    populate_trustee_names_ = 'true' if populate_trustee_names else 'false'

    uri = str(
        UriBuilder(path='/v3/smb/shares/', rstrip_slash=False).add_query_param(
            'populate-trustee-names', populate_trustee_names_
        )
    )

    return conninfo.send_request('GET', uri)


@request.request
def smb_list_share(
    conninfo: request.Connection, _credentials: Optional[Credentials], share_id: str
) -> request.RestResponse:
    return conninfo.send_request('GET', f'/v3/smb/shares/{share_id}')


@request.request
def smb_add_share(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    share_name: str,
    fs_path: str,
    description: str,
    permissions: Optional[Sequence[object]] = None,
    tenant_id: Optional[int] = None,
    allow_fs_path_create: bool = False,
    access_based_enumeration_enabled: Optional[bool] = None,
    default_file_create_mode: Optional[str] = None,
    default_directory_create_mode: Optional[str] = None,
    require_encryption: Optional[bool] = None,
    network_permissions: Optional[Sequence[object]] = None,
) -> request.RestResponse:
    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    share_info: Dict[str, object] = {
        'share_name': share_name,
        'fs_path': fs_path,
        'description': description,
        'permissions': permissions if permissions is not None else ALLOW_ALL_USER_PERMISSIONS,
    }

    if tenant_id is not None:
        share_info['tenant_id'] = tenant_id

    if network_permissions is not None:
        # If not specified, default is an allow-all ACL.
        share_info['network_permissions'] = network_permissions

    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = access_based_enumeration_enabled

    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = default_file_create_mode

    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = default_directory_create_mode

    if require_encryption is not None:
        share_info['require_encryption'] = require_encryption

    uri = str(
        UriBuilder(path='/v3/smb/shares/', rstrip_slash=False).add_query_param(
            'allow-fs-path-create', allow_fs_path_create_
        )
    )

    return conninfo.send_request('POST', uri, body=share_info)


@request.request
def smb_modify_share(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    share_id: str,
    share_name: Optional[str] = None,
    fs_path: Optional[str] = None,
    description: Optional[str] = None,
    permissions: Optional[Sequence[object]] = None,
    tenant_id: Optional[int] = None,
    allow_fs_path_create: bool = False,
    access_based_enumeration_enabled: Optional[bool] = None,
    default_file_create_mode: Optional[str] = None,
    default_directory_create_mode: Optional[str] = None,
    require_encryption: Optional[bool] = None,
    network_permissions: Optional[Sequence[object]] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    method = 'PATCH'
    uri = str(
        UriBuilder(path=f'/v3/smb/shares/{share_id}').add_query_param(
            'allow-fs-path-create', allow_fs_path_create_
        )
    )

    share_info: Dict[str, object] = {}
    if share_name is not None:
        share_info['share_name'] = share_name
    if fs_path is not None:
        share_info['fs_path'] = fs_path
    if description is not None:
        share_info['description'] = description
    if permissions is not None:
        share_info['permissions'] = permissions
    if tenant_id is not None:
        share_info['tenant_id'] = tenant_id
    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = access_based_enumeration_enabled
    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = default_file_create_mode
    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = default_directory_create_mode
    if require_encryption is not None:
        share_info['require_encryption'] = require_encryption
    if network_permissions is not None:
        share_info['network_permissions'] = network_permissions

    return conninfo.send_request(method, uri, body=share_info, if_match=if_match)


@request.request
def smb_delete_share(
    conninfo: request.Connection, _credentials: Optional[Credentials], share_id: str
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v3/smb/shares/{share_id}'
    return conninfo.send_request(method, uri)


#                _                 _   _   _
#  ___ _ __ ___ | |__     ___  ___| |_| |_(_)_ __   __ _ ___
# / __| '_ ` _ \| '_ \   / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \ | | | | | |_) |  \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/_| |_| |_|_.__/___|___/\___|\__|\__|_|_| |_|\__, |___/
#                   |_____|                        |___/
#  FIGLET: smb_settings
#


@request.request
def set_smb_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials], settings: Dict[str, object]
) -> request.RestResponse:
    uri = '/v1/smb/settings'
    return conninfo.send_request('PUT', uri, settings)


@request.request
def patch_smb_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials], settings: Dict[str, object]
) -> request.RestResponse:
    uri = '/v1/smb/settings'
    return conninfo.send_request('PATCH', uri, settings)


@request.request
def get_smb_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('GET', '/v1/smb/settings')


#                            __ _ _
#   ___  _ __   ___ _ __    / _(_) | ___  ___
#  / _ \| '_ \ / _ \ '_ \  | |_| | |/ _ \/ __|
# | (_) | |_) |  __/ | | | |  _| | |  __/\__ \
#  \___/| .__/ \___|_| |_| |_| |_|_|\___||___/
#       |_|


@request.request
def list_file_handles(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    file_number: Optional[str] = None,
    resolve_paths: Optional[bool] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.PagingIterator:
    method = 'GET'
    uri = UriBuilder(path='/v1/smb/files')
    if file_number is not None:
        uri.add_query_param('file_number', file_number)
    if resolve_paths is not None:
        uri.add_query_param('resolve_paths', resolve_paths)
    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)
    uri.append_slash()

    def get_files(uri: UriBuilder) -> request.RestResponse:
        return conninfo.send_request(method, str(uri))

    return request.PagingIterator(str(uri), get_files)


@request.request
def close_smb_file(
    conninfo: request.Connection, _credentials: Optional[Credentials], location: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/smb/files/close'
    # N.B.: the structure of the POST arguments needs to match the output of v1/smb/files,
    # in that the location is found in a `handle_info` object. This is so that the output of
    # v1/smb/files can be valid input to the close API (the extra fields will be ignored).
    return conninfo.send_request(method, uri, body=[{'handle_info': {'location': location}}])


@request.request
def list_smb_sessions(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    limit: Optional[int] = None,
    after: Optional[str] = None,
    identity: Optional[str] = None,
) -> request.PagingIterator:
    method = 'GET'
    uri = UriBuilder(path='/v1/smb/sessions')

    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)
    if identity is not None:
        uri.add_query_param('identity', identity)
    uri.append_slash()

    def get_sessions(uri: UriBuilder) -> request.RestResponse:
        return conninfo.send_request(method, str(uri))

    return request.PagingIterator(str(uri), get_sessions)


@request.request
def close_smb_sessions(
    conninfo: request.Connection, _credentials: Optional[Credentials], sessions: Sequence[object]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/smb/sessions/close'
    return conninfo.send_request(method, uri, body=sessions)
