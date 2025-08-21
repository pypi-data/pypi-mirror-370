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


from typing import Dict, Optional, Sequence

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection
from qumulo.lib.uri import UriBuilder


@request.request
def replicate(
    conninfo: Connection, _credentials: Optional[Credentials], relationship: str
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v2/replication/source-relationships/{relationship}/replicate'
    return conninfo.send_request(method, str(uri))


@request.request
def create_source_relationship(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    target_path: str,
    address: str,
    source_id: Optional[int] = None,
    source_path: Optional[str] = None,
    source_root_read_only: Optional[bool] = None,
    map_local_ids_to_nfs_ids: Optional[bool] = None,
    replication_enabled: Optional[bool] = None,
    target_port: Optional[int] = None,
    replication_mode: Optional[str] = None,
    snapshot_policies: Optional[Sequence[Dict[str, object]]] = None,
) -> request.RestResponse:
    body: Dict[str, object] = {'target_root_path': target_path, 'target_address': address}

    if source_id is not None:
        body['source_root_id'] = source_id

    if source_path is not None:
        body['source_root_path'] = source_path

    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only

    if target_port is not None:
        body['target_port'] = target_port

    if map_local_ids_to_nfs_ids is not None:
        body['map_local_ids_to_nfs_ids'] = map_local_ids_to_nfs_ids

    if replication_enabled is not None:
        body['replication_enabled'] = replication_enabled

    if replication_mode is not None:
        body['replication_mode'] = replication_mode

    if snapshot_policies is not None:
        body['snapshot_policies'] = snapshot_policies

    method = 'POST'
    uri = '/v2/replication/source-relationships/'
    return conninfo.send_request(method, uri, body=body)


@request.request
def list_source_relationships(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/source-relationships/'
    return conninfo.send_request(method, uri)


@request.request
def get_source_relationship(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def delete_source_relationship(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v2/replication/source-relationships/{relationship_id}'
    return conninfo.send_request(method, uri, if_match=if_match)


@request.request
def delete_target_relationship(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/delete'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def modify_source_relationship(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    new_target_address: Optional[str] = None,
    new_target_port: Optional[int] = None,
    source_root_read_only: Optional[bool] = None,
    map_local_ids_to_nfs_ids: Optional[bool] = None,
    replication_enabled: Optional[bool] = None,
    blackout_windows: Optional[Sequence[Dict[str, object]]] = None,
    blackout_window_timezone: Optional[str] = None,
    replication_mode: Optional[str] = None,
    snapshot_policies: Optional[Sequence[Dict[str, object]]] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = f'/v2/replication/source-relationships/{relationship_id}'

    body: Dict[str, object] = {}
    if new_target_address is not None:
        body['target_address'] = new_target_address
    if new_target_port is not None:
        body['target_port'] = new_target_port
    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only
    if map_local_ids_to_nfs_ids is not None:
        body['map_local_ids_to_nfs_ids'] = map_local_ids_to_nfs_ids
    if replication_enabled is not None:
        body['replication_enabled'] = replication_enabled
    if blackout_windows is not None:
        body['blackout_windows'] = blackout_windows
    if blackout_window_timezone is not None:
        body['blackout_window_timezone'] = blackout_window_timezone
    if replication_mode is not None:
        body['replication_mode'] = replication_mode
    if snapshot_policies is not None:
        body['snapshot_policies'] = snapshot_policies

    return conninfo.send_request(method, uri, body=body, if_match=if_match)


@request.request
def list_source_relationship_statuses(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/source-relationships/status/'
    return conninfo.send_request(method, uri)


@request.request
def list_target_relationship_statuses(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/target-relationships/status/'
    return conninfo.send_request(method, uri)


@request.request
def get_source_relationship_status(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}/status'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def get_target_relationship_status(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/target-relationships/{}/status'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def authorize(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    allow_non_empty_directory: Optional[bool] = None,
    allow_fs_path_create: Optional[bool] = None,
) -> request.RestResponse:
    method = 'POST'

    uri = UriBuilder(path=f'/v2/replication/target-relationships/{relationship_id}/authorize')

    if allow_non_empty_directory is not None:
        uri.add_query_param(
            'allow-non-empty-directory', 'true' if allow_non_empty_directory else 'false'
        )
    if allow_fs_path_create is not None:
        uri.add_query_param('allow-fs-path-create', 'true' if allow_fs_path_create else 'false')

    return conninfo.send_request(method, str(uri))


@request.request
def reconnect_target_relationship(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/reconnect'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def abort_replication(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    skip_active_policy_snapshot: Optional[bool] = None,
) -> request.RestResponse:
    method = 'POST'

    uri = UriBuilder(
        path=f'/v2/replication/source-relationships/{relationship_id}/abort-replication'
    )

    if skip_active_policy_snapshot is not None:
        uri.add_query_param(
            'skip-active-policy-snapshot', 'true' if skip_active_policy_snapshot else 'false'
        )

    return conninfo.send_request(method, str(uri))


@request.request
def make_target_writable(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/make-writable'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def reverse_target_relationship(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    source_address: str,
    source_port: Optional[int] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/source-relationships/reverse-target-relationship'

    body: Dict[str, object] = {
        'target_relationship_id': relationship_id,
        'source_address': source_address,
    }
    if source_port is not None:
        body['source_port'] = source_port

    return conninfo.send_request(method, uri, body=body)


@request.request
def dismiss_source_relationship_error(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/source-relationships/{}/dismiss-error'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def dismiss_target_relationship_error(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/replication/target-relationships/{}/dismiss-error'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def list_queued_snapshots(
    conninfo: Connection, _credentials: Optional[Credentials], relationship_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/replication/source-relationships/{}/queued-snapshots/'
    return conninfo.send_request(method, uri.format(relationship_id))


@request.request
def release_queued_snapshot(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    snapshot_id: str,
) -> request.RestResponse:
    method = 'DELETE'
    uri = '/v2/replication/source-relationships/{}/queued-snapshots/{}'
    return conninfo.send_request(method, uri.format(relationship_id, snapshot_id))


@request.request
def set_target_relationship_lock(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    relationship_id: str,
    lock_key: Optional[str],
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v2/replication/target-relationships/{relationship_id}/lock'
    body = {'lock_key_ref': lock_key}
    return conninfo.send_request(method, uri, body=body)
