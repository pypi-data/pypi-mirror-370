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


from typing import Dict, Mapping, Optional, Sequence, Union

import qumulo.lib.obj as obj
import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


class NFSExportRestriction(obj.Object):
    """
    A representation of the restrictions one can place on an individual NFS
    export. Each export must have one or more of these objects.

    A NFSExportRestriction object specifies

      * Whether the export is read_only (otherwise it is read/write).
      * Whether the export can only be mounted by clients coming from a
        privileged port (those less than 1024).
      * What hosts (IP addresses) are allowed to mount the export.
      * Whether to treat certain or all users as ("map" them to) a specific user
        identity.
    """

    @classmethod
    def create_default(cls) -> 'NFSExportRestriction':
        return cls(
            {
                'read_only': False,
                'require_privileged_port': False,
                'host_restrictions': [],
                'user_mapping': 'NFS_MAP_ROOT',
                'map_to_user': {'id_type': 'LOCAL_USER', 'id_value': 'guest'},
            }
        )


@request.request
def get_nfs_config(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Retrieve current NFS server configuration.
    """

    method = 'GET'
    uri = '/v2/nfs/settings'

    return conninfo.send_request(method, uri)


@request.request
def set_nfs_config(
    conninfo: request.Connection, _credentials: Optional[Credentials], config: Mapping[str, bool]
) -> request.RestResponse:
    """
    Modify current NFS server configuration.
    """

    method = 'PATCH'
    uri = '/v2/nfs/settings'

    return conninfo.send_request(method, uri, body=config)


@request.request
def nfs_list_exports(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Return all the NFS exports configured in the system for the tenant.
    """
    method = 'GET'

    return conninfo.send_request(method, '/v3/nfs/exports/')


@request.request
def nfs_add_export(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    export_path: str,
    fs_path: str,
    description: str,
    restrictions: Sequence[NFSExportRestriction],
    allow_fs_path_create: bool = False,
    tenant_id: Optional[int] = None,
    fields_to_present_as_32_bit: Optional[Sequence[str]] = None,
) -> request.RestResponse:
    """
    Add an NFS export which exports a given filesystem path (fs_path), allowing
    clients to mount that path using the given export_path.

    @param export_path: The path clients will use to specify this export as the
        one to mount. Essentially, the public name of the export.
    @param fs_path: The true path in the Qumulo file system which will then be
        mounted. Clients will not normally be aware of this path when mounting;
        and through the export will not be able to see files/directories outside
        of this path.
    @param description: A description of the export, for administrative
        reference.
    @param restrictions: a list of NFSExportRestriction objects representing
        restrictions on the ways the export can be used (See
        NFSExportRestriction for details).

        The restriction that applies to a given client connection is the first
        one in the list whose "host_restrictions" field includes the client's
        IP address.
    @param allow_fs_path_create: When true, the server will create the fs_path
        directories if they don't exist already.
    @param tenant_id: The tenant that this export will be accessible to.
    @param fields_to_present_as_32_bit a list of field types that should be
        forced to fit in 32bit integers for mounts of this export.  This is
        useful for supporting legacy clients / applictations.  The following
        fields are supported:
        "FILE_IDS" - Hash large file IDs (inode numbers) to fit in 32bits.
            This is known to be necessary for certain deprecated linux system
            calls (e.g. to list a directory) to work. This might break
            applications that try to use inode number to uniquely identify
            files, e.g. rsync hardlink detection.
        "FS_SIZE" - Saturate reported total, used, and free space to 4GiB.
            This is the information that feeds tools like "df".  Note
            that this does not (directly) limit space that is actually available
            to the application.
        "FILE_SIZES" - Saturate size reported for large files to 4GiB.
            This should be used with caution, as it could result in serious
            misbehavior by 64bit applications accessing larger files via this
            export.
    """
    method = 'POST'
    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    uri = str(
        UriBuilder(path='/v3/nfs/exports/', rstrip_slash=False).add_query_param(
            'allow-fs-path-create', allow_fs_path_create_
        )
    )

    export_info: Dict[str, object] = {
        'export_path': export_path,
        'fs_path': fs_path,
        'description': description,
        'restrictions': [r.dictionary() for r in restrictions],
    }
    if tenant_id is not None:
        export_info['tenant_id'] = tenant_id
    if fields_to_present_as_32_bit is not None:
        export_info['fields_to_present_as_32_bit'] = fields_to_present_as_32_bit

    return conninfo.send_request(method, uri, body=export_info)


@request.request
def nfs_get_export(
    conninfo: request.Connection, _credentials: Optional[Credentials], export_id: Union[int, str]
) -> request.RestResponse:
    """
    Return a specific NFS export, specified by its ID.
    """

    method = 'GET'
    uri = f'/v3/nfs/exports/{export_id}'
    return conninfo.send_request(method, uri)


@request.request
def nfs_modify_export(
    conninfo: request.Connection,
    _credentials: Optional[Credentials],
    export_id: Union[int, str],
    export_path: Optional[str] = None,
    fs_path: Optional[str] = None,
    description: Optional[str] = None,
    restrictions: Optional[Sequence[NFSExportRestriction]] = None,
    allow_fs_path_create: bool = False,
    tenant_id: Optional[int] = None,
    fields_to_present_as_32_bit: Optional[Sequence[str]] = None,
    if_match: Optional[str] = None,
) -> request.RestResponse:
    """
    Set all the aspects of an export, specified by ID, to the values given.
    See @ref nfs_add_export for detailed descriptions of arguments.
    """

    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    method = 'PATCH'
    uri = str(
        UriBuilder(path=f'/v3/nfs/exports/{export_id}').add_query_param(
            'allow-fs-path-create', allow_fs_path_create_
        )
    )

    export_info: Dict[str, object] = {}
    if export_path is not None:
        export_info['export_path'] = export_path
    if fs_path is not None:
        export_info['fs_path'] = fs_path
    if description is not None:
        export_info['description'] = description
    if restrictions is not None:
        export_info['restrictions'] = [r.dictionary() for r in restrictions]
    if tenant_id is not None:
        export_info['tenant_id'] = tenant_id
    if fields_to_present_as_32_bit is not None:
        export_info['fields_to_present_as_32_bit'] = fields_to_present_as_32_bit

    return conninfo.send_request(method, uri, body=export_info, if_match=if_match)


@request.request
def nfs_delete_export(
    conninfo: request.Connection, _credentials: Optional[Credentials], export_id: Union[int, str]
) -> request.RestResponse:
    """
    Delete an NFS export, specified by its ID.
    """

    method = 'DELETE'
    uri = f'/v3/nfs/exports/{export_id}'
    return conninfo.send_request(method, uri)
