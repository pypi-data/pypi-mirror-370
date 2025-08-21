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

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import config as dc_config
from dataclasses_json import DataClassJsonMixin

import qumulo.lib.request as request

MULTITENANCY_URI = '/v1/multitenancy/'
MULTITENANCY_TENANTS_URI = MULTITENANCY_URI + 'tenants/'


# exclude is mistyped: https://github.com/lidatong/dataclasses-json/pull/231
def ExcludeIfNone(*v: object) -> bool:
    return v[0] is None


@dataclass
class TenantConfig(DataClassJsonMixin):
    id: int
    name: str
    networks: List[int]
    nfs_enabled: bool
    replication_enabled: bool
    rest_api_enabled: bool
    smb_enabled: bool
    ssh_enabled: bool
    web_ui_enabled: bool
    identity_config_id: int


@dataclass
class _TenantConfigCreatePatchBase(DataClassJsonMixin):
    networks: Optional[List[int]] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))
    nfs_enabled: Optional[bool] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))
    replication_enabled: Optional[bool] = field(
        default=None, metadata=dc_config(exclude=ExcludeIfNone)
    )
    rest_api_enabled: Optional[bool] = field(
        default=None, metadata=dc_config(exclude=ExcludeIfNone)
    )
    smb_enabled: Optional[bool] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))
    ssh_enabled: Optional[bool] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))
    web_ui_enabled: Optional[bool] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))


@dataclass
class _TenantCreateBase(DataClassJsonMixin):
    name: str
    identity_config_id: Optional[int] = field(default=1)


@dataclass
class TenantConfigCreate(_TenantConfigCreatePatchBase, _TenantCreateBase):
    pass


@dataclass
class TenantConfigPatch(_TenantConfigCreatePatchBase):
    name: Optional[str] = field(default=None, metadata=dc_config(exclude=ExcludeIfNone))
    identity_config_id: Optional[int] = field(
        default=None, metadata=dc_config(exclude=ExcludeIfNone)
    )


class Multitenancy:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def create_tenant(self, config: TenantConfigCreate) -> request.ResponseWithEtag[TenantConfig]:
        response = self.client.send_request('POST', MULTITENANCY_TENANTS_URI, body=config.to_dict())
        assert response.etag is not None
        return request.ResponseWithEtag(TenantConfig.schema().load(response.data), response.etag)

    def get_tenant(self, tenant_id: int) -> request.ResponseWithEtag[TenantConfig]:
        response = self.client.send_request('GET', MULTITENANCY_TENANTS_URI + str(tenant_id))
        assert response.etag is not None
        return request.ResponseWithEtag(TenantConfig.schema().load(response.data), response.etag)

    def list_tenants(self) -> List[TenantConfig]:
        response = self.client.send_request('GET', MULTITENANCY_TENANTS_URI)
        assert response.etag is None
        return [TenantConfig.schema().load(config) for config in response.data['entries']]

    def delete_tenant(self, tenant_id: int, if_match: Optional[str] = None) -> None:
        response = self.client.send_request(
            'DELETE', MULTITENANCY_TENANTS_URI + str(tenant_id), if_match=if_match
        )
        assert response.etag is None

    def set_tenant(
        self, tenant_id: int, config: TenantConfig, if_match: Optional[str] = None
    ) -> request.ResponseWithEtag[TenantConfig]:
        response = self.client.send_request(
            'PUT',
            MULTITENANCY_TENANTS_URI + str(tenant_id),
            body=config.to_dict(),
            if_match=if_match,
        )
        assert response.etag is not None
        return request.ResponseWithEtag(TenantConfig.schema().load(response.data), response.etag)

    def modify_tenant(
        self, tenant_id: int, config: TenantConfigPatch, if_match: Optional[str] = None
    ) -> request.ResponseWithEtag[TenantConfig]:
        response = self.client.send_request(
            'PATCH',
            MULTITENANCY_TENANTS_URI + str(tenant_id),
            body=config.to_dict(),
            if_match=if_match,
        )
        assert response.etag is not None
        return request.ResponseWithEtag(TenantConfig.schema().load(response.data), response.etag)
