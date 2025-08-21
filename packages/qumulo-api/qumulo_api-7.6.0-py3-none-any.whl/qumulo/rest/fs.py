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

import base64
import http.client as httplib
import json
import select
import sys

from enum import Enum
from typing import (
    Any,
    AnyStr,
    Callable,
    cast,
    Dict,
    IO,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Union,
)

import qumulo.lib.request as request

from qumulo.lib import log
from qumulo.lib.auth import Credentials
from qumulo.lib.identity_util import ApiIdentity, Identity
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection, RequestError
from qumulo.lib.uri import UriBuilder

try:
    from qumulo.lib.keys import KeyOps

    can_load_private_keys = True
except ImportError:
    can_load_private_keys = False


@request.request
def read_fs_stats(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/file-system'
    return conninfo.send_request(method, str(uri))


def ref(path: Optional[str], id_: Optional[str]) -> str:
    """
    A "ref" is either a path or file ID. Here, given an argument for both,
    where only one is really present, return the ref.
    """
    assert (path is not None) ^ (id_ is not None), 'One of path or id is required'
    if path is not None and not path.startswith('/'):
        raise ValueError('Path must be absolute.')
    return path if path is not None else str(id_)


@request.request
def set_acl(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    control: Optional[Iterable[str]] = None,
    aces: Optional[Iterable[Mapping[str, object]]] = None,
    if_match: Optional[str] = None,
    posix_special_permissions: Optional[Iterable[str]] = None,
) -> request.RestResponse:
    if control is None or aces is None:
        raise ValueError('Must specify both control flags and ACEs')

    # Don't require POSIX special permissions in the input ACL
    if not posix_special_permissions:
        posix_special_permissions = []

    uri = build_files_uri([ref(path, id_), 'info', 'acl'])

    if_match = None if not if_match else str(if_match)

    config = {
        'aces': list(aces),
        'control': list(control),
        'posix_special_permissions': list(posix_special_permissions),
    }
    method = 'PUT'

    return conninfo.send_request(method, str(uri), body=config, if_match=if_match)


@request.request
def set_acl_v2(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    acl: Mapping[str, object],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(path, id_), 'info', 'acl'], api_version=2)
    if_match = None if not if_match else str(if_match)
    method = 'PUT'
    return conninfo.send_request(method, str(uri), body=acl, if_match=if_match)


@request.request
def get_file_attr(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    id_: Optional[str] = None,
    path: Optional[str] = None,
    snapshot: Optional[int] = None,
    retrieve_file_lock: bool = False,
    stream_id: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'

    uri = None
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'attributes'])
    else:
        uri = build_files_uri([ref(path, id_), 'info', 'attributes'])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)
    if retrieve_file_lock:
        uri.add_query_param('retrieve-file-lock', True)

    return conninfo.send_request(method, str(uri))


class FSIdentity:
    def __init__(self, id_type: str, value: object) -> None:
        self.id_type = id_type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FSIdentity):
            return NotImplemented

        return self.id_type == other.id_type and self.value == other.value

    def body(self) -> Dict[str, str]:
        return {'id_type': self.id_type, 'id_value': str(self.value)}


class NFSUID(FSIdentity):
    def __init__(self, uid: object) -> None:
        super().__init__('NFS_UID', uid)


class NFSGID(FSIdentity):
    def __init__(self, gid: object) -> None:
        super().__init__('NFS_GID', gid)


class SMBSID(FSIdentity):
    def __init__(self, sid: object) -> None:
        super().__init__('SMB_SID', sid)


class LocalUser(FSIdentity):
    def __init__(self, name: object) -> None:
        super().__init__('LOCAL_USER', str_decode(name))


class LocalGroup(FSIdentity):
    def __init__(self, name: object) -> None:
        super().__init__('LOCAL_GROUP', str_decode(name))


class InternalIdentity(FSIdentity):
    def __init__(self, name: object) -> None:
        super().__init__('INTERNAL', name)


@request.request
def set_file_attr(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    mode: Optional[str] = None,
    owner: Optional[Union[str, FSIdentity]] = None,
    group: Optional[Union[str, FSIdentity]] = None,
    size: Optional[object] = None,
    creation_time: Optional[str] = None,
    access_time: Optional[str] = None,
    modification_time: Optional[str] = None,
    change_time: Optional[str] = None,
    id_: Optional[str] = None,
    extended_attributes: Optional[Mapping[str, bool]] = None,
    if_match: Optional[str] = None,
    path: Optional[str] = None,
    stream_id: Optional[str] = None,
) -> request.RestResponse:
    """
    Updates select file attributes on the specified file system object.
    Attributes that are not to be updated should have None specified as
    their values.
    """
    method = 'PATCH'

    uri = None
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'attributes'])
    else:
        uri = build_files_uri([ref(path, id_), 'info', 'attributes'])

    if_match = None if not if_match else str(if_match)
    config: Dict[str, object] = {}
    if mode is not None:
        config['mode'] = str(mode)

    if owner is not None:
        if isinstance(owner, FSIdentity):
            config['owner_details'] = owner.body()
        else:
            config['owner'] = str(owner)

    if group is not None:
        if isinstance(group, FSIdentity):
            config['group_details'] = group.body()
        else:
            config['group'] = str(group)

    if size is not None:
        config['size'] = str(size)

    if creation_time is not None:
        config['creation_time'] = str(creation_time)

    if access_time is not None:
        config['access_time'] = str(access_time)

    if modification_time is not None:
        config['modification_time'] = str(modification_time)

    if change_time is not None:
        config['change_time'] = str(change_time)

    if extended_attributes is not None:
        config['extended_attributes'] = extended_attributes

    return conninfo.send_request(method, str(uri), body=config, if_match=if_match)


