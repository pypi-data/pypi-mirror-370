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

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from dataclasses_json import dataclass_json, DataClassJsonMixin

import qumulo.lib.request as request


class NetworkAlreadyExistsError(Exception):
    def __init__(self, network_id: int) -> None:
        super().__init__(f'Network {network_id} already exists')


class NetworkNotFoundError(Exception):
    def __init__(self, network_id: int) -> None:
        super().__init__(f'Network {network_id} does not exist')


class OrphanedVlanError(Exception):
    def __init__(self, vlan_id: int) -> None:
        super().__init__(f'Vlan {vlan_id} does not have any networks')


@dataclass_json
@dataclass
class StaticAddresses:
    default_gateway: str
    ip_ranges: List[str]
    floating_ip_ranges: List[str]
    netmask: str


@dataclass_json
@dataclass
class DhcpAddresses:
    floating_ip_ranges: List[str]
    netmask: Optional[str]


@dataclass_json
@dataclass
class HostAddresses:
    floating_ip_ranges: List[str]
    netmask: Optional[str]


class AddressesKind(str, Enum):
    DHCP = 'DHCP'
    HOST = 'HOST'
    STATIC = 'STATIC'


@dataclass_json
@dataclass
class Addresses:
    type: AddressesKind
    static_addresses: Optional[StaticAddresses] = None
    dhcp_addresses: Optional[DhcpAddresses] = None
    host_addresses: Optional[HostAddresses] = None


@dataclass_json
@dataclass
class FrontendNetwork:
    id: int
    name: str
    addresses: Addresses
    tenant_id: Optional[int] = None

    def modify_addresses(self, **kwargs: Optional[object]) -> None:
        if self.addresses.type == AddressesKind.DHCP:
            assert self.addresses.dhcp_addresses is not None
            addresses_dict = asdict(self.addresses.dhcp_addresses)
            addresses_dict.update(kwargs)
            self.addresses.dhcp_addresses = DhcpAddresses(**addresses_dict)
        elif self.addresses.type == AddressesKind.HOST:
            assert self.addresses.host_addresses is not None
            addresses_dict = asdict(self.addresses.host_addresses)
            addresses_dict.update(kwargs)
            self.addresses.host_addresses = HostAddresses(**addresses_dict)
        elif self.addresses.type == AddressesKind.STATIC:
            assert self.addresses.static_addresses is not None
            addresses_dict = asdict(self.addresses.static_addresses)
            addresses_dict.update(kwargs)
            self.addresses.static_addresses = StaticAddresses(**addresses_dict)
        else:
            raise Exception('unreachable')

    def get_floating_ips(self) -> List[str]:
        if self.addresses.type == AddressesKind.DHCP:
            assert self.addresses.dhcp_addresses is not None
            return self.addresses.dhcp_addresses.floating_ip_ranges
        elif self.addresses.type == AddressesKind.HOST:
            assert self.addresses.host_addresses is not None
            return self.addresses.host_addresses.floating_ip_ranges
        elif self.addresses.type == AddressesKind.STATIC:
            assert self.addresses.static_addresses is not None
            return self.addresses.static_addresses.floating_ip_ranges
        else:
            raise Exception('unreachable')


@dataclass_json
@dataclass
class BondConfig:
    interface_name: str
    bonding_mode: str
    mtu: int
    networks: List[int]


@dataclass_json
@dataclass
class VlanConfig:
    vlan_id: int
    mtu: Optional[int]
    network_id: int
    secondary_network_id: Optional[int]


@dataclass_json
@dataclass
class ManagedInterfaces:
    frontend_bond_config: BondConfig
    frontend_vlans: List[VlanConfig]
    backend_bond_config: Optional[BondConfig] = None


