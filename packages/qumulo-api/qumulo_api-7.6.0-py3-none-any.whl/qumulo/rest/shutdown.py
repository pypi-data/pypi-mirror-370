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


from typing import Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials


@request.request
def halt_cluster(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/shutdown/halt'

    return conninfo.send_request(method, uri)


@request.request
def reboot_start(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    is_rolling: bool = False,
    num_nodes_to_reboot: Optional[int] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/shutdown/reboot/start'

    body = {'is_rolling': is_rolling, 'num_nodes_to_reboot': num_nodes_to_reboot}

    return conninfo.send_request(method, uri, body=body)


@request.request
def reboot_pause(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/shutdown/reboot/pause'
    return conninfo.send_request(method, uri)


@request.request
def reboot_resume(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/shutdown/reboot/resume'
    return conninfo.send_request(method, uri)


@request.request
def reboot_status(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/shutdown/reboot/status'
    return conninfo.send_request(method, uri)


@request.request
def container_restart(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/shutdown/node/container-restart'

    return conninfo.send_request(method, uri)


@request.request
def container_restart_node(
    conninfo: request.Connection, _credentials: Optional[Credentials], node_id: int
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v1/shutdown/container-restart/{node_id}'

    return conninfo.send_request(method, uri)