@request.request
def write_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    data_file: IO[AnyStr],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    if_match: Optional[str] = None,
    offset: Optional[int] = None,
    stream_id: Optional[str] = None,
) -> request.RestResponse:
    """
    @param data_file The data to be written to the file
    @param path      Path to the file. If None, id must not be None
    @param id        File id of the file. If None, path must not be None
    @param if_match  If not None, it will be the etag to use
    @param offset    The position to write in the file.
                     If None, the contents will be completely replaced
    """
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'data'])
    else:
        uri = build_files_uri([ref(path, id_), 'data'])

    if_match = None if not if_match else str(if_match)
    if offset is None:
        method = 'PUT'
    else:
        method = 'PATCH'
        uri = uri.add_query_param('offset', offset)

    return conninfo.send_request(
        method,
        str(uri),
        body_file=data_file,
        if_match=if_match,
        request_content_type=request.CONTENT_TYPE_BINARY,
        chunked=True,
    )


class CopyProgressTracker(Protocol):
    def update_to_completion(self) -> None:
        ...

    def update(self, copied_bytes: int) -> None:
        ...


@request.request
def copy(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    source_path: Optional[str] = None,
    source_id: Optional[str] = None,
    source_snapshot: Optional[int] = None,
    target_path: Optional[str] = None,
    target_id: Optional[str] = None,
    source_stream_id: Optional[str] = None,
    target_stream_id: Optional[str] = None,
    source_etag: Optional[str] = None,
    target_etag: Optional[str] = None,
    progress_tracker: Optional[CopyProgressTracker] = None,
) -> str:
    method = 'POST'

    source_ref = ref(source_path, source_id)
    source_ref_key = 'source_id' if source_id else 'source_path'

    target_ref = ref(target_path, target_id)
    if target_stream_id:
        uri = build_files_uri([target_ref, 'streams', target_stream_id])
    else:
        uri = build_files_uri([target_ref])
    uri.add_path_component('copy-chunk')

    body: Dict[str, object] = {source_ref_key: source_ref}

    if source_stream_id is not None:
        body['source_stream_id'] = source_stream_id

    if source_etag is not None:
        body['source_etag'] = source_etag

    if source_snapshot:
        body.update({'source_snapshot': source_snapshot})

    do_request = lambda body, etag: conninfo.send_request(  # noqa: E731
        method, str(uri), body=body, if_match=etag
    )

    result = body
    last_copied_offset = 0
    while True:
        result, target_etag = do_request(result, target_etag)
        if not result:
            if progress_tracker is not None:
                progress_tracker.update_to_completion()
            break

        new_offset = int(cast(str, result['target_offset']))
        copied_bytes = new_offset - last_copied_offset
        last_copied_offset = new_offset

        if progress_tracker is not None:
            progress_tracker.update(copied_bytes)

    assert target_etag is not None
    return target_etag


@request.request
def get_acl(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(path, id_), 'info', 'acl'])

    method = 'GET'

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    return conninfo.send_request(method, str(uri))


@request.request
def get_acl_v2(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(path, id_), 'info', 'acl'], api_version=2)
    if snapshot:
        uri.add_query_param('snapshot', snapshot)
    return conninfo.send_request('GET', str(uri))


@request.request
def read_directory(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    page_size: Optional[int] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
    smb_pattern: Optional[str] = None,
) -> request.RestResponse:
    """
    @param page_size   How many entries to return
    @param path        Directory to read, by path
    @param id_         Directory to read, by ID
    @param snapshot    Snapshot ID of directory to read
    @param smb_pattern SMB style match pattern.
    """
    uri = build_files_uri([ref(path, id_), 'entries']).append_slash()

    method = 'GET'

    if page_size is not None:
        uri.add_query_param('limit', page_size)

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    if smb_pattern:
        uri.add_query_param('smb-pattern', smb_pattern)

    return conninfo.send_request(method, str(uri))


@request.request
def read_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    file_: IO[bytes],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
    offset: Optional[int] = None,
    length: Optional[int] = None,
    stream_id: Optional[str] = None,
) -> request.RestResponse:
    uri = None
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'data'])
    else:
        uri = build_files_uri([ref(path, id_), 'data'])

    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    if offset is not None:
        uri.add_query_param('offset', offset)
    if length is not None:
        uri.add_query_param('length', length)

    method = 'GET'
    return conninfo.send_request(method, str(uri), response_file=file_)


@request.request
def create_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config = {'name': str(name).rstrip('/'), 'action': 'CREATE_FILE'}

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


DEVICE_TYPES = ('FS_FILE_TYPE_UNIX_BLOCK_DEVICE', 'FS_FILE_TYPE_UNIX_CHARACTER_DEVICE')


