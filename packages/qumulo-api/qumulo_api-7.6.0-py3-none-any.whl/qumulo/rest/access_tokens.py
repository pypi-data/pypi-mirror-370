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
from datetime import datetime
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin

from qumulo.lib.identity_util import ApiIdentity, Identity
from qumulo.lib.request import RestResponse, SendRequestObject, TypedPagingIterator
from qumulo.lib.uri import UriBuilder

ACCESS_TOKENS_URI = '/v1/auth/access-tokens/'


@dataclass
class AccessToken(DataClassJsonMixin):
    id: str
    bearer_token: str


@dataclass
class AccessTokenMetadata(DataClassJsonMixin):
    id: str
    user: ApiIdentity
    creator: ApiIdentity
    creation_time: str
    # expiration_time was added in 5.3.2 and must be optional to maintain backwards compatibility.
    expiration_time: Optional[str] = None
    # enabled was added in 5.3.3 and defaults to true for backwards compatibility.
    enabled: bool = True


@dataclass
class AccessTokenMetadataListPaginationToken(DataClassJsonMixin):
    next: Optional[str]


@dataclass
class AccessTokenMetadataList(DataClassJsonMixin):
    entries: List[AccessTokenMetadata]
    paging: AccessTokenMetadataListPaginationToken

    @classmethod
    def from_rest_response(cls, response: RestResponse) -> 'AccessTokenMetadataList':
        return cls.from_dict(response.data)


def format_datetime_as_rfc3339(dt: datetime) -> str:
    # A datetime without tzinfo will not format in a way that QFSD understands.
    if dt.tzinfo is None:
        raise ValueError('expiration_time must have time zone information')
    return dt.isoformat()


class AccessTokens:
    def __init__(self, client: SendRequestObject):
        self.client = client

    def create(self, user: Identity, expiration_time: Optional[datetime] = None) -> AccessToken:
        """
        Create a long-lived access token for the given user.
        """
        req = {'user': user.dictionary()}
        if expiration_time is not None:
            req['expiration_time'] = format_datetime_as_rfc3339(expiration_time)

        response = self.client.send_request('POST', ACCESS_TOKENS_URI, body=req)
        return AccessToken.from_dict(response.data)

    def get(self, token_id: str) -> AccessTokenMetadata:
        """
        Get metadata for the given access token.
        """
        uri = UriBuilder(path=ACCESS_TOKENS_URI).add_path_component(token_id)
        response = self.client.send_request('GET', str(uri))
        return AccessTokenMetadata.from_dict(response.data)

    def modify(
        self,
        token_id: str,
        expiration_time: Optional[datetime] = None,
        enabled: Optional[bool] = None,
    ) -> AccessTokenMetadata:
        req: Dict[str, object] = {}
        if expiration_time is not None:
            req['expiration_time'] = format_datetime_as_rfc3339(expiration_time)
        if enabled is not None:
            req['enabled'] = enabled

        uri = UriBuilder(path=ACCESS_TOKENS_URI).add_path_component(token_id)
        response = self.client.send_request('PATCH', str(uri), body=req)
        return AccessTokenMetadata.from_dict(response.data)

    def delete(self, token_id: str) -> None:
        """
        Delete the given access token.
        """
        uri = UriBuilder(path=ACCESS_TOKENS_URI).add_path_component(token_id)
        self.client.send_request('DELETE', str(uri))

    def list(
        self, user: Optional[Identity] = None, limit: Optional[int] = None
    ) -> TypedPagingIterator[AccessTokenMetadataList]:
        """
        List metadata for all access tokens with pagination.
        """
        uri = UriBuilder(path=ACCESS_TOKENS_URI, rstrip_slash=False)

        if user is not None:
            uri.add_query_param('user', user)

        def get_tokens(uri: UriBuilder) -> RestResponse:
            return self.client.send_request('GET', str(uri))

        return TypedPagingIterator(
            str(uri), get_tokens, AccessTokenMetadataList.from_rest_response, page_size=limit
        )
