# Copyright (c) 2015 Qumulo, Inc.
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


from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Mapping, Optional, Protocol, Sequence, TypedDict, Union

from dataclasses_json import config as dc_config

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.rest_util import dataclass_to_dict_omit_none_fields

# keep the aliases in the real code in sync with any types added here!
ApiResolvedIpResult = Union[
    Literal['OK'], Literal['ERROR'], Literal['NOT_FOUND'], Literal['TIMEOUT']
]


class ApiResolvedIp(TypedDict):
    ip_address: str
    hostname: str
    result: ApiResolvedIpResult


class ApiResolvedHostname(TypedDict):
    hostname: str
    ip_addresses: Sequence[str]
    result: ApiResolvedIpResult


class DnsLookupOverride(TypedDict):
    ip_address: str
    aliases: Sequence[str]


class ApiDnsClearCache(TypedDict):
    dns_config_id: Optional[int]
    skip_forward_cache: bool
    skip_reverse_cache: bool


class ApiDnsLookupOverrideConfig(TypedDict):
    lookup_overrides: Sequence[DnsLookupOverride]


# exclude is mistyped: https://github.com/lidatong/dataclasses-json/pull/231
def ExcludeIfNone(*v: object) -> bool:
    return v[0] is None


class ApiDnsConfig(TypedDict):
    id: int
    dns_servers: Sequence[str]
    dns_search_domains: Sequence[str]
    lookup_overrides: Sequence[DnsLookupOverride]


@dataclass
class ApiDnsConfigPatch:
    dns_servers: Optional[Sequence[str]] = field(
        default=None, metadata=dc_config(exclude=ExcludeIfNone)
    )
    dns_search_domains: Optional[Sequence[str]] = field(
        default=None, metadata=dc_config(exclude=ExcludeIfNone)
    )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ApiDnsConfigPatch':
        info = ApiDnsConfigPatch(
            dns_servers=data.get('dns_servers'), dns_search_domains=data.get('dns_search_domains')
        )
        return info

    def to_dict(self) -> Mapping[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


@request.request
def clear_cache(
    conninfo: request.Connection, _credentials: Optional[Credentials], options: ApiDnsClearCache
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/dns/clear-dns-cache'
    return conninfo.send_request(method, uri, body=options)


@request.request
def resolve_ips_to_names(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    ips: Sequence[str],
    dns_config_id: Optional[int] = None,
) -> request.RestResponse:
    method = 'POST'

    if dns_config_id is not None:
        uri = f'/v1/dns/configs/{dns_config_id}/resolve-ips-to-names'
        return conninfo.send_request(method, uri, body=ips)
    else:
        uri = '/v1/dns/resolve-ips-to-names'
        return conninfo.send_request(method, uri, body=ips)


@request.request
def resolve_names_to_ips(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    hosts: Sequence[str],
    dns_config_id: Optional[int] = None,
) -> request.RestResponse:
    method = 'POST'

    if dns_config_id is not None:
        uri = f'/v1/dns/configs/{dns_config_id}/resolve-names-to-ips'
        return conninfo.send_request(method, uri, body=hosts)
    else:
        uri = '/v1/dns/resolve-names-to-ips'
        return conninfo.send_request(method, uri, body=hosts)


@request.request
def lookup_overrides_get(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/dns/lookup-override-config'
    return conninfo.send_request(method, uri)


@request.request
def lookup_overrides_set(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    overrides: ApiDnsLookupOverrideConfig,
) -> request.RestResponse:
    method = 'PUT'
    uri = '/v1/dns/lookup-override-config'
    return conninfo.send_request(method, uri, body=overrides)


@request.request
def system_config_get(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/dns/configs/system'
    return conninfo.send_request(method, uri)


@request.request
def system_config_modify(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    config: ApiDnsConfigPatch,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v1/dns/configs/system'
    return conninfo.send_request(method, uri, body=config.to_dict(), if_match=if_match)


class Dns(Protocol):
    """
    Used for typing in RestClient. Keep in sync with the module-level functions above.
    """

    @staticmethod
    def clear_cache(clear_dns_cache_options: ApiDnsClearCache) -> None:
        ...

    @staticmethod
    def resolve_ips_to_names(
        ips: Sequence[str], dns_config_id: Optional[int] = None
    ) -> Sequence[ApiResolvedIp]:
        ...

    @staticmethod
    def resolve_names_to_ips(
        hosts: Sequence[str], dns_config_id: Optional[int] = None
    ) -> Sequence[ApiResolvedHostname]:
        ...

    @staticmethod
    def lookup_overrides_get() -> ApiDnsLookupOverrideConfig:
        ...

    @staticmethod
    def lookup_overrides_set(overrides: ApiDnsLookupOverrideConfig) -> None:
        ...

    @staticmethod
    def system_config_get() -> ApiDnsConfig:
        ...

    @staticmethod
    def system_config_modify(config: ApiDnsConfigPatch, if_match: Optional[str] = None) -> None:
        ...