def validate_major_minor_numbers(file_type: str, major_minor_numbers: Optional[object]) -> None:
    if file_type in DEVICE_TYPES:
        if major_minor_numbers is None:
            raise ValueError('major_minor_numbers required for ' + file_type)
    elif major_minor_numbers is not None:
        raise ValueError('cannot use major_minor_numbers with ' + file_type)


@request.request
def create_unix_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    file_type: str,
    major_minor_numbers: Optional[Mapping[str, int]] = None,
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config: Dict[str, object] = {
        'name': str(name).rstrip('/'),
        'action': 'CREATE_UNIX_FILE',
        'unix_file_type': file_type,
    }

    validate_major_minor_numbers(file_type, major_minor_numbers)

    if major_minor_numbers is not None:
        config['major_minor_numbers'] = major_minor_numbers

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


@request.request
def create_directory(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config = {'name': str(name), 'action': 'CREATE_DIRECTORY'}

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


@request.request
def create_symlink(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    target: Union[str, bytes],
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
    target_type: Optional[str] = None,
) -> request.RestResponse:
    # symlink targets are expected to be a utf-8 string in QFSD, so restrict
    # the target parameter to being byte arrays that can be decoded to a utf-8
    # string, or a string. This aligns with the behavior of read_file which
    # returns a utf-8 string as a byte array
    if isinstance(target, bytes):
        target = target.decode()
    else:
        assert isinstance(target, str)

    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config = {'name': str(name).rstrip('/'), 'old_path': target, 'action': 'CREATE_SYMLINK'}
    if target_type is not None:
        config['symlink_target_type'] = target_type

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


@request.request
def create_link(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    target: Union[str, bytes],
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config = {'name': str(name).rstrip('/'), 'old_path': str(target), 'action': 'CREATE_LINK'}

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


@request.request
def rename(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    name: str,
    source: str,
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
    clobber: bool = False,
) -> request.RestResponse:
    """
    Rename a file or directory from the full path "source" to the destination
    directory (parent of the new location) specified by either dir_path or
    dir_id and new name "name".
    """
    uri = build_files_uri([ref(dir_path, dir_id), 'entries']).append_slash()

    config = {
        'name': str(name).rstrip('/'),
        'old_path': str(source),
        'action': 'RENAME',
        'clobber': clobber,
    }

    method = 'POST'
    return conninfo.send_request(method, str(uri), body=config)


@request.request
def delete(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(path, id_)])
    method = 'DELETE'
    return conninfo.send_request(method, str(uri))


@request.request
def unlink(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    entry_name: str,
    dir_path: Optional[str] = None,
    dir_id: Optional[str] = None,
) -> request.RestResponse:
    uri = build_files_uri([ref(dir_path, dir_id), 'entries', entry_name])
    method = 'DELETE'
    return conninfo.send_request(method, str(uri))


@request.request
def read_dir_aggregates(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    recursive: bool = False,
    max_entries: Optional[int] = None,
    max_depth: Optional[int] = None,
    order_by: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    method = 'GET'

    aggregate = 'recursive-aggregates' if recursive else 'aggregates'
    uri = build_files_uri([ref(path, id_), aggregate]).append_slash()

    if max_entries is not None:
        uri.add_query_param('max-entries', max_entries)
    if max_depth is not None:
        uri.add_query_param('max-depth', max_depth)
    if order_by is not None:
        uri.add_query_param('order-by', order_by)
    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    return conninfo.send_request(method, str(uri))


@request.request
def get_file_samples(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: str,
    count: int,
    by_value: str,
    id_: Optional[str] = None,
) -> request.RestResponse:
    method = 'GET'

    uri = build_files_uri([ref(path, id_), 'sample']).append_slash()
    uri.add_query_param('by-value', by_value)
    uri.add_query_param('limit', count)

    return conninfo.send_request(method, str(uri))


@request.request
def resolve_paths(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    ids: List[str],
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = build_files_uri(['resolve'])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    return conninfo.send_request(method, str(uri), body=ids)


@request.request
def punch_hole(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    offset: int,
    size: int,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    if_match: Optional[str] = None,
    stream_id: Optional[str] = None,
) -> request.RestResponse:
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'punch-hole'])
    else:
        uri = build_files_uri([ref(path, id_), 'punch-hole'])

    if_match = None if not if_match else str(if_match)
    body = {'offset': str(offset), 'size': str(size)}
    return conninfo.send_request('POST', str(uri), body=body, if_match=if_match)


# __        __    _ _
# \ \      / /_ _(_) |_ ___ _ __ ___
#  \ \ /\ / / _` | | __/ _ \ '__/ __|
#   \ V  V / (_| | | ||  __/ |  \__ \
#    \_/\_/ \__,_|_|\__\___|_|  |___/
#  FIGLET: Waiters
#
VALID_WAITER_PROTO_TYPE_COMBINATIONS = [('nlm', 'byte-range')]


@request.request
def list_waiters_by_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    snapshot_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    assert (protocol, lock_type) in VALID_WAITER_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type, 'waiters'], append_slash=True
    )
    if limit:
        uri.add_query_param('limit', limit)
    if after:
        uri.add_query_param('after', after)
    if snapshot_id:
        uri.add_query_param('snapshot', snapshot_id)
    return conninfo.send_request('GET', str(uri))


