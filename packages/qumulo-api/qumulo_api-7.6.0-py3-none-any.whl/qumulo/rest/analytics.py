# Copyright (c) 2013 Qumulo, Inc.
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


from typing import Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


@request.request
def time_series_get(
    conninfo: request.Connection, _credentials: Optional[Credentials], begin_time: int = 0
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v1/analytics/time-series/?begin-time={begin_time}'
    return conninfo.send_request(method, uri)


@request.request
def current_activity_get(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    specific_type: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = UriBuilder(path='/v1/analytics/activity/current')
    if specific_type:
        uri.add_query_param('type', specific_type)

    return conninfo.send_request(method, str(uri))


@request.request
def capacity_history_get(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interval: object,
    begin_time: object,
    end_time: Optional[object] = None,
) -> request.RestResponse:
    method = 'GET'

    end_time_component = f'&end-time={end_time}' if end_time else ''
    uri = (
        f'/v1/analytics/capacity-history/?begin-time={begin_time}'
        + end_time_component
        + f'&interval={interval}'
    )

    return conninfo.send_request(method, uri)


@request.request
def capacity_history_files_get(
    conninfo: request.Connection, _credentials: Optional[Credentials], timestamp: object
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v1/analytics/capacity-history/{timestamp}/'

    return conninfo.send_request(method, uri)
