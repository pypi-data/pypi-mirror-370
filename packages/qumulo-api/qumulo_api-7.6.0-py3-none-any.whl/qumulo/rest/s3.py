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
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

from dataclasses_json import DataClassJsonMixin
from marshmallow import EXCLUDE

import qumulo.lib.request as request

from qumulo.lib.identity_util import ApiIdentity, Identity
from qumulo.lib.rest_util import dataclass_to_dict_omit_none_fields
from qumulo.lib.uri import UriBuilder

S3_ACCESS_KEYS_URI = '/v1/s3/access-keys/'
S3_SETTINGS_URI = '/v1/s3/settings'
S3_BUCKETS_URI = '/v1/s3/buckets/'
S3_BUCKETS_DELETE_URI = S3_BUCKETS_URI + '{}?delete-root-dir={}'
S3_BUCKETS_MODIFY_URI = S3_BUCKETS_URI + '{}'


@dataclass
class Config(DataClassJsonMixin):
    enabled: bool
    base_path: str
    multipart_upload_expiry_interval: str
    secure: bool


@dataclass
class ConfigPatch:
    enabled: Optional[bool] = None
    base_path: Optional[str] = None
    multipart_upload_expiry_interval: Optional[str] = None
    secure: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


@dataclass
class AccessKeyDescription:
    access_key_id: str
    owner: ApiIdentity
    creation_time: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AccessKeyDescription':
        return AccessKeyDescription(
            access_key_id=data['access_key_id'],
            owner=data['owner'],
            creation_time=data['creation_time'],
        )


@dataclass
class AccessKeyDescriptionListPaginationToken(DataClassJsonMixin):
    next: Optional[str]


@dataclass
class AccessKeyDescriptionList:
    entries: List[AccessKeyDescription]
    paging: AccessKeyDescriptionListPaginationToken

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AccessKeyDescriptionList':
        return AccessKeyDescriptionList(
            entries=[AccessKeyDescription.from_dict(entry) for entry in data['entries']],
            paging=AccessKeyDescriptionListPaginationToken.from_dict(data['paging']),
        )


@dataclass
class CreatedAccessKey:
    access_key_id: str
    owner: ApiIdentity
    secret_access_key: str
    creation_time: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CreatedAccessKey':
        return CreatedAccessKey(
            access_key_id=data['access_key_id'],
            owner=data['owner'],
            secret_access_key=data['secret_access_key'],
            creation_time=data['creation_time'],
        )


@dataclass
class BucketDefaultRetention:
    units: str
    value: int

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BucketDefaultRetention':
        return BucketDefaultRetention(units=data['units'], value=data['value'])

    def to_dict(self) -> Dict[str, Any]:
        return {'units': self.units, 'value': self.value}


@dataclass
class BucketLockConfiguration:
    enabled: bool
    default_retention: Optional[BucketDefaultRetention] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BucketLockConfiguration':
        default_retention = data.get('default_retention')
        if default_retention:
            return BucketLockConfiguration(
                enabled=data['enabled'],
                default_retention=BucketDefaultRetention.from_dict(default_retention),
            )
        else:
            return BucketLockConfiguration(enabled=data['enabled'])

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


@dataclass
class BucketDescription:
    name: str
    creation_time: str
    path: str
    versioning: str
    lock_config: BucketLockConfiguration

    ## DEPRECATION NOTICE: Use Bucket Policies to enable anonymous access!
    anonymous_access_enabled: bool

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BucketDescription':
        # XXX charward: versioning is not present in 7.0.1 and earlier builds. Remove this condition
        # when we no longer support upgrade from these.
        versioning = 'Unversioned'
        if 'versioning' in data:
            versioning = data['versioning']

        # XXX charward: remove when we no longer support upgrade from 7.2.0
        lock_config = BucketLockConfiguration(enabled=False)
        if 'lock_config' in data:
            lock_config = BucketLockConfiguration.from_dict(data['lock_config'])

        return BucketDescription(
            name=data['name'],
            creation_time=data['creation_time'],
            path=data['path'],
            anonymous_access_enabled=data['anonymous_access_enabled'],
            versioning=versioning,
            lock_config=lock_config,
        )

    def __hash__(self) -> int:
        return hash(repr(self))


@dataclass
class BucketDescriptionList:
    buckets: List[BucketDescription]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BucketDescriptionList':
        return BucketDescriptionList(
            buckets=[BucketDescription.from_dict(bucket) for bucket in data['buckets']]
        )


## DEPRECATION NOTICE: Use Bucket Policies to enable anonymous access!
@dataclass
class BucketPatch:
    anonymous_access_enabled: Optional[bool] = None
    versioning: Optional[str] = None
    lock_config: Optional[BucketLockConfiguration] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_to_dict_omit_none_fields(self)


