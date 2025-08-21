# Copyright (c) 2022 Qumulo, Inc.
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

from typing import Dict, Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def get_global_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Retrieve the global default NFS settings configured in the system.
    """
    method = 'GET'
    uri = '/v1/multitenancy/nfs/global-settings'

    return conninfo.send_request(method, uri)


@request.request
def modify_global_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    v4_enabled: Optional[bool] = None,
    krb5_enabled: Optional[bool] = None,
    krb5i_enabled: Optional[bool] = None,
    krb5p_enabled: Optional[bool] = None,
    auth_sys_enabled: Optional[bool] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Modify the global default NFS settings configured in the system.
    """
    method = 'PATCH'
    uri = '/v1/multitenancy/nfs/global-settings'

    body: Dict[str, bool] = {}
    if v4_enabled is not None:
        body['v4_enabled'] = v4_enabled
    if krb5_enabled is not None:
        body['krb5_enabled'] = krb5_enabled
    if krb5i_enabled is not None:
        body['krb5i_enabled'] = krb5i_enabled
    if krb5p_enabled is not None:
        body['krb5p_enabled'] = krb5p_enabled
    if auth_sys_enabled is not None:
        body['auth_sys_enabled'] = auth_sys_enabled

    return conninfo.send_request(method, uri, body=body, if_match=if_match)


@request.request
def list_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Retrieve all NFS settings configured in the system for any tenant.
    """
    uri = '/v1/multitenancy/nfs/settings/'
    return conninfo.send_request('GET', uri)


@request.request
def get_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials], tenant_id: int
) -> request.RestResponse:
    """
    Retrieve the NFS settings configured in the system for the tenant, if overridden from the
    default global settings.
    """
    method = 'GET'
    uri = f'/v1/multitenancy/nfs/settings/{tenant_id}'

    return conninfo.send_request(method, uri)


@request.request
def set_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    v4_enabled: bool,
    krb5_enabled: bool,
    krb5i_enabled: bool,
    krb5p_enabled: bool,
    auth_sys_enabled: bool,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Set the NFS settings configured in the system for the tenant, overriding the default global
    settings.
    """
    method = 'PUT'
    uri = f'/v1/multitenancy/nfs/settings/{tenant_id}'

    body = {
        'v4_enabled': v4_enabled,
        'krb5_enabled': krb5_enabled,
        'krb5i_enabled': krb5i_enabled,
        'krb5p_enabled': krb5p_enabled,
        'auth_sys_enabled': auth_sys_enabled,
    }

    return conninfo.send_request(method, uri, body=body, if_match=if_match)


@request.request
def modify_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    v4_enabled: Optional[bool] = None,
    krb5_enabled: Optional[bool] = None,
    krb5i_enabled: Optional[bool] = None,
    krb5p_enabled: Optional[bool] = None,
    auth_sys_enabled: Optional[bool] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Modify the NFS settings configured in the system for the tenant. The tenant settings must have
    previously been configured through set_settings.
    """
    method = 'PATCH'
    uri = f'/v1/multitenancy/nfs/settings/{tenant_id}'

    body: Dict[str, bool] = {}
    if v4_enabled is not None:
        body['v4_enabled'] = v4_enabled
    if krb5_enabled is not None:
        body['krb5_enabled'] = krb5_enabled
    if krb5i_enabled is not None:
        body['krb5i_enabled'] = krb5i_enabled
    if krb5p_enabled is not None:
        body['krb5p_enabled'] = krb5p_enabled
    if auth_sys_enabled is not None:
        body['auth_sys_enabled'] = auth_sys_enabled

    return conninfo.send_request(method, uri, body=body, if_match=if_match)


@request.request
def delete_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Delete the NFS settings configured in the system for the tenant, restoring the global default
    settings for the tenant.
    """
    method = 'DELETE'
    uri = f'/v1/multitenancy/nfs/settings/{tenant_id}'

    return conninfo.send_request(method, uri, if_match=if_match)
