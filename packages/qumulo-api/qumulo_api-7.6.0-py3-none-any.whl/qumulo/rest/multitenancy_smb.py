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
    Retrieve the global default SMB settings configured in the system.
    """
    uri = '/v1/multitenancy/smb/global-settings'

    return conninfo.send_request('GET', uri)


@request.request
def modify_global_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    settings: Dict[str, object],
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Modify the global default SMB settings configured in the system.
    """
    uri = '/v1/multitenancy/smb/global-settings'

    return conninfo.send_request('PATCH', uri, body=settings, if_match=if_match)


@request.request
def list_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Retrieve all SMB settings configured on any tenant.
    """
    uri = '/v1/multitenancy/smb/settings/'
    return conninfo.send_request('GET', uri)


@request.request
def get_settings(
    conninfo: request.Connection, _credentials: Optional[Credentials], tenant_id: int
) -> request.RestResponse:
    """
    Retrieve the SMB settings configured in the system for the tenant, if overridden from the
    default global settings.
    """
    uri = f'/v1/multitenancy/smb/settings/{tenant_id}'
    return conninfo.send_request('GET', uri)


@request.request
def set_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    settings: Dict[str, object],
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Set the SMB settings configured in the system for the tenant, overriding the default global
    settings.
    """
    uri = f'/v1/multitenancy/smb/settings/{tenant_id}'
    return conninfo.send_request('PUT', uri, body=settings, if_match=if_match)


@request.request
def modify_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    settings: Dict[str, object],
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Modify the SMB settings configured in the system for the tenant. The tenant settings must have
    previously been configured through set_settings.
    """
    uri = f'/v1/multitenancy/smb/settings/{tenant_id}'
    return conninfo.send_request('PATCH', uri, body=settings, if_match=if_match)


@request.request
def delete_settings(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    tenant_id: int,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Delete the SMB settings configured in the system for the tenant, restoring the global default
    settings for the tenant.
    """
    uri = f'/v1/multitenancy/smb/settings/{tenant_id}'

    return conninfo.send_request('DELETE', uri, if_match=if_match)