@dataclass
class UploadDescription:
    id: str
    key: str
    bucket: str
    initiator: ApiIdentity
    initiated: str
    last_modified: str
    total_blocks: int
    datablocks: int
    metablocks: int
    completing: bool
    system_initiated: bool

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UploadDescription':
        return UploadDescription(
            id=data['id'],
            key=data['key'],
            bucket=data['bucket'],
            initiator=data['initiator'],
            initiated=data['initiated'],
            last_modified=data['last_modified'],
            total_blocks=data['total_blocks'],
            datablocks=data['datablocks'],
            metablocks=data['metablocks'],
            completing=data['completing'],
            system_initiated=data['system_initiated'],
        )


@dataclass
class UploadDescriptionListPaginationToken(DataClassJsonMixin):
    next: Optional[str]


@dataclass
class UploadDescriptionList:
    uploads: List[UploadDescription]
    paging: UploadDescriptionListPaginationToken

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UploadDescriptionList':
        return UploadDescriptionList(
            uploads=[UploadDescription.from_dict(entry) for entry in data['uploads']],
            paging=UploadDescriptionListPaginationToken.from_dict(data['paging']),
        )


@dataclass
class PolicyStatement:
    effect: str
    principals: List[str]
    action: List[str]
    sid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        ans = {
            'Effect': self.effect,
            'Principal': {'Qumulo': self.principals},
            'Action': self.action,
        }
        if self.sid is not None:
            ans['Sid'] = self.sid
        return ans

    @staticmethod
    def from_dict(policy: Dict[str, Any]) -> 'PolicyStatement':
        ans = PolicyStatement(
            effect=policy['Effect'],
            principals=policy['Principal']['Qumulo'],
            action=policy['Action'],
            sid=None,
        )
        if 'Sid' in policy:
            ans.sid = policy['Sid']
        return ans


POLICY_VERSION_2012 = '2012-10-17'
POLICY_VERSION_2008 = '2008-10-17'


@dataclass
class Policy:
    statements: List[PolicyStatement]
    id: Optional[str] = None
    version: Optional[str] = None

    def to_dict_no_index(self) -> Dict[str, Any]:
        ans: Dict[str, Any] = {}
        ans['Statement'] = [s.to_dict() for s in self.statements]
        if self.id is not None:
            ans['Id'] = self.id
        if self.version is not None:
            ans['Version'] = self.version
        return ans

    def to_dict(self) -> Dict[str, Any]:
        ans = self.to_dict_no_index()
        for i, s in enumerate(ans['Statement']):
            s['Index'] = i + 1
        return ans

    @staticmethod
    def from_dict(policy: Dict[str, Any]) -> 'Policy':
        ans = Policy(
            id=None,
            version=None,
            statements=[PolicyStatement.from_dict(s) for s in policy['Statement']],
        )
        if 'Id' in policy:
            ans.id = policy['Id']
        if 'Version' in policy:
            ans.version = policy['Version']
        return ans