@request.request
def list_waiters_by_client(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    owner_name: Optional[str] = None,
    owner_address: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    assert (protocol, lock_type) in VALID_WAITER_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(['locks', protocol, lock_type, 'waiters'], append_slash=True)
    if limit:
        uri.add_query_param('limit', limit)
    if after:
        uri.add_query_param('after', after)
    if owner_name:
        uri.add_query_param('owner_name', owner_name)
    if owner_address:
        uri.add_query_param('owner_address', owner_address)
    return conninfo.send_request('GET', str(uri))


@request.request
def list_all_waiters_by_file(
    conninfo: Connection,
    credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    snapshot_id: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, object]]:
    """
    Re-assembles the paginated list of lock waiters for the given file.
    """
    result = list_waiters_by_file(
        conninfo, credentials, protocol, lock_type, file_path, file_id, snapshot_id, limit
    )
    return _get_remaining_pages_for_list_lock_requests(
        conninfo, credentials, result, limit, req_type='waiters'
    )


@request.request
def list_all_waiters_by_client(
    conninfo: Connection,
    credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    owner_name: Optional[str] = None,
    owner_address: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, object]]:
    """
    Re-assembles the paginated list of lock waiters for the given client.
    """
    result = list_waiters_by_client(
        conninfo, credentials, protocol, lock_type, owner_name, owner_address, limit
    )
    return _get_remaining_pages_for_list_lock_requests(
        conninfo, credentials, result, limit, req_type='waiters'
    )


#  _               _
# | |    ___   ___| | _____
# | |   / _ \ / __| |/ / __|
# | |__| (_) | (__|   <\__ \
# |_____\___/ \___|_|\_\___/
# FIGLET: Locks

VALID_LOCK_PROTO_TYPE_COMBINATIONS = [
    ('smb', 'byte-range'),
    ('smb', 'share-mode'),
    ('nlm', 'byte-range'),
    ('nfs4', 'byte-range'),
]


def validate_lock_proto_type_combination(protocol: str, lock_type: str) -> None:
    if (protocol, lock_type) not in VALID_LOCK_PROTO_TYPE_COMBINATIONS:
        raise RequestError(
            400,
            'Invalid request',
            {
                'error_class': 'invalid_request_error',
                'description': (
                    f'Listing lock type {lock_type} for protocol {protocol} is not a supported'
                    f' operation! Supported operations are {VALID_LOCK_PROTO_TYPE_COMBINATIONS}'
                ),
            },
        )


@request.request
def list_locks_by_file(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    snapshot_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    validate_lock_proto_type_combination(protocol, lock_type)
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type], append_slash=True
    )
    if limit:
        uri.add_query_param('limit', limit)
    if after:
        uri.add_query_param('after', after)
    if snapshot_id:
        uri.add_query_param('snapshot', snapshot_id)
    return conninfo.send_request('GET', str(uri))


@request.request
def list_locks_by_client(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    owner_name: Optional[str] = None,
    owner_address: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None,
) -> request.RestResponse:
    validate_lock_proto_type_combination(protocol, lock_type)
    uri = build_files_uri(['locks', protocol, lock_type], append_slash=True)
    if limit:
        uri.add_query_param('limit', limit)
    if after:
        uri.add_query_param('after', after)
    if owner_name:
        uri.add_query_param('owner_name', owner_name)
    if owner_address:
        uri.add_query_param('owner_address', owner_address)
    return conninfo.send_request('GET', str(uri))


def _get_remaining_pages_for_list_lock_requests(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    result: request.RestResponse,
    limit: int,
    req_type: str = 'grants',
) -> List[Dict[str, object]]:
    """
    Given the first page of a lock grant listing, retrieves all subsequent
    pages, and returns the complete grant list.
    @p req_type can either be 'grants' or 'waiters'
    """
    full_list = result.data[req_type]
    while len(result.data[req_type]) == limit:
        # If we got a full page, there are probably more pages.  Waiting for
        # an empty page would also be reasonable, but carries the risk of
        # never terminating if clients are frequently taking new locks.
        result = conninfo.send_request('GET', result.data['paging']['next'])
        full_list += result.data[req_type]
    return full_list


@request.request
def list_all_locks_by_file(
    conninfo: Connection,
    credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    snapshot_id: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, object]]:
    """
    Re-assembles the paginated list of lock grants for the given file.
    """
    result = list_locks_by_file(
        conninfo, credentials, protocol, lock_type, file_path, file_id, snapshot_id, limit
    )
    return _get_remaining_pages_for_list_lock_requests(conninfo, credentials, result, limit)


@request.request
def list_all_locks_by_client(
    conninfo: Connection,
    credentials: Optional[Credentials],
    protocol: str,
    lock_type: str,
    owner_name: Optional[str] = None,
    owner_address: Optional[str] = None,
    limit: int = 1000,
) -> List[Dict[str, object]]:
    """
    Re-assembles the paginated list of lock grants for the given client.
    """
    result = list_locks_by_client(
        conninfo, credentials, protocol, lock_type, owner_name, owner_address, limit
    )
    return _get_remaining_pages_for_list_lock_requests(conninfo, credentials, result, limit)


