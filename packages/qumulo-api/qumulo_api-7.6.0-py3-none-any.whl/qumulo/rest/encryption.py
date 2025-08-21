# Copyright (c) 2020 Qumulo, Inc.
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
from typing import Any, Dict, Optional, Union

import qumulo.lib.request as request

from qumulo.lib.rest_util import dataclass_to_dict_omit_none_fields


@dataclass
class KeyStoreConfigDetailsLocal:
    status: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'KeyStoreConfigDetailsLocal':
        return KeyStoreConfigDetailsLocal(status=data['status'])


@dataclass
class KeyStoreConfigDetailsKmip:
    hostname: str
    port: int
    key_id: str
    config_creation_time: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'KeyStoreConfigDetailsKmip':
        return KeyStoreConfigDetailsKmip(
            hostname=data['hostname'],
            port=data['port'],
            key_id=data['key_id'],
            config_creation_time=data['config_creation_time'],
        )


@dataclass
class KeyStoreConfig:
    config_type: str
    config_details: Union[KeyStoreConfigDetailsLocal, KeyStoreConfigDetailsKmip]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'KeyStoreConfig':
        config_type = data['type']
        if config_type == 'Local':
            return KeyStoreConfig(
                config_type=config_type,
                config_details=KeyStoreConfigDetailsLocal.from_dict(data['local_store']),
            )
        elif config_type == 'KMS':
            return KeyStoreConfig(
                config_type=config_type,
                config_details=KeyStoreConfigDetailsKmip.from_dict(data['kms_store']),
            )
        else:
            raise NotImplementedError(f'Unknown encryption config type: {config_type}')


@dataclass
class KmipKeyStoreConfigPut:
    client_cert: str
    client_private_key: str
    hostname: str
    key_id: str
    port: str
    server_ca_cert: str

    def to_dict(self) -> Dict[str, Any]:
        return {'type': 'KMS', 'kms_store': dataclass_to_dict_omit_none_fields(self)}


@dataclass
class KmipKeyCreateParams:
    client_cert: str
    client_private_key: str
    hostname: str
    port: str
    server_ca_cert: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


@dataclass
class KmipKeyCreatePost:
    kms_config: Optional[KmipKeyCreateParams]
    key_name: str

    # dataclass_to_dict_omit_none_fields does not recursively call
    # kms_config.dataclass_to_dict_omit_none_fields. Instead it leaves the object in the map,
    # which will fail to JSON serialize later.
    def to_dict(self) -> Dict[str, Any]:
        if self.kms_config:
            return {'key_name': self.key_name, 'kms_config': self.kms_config.to_dict()}
        else:
            return {'key_name': self.key_name}


@dataclass
class KeyStoreStatus:
    config_type: str
    status: str
    ca_cert_expiry: Optional[str]
    client_cert_expiry: Optional[str]
    last_key_rotation_time: Optional[str]
    last_status_update_time: Optional[str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'KeyStoreStatus':
        return KeyStoreStatus(
            config_type=data['type'],
            status=data['status'],
            ca_cert_expiry=data['ca_cert_expiry'],
            client_cert_expiry=data['client_cert_expiry'],
            last_key_rotation_time=data['last_key_rotation_time'],
            last_status_update_time=data['last_status_update_time'],
        )

    def to_dict(self) -> Dict[str, Any]:
        status = dataclass_to_dict_omit_none_fields(self)
        status['type'] = status.pop('config_type')
        return status


class Encryption:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def create_kmip_key(self, config: KmipKeyCreatePost) -> str:
        method = 'POST'
        uri = '/v2/encryption/external-kms/keys/create'

        rsp = self.client.send_request(method, uri, body=config.to_dict())
        return rsp.data['key_id']

    def rotate_keys(self) -> Dict[str, str]:
        method = 'POST'
        uri = '/v1/encryption/rotate-keys'

        return self.client.send_request(method, uri).data

    def status(self) -> Dict[str, str]:
        method = 'GET'
        uri = '/v1/encryption/status'

        return self.client.send_request(method, uri).data

    def rotate_keys_v2(self, key_id: Optional[str] = None) -> None:
        method = 'POST'
        uri = '/v2/encryption/rotate-keys'

        req = {}
        if key_id != None:  # noqa: E711
            req['key_id'] = key_id

        self.client.send_request(method, uri, body=req)

    def get_key_store_config(self) -> KeyStoreConfig:
        method = 'GET'
        uri = '/v2/encryption/key-store'

        return KeyStoreConfig.from_dict(self.client.send_request(method, uri).data)

    def put_key_store_config(self, config: Optional[KmipKeyStoreConfigPut] = None) -> None:
        method = 'PUT'
        uri = '/v2/encryption/key-store'

        if config:
            self.client.send_request(method, uri, body=config.to_dict())
        else:
            self.client.send_request(method, uri, body={'type': 'Local'})

    def get_key_store_status(self) -> KeyStoreStatus:
        method = 'GET'
        uri = '/v2/encryption/key-store/status'

        return KeyStoreStatus.from_dict(self.client.send_request(method, uri).data)
