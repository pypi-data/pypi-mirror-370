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

V1_SETTINGS_FIELDS = {
    'assigned_by',
    'ip_ranges',
    'floating_ip_ranges',
    'netmask',
    'gateway',
    'gateway_ipv6',
    'dns_servers',
    'dns_search_domains',
    'mtu',
    'bonding_mode',
}


@request.request
def get_cluster_network_config(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/network/settings'

    return conninfo.send_request(method, uri)


@request.request
def modify_cluster_network_config(
    conninfo: request.Connection, _credentials: Optional[Credentials], **kwargs: Optional[object]
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v1/network/settings'

    config = {}

    for key, value in kwargs.items():
        assert key in V1_SETTINGS_FIELDS, f'Unknown setting {key}'
        if value is not None:
            config[key] = value

    if set(kwargs.keys()) == V1_SETTINGS_FIELDS:
        method = 'PUT'

    return conninfo.send_request(method, uri, body=config)


@request.request
def list_interfaces(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/network/interfaces/'

    return conninfo.send_request(method, uri)


@request.request
def get_interface(
    conninfo: request.Connection, _credentials: Optional[Credentials], interface_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v2/network/interfaces/{interface_id}'

    return conninfo.send_request(method, uri)


@request.request
def list_networks(
    conninfo: request.Connection, _credentials: Optional[Credentials], interface_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v2/network/interfaces/{interface_id}/networks/'

    return conninfo.send_request(method, uri)


@request.request
def get_network(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    network_id: str,
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v2/network/interfaces/{interface_id}/networks/{network_id}'

    return conninfo.send_request(method, uri)


# Don't allow setting interface ID and name.
V2_INTERFACE_FIELDS = {'bonding_mode', 'default_gateway', 'default_gateway_ipv6', 'mtu'}


@request.request
def modify_interface(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    **kwargs: Optional[object],
) -> request.RestResponse:
    # Always patch and don't allow setting interface ID and name.
    method = 'PATCH'
    uri = f'/v2/network/interfaces/{interface_id}'

    config = {}

    for key, value in kwargs.items():
        assert key in V2_INTERFACE_FIELDS, f'Unknown setting {key}'
        if value is not None:
            config[key] = value

    if set(config.keys()) == V2_INTERFACE_FIELDS:
        method = 'PUT'

    return conninfo.send_request(method, uri, body=config)


V2_NETWORK_FIELDS = {
    'assigned_by',
    'name',
    'ip_ranges',
    'floating_ip_ranges',
    'netmask',
    'dns_servers',
    'dns_search_domains',
    'mtu',
    'vlan_id',
    'tenant_id',
}


def populate_request_body(body: Dict[str, object], **kwargs: Optional[object]) -> Dict[str, object]:
    for key, value in kwargs.items():
        assert key in V2_NETWORK_FIELDS, f'Unknown setting {key}'
        # tenant_id may be None to unassign the network
        if key == 'tenant_id' or value is not None:
            body[key] = value

    if 'floating_ip_ranges' in body and body['floating_ip_ranges'] == ['']:
        body['floating_ip_ranges'] = []

    if 'dns_servers' in body and body['dns_servers'] == ['']:
        body['dns_servers'] = []

    if 'dns_search_domains' in body and body['dns_search_domains'] == ['']:
        body['dns_search_domains'] = []

    return body


@request.request
def add_network(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    **kwargs: Optional[object],
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v2/network/interfaces/{interface_id}/networks/'
    body = populate_request_body({}, **kwargs)

    return conninfo.send_request(method, uri, body=body)


@request.request
def delete_network(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    network_id: str,
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v2/network/interfaces/{interface_id}/networks/{network_id}'

    return conninfo.send_request(method, uri)


@request.request
def modify_network(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    network_id: str,
    **kwargs: Optional[object],
) -> request.RestResponse:
    method = 'PATCH'
    uri = f'/v2/network/interfaces/{interface_id}/networks/{network_id}'

    body = populate_request_body({'id': network_id}, **kwargs)
    return conninfo.send_request(method, uri, body=body)


@request.request
def set_dhcp_network(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    network_id: str,
    name: str,
    floating_ip_ranges: Optional[Sequence[str]] = None,
    dns_servers: Optional[Sequence[str]] = None,
    dns_search_domains: Optional[Sequence[str]] = None,
) -> request.RestResponse:
    method = 'PUT'
    uri = f'/v2/network/interfaces/{interface_id}/networks/{network_id}'

    dhcp_network_config = {
        'id': network_id,
        'assigned_by': 'DHCP',
        'name': name,
        'floating_ip_ranges': floating_ip_ranges or [],
        'dns_servers': dns_servers or [],
        'dns_search_domains': dns_search_domains or [],
        # The rest of these fields are STATIC only and these are the defaults
        'ip_ranges': [],
        'netmask': '',
        'vlan_id': 0,
    }

    return conninfo.send_request(method, uri, body=dhcp_network_config)


@request.request
def list_network_status_v2(
    conninfo: request.Connection, _credentials: Optional[Credentials], interface_id: int = 1
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v2/network/interfaces/{interface_id}/status/'

    return conninfo.send_request(method, uri)


@request.request
def get_network_status_v2(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    interface_id: str,
    node_id: str,
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v2/network/interfaces/{interface_id}/status/{node_id}'

    return conninfo.send_request(method, uri)


@request.request
def get_static_ip_allocation(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    try_ranges: Optional[str] = None,
    try_netmask: Optional[str] = None,
    try_floating_ranges: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/network/static-ip-allocation'

    query_params = []

    if try_ranges:
        query_params.append(f'try={try_ranges}')
    if try_netmask:
        query_params.append(f'netmask={try_netmask}')
    if try_floating_ranges:
        query_params.append(f'floating={try_floating_ranges}')

    if query_params:
        uri = uri + '?' + '&'.join(query_params)

    return conninfo.send_request(method, uri)


@request.request
def get_floating_ip_allocation(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/network/floating-ip-allocation'

    return conninfo.send_request(method, uri)


@request.request
def connections(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/network/connections/'

    return conninfo.send_request(method, uri)