@dataclass
class StatementAccess:
    allow: bool
    actions: List[str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StatementAccess':
        return StatementAccess(allow=data['allow'], actions=data['actions'])


@dataclass
class PolicyAccessExplanation:
    allowed_actions: List[str]
    rbac_allowed_actions: List[str]
    statement_access: List[Optional[StatementAccess]]
    identity: Optional[ApiIdentity] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PolicyAccessExplanation':
        statement_access: List[Optional[StatementAccess]] = []
        for statement in data['statement_access']:
            if statement:
                statement_access.append(StatementAccess.from_dict(statement))
            else:
                statement_access.append(None)
        res = PolicyAccessExplanation(
            allowed_actions=data['allowed_actions'],
            rbac_allowed_actions=data['rbac_allowed_actions'],
            statement_access=statement_access,
        )
        if 'identity' in data:
            res.identity = data['identity']
        return res


@dataclass
class PolicyAccessExplanationOptions:
    identity: Optional[Identity] = None

    def to_dict(self) -> Dict[str, Any]:
        ans: Dict[str, Any] = {}
        if self.identity:
            ans['identity'] = self.identity.dictionary()
        return ans


def extract_query_param_from_uri(uri: str, param: str) -> str:
    query = urlsplit(uri).query
    return parse_qs(query)[param][0]


class S3:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def get_settings(self) -> Config:
        response = self.client.send_request('GET', S3_SETTINGS_URI)
        return Config.schema().load(response.data, unknown=EXCLUDE)

    def modify_settings(self, config: ConfigPatch) -> Config:
        response = self.client.send_request('PATCH', S3_SETTINGS_URI, body=config.to_dict())
        assert response.etag is None
        return Config.schema().load(response.data, unknown=EXCLUDE)

    def list_access_keys(
        self,
        user: Optional[Identity] = None,
        limit: Optional[int] = None,
        start_at: Optional[str] = None,
    ) -> AccessKeyDescriptionList:
        uri = UriBuilder(path=S3_ACCESS_KEYS_URI, rstrip_slash=False)

        if user is not None:
            uri.add_query_param('user', user)

        if limit is not None:
            uri.add_query_param('limit', limit)

        if start_at is not None:
            uri.add_query_param('after', start_at)

        response = self.client.send_request('GET', str(uri))
        assert response.etag is None

        access_key_list = AccessKeyDescriptionList.from_dict(response.data)
        if access_key_list.paging.next is not None:
            # Extract the continuation token from the next URI. This way callers don't have to know
            # about the actual format.
            access_key_list.paging.next = extract_query_param_from_uri(
                access_key_list.paging.next, 'after'
            )

        return access_key_list

    def create_access_key(self, user: Identity) -> CreatedAccessKey:
        req = {'user': user.dictionary()}
        response = self.client.send_request('POST', S3_ACCESS_KEYS_URI, body=req)
        assert response.etag is None
        return CreatedAccessKey.from_dict(response.data)

    def delete_access_key(self, access_key_id: str) -> None:
        response = self.client.send_request('DELETE', S3_ACCESS_KEYS_URI + access_key_id)
        assert response.etag is None

    # The path used as the bucket root, if specified in the path parameter, must be an absolute
    # path.
    def create_bucket(
        self,
        name: str,
        path: Optional[str] = None,
        create_path: bool = False,
        object_lock_enabled: Optional[bool] = None,
    ) -> BucketDescription:
        req = {'name': name, 'path': path, 'create_fs_path': create_path}
        if object_lock_enabled is not None:
            req['object_lock_enabled'] = object_lock_enabled

        response = self.client.send_request('POST', S3_BUCKETS_URI, body=req)
        assert response.etag is None
        return BucketDescription.from_dict(response.data)

    def list_buckets(self) -> BucketDescriptionList:
        response = self.client.send_request('GET', S3_BUCKETS_URI)
        assert response.etag is None
        return BucketDescriptionList.from_dict(response.data)

    def delete_bucket(self, name: str, delete_root_dir: bool) -> None:
        response = self.client.send_request(
            'DELETE', S3_BUCKETS_DELETE_URI.format(name, str(delete_root_dir).lower())
        )
        assert response.etag is None
        assert response.data is None

    ## DEPRECATION NOTICE: Use Bucket Policies to enable anonymous access!
    ##
    ## This endpoint supports modifying the versioning or locking settings for a bucket.
    def modify_bucket(self, name: str, patch: BucketPatch) -> BucketDescription:
        response = self.client.send_request(
            'PATCH', S3_BUCKETS_MODIFY_URI.format(name), body=patch.to_dict()
        )
        assert response.etag is None
        return BucketDescription.from_dict(response.data)

    def list_uploads(
        self, bucket: str, limit: Optional[int] = None, start_after: Optional[str] = None
    ) -> UploadDescriptionList:
        uri = UriBuilder(path=f'/v1/s3/buckets/{bucket}/uploads/', rstrip_slash=False)

        if limit is not None:
            uri.add_query_param('limit', limit)

        if start_after is not None:
            uri.add_query_param('after', start_after)

        response = self.client.send_request('GET', str(uri))
        assert response.etag is None

        upload_list = UploadDescriptionList.from_dict(response.data)
        if upload_list.paging.next is not None:
            # Extract the continuation token from the next URI. This way callers don't have to know
            # about the actual format.
            upload_list.paging.next = extract_query_param_from_uri(upload_list.paging.next, 'after')

        return upload_list

    def abort_upload(self, bucket: str, upload_id: str) -> None:
        response = self.client.send_request(
            'DELETE', f'/v1/s3/buckets/{bucket}/uploads/{upload_id}'
        )
        assert response.etag is None
        assert response.data is None

    def get_bucket_policy(self, bucket: str) -> Optional[Policy]:
        response = self.client.send_request('GET', f'/v1/s3/buckets/{bucket}/policy')

        if len(response.data) == 0:
            return None

        return Policy.from_dict(response.data)

    def put_bucket_policy(
        self, bucket: str, policy: Policy, allow_remove_self: Optional[bool] = None
    ) -> None:
        uri = UriBuilder(path=f'/v1/s3/buckets/{bucket}/policy')

        if allow_remove_self is not None:
            uri.add_query_param('allow-remove-self', str(allow_remove_self).lower())

        response = self.client.send_request('PUT', str(uri), body=policy.to_dict_no_index())

        assert response.data is None

    def delete_bucket_policy(self, bucket: str) -> None:
        response = self.client.send_request('PUT', f'/v1/s3/buckets/{bucket}/policy', body={})
        assert response.data is None

    # Pass identity = None to explain access for an anonymous user.
    def bucket_policy_explain_access(
        self, bucket: str, identity: Optional[Identity]
    ) -> PolicyAccessExplanation:
        body = PolicyAccessExplanationOptions(identity).to_dict()
        response = self.client.send_request(
            'POST', f'/v1/s3/buckets/{bucket}/policy/explain-access', body=body
        )

        assert response.etag is None
        return PolicyAccessExplanation.from_dict(response.data)
