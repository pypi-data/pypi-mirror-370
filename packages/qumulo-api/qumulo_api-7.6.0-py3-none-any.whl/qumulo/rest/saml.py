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

from dataclasses import dataclass
from typing import Any, Dict, Optional

from dataclasses_json import DataClassJsonMixin
from marshmallow import EXCLUDE

import qumulo.lib.request as request

from qumulo.lib.rest_util import dataclass_to_dict_omit_none_fields

SAML_SETTINGS_URI = '/v1/saml/settings'


@dataclass
class ConfigV1(DataClassJsonMixin):
    enabled: bool
    idp_sso_url: str
    idp_certificate: str
    idp_entity_id: str
    cluster_dns_name: str
    require_sso: bool


@dataclass
class ConfigV1Patch:
    enabled: Optional[bool] = None
    idp_sso_url: Optional[str] = None
    idp_certificate: Optional[str] = None
    idp_entity_id: Optional[str] = None
    cluster_dns_name: Optional[str] = None
    require_sso: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


class Saml:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def get_settings(self) -> request.ResponseWithEtag[ConfigV1]:
        response = self.client.send_request('GET', SAML_SETTINGS_URI)
        assert response.etag is not None
        return request.ResponseWithEtag(
            ConfigV1.schema().load(response.data, unknown=EXCLUDE), response.etag
        )

    def modify_settings(
        self, config: ConfigV1Patch, etag: Optional[str] = None
    ) -> request.ResponseWithEtag[ConfigV1]:
        response = self.client.send_request(
            'PATCH', SAML_SETTINGS_URI, body=config.to_dict(), if_match=etag
        )
        assert response.etag is not None
        return request.ResponseWithEtag(
            ConfigV1.schema().load(response.data, unknown=EXCLUDE), response.etag
        )

    def set_settings(
        self, config: ConfigV1, etag: Optional[str] = None
    ) -> request.ResponseWithEtag[ConfigV1]:
        response = self.client.send_request(
            'PUT', SAML_SETTINGS_URI, body=config.to_dict(), if_match=etag
        )
        assert response.etag is not None
        return request.ResponseWithEtag(
            ConfigV1.schema().load(response.data, unknown=EXCLUDE), response.etag
        )
