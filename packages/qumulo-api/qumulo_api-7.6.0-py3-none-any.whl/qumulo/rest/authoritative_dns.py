# Copyright (c) 2025 Qumulo, Inc.
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

from typing import Dict, List, Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection, RestResponse


@request.request
def get_settings(conninfo: Connection, _credentials: Optional[Credentials]) -> RestResponse:
    method = 'GET'
    uri = '/v1/authoritative-dns/settings'
    return conninfo.send_request(method, uri)


@request.request
def modify_settings(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    fqdn: Optional[str] = None,
    enabled: Optional[bool] = None,
    host_restrictions: Optional[List[str]] = None,
) -> RestResponse:
    method = 'PATCH'
    uri = '/v1/authoritative-dns/settings'

    settings: Dict[str, object] = {}
    if fqdn is not None:
        settings['fqdn'] = fqdn
    if enabled is not None:
        settings['enabled'] = enabled
    if host_restrictions is not None:
        settings['host_restrictions'] = host_restrictions

    return conninfo.send_request(method, uri, body=settings)
