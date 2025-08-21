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


@request.request
def get_time(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/time/settings'

    return conninfo.send_request(method, uri)


@request.request
def set_time(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    use_ad_for_primary: Optional[bool] = None,
    ntp_servers: Optional[Sequence[str]] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v1/time/settings'

    time_config: Dict[str, object] = {}

    if use_ad_for_primary is not None:
        time_config['use_ad_for_primary'] = bool(use_ad_for_primary)

    if ntp_servers is not None:
        time_config['ntp_servers'] = list(ntp_servers)

    return conninfo.send_request(method, uri, body=time_config)


@request.request
def get_time_status(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/time/status'

    return conninfo.send_request(method, uri)


@request.request
def list_timezones(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/time/timezones'

    return conninfo.send_request(method, uri)