@request.request
def release_nlm_locks_by_client(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    owner_name: Optional[str] = None,
    owner_address: Optional[str] = None,
) -> request.RestResponse:
    assert owner_name or owner_address
    protocol, lock_type = 'nlm', 'byte-range'
    uri = build_files_uri(['locks', protocol, lock_type], append_slash=True)
    if owner_name:
        uri.add_query_param('owner_name', owner_name)
    if owner_address:
        uri.add_query_param('owner_address', owner_address)
    return conninfo.send_request('DELETE', str(uri))


@request.request
def release_nlm_lock(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    offset: int,
    size: int,
    owner_id: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    protocol, lock_type = 'nlm', 'byte-range'
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type], append_slash=True
    )
    uri.add_query_param('offset', offset)
    uri.add_query_param('size', size)
    uri.add_query_param('owner_id', owner_id)
    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    return conninfo.send_request('DELETE', str(uri))


#  _   _      _
# | | | | ___| |_ __   ___ _ __ ___
# | |_| |/ _ \ | '_ \ / _ \ '__/ __|
# |  _  |  __/ | |_) |  __/ |  \__ \
# |_| |_|\___|_| .__/ \___|_|  |___/
#              |_|
#
def build_files_uri(
    components: Iterable[str], append_slash: bool = False, api_version: int = 1
) -> UriBuilder:
    uri = UriBuilder(path=f'/v{api_version}/files')

    if components:
        for component in components:
            uri.add_path_component(component)

    if append_slash:
        uri.append_slash()

    return uri


# Return an iterator that reads an entire directory. Each iteration returns a
# page of files, which will be the specified page size or less.
@request.request
def read_entire_directory(
    conninfo: Connection,
    credentials: Optional[Credentials],
    page_size: Optional[int] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
    smb_pattern: Optional[str] = None,
) -> Iterator[request.RestResponse]:
    # Perform initial read_directory normally.
    result = read_directory(
        conninfo,
        credentials,
        page_size=page_size,
        path=path,
        id_=id_,
        snapshot=snapshot,
        smb_pattern=smb_pattern,
    )
    next_uri = result.data['paging']['next']
    yield result

    while next_uri != '':
        # Perform raw read_directory with paging URI.
        result = conninfo.send_request('GET', next_uri)
        next_uri = result.data['paging']['next']
        yield result


@request.request
def enumerate_entire_directory(
    conninfo: Connection, credentials: Optional[Credentials], **kwargs: Any
) -> Iterator[request.RestResponse]:
    """
    Same as @ref read_entire_directory but hides the paging mechanism and yields
    individual directory entries.
    """
    for result in read_entire_directory(conninfo, credentials, **kwargs):
        for entry in result.data['files']:
            yield request.RestResponse(entry, result.etag)