@dataclass_json
@dataclass
class ClusterNetworkManagement(DataClassJsonMixin):
    managed_interfaces: Optional[ManagedInterfaces]
    frontend_networks: List[FrontendNetwork]

    def find_network(self, network_id: int) -> Optional[FrontendNetwork]:
        for network in self.frontend_networks:
            if network.id == network_id:
                return network

        return None

    def modify_network_addresses(self, network_id: int, **kwargs: Optional[object]) -> None:
        network = self.find_network(network_id)
        assert network is not None, f'Unable to locate network {network_id}'

        network.modify_addresses(**kwargs)

    def add_network(
        self,
        network_id: int,
        name: str,
        addresses_kind: AddressesKind,
        tenant_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        if self.find_network(network_id) is not None:
            raise NetworkAlreadyExistsError(network_id)

        if addresses_kind == AddressesKind.HOST:
            addresses_dict = {}
            addresses_dict.update(kwargs)
            addresses = Addresses(
                type=addresses_kind, host_addresses=HostAddresses(**addresses_dict)
            )
        else:
            raise Exception(f'Only {AddressesKind.HOST} networks are supported')

        self.frontend_networks.append(
            FrontendNetwork(id=network_id, name=name, addresses=addresses, tenant_id=tenant_id)
        )

    def delete_network(self, network_id: int, delete_orphaned_vlans: bool = False) -> None:
        if self.find_network(network_id) is None:
            raise NetworkNotFoundError(network_id)

        self.frontend_networks = list(
            filter(lambda network: network.id != network_id, self.frontend_networks)
        )

        if self.managed_interfaces is None:
            return

        frontend_bond_config = self.managed_interfaces.frontend_bond_config
        backend_bond_config = self.managed_interfaces.backend_bond_config
        frontend_vlans = self.managed_interfaces.frontend_vlans

        # Remove any references to the deleted network
        frontend_bond_config.networks = list(
            filter(lambda id: id != network_id, frontend_bond_config.networks)
        )

        if backend_bond_config is not None:
            backend_bond_config.networks = list(
                filter(lambda id: id != network_id, backend_bond_config.networks)
            )

        vlan_ids_to_remove: Set[int] = set()
        for vlan in frontend_vlans:
            if vlan.network_id == network_id:
                if vlan.secondary_network_id is not None:
                    vlan.network_id = vlan.secondary_network_id
                    vlan.secondary_network_id = None
                elif delete_orphaned_vlans:
                    vlan_ids_to_remove.add(vlan.vlan_id)
                else:
                    raise OrphanedVlanError(vlan.vlan_id)
            elif vlan.secondary_network_id is not None and vlan.secondary_network_id == network_id:
                vlan.secondary_network_id = None

        self.managed_interfaces.frontend_vlans = list(
            filter(lambda vlan: vlan.vlan_id not in vlan_ids_to_remove, frontend_vlans)
        )


class NetworkV3:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def get_config_raw(self) -> request.RestResponse:
        method = 'GET'
        uri = '/v3/network'

        return self.client.send_request(method, uri)

    def get_config(self) -> ClusterNetworkManagement:
        return ClusterNetworkManagement.from_dict(self.get_config_raw().data)

    def validate(
        self, config: Dict[str, Any], if_match: Optional[str] = None
    ) -> request.RestResponse:
        method = 'PUT'
        uri = '/v3/network/validate'

        return self.client.send_request(method, uri, body=config, if_match=if_match)

    def put_config(
        self, config: Dict[str, Any], if_match: Optional[str] = None
    ) -> request.RestResponse:
        method = 'PUT'
        uri = '/v3/network'

        return self.client.send_request(method, uri, body=config, if_match=if_match)

    def get_network_status(self, node_id: int) -> Dict[str, Any]:
        method = 'GET'
        uri = f'/v3/network/status/{node_id}'

        return self.client.send_request(method, uri).data

    def list_network_statuses(self) -> List[Any]:
        method = 'GET'
        uri = '/v3/network/status'

        return self.client.send_request(method, uri).data

    def get_cluster_frontend_interfaces(self) -> Dict[int, List[str]]:
        method = 'GET'
        uri = '/v3/network/frontend-interfaces'

        return self.client.send_request(method, uri).data

    def get_cluster_backend_interfaces(self) -> Dict[int, List[str]]:
        method = 'GET'
        uri = '/v3/network/backend-interfaces'

        return self.client.send_request(method, uri).data

    def modify_config(
        self, modify_cb: Callable[[ClusterNetworkManagement], None]
    ) -> request.RestResponse:
        response = self.get_config_raw()
        config = ClusterNetworkManagement.from_dict(response.data)
        modify_cb(config)
        return self.put_config(config.to_dict(), if_match=response.etag)
