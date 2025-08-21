# Copyright (c) 2016 Qumulo, Inc.
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
from enum import Enum
from typing import cast, Dict, List, Mapping, Optional, Sequence

import qumulo.lib.request as request
import qumulo.rest.fs

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


class InDeleteFilter(Enum):
    ALL = 'all'
    EXCLUDE_IN_DELETE = 'exclude_in_delete'
    ONLY_IN_DELETE = 'only_in_delete'


class SnapshotStatusFilter(Enum):
    EXCLUDE_IN_DELETE = 'api_snapshots_exclude_in_delete'
    ONLY_IN_DELETE = 'api_snapshots_exclude_not_in_delete'
    EXCLUDE_LOCKED = 'api_snapshots_exclude_locked'
    ONLY_LOCKED = 'api_snapshots_exclude_not_locked'


@request.request
def list_snapshots(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    in_delete_filter: InDeleteFilter = InDeleteFilter.ALL,
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v3/snapshots/?filter={in_delete_filter.value}'

    return conninfo.send_request(method, uri)


@request.request
def get_snapshot(
    conninfo: request.Connection, _credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/{}'

    return conninfo.send_request(method, uri.format(snapshot_id))


@request.request
def create_snapshot(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    name: Optional[str] = None,
    expiration: Optional[str] = None,
    source_file_id: Optional[str] = None,
    path: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v3/snapshots/'
    snapshot = {}

    # name is an optional parameter
    if name is not None:
        snapshot['name_suffix'] = name

    snapshot['expiration'] = expiration if expiration is not None else ''

    assert path is None or source_file_id is None, 'Cannot specify both path and file id'

    # Take a snapshot on a particular path or ID
    if path is not None:
        source_file_id = cast(
            str,
            qumulo.rest.fs.get_file_attr(conninfo, credentials, path=path).lookup('file_number'),
        )
    if source_file_id is None:
        # If neither the path or the file_id is supplied, default to root
        source_file_id = cast(
            str, qumulo.rest.fs.get_file_attr(conninfo, credentials, path='/').lookup('file_number')
        )

    snapshot['source_file_id'] = source_file_id
    return conninfo.send_request(method, uri, body=snapshot)


@request.request
def modify_snapshot(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    snapshot_id: int,
    expiration: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v3/snapshots/{}'
    snapshot = {}

    # expiration is an optional parameter
    if expiration != None:  # noqa: E711
        snapshot['expiration'] = expiration

    return conninfo.send_request(method, uri.format(snapshot_id), body=snapshot)


@request.request
def delete_snapshot(
    conninfo: request.Connection, _credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'DELETE'
    uri = '/v3/snapshots/{}'

    return conninfo.send_request(method, uri.format(snapshot_id))


@request.request
def list_snapshot_statuses(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    snapshot_status_filter: List[SnapshotStatusFilter],
) -> request.RestResponse:
    method = 'GET'

    uri = UriBuilder(path='/v4/snapshots/status/', rstrip_slash=False)
    if snapshot_status_filter:
        filters = ','.join([f.value for f in snapshot_status_filter])
        uri.add_query_param('filter', filters)

    return conninfo.send_request(method, str(uri))


@request.request
def get_snapshot_status(
    conninfo: request.Connection, _credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/status/{}'

    return conninfo.send_request(method, uri.format(snapshot_id))


@dataclass
class LockKeyRef:
    ref: Optional[str]


@request.request
def create_policy(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    policy_name: str,
    schedule_info: Mapping[str, object],
    snapshot_name_template: Optional[str] = None,
    directory_id: Optional[str] = None,
    enabled: Optional[bool] = None,
    lock_key_ref: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v3/snapshots/policies/'

    if directory_id == None:  # noqa: E711
        directory_id = cast(
            str, qumulo.rest.fs.get_file_attr(conninfo, credentials, path='/').lookup('file_number')
        )

    policy = {
        'policy_name': policy_name,
        'schedule': schedule_info,
        'source_file_id': directory_id,
        'enabled': enabled if enabled is not None else True,
        'snapshot_name_template': snapshot_name_template,
        'lock_key_ref': lock_key_ref,
    }

    return conninfo.send_request(method, uri, body=policy)


@request.request
def modify_policy(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    policy_id: int,
    name: Optional[str] = None,
    snapshot_name_template: Optional[str] = None,
    schedule_info: Optional[Mapping[str, object]] = None,
    enabled: Optional[bool] = None,
    lock_key_ref: Optional[LockKeyRef] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v3/snapshots/policies/{}'

    policy: Dict[str, object] = {}
    if name is not None:
        policy.update({'policy_name': name})
    if snapshot_name_template is not None:
        policy.update({'snapshot_name_template': snapshot_name_template})
    if schedule_info is not None:
        policy.update({'schedule': schedule_info})
    if enabled is not None:
        policy.update({'enabled': enabled})
    if lock_key_ref is not None:
        policy.update(
            {'lock_key_ref': f'{lock_key_ref.ref}' if lock_key_ref.ref is not None else None}
        )

    return conninfo.send_request(method, uri.format(policy_id), body=policy, if_match=if_match)


@request.request
def list_policies(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/policies/'

    return conninfo.send_request(method, uri)


@request.request
def get_policy(
    conninfo: request.Connection, _credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/policies/{}'

    return conninfo.send_request(method, uri.format(policy_id))


@request.request
def delete_policy(
    conninfo: request.Connection, _credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'DELETE'
    uri = '/v3/snapshots/policies/{}'

    return conninfo.send_request(method, uri.format(policy_id))


@request.request
def list_policy_statuses(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/policies/status/'

    return conninfo.send_request(method, uri)


@request.request
def get_policy_status(
    conninfo: request.Connection, _credentials: Optional[Credentials], policy_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v3/snapshots/policies/status/{}'

    return conninfo.send_request(method, uri.format(policy_id))


@request.request
def get_total_used_capacity(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/total-used-capacity'

    return conninfo.send_request(method, uri)


@request.request
def calculate_used_capacity(
    conninfo: request.Connection, _credentials: Optional[Credentials], ids: Sequence[int]
) -> request.RestResponse:
    method = 'POST'
    uri = '/v1/snapshots/calculate-used-capacity'

    return conninfo.send_request(method, uri, body=ids)


@request.request
def capacity_used_per_snapshot(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/'

    return conninfo.send_request(method, uri)


@request.request
def capacity_used_by_snapshot(
    conninfo: request.Connection, _credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/{}'

    return conninfo.send_request(method, uri.format(snapshot_id))


@request.request
def get_snapshot_tree_diff(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = UriBuilder(path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}')

    if limit is not None:
        uri.add_query_param('limit', limit)

    if after is not None:
        uri.add_query_param('after', after)

    return conninfo.send_request(method, str(uri))


@request.request
def get_all_snapshot_tree_diff(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    limit: Optional[int] = None,
) -> request.PagingIterator:
    uri = UriBuilder(path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}')

    def get_a_snapshot_tree_diff(uri: UriBuilder) -> request.RestResponse:
        return conninfo.send_request('GET', str(uri))

    return request.PagingIterator(str(uri), get_a_snapshot_tree_diff, page_size=limit)


def get_snapshot_file_diff_uri(
    newer_snap: int, older_snap: int, path: Optional[str] = None, file_id: Optional[str] = None
) -> UriBuilder:
    assert (path is not None) ^ (
        file_id is not None
    ), f'One of path ({path}) or id ({file_id}) is required'
    file_ref = str(path if path else file_id)

    return UriBuilder(
        path=f'/v2/snapshots/{newer_snap:d}/changes-since/{older_snap:d}/files'
    ).add_path_component(file_ref)


@request.request
def get_snapshot_file_diff(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    path: Optional[str] = None,
    file_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)
    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)

    return conninfo.send_request('GET', str(uri))


@request.request
def get_all_snapshot_file_diff(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    newer_snap: int,
    older_snap: int,
    path: Optional[str] = None,
    file_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> request.PagingIterator:
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)

    def get_a_snapshot_file_diff(uri: UriBuilder) -> request.RestResponse:
        return conninfo.send_request('GET', str(uri))

    return request.PagingIterator(str(uri), get_a_snapshot_file_diff, page_size=limit)


@request.request
def lock_snapshot(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    snapshot_id: int,
    lock_key_ref: str,
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v3/snapshots/{snapshot_id}/lock'
    body = {'lock_key_ref': f'{lock_key_ref}'}
    return conninfo.send_request(method, uri, body=body)


@request.request
def unlock_snapshot(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    snapshot_id: int,
    signature: str,
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v3/snapshots/{snapshot_id}/unlock'
    body = {'signature': f'{signature}'}
    return conninfo.send_request(method, uri, body=body)


@request.request
def get_unlock_challenge_snapshot(
    conninfo: request.Connection, _credentials: Optional[Credentials], snapshot_id: int
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v3/snapshots/{snapshot_id}/unlock-challenge'
    return conninfo.send_request(method, uri, body=None)