# Return an iterator that reads an entire directory. Each iteration returns a
# page of files. Any fs_no_such_entry_error returned is logged and ignored,
# ending the iteration.
def read_entire_directory_and_ignore_not_found(
    conninfo: Connection,
    credentials: Optional[Credentials],
    page_size: Optional[int] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> Iterator[request.RestResponse]:
    try:
        yield from read_entire_directory(conninfo, credentials, page_size, path, id_, snapshot)
    except request.RequestError as e:
        if e.status_code != 404 or e.error_class != 'fs_no_such_entry_error':
            raise


# Return an iterator that walks a file system tree depth-first and pre-order
@request.request
def tree_walk_preorder(
    conninfo: Connection,
    credentials: Optional[Credentials],
    path: str,
    snapshot: Optional[int] = None,
    max_depth: int = -1,
) -> Iterator[request.RestResponse]:
    def call_read_dir(
        conninfo: Connection, credentials: Optional[Credentials], id_: str, max_depth: int
    ) -> Iterator[request.RestResponse]:
        if max_depth == 0:
            return

        max_depth -= 1

        for result in read_entire_directory_and_ignore_not_found(
            conninfo, credentials, id_=id_, snapshot=snapshot
        ):
            if 'files' in result.data:
                for f in result.data['files']:
                    yield request.RestResponse(f, result.etag)

                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        yield from call_read_dir(conninfo, credentials, f['id'], max_depth)

    result = get_file_attr(conninfo, credentials, path=path, snapshot=snapshot)
    yield result

    yield from call_read_dir(conninfo, credentials, result.data['id'], max_depth)


# Return an iterator that walks a file system tree depth-first and post-order
@request.request
def tree_walk_postorder(
    conninfo: Connection,
    credentials: Optional[Credentials],
    path: str,
    snapshot: Optional[int] = None,
) -> Iterator[request.RestResponse]:
    def call_read_dir(
        conninfo: Connection, credentials: Optional[Credentials], id_: str
    ) -> Iterator[request.RestResponse]:
        for result in read_entire_directory_and_ignore_not_found(
            conninfo, credentials, id_=id_, snapshot=snapshot
        ):
            if 'files' in result.data:
                for f in result.data['files']:
                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        yield from call_read_dir(conninfo, credentials, f['id'])
                    yield request.RestResponse(f, result.etag)

    result = get_file_attr(conninfo, credentials, path=path, snapshot=snapshot)

    yield from call_read_dir(conninfo, credentials, result.data['id'])

    yield result


@request.request
def acl_explain_posix_mode(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-posix-mode'])

    return conninfo.send_request(method, str(uri))


@request.request
def acl_explain_chmod(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    mode: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-set-mode'])

    return conninfo.send_request(method, str(uri), body={'mode': mode})


IdentityTypes = Union[ApiIdentity, Identity, str]


@request.request
def acl_explain_rights(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    user: IdentityTypes,
    group: IdentityTypes,
    ids: Optional[Iterable[IdentityTypes]] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    """
    @param user      User for whom to explain rights.
    @param path      Path to the file. If None, id must not be None
    @param id        File id of the file. If None, path must not be None
    @param group     User's primary group.
    @param ids       User's additional groups and related identities.
    """

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-rights'])

    payload = {'user': Identity(user).dictionary()}
    if group:
        payload['primary_group'] = Identity(group).dictionary()
    if ids:
        payload['auxiliary_identities'] = [Identity(i).dictionary() for i in ids]

    return conninfo.send_request(method, str(uri), body=payload)


#     _    ____  ____
#    / \  |  _ \/ ___|
#   / _ \ | | | \___ \
#  / ___ \| |_| |___) |
# /_/   \_\____/|____/
#  FIGLET: ADS
#


@request.request
def list_named_streams(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    path: Optional[str] = None,
    id_: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = build_files_uri([ref(path, id_), 'streams']).append_slash()

    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    return conninfo.send_request(method, str(uri))


@request.request
def create_stream(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    stream_name: str,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'
    uri = build_files_uri([ref(path, id_), 'streams']).append_slash()
    if_match = None if not if_match else str(if_match)

    config = {'stream_name': stream_name}
    return conninfo.send_request(method, str(uri), body=config, if_match=if_match)


@request.request
def remove_stream(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    stream_id: str,
    path: Optional[str] = None,
    id_: Optional[str] = None,
) -> request.RestResponse:
    method = 'DELETE'
    uri = build_files_uri([ref(path, id_), 'streams', stream_id])

    return conninfo.send_request(method, str(uri))


@request.request
def rename_stream(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    old_id: str,
    new_name: str,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'POST'

    uri = build_files_uri([ref(path, id_), 'streams', old_id, 'rename'])
    if_match = None if not if_match else str(if_match)
    config = {'stream_name': new_name}
    return conninfo.send_request(method, str(uri), body=config, if_match=if_match)


#   ____ _                              _   _       _   _  __
#  / ___| |__   __ _ _ __   __ _  ___  | \ | | ___ | |_(_)/ _|_   _
# | |   | '_ \ / _` | '_ \ / _` |/ _ \ |  \| |/ _ \| __| | |_| | | |
# | |___| | | | (_| | | | | (_| |  __/ | |\  | (_) | |_| |  _| |_| |
#  \____|_| |_|\__,_|_| |_|\__, |\___| |_| \_|\___/ \__|_|_|  \__, |
#                          |___/                              |___/
#  FIGLET: Change Notify
#


class ChangeNotifyCancelerProtocol(Protocol):
    def fileno(self) -> int:
        ...

    def read(self) -> str:
        ...


@request.request
def get_change_notify_listener(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    recursive: bool,
    type_filter: Optional[Iterable[str]] = None,
    path: Optional[str] = None,
    id_: Optional[str] = None,
    canceler: Optional[ChangeNotifyCancelerProtocol] = None,
) -> request.RestResponse:
    method = 'GET'
    uri = build_files_uri([ref(path, id_), 'notify'])
    uri = uri.add_query_param('recursive', recursive)
    if type_filter:
        uri = uri.add_query_param('filter', ','.join(type_filter))

    resp = conninfo.send_request(method, str(uri))
    if isinstance(resp.data, httplib.HTTPResponse):
        resp = request.RestResponse(ChangesIterator(resp.data, canceler=canceler), resp.etag)
    return resp


class ChangeNotifyDataProtocol(Protocol):
    def readline(self) -> bytes:
        ...

    def fileno(self) -> int:
        ...


class ChangesIterator:
    def __init__(
        self,
        data: ChangeNotifyDataProtocol,
        canceler: Optional[ChangeNotifyCancelerProtocol] = None,
        select_fn: Callable[
            [Iterable[int], Iterable[int], Iterable[int], float],
            Tuple[Iterable[int], Iterable[int], Iterable[int]],
        ] = select.select,
    ) -> None:
        self.data = data
        self.canceler = canceler
        self.select_fn = select_fn
        self.cache: List[str] = []
        self._started = False
        self._alive = True

        self.data_fd = data.fileno()
        self.canceler_fd = canceler.fileno() if canceler is not None else None

        self.fds = [self.data_fd]
        if self.canceler_fd is not None:
            self.fds.append(self.canceler_fd)

    def started(self) -> bool:
        if not self._started:
            self._load_cache()
            if any([x.startswith(': watching') for x in self.cache]):
                self._started = True

        return self._started

    @property
    def alive(self) -> bool:
        if self._alive:
            # if the socket has died, we'll load some cache until EOF and mark the iterator dead.
            self._load_cache()

        return self._alive

    def _read_available_data(self) -> None:
        if not self._alive:
            return

        lines_read = 0
        while True:
            ready = list(self.select_fn([self.data_fd], [], [], 0.001)[0])
            # Early return if there's no data or if we want to let the iterator do some work.
            if len(ready) == 0 or lines_read == 100:
                return
            self.cache += [self.data.readline().decode()]
            lines_read += 1

            if len(self.cache[-1]) == 0:
                self._alive = False
                return

    def _load_cache(self) -> None:
        if not self._alive:
            return

        try:
            while True:
                ready = list(self.select_fn(self.fds, [], [], 60)[0])
                if len(ready) == 0:
                    self._alive = False
                for stream in ready:
                    if self.canceler_fd is not None and stream == self.canceler_fd:
                        assert self.canceler is not None
                        self.canceler.read()  # ignore anything but EOF
                    if stream == self.data_fd:
                        self._read_available_data()
                        return
        except EOFError:
            self._alive = False

    def __iter__(self) -> Iterator[object]:
        return self

    def __next__(self) -> object:
        while True:
            if len(self.cache) == 0:
                self._load_cache()
            if len(self.cache) == 0:
                raise StopIteration

            line = self.cache.pop(0)
            if len(line) == 0:
                self._alive = False
                raise EOFError('Remote socket closed')
            line = line.rstrip('\n')
            if len(line) == 0:
                continue

            data_prefix = 'data: '
            comment_prefix = ': '
            if line.startswith(comment_prefix):
                line = line[len(comment_prefix) :]
                if line.startswith(': watching'):
                    self._started = True
                log_cmd = log.debug if line == 'keepalive' else log.info
                log_cmd(line)
                continue

            elif line.startswith(data_prefix):
                return json.loads(line[len(data_prefix) :])
            else:
                raise KeyError(
                    f'expected either "{comment_prefix}<comment>" or "{data_prefix}<json>",'
                    f' received {line}'
                )


#  ____            _                               _     _
# / ___| _   _ ___| |_ ___ _ __ ___      __      _(_) __| | ___
# \___ \| | | / __| __/ _ \ '_ ` _ \ ____\ \ /\ / / |/ _` |/ _ \
#  ___) | |_| \__ \ ||  __/ | | | | |_____\ V  V /| | (_| |  __/
# |____/ \__, |___/\__\___|_| |_| |_|      \_/\_/ |_|\__,_|\___|
#        |___/
#           _   _   _
#  ___  ___| |_| |_(_)_ __   __ _ ___
# / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/\___|\__|\__|_|_| |_|\__, |___/
#                           |___/
#  FIGLET: System-wide settings
#


@request.request
def get_permissions_settings(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('GET', '/v1/file-system/settings/permissions')


@request.request
def set_permissions_settings(
    conninfo: Connection, _credentials: Optional[Credentials], mode: str
) -> request.RestResponse:
    """
    @param mode  NATIVE, _DEPRECATED_MERGED_V1, or CROSS_PROTOCOL
    """
    return conninfo.send_request('PUT', '/v1/file-system/settings/permissions', body={'mode': mode})


@request.request
def get_atime_settings(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('GET', '/v1/file-system/settings/atime')


@request.request
def set_atime_settings(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    enabled: Optional[bool] = None,
    granularity: Optional[str] = None,
) -> request.RestResponse:
    payload: Dict[str, Union[bool, str]] = {}
    if enabled is not None:
        payload['enabled'] = enabled
    if granularity is not None:
        payload['granularity'] = granularity

    return conninfo.send_request('PATCH', '/v1/file-system/settings/atime', body=payload)


@request.request
def get_notify_settings(
    conninfo: Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    return conninfo.send_request('GET', '/v1/file-system/settings/notify')


@request.request
def set_notify_settings(
    conninfo: Connection, _credentials: Optional[Credentials], recursive_mode: str
) -> request.RestResponse:
    return conninfo.send_request(
        'PUT', '/v1/file-system/settings/notify', body={'recursive_mode': recursive_mode}
    )


@request.request
def security_add_key(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    name: str,
    public_key_data: str,
    verification_signature: str,
    comment: str = '',
) -> request.RestResponse:
    uri = '/v1/file-system/security/keys/'
    body = {
        'name': name,
        'public_key': public_key_data,
        'verification_signature': verification_signature,
        'comment': comment,
    }

    method = 'POST'
    return conninfo.send_request(method, uri, body)


@request.request
def security_get_key(
    conninfo: request.Connection, _credentials: Optional[Credentials], key_ref: str
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v1/file-system/security/keys/{key_ref}'
    return conninfo.send_request(method, uri)


@request.request
def security_get_key_usage(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    key_ref: str,
    page_size: Optional[int] = None,
) -> request.PagingIterator:
    def get(uri: UriBuilder) -> request.RestResponse:
        return conninfo.send_request('GET', str(uri))

    return request.PagingIterator(f'/v1/file-system/security/keys/{key_ref}/usages', get, page_size)


@request.request
def security_modify_key(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    key_ref: str,
    name: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = f'/v1/file-system/security/keys/{key_ref}'

    body: Dict[str, Union[str, bool]] = {}
    if name is not None:
        body['name'] = name
    if comment is not None:
        body['comment'] = comment
    if disabled is not None:
        body['disabled'] = disabled

    return conninfo.send_request(method, uri, body=body)


@request.request
def security_list_keys(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/file-system/security/keys/'
    return conninfo.send_request(method, uri)


@request.request
def security_get_key_replace_challenge(
    conninfo: request.Connection, _credentials: Optional[Credentials], key_ref: str
) -> request.RestResponse:
    method = 'GET'
    uri = f'/v1/file-system/security/keys/{key_ref}/key-replacement-challenge'
    return conninfo.send_request(method, uri)


@request.request
def security_replace_key(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    key_ref: str,
    replacement_key: str,
    old_key_verification_signature: str,
    replacement_key_verification_signature: str,
) -> request.RestResponse:
    method = 'POST'
    uri = f'/v1/file-system/security/keys/{key_ref}/replace'

    body = {
        'replacement_key': replacement_key,
        'old_key_verification_signature': old_key_verification_signature,
        'replacement_key_verification_signature': replacement_key_verification_signature,
    }

    return conninfo.send_request(method, uri, body)


def get_verified_public_key(private_key_data: str, challenge: str) -> Tuple[str, str]:
    if not can_load_private_keys:
        print(
            'In order to use a private key file, first install the Python cryptography package'
            ' by running the following command:\n  pip install cryptography',
            file=sys.stderr,
        )
        sys.exit(1)

    ops = KeyOps(private_key_data)
    return ops.public_bytes_as_base64(), ops.sign(challenge)


@request.request
def security_delete_key(
    conninfo: request.Connection, _credentials: Optional[Credentials], key_ref: str
) -> request.RestResponse:
    method = 'DELETE'
    uri = f'/v1/file-system/security/keys/{key_ref}'
    return conninfo.send_request(method, uri)


#  _   _                 __  __      _            _       _
# | | | |___  ___ _ __  |  \/  | ___| |_ __ _  __| | __ _| |_ __ _
# | | | / __|/ _ \ '__| | |\/| |/ _ \ __/ _` |/ _` |/ _` | __/ _` |
# | |_| \__ \  __/ |    | |  | |  __/ || (_| | (_| | (_| | || (_| |
#  \___/|___/\___|_|    |_|  |_|\___|\__\__,_|\__,_|\__,_|\__\__,_|
#  FIGLET: User Metadata
#


# Keep this in sync with fs_user_metadata_type
class UserMetadataType(Enum):
    GENERIC = 'generic'
    S3 = 's3'


@request.request
def get_user_metadata(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    type_: UserMetadataType,
    key: str,
    id_: Optional[str] = None,
    path: Optional[str] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    method = 'GET'

    uri = build_files_uri([ref(path, id_), 'user-metadata', type_.value, key])

    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)

    response, etag = conninfo.send_request(method, str(uri))

    return request.RestResponse(base64.b64decode(response['value']), etag=etag)


@request.request
def set_user_metadata(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    type_: UserMetadataType,
    key: str,
    value: bytes,
    id_: Optional[str] = None,
    path: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'PUT'

    uri = build_files_uri([ref(path, id_), 'user-metadata', type_.value, key])

    return conninfo.send_request(
        method, str(uri), body={'value': base64.b64encode(value).decode('utf8')}, if_match=if_match
    )


@request.request
def delete_user_metadata(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    type_: UserMetadataType,
    key: str,
    id_: Optional[str] = None,
    path: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'DELETE'

    uri = build_files_uri([ref(path, id_), 'user-metadata', type_.value, key])

    return conninfo.send_request(method, str(uri), if_match=if_match)


@request.request
def list_user_metadata(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    id_: Optional[str] = None,
    path: Optional[str] = None,
    limit: Optional[int] = None,
    type_: Optional[UserMetadataType] = None,
    snapshot: Optional[int] = None,
) -> request.PagingIterator:
    method = 'GET'

    uri_components = [ref(path, id_), 'user-metadata']
    if type_ is not None:
        uri_components.append(type_.value)

    uri = build_files_uri(uri_components, append_slash=True)

    query_params = {}
    if snapshot is not None:
        query_params['snapshot'] = snapshot

    def get_user_metadata_range(uri: UriBuilder) -> request.RestResponse:
        response = conninfo.send_request(method, str(uri))
        # XXX charward: need to make sure the index name here is the same as the name of the vector
        # in the API type.
        for record in response.data['entries']:
            record['value'] = base64.b64decode(record['value'])
        return response

    return request.PagingIterator(
        str(uri), get_user_metadata_range, page_size=limit, query_params=query_params
    )


@request.request
def get_all_user_metadata(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    id_: Optional[str] = None,
    path: Optional[str] = None,
    limit: Optional[int] = None,
    type_: Optional[UserMetadataType] = None,
    snapshot: Optional[int] = None,
) -> request.RestResponse:
    iterator = list_user_metadata(conninfo, _credentials, id_, path, limit, type_, snapshot)

    entries = []
    for _, val in enumerate(iterator):
        entries.extend(val.data['entries'])

    return request.RestResponse(entries, etag=None)


@request.request
def modify_file_lock(
    conninfo: Connection,
    _credentials: Optional[Credentials],
    retention_period: Optional[str] = None,
    legal_hold: Optional[bool] = None,
    id_: Optional[str] = None,
    path: Optional[str] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'

    uri = build_files_uri([ref(path, id_), 'file-lock'])

    config: Dict[str, object] = {}
    if retention_period is not None:
        config['retention_period'] = str(retention_period)
    if legal_hold is not None:
        config['legal_hold'] = legal_hold

    return conninfo.send_request(method, str(uri), body=config, if_match=if_match)
