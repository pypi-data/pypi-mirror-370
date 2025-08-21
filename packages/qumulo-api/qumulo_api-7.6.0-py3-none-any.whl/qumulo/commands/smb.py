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

"""
Share commands
"""

import argparse
import re
import sys
import textwrap

from typing import Any, Dict, IO, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Union

import qumulo.lib.opts
import qumulo.lib.request as request
import qumulo.rest.fs as fs
import qumulo.rest.smb as smb

from qumulo.lib.acl_util import AceTranslator, AclEditor
from qumulo.lib.opts import str_decode
from qumulo.lib.tenant import get_entry_id_from_entries
from qumulo.lib.util import bool_from_string, tabulate
from qumulo.rest_client import RestClient

#     _    ____ _
#    / \  / ___| |
#   / _ \| |   | |
#  / ___ \ |___| |___
# /_/   \_\____|_____|_             _       _   _
# |  \/  | __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __
# | |\/| |/ _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \
# | |  | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
# |_|  |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
#                      |_|
# FIGLET: ACL Manipulation

NO_ACCESS = 'NONE'
READ_ACCESS = 'READ'
WRITE_ACCESS = 'WRITE'
CHANGE_PERMISSIONS_ACCESS = 'CHANGE_PERMISSIONS'
ALL_ACCESS = 'ALL'
ALL_RIGHTS = (NO_ACCESS, READ_ACCESS, WRITE_ACCESS, CHANGE_PERMISSIONS_ACCESS, ALL_ACCESS)

ALLOWED_TYPE = 'ALLOWED'
DENIED_TYPE = 'DENIED'

LOCAL_DOMAIN = 'LOCAL'
WORLD_DOMAIN = 'WORLD'
POSIX_USER_DOMAIN = 'POSIX_USER'
POSIX_GROUP_DOMAIN = 'POSIX_GROUP'
AD_DOMAIN = 'ACTIVE_DIRECTORY'

EVERYONE_NAME = 'Everyone'
GUEST_NAME = 'Guest'

# A SID starts with S, followed by hyphen separated version, authority, and at
# least one sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

VALID_DOMAIN_TYPES = ('local', 'world', 'ldap_user', 'ldap_group', 'ad')
VALID_TRUSTEE_TYPES = VALID_DOMAIN_TYPES + ('name', 'sid', 'uid', 'gid', 'auth_id')


class ShareAceTranslator(AceTranslator):
    def _parse_rights(self, rights: Iterable[str]) -> List[str]:
        api_rights = [r.upper().replace(' ', '_') for r in rights]
        assert all(r in ALL_RIGHTS for r in api_rights)
        return api_rights

    def parse_rights(self, rights: Iterable[str], ace: MutableMapping[str, Any]) -> None:
        ace['rights'] = self._parse_rights(rights)

    def pretty_rights(self, ace: Mapping[str, Any]) -> str:
        # Replace the _ in CHANGE_PERMISSIONS:
        rights = [r.replace('_', ' ') for r in ace['rights']]
        rights = [r.capitalize() for r in rights]
        return ', '.join(rights)

    def ace_rights_equal(self, ace: Mapping[str, Any], rights: Iterable[str]) -> bool:
        return set(ace['rights']) == set(self._parse_rights(rights))

    @property
    def has_flags(self) -> bool:
        return False

    # Keeps pylint happy:
    def parse_flags(self, flags: Iterable[str], ace: MutableMapping[str, Any]) -> None:
        raise TypeError('SMB share aces do not have flags.')

    def pretty_flags(self, ace: Mapping[str, Any]) -> str:
        raise TypeError('SMB share aces do not have flags.')

    def ace_flags_equal(self, ace: Mapping[str, Any], flags: Iterable[str]) -> bool:
        raise TypeError('SMB share aces do not have flags.')


class NetworkAceTranslator(ShareAceTranslator):
    def parse_trustee(self, trustee: List[str], ace: MutableMapping[str, Any]) -> None:
        if trustee == ['*']:  # Star or empty means all hosts.
            ace['address_ranges'] = []
        else:
            ace['address_ranges'] = trustee

    def pretty_trustee(self, ace: Mapping[str, Any]) -> str:
        if not ace['address_ranges']:
            return '*'
        else:
            return ', '.join(ace['address_ranges'])

    def ace_trustee_equal(self, ace: Mapping[str, Any], trustee: List[str]) -> bool:
        # AclEditor calls ace_trustee_equal in modify() and remove(), and those actions are not used
        # with network permissions.
        raise TypeError('SMB share network permissions cannot be changed individually.')


def pretty_share_list(shares: Sequence[Dict[str, Any]]) -> str:
    headers = ['ID', 'Tenant ID', 'Name', 'Path', 'Description']
    rows = [
        [row['id'], row['tenant_id'], row['share_name'], row['fs_path'], row['description']]
        for row in shares
    ]
    return tabulate(rows, headers)


def get_id_from_args(rest_client: RestClient, args: argparse.Namespace, smb_mod: Any) -> int:
    def get_shares_matching_name(share_name: str) -> Dict[Optional[int], int]:
        res = smb_mod.smb_list_shares(rest_client.conninfo, rest_client.credentials)
        shares = res.data['entries']
        return {s.get('tenant_id'): s['id'] for s in shares if s['share_name'] == share_name}

    return get_entry_id_from_entries(
        args.id, args.name, args.tenant_id, 'SMB Share', get_shares_matching_name
    )


#  _     _     _     ____  _
# | |   (_)___| |_  / ___|| |__   __ _ _ __ ___  ___
# | |   | / __| __| \___ \| '_ \ / _` | '__/ _ \/ __|
# | |___| \__ \ |_   ___) | | | | (_| | | |  __/\__ \
# |_____|_|___/\__| |____/|_| |_|\__,_|_|  \___||___/
# FIGLET: List Shares


class SMBListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_shares'
    SYNOPSIS = 'List all SMB shares'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of shares.'
        )
        parser.add_argument(
            '--populate-trustee-names',
            action='store_true',
            help='Populate trustee names in the response.',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        res = smb.smb_list_shares(
            rest_client.conninfo, rest_client.credentials, args.populate_trustee_names
        )
        if args.json:
            print(res)
        else:
            print(pretty_share_list(res.data['entries']))


def _print_share(response: request.RestResponse, json_fmt: bool, outfile: IO[str]) -> None:
    if json_fmt:
        outfile.write(f'{response}\n')
    else:
        body, _etag = response
        outfile.write(
            'ID: {id}\n'
            'Tenant ID: {tenant_id}\n'
            'Name: {share_name}\n'
            'Path: {fs_path}\n'
            'Description: {description}\n'
            'Access Based Enumeration: '
            '{access_based_enumeration_enabled}\n'
            'Encryption Required: {require_encryption}\n'
            'Default File Create Mode: {default_file_create_mode}\n'
            'Default Directory Create Mode: '
            '{default_directory_create_mode}\n'.format(**body)
        )
        outfile.write('\n')
        outfile.write(
            'Permissions:\n{}\n'.format(
                AclEditor(ShareAceTranslator(), body['permissions']).pretty_str()
            )
        )
        # Network permissions are a niche feature, so don't distract people
        # by telling them all hosts are allowed all access:
        if body['network_permissions'] != smb.ALLOW_ALL_NETWORK_PERMISSIONS:
            net_editor = AclEditor(NetworkAceTranslator(), body['network_permissions'])
            outfile.write(f'\nNetwork Permissions:\n{net_editor.pretty_str()}\n')


class SMBListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_share'
    SYNOPSIS = 'List a share'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to list.')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to list.')
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='ID of the tenant to get the share from. Only used if using the --name argument.',
        )

        parser.add_argument('--json', action='store_true', help='Print the raw JSON response.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace, smb_mod: Any = smb) -> None:
        share_id = get_id_from_args(rest_client, args, smb_mod)
        _print_share(
            smb_mod.smb_list_share(rest_client.conninfo, rest_client.credentials, share_id),
            args.json,
            sys.stdout,
        )


#     _       _     _   ____  _
#    / \   __| | __| | / ___|| |__   __ _ _ __ ___
#   / _ \ / _` |/ _` | \___ \| '_ \ / _` | '__/ _ \
#  / ___ \ (_| | (_| |  ___) | | | | (_| | | |  __/
# /_/   \_\__,_|\__,_| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Add Share


def _add_initial_acl_args(parser: argparse.ArgumentParser) -> None:
    # Permissions options:
    exclusive_perms = parser.add_mutually_exclusive_group()
    exclusive_perms.add_argument('--no-access', action='store_true', help='Grant no access.')
    exclusive_perms.add_argument(
        '--read-only', action='store_true', help='Grant everyone except guest read-only access.'
    )
    exclusive_perms.add_argument(
        '--all-access', action='store_true', help='Grant everyone except guest full access.'
    )

    # These are all exclusive with read-only or no-access, but not with
    # all-access or each other, which argparse can't express:
    parser.add_argument(
        '--grant-read-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help="""
            Grant read access to the specified trustees. For example: Everyone, uid:1000, gid:1001,
            sid:S-1-5-2-3-4, auth_id:500
            """,
    )
    parser.add_argument(
        '--grant-read-write-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Grant read-write access to these trustees.',
    )
    parser.add_argument(
        '--grant-all-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Grant all access to these trustees.',
    )
    parser.add_argument(
        '--deny-access',
        type=str_decode,
        nargs='+',
        metavar='TRUSTEE',
        help='Deny all access to these trustees.',
    )


def _create_new_acl(args: argparse.Namespace) -> Sequence[object]:
    have_grants = any(
        [
            args.all_access,
            args.grant_read_access,
            args.grant_read_write_access,
            args.grant_all_access,
        ]
    )
    if args.no_access and have_grants:
        raise ValueError('Cannot specify --no-access and grant other access.')
    if args.read_only and have_grants:
        raise ValueError('Cannot specify --read-only and grant other access.')
    if not any([args.no_access, args.read_only, args.deny_access, have_grants]):
        raise ValueError(
            'Must specify initial permissions (--no-access, '
            '--read-only, --all-access, --grant-read-access, etc.)'
        )

    acl = AclEditor(ShareAceTranslator())

    # Note that order shouldn't matter, the AclEditor should always put
    # these ACEs at the beginning, so they will override any grants
    if args.deny_access:
        acl.deny(args.deny_access, [ALL_ACCESS])

    if args.read_only:
        acl.grant([EVERYONE_NAME], [READ_ACCESS])
    if args.all_access:
        acl.grant([EVERYONE_NAME], [ALL_ACCESS])
    if args.grant_read_access:
        acl.grant(args.grant_read_access, [READ_ACCESS])
    if args.grant_read_write_access:
        acl.grant(args.grant_read_write_access, [READ_ACCESS, WRITE_ACCESS])
    if args.grant_all_access:
        acl.grant(args.grant_all_access, [ALL_ACCESS])

    return acl.acl


def _add_network_permissions_args(parser: argparse.ArgumentParser) -> None:
    net_group = parser.add_argument_group(
        'Network Permissions',
        textwrap.dedent(
            """
            Provides options for controlling share access by using the client address. By default,
            all hosts have the same rights which share and file permissions grant.

            It is possible to add multiple entries for each Deny and Allow option. To add entries,
            enter a space-separated list of IP addresses or subnet ranges in CIDR notation. To
            represent all available addresses, use the wildcard "*" including the quotation marks
            (to prevent shell expansion).

            To remove all entries and return to the default state, use the --full-control-hosts flag
            with the "*" wildcard.

            Examples of acceptable entries:

            Single IP address: 172.16.33.10
            IP address ranges: 10.120.150.50-60 (.50 to .60 inclusive)
            Space-separated list of IP addresses: 10.0.10.10 10.0.10.20
            Subnet ranges in CIDR notation: 10.120.0.0/16
            Space-separated combinations of any of the above: 10.200.0.10 10.220.0.0/16 10.120.1.10-15
            """  # noqa: E501
        ),
    )
    net_group.add_argument(
        '--full-control-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='IP/RANGE',
        help="""
            The host addresses or subnet ranges for which access to to this share are not limited by
            network permissions. Access may still be limited by share and file permissions.
            """,
    )
    net_group.add_argument(
        '--read-only-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='IP/RANGE',
        help='Address ranges which should be permitted read-only access at most.',
    )
    net_group.add_argument(
        '--deny-hosts',
        type=str_decode,
        nargs='+',
        default=None,
        metavar='IP/RANGE',
        help="""
            The host addresses or subnet ranges for which access to the specified share is denied,
            regardless of other permissions. Important: Because using this flag alone results in all
            hosts being denied, use the correct --full-control-hosts or --read-only-hosts flags as
            necessary.
            """,
    )
    net_group.add_argument(
        '--deny-all-hosts',
        action='store_true',
        help="""
            Deny all access to this share. Important: To avoid configuration issues, do not apply
            this flag alongside any others.
            """,
    )


def _net_permissions_from_args(
    args: argparse.Namespace, default: Optional[List[Dict[str, Any]]]
) -> Optional[List[Dict[str, Any]]]:
    have_hosts = (None, None, None) != (
        args.full_control_hosts,
        args.read_only_hosts,
        args.deny_hosts,
    )
    if args.deny_all_hosts:
        if have_hosts:
            raise ValueError('Cannot specify --deny-all-hosts with other host access options')
        return smb.DENY_ALL_NETWORK_PERMISSIONS
    if not have_hosts:
        return default

    editor = AclEditor(NetworkAceTranslator(), [])
    if args.deny_hosts:
        editor.deny([args.deny_hosts], ['All'])
    if args.read_only_hosts:
        # If there are full_control hosts, insert a deny to make sure read_only
        # hosts don't pick up more rights from the full_control ace.
        if args.full_control_hosts:
            editor.deny([args.read_only_hosts], ['Write', 'Change permissions'])
        editor.grant([args.read_only_hosts], ['Read'])
    if args.full_control_hosts:
        editor.grant([args.full_control_hosts], ['All'])
    return editor.acl


class SMBAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_add_share'
    SYNOPSIS = 'Add a new SMB share'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='The ID of the tenant to which to add the share.',
        )
        parser.add_argument(
            '--name', type=str_decode, default=None, required=True, help='Name of share.'
        )
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, required=True, help='File system path.'
        )
        parser.add_argument(
            '--description', type=str_decode, default='', help='Description of this share.'
        )
        parser.add_argument(
            '--access-based-enumeration-enabled',
            type=bool_from_string,
            default=False,
            metavar='{true,false}',
            help='Enable Access-Based Enumeration for this share.',
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if the path does not exist already.',
        )
        parser.add_argument(
            '--default-file-create-mode',
            type=str_decode,
            default=None,
            help="""
                Change the default POSIX file create mode bits (octal) for the specified SMB share.
                These mode bits are applied to new files as they are created. Note: If an
                inheritable ACE is present in the permissions ACL, this flag has no effect.
                """,
        )
        parser.add_argument(
            '--default-directory-create-mode',
            type=str_decode,
            default=None,
            help="""
                Change the default POSIX directory create mode bits (octal) for the specified SMB
                share. These mode bits are applied to new directories as they are created. Note: If
                an inheritable ACE is present in the permissions ACL, this flag has no effect.
                """,
        )

        parser.add_argument(
            '--require-encryption',
            type=bool_from_string,
            default=False,
            metavar='{true,false}',
            help="""
                Require encryption for all traffic for the specified share. When set to true,
                clients without encryption capability cannot connect to this share.
                """,
        )
        parser.add_argument('--json', action='store_true', help='Print the raw JSON response.')

        _add_initial_acl_args(parser)
        _add_network_permissions_args(parser)

    @staticmethod
    def main(
        rest_client: RestClient,
        args: argparse.Namespace,
        outfile: IO[str] = sys.stdout,
        smb_mod: Any = smb,
    ) -> None:
        acl = _create_new_acl(args)
        net_acl = _net_permissions_from_args(args, default=smb.ALLOW_ALL_NETWORK_PERMISSIONS)

        result = smb_mod.smb_add_share(
            rest_client.conninfo,
            rest_client.credentials,
            args.name,
            args.fs_path,
            args.description,
            permissions=acl,
            tenant_id=args.tenant_id,
            allow_fs_path_create=args.create_fs_path,
            access_based_enumeration_enabled=args.access_based_enumeration_enabled,
            default_file_create_mode=args.default_file_create_mode,
            default_directory_create_mode=args.default_directory_create_mode,
            require_encryption=args.require_encryption,
            network_permissions=net_acl,
        )

        _print_share(result, args.json, outfile)


#  ____       _      _         ____  _
# |  _ \  ___| | ___| |_ ___  / ___|| |__   __ _ _ __ ___
# | | | |/ _ \ |/ _ \ __/ _ \ \___ \| '_ \ / _` | '__/ _ \
# | |_| |  __/ |  __/ ||  __/  ___) | | | | (_| | | |  __/
# |____/ \___|_|\___|\__\___| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Delete Share


class SMBDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_delete_share'
    SYNOPSIS = 'Delete a share'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='ID of share to delete.')
        share.add_argument('--name', type=str_decode, default=None, help='Name of share to delete.')
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help="""
                The ID of the tenant from which to delete the share. Use this flag only if you also
                use the --name flag.
                """,
        )

    @staticmethod
    def main(
        rest_client: RestClient,
        args: argparse.Namespace,
        outfile: IO[str] = sys.stdout,
        smb_mod: Any = smb,
    ) -> None:
        share_id = get_id_from_args(rest_client, args, smb_mod)
        smb_mod.smb_delete_share(rest_client.conninfo, rest_client.credentials, share_id)
        outfile.write(
            'Share {} has been deleted.\n'.format(args.id if args.id else f'"{args.name}"')
        )


#  __  __           _ _  __         ____  _
# |  \/  | ___   __| (_)/ _|_   _  / ___|| |__   __ _ _ __ ___
# | |\/| |/ _ \ / _` | | |_| | | | \___ \| '_ \ / _` | '__/ _ \
# | |  | | (_) | (_| | |  _| |_| |  ___) | | | | (_| | | |  __/
# |_|  |_|\___/ \__,_|_|_|  \__, | |____/|_| |_|\__,_|_|  \___|
#                           |___/
# FIGLET: Modify Share


class SMBModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_mod_share'
    SYNOPSIS = 'Modify a share'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='The ID of the share to modify.')
        share.add_argument(
            '--name', type=str_decode, default=None, help='The name of the share to modify.'
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='ID of the tenant the share is in. Only used if using the --name argument.',
        )

        parser.add_argument('--new-name', default=None, help='Change SMB share name.')
        parser.add_argument(
            '--new-tenant-id',
            type=int,
            default=None,
            help='Change the tenant that the share is in.',
        )
        parser.add_argument(
            '--fs-path', type=str_decode, default=None, help='Change file system path.'
        )
        parser.add_argument(
            '--description', type=str_decode, default=None, help='Change share description.'
        )
        parser.add_argument(
            '--access-based-enumeration-enabled',
            type=bool_from_string,
            default=None,
            metavar='{true,false}',
            help='Enable Access-Based Enumeration for this share.',
        )
        parser.add_argument(
            '--create-fs-path',
            action='store_true',
            help='Creates the specified file system path if the path does not exist already.',
        )
        parser.add_argument(
            '--default-file-create-mode',
            type=str_decode,
            default=None,
            help="""
                Change the default POSIX file create mode bits (octal) for the specified SMB share.
                These mode bits are applied to new files as they are created. Note: If an
                inheritable ACE is present in the permissions ACL, this flag has no effect.
                """,
        )
        parser.add_argument(
            '--default-directory-create-mode',
            type=str_decode,
            default=None,
            help="""
                Change the default POSIX directory create mode bits (octal) for the specified SMB
                share. These mode bits are applied to new directories as they are created. Note: If
                an inheritable ACE is present in the permissions ACL, this flag has no effect.
                """,
        )
        parser.add_argument(
            '--require-encryption',
            type=bool_from_string,
            default=None,
            metavar='{true,false}',
            help=(
                'Require all traffic for this share to be encrypted. If true, clients without '
                'encryption capabilities will not be able to connect.'
            ),
        )
        parser.add_argument('--json', action='store_true', help='Print the raw JSON response.')

        _add_network_permissions_args(parser)

    @staticmethod
    def main(
        rest_client: RestClient,
        args: argparse.Namespace,
        outfile: IO[str] = sys.stdout,
        smb_mod: Any = smb,
    ) -> None:
        share_id = get_id_from_args(rest_client, args, smb_mod)
        share_info: Dict[str, Any] = {'share_id': share_id}

        if args.create_fs_path is True:
            share_info['allow_fs_path_create'] = True

        if args.new_name is not None:
            share_info['share_name'] = args.new_name
        if args.new_tenant_id is not None:
            share_info['tenant_id'] = args.new_tenant_id
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description
        if args.access_based_enumeration_enabled is not None:
            share_info['access_based_enumeration_enabled'] = args.access_based_enumeration_enabled
        if args.default_file_create_mode is not None:
            share_info['default_file_create_mode'] = args.default_file_create_mode
        if args.default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = args.default_directory_create_mode
        if args.require_encryption is not None:
            share_info['require_encryption'] = args.require_encryption

        net_acl = _net_permissions_from_args(args, default=None)
        if net_acl is not None:
            share_info['network_permissions'] = net_acl

        _print_share(
            smb_mod.smb_modify_share(rest_client.conninfo, rest_client.credentials, **share_info),
            args.json,
            outfile,
        )


#  __  __           _ _  __
# |  \/  | ___   __| (_)/ _|_   _
# | |\/| |/ _ \ / _` | | |_| | | |
# | |  | | (_) | (_| | |  _| |_| |
# |_|  |_|\___/ \__,_|_|_|  \__, |
#  ___                      |___/     _
# |  _ \ ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __  ___
# | |_) / _ \ '__| '_ ` _ \| / __/ __| |/ _ \| '_ \/ __|
# |  __/  __/ |  | | | | | | \__ \__ \ | (_) | | | \__ \
# |_|   \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|___/
# FIGLET: Modify Permissions

TYPE_CHOICES = [t.capitalize() for t in [ALLOWED_TYPE, DENIED_TYPE]]
RIGHT_CHOICES = [t.replace('_', ' ').capitalize() for t in ALL_RIGHTS]


def _put_new_acl(
    smb_mod: Any,
    rest_client: RestClient,
    share_id: str,
    new_acl: Sequence[object],
    etag: Optional[str],
    print_json: bool,
) -> str:
    result = smb_mod.smb_modify_share(
        rest_client.conninfo,
        rest_client.credentials,
        share_id=share_id,
        permissions=new_acl,
        if_match=etag,
    )

    if print_json:
        return str(result)
    else:
        body, etag = result
        return 'New permissions:\n{}'.format(
            AclEditor(ShareAceTranslator(), body['permissions']).pretty_str()
        )


def _get_share(
    smb_mod: Any, rest_client: RestClient, args: argparse.Namespace
) -> request.RestResponse:
    share_id = get_id_from_args(rest_client, args, smb_mod)
    return smb_mod.smb_list_share(rest_client.conninfo, rest_client.credentials, share_id)


def do_add_entry(smb_mod: Any, rest_client: RestClient, args: argparse.Namespace) -> str:
    share, etag = _get_share(smb_mod, rest_client, args)

    # Modify:
    translator = ShareAceTranslator()
    acl = AclEditor(translator, share['permissions'])
    ace_type = translator.parse_type_enum_value(args.type)
    if ace_type == ALLOWED_TYPE:
        acl.grant([args.trustee], args.rights)
    else:
        assert ace_type == DENIED_TYPE
        acl.deny([args.trustee], args.rights)

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, rest_client, share['id'], acl.acl, etag, args.json)


def do_remove_entry(smb_mod: Any, rest_client: RestClient, args: argparse.Namespace) -> str:
    share, etag = _get_share(smb_mod, rest_client, args)

    # Remove:
    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.remove(
        position=args.position,
        trustee=args.trustee,
        ace_type=args.type,
        rights=args.rights,
        allow_multiple=args.all_matching,
    )

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, rest_client, share['id'], acl.acl, etag, args.json)


def do_modify_entry(smb_mod: Any, rest_client: RestClient, args: argparse.Namespace) -> str:
    share, etag = _get_share(smb_mod, rest_client, args)

    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.modify(
        args.position,
        args.old_trustee,
        args.old_type,
        args.old_rights,
        None,
        args.new_trustee,
        args.new_type,
        args.new_rights,
        None,
        args.all_matching,
    )

    if args.dry_run:
        return f'New permissions would be:\n{acl.pretty_str()}'

    return _put_new_acl(smb_mod, rest_client, share['id'], acl.acl, etag, args.json)


def do_replace(smb_mod: Any, rest_client: RestClient, args: argparse.Namespace) -> str:
    share, etag = _get_share(smb_mod, rest_client, args)
    acl = _create_new_acl(args)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(
            AclEditor(ShareAceTranslator(), acl).pretty_str()
        )

    return _put_new_acl(smb_mod, rest_client, share['id'], acl, etag, args.json)


# This is separate from smb_mode_share because argparse doesn't allow sub-commands to be optional.
class SMBModShareAclCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_mod_share_permissions'
    SYNOPSIS = "Modify a share's permissions"

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument('--id', type=int, default=None, help='The ID of the share to modify.')
        share.add_argument(
            '--name', type=str_decode, default=None, help='The name of the share to modify.'
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help="""
                The ID of the tenant from which to delete the share. Use this flag only if you also
                use the --name flag.
                """,
        )

        parser.add_argument('--json', action='store_true', help='Print the raw JSON response.')

        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True

        add_entry = subparsers.add_parser(
            'add_entry', help="Add an entry to the share's permissions."
        )
        add_entry.set_defaults(command=do_add_entry)
        add_entry.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            required=True,
            help="""
                The trustee to add to the share permissions. For example: Everyone, uid:1000,
                gid:1001, sid:S-1-5-2-3-4, auth_id:500
                """,
        )
        add_entry.add_argument(
            '-y',
            '--type',
            type=str_decode,
            required=True,
            choices=TYPE_CHOICES,
            help='Allow or deny the trustee the specified rights.',
        )
        add_entry.add_argument(
            '-r',
            '--rights',
            type=str_decode,
            nargs='+',
            required=True,
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='The rights to allow or deny to the trustee. Available rights: '
            + ', '.join(RIGHT_CHOICES),
        )
        add_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            help='Do nothing; display what the result of the change would be.',
        )

        remove_entry = subparsers.add_parser(
            'remove_entry', help="Remove an entry from the share's permissions."
        )
        remove_entry.set_defaults(command=do_remove_entry)
        remove_entry.add_argument(
            '-p', '--position', type=int, help='The position of the entry to remove.'
        )
        remove_entry.add_argument(
            '-t',
            '--trustee',
            type=str_decode,
            help="""
                Remove the entry that includes this trustee from the share's permissions. For
                example: Everyone, uid:1000, gid:1001, sid:S-1-5-2-3-4, auth_id:500
                """,
        )
        remove_entry.add_argument(
            '-y',
            '--type',
            type=str_decode,
            choices=TYPE_CHOICES,
            help='Remove an entry of the specified type.',
        )
        remove_entry.add_argument(
            '-r',
            '--rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Remove an entry with the specified rights. Available rights: '
            + ', '.join(RIGHT_CHOICES),
        )
        remove_entry.add_argument(
            '-a',
            '--all-matching',
            action='store_true',
            help='If multiple entries match the specified arguments, remove all of the entries.',
        )
        remove_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            help='Do nothing; display what the result of the change would be.',
        )

        modify_entry = subparsers.add_parser(
            'modify_entry', help='Modify an existing permission entry in place'
        )
        modify_entry.set_defaults(command=do_modify_entry)
        modify_entry.add_argument(
            '-p', '--position', type=int, help='The position of the entry to modify.'
        )
        modify_entry.add_argument(
            '--old-trustee',
            type=str_decode,
            help="""
                Modify an entry with the specified trustee. For example: Everyone, uid:1000,
                gid:1001, sid:S-1-5-2-3-4, auth_id:500
                """,
        )
        modify_entry.add_argument(
            '--old-type',
            type=str_decode,
            choices=TYPE_CHOICES,
            help='Modify an entry of the specified type.',
        )
        modify_entry.add_argument(
            '--old-rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Modify an entry with the specified rights. Available rights: '
            + ', '.join(RIGHT_CHOICES),
        )
        modify_entry.add_argument(
            '--new-trustee',
            type=str_decode,
            help=(
                'Set the entry to have this trustee.  e.g. Everyone, '
                'uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500'
            ),
        )
        modify_entry.add_argument(
            '--new-type', type=str_decode, choices=TYPE_CHOICES, help='Set the type of the entry.'
        )
        modify_entry.add_argument(
            '--new-rights',
            type=str_decode,
            nargs='+',
            metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help='Set the rights for the specified entry. Available rights: '
            + ', '.join(RIGHT_CHOICES),
        )
        modify_entry.add_argument(
            '-a',
            '--all-matching',
            action='store_true',
            help='If multiple entries match the specified arguments, modify all of the entries.',
        )
        modify_entry.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            help='Do nothing; display what the result of the change would be.',
        )

        replace = subparsers.add_parser(
            'replace',
            help="""
                Replace any existing share permissions with specified permissions. If you don't
                specify new permissions, all access is denied.
                """,
        )
        replace.add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            help='Do nothing; display what the result of the change would be.',
        )
        _add_initial_acl_args(replace)
        replace.set_defaults(command=do_replace)

    @staticmethod
    def main(
        rest_client: RestClient,
        args: argparse.Namespace,
        outfile: IO[str] = sys.stdout,
        smb_mod: Any = smb,
    ) -> None:
        outfile.write(f'{args.command(smb_mod, rest_client, args)}\n')


#                _                 _   _   _
#  ___ _ __ ___ | |__     ___  ___| |_| |_(_)_ __   __ _ ___
# / __| '_ ` _ \| '_ \   / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \ | | | | | |_) |  \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/_| |_| |_|_.__/___|___/\___|\__|\__|_|_| |_|\__, |___/
#                   |_____|                        |___/
#  FIGLET: smb_settings
#


def add_smb_settings_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '-e',
        '--encryption-mode',
        help='Server encryption mode to set',
        choices=('NONE', 'PREFERRED', 'REQUIRED'),
        metavar='{none,preferred,required}',
        type=lambda s: s.upper(),
    )

    available_dialects = [
        'SMB2_DIALECT_2_002',
        'SMB2_DIALECT_2_1',
        'SMB2_DIALECT_3_0',
        'SMB2_DIALECT_3_11',
    ]

    class DialectAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Union[str, Sequence[str], None],
            _option_strings: Optional[str] = None,
        ) -> None:
            assert values is not None
            cur_values = getattr(namespace, self.dest)
            if cur_values is None:
                cur_values = []

            if 'ALL' in values:
                if len(values) == 1:
                    cur_values = available_dialects
                else:
                    raise ValueError('The "ALL" supported dialect option must be used alone.')
            else:
                for val in values:
                    if val in cur_values:
                        raise ValueError('Duplicate dialect "%s".' % val)
                    if val != '':
                        cur_values.append(val)
            setattr(namespace, self.dest, cur_values)

    pretty_available_dialects = ', '.join(available_dialects).lower()
    parser.add_argument(
        '-d',
        '--supported-dialects',
        action=DialectAction,
        type=lambda s: s.upper(),
        choices=available_dialects + ['ALL', ''],
        metavar=('dialect_1', 'dialect_2'),
        nargs='+',
        help=f"""
            Specify a space-separated list of SMB dialects that clients are permitted to negotiate.
            To disable SMB, specify -d "". Available dialects: {pretty_available_dialects}.
            Alternatively, use -d ALL to allow all supported dialects.
            """,
    )

    parser.add_argument(
        '--hide-shares-from-unauthorized-hosts',
        type=bool_from_string,
        metavar='{true,false}',
        default=None,
        help="""
            Configure share listing to omit shares to which the requesting host isn't authorized to
            connect.
            """,
    )
    parser.add_argument(
        '--hide-shares-from-unauthorized-users',
        type=bool_from_string,
        metavar='{true,false}',
        default=None,
        help="""
            Configure share listing to omit shares to which the requesting user isn't authorized to
            connect. Important: Clients which don't have passwordless authentication typically list
            shares by using guest privileges. This flag typically hides all shares from this client
            type.
            """,
    )
    parser.add_argument(
        '--snapshot-directory-mode',
        choices=['visible', 'hidden', 'disabled'],
        default=None,
        help="""
            When you set this flag to visible, the .snapshot directory appears at the root of shares
            during directory listing operations. The .snapshot directory is also accessible by name
            in any directory. When you set this flag to hidden, .snapshot directories do not appear
            in directory listings but remains accessible by name. When you set this flag to
            disabled, .snapshot directories are not accessible and snapshots are available only
            through the Restore Previous Versions dialog box on Windows.
            """,
    )
    parser.add_argument(
        '--bypass-traverse-checking',
        type=bool_from_string,
        metavar='{true,false}',
        default=None,
        help="""
            Enables bypass traverse checking for all users and directories. For example, a user who
            tries to access directory /x/y and has permissions to the /x directory but not to the
            /x/y directory can access the /x/y directory. A user still requires permissions to the
            /x directory to view its contents.
            """,
    )
    parser.add_argument(
        '--signing-required',
        type=bool_from_string,
        metavar='{true,false}',
        default=None,
        help="""
            If the user is not a guest, require all messages to be signed. This flag applies to all
            SMB shares.
            """,
    )


def extract_modify_settings_args(args: argparse.Namespace) -> Dict[str, Any]:
    settings_json = {}

    if args.encryption_mode is not None:
        settings_json['session_encryption'] = args.encryption_mode
    if args.supported_dialects is not None:
        settings_json['supported_dialects'] = args.supported_dialects
    if args.hide_shares_from_unauthorized_hosts is not None:
        settings_json[
            'hide_shares_from_unauthorized_hosts'
        ] = args.hide_shares_from_unauthorized_hosts
    if args.hide_shares_from_unauthorized_users is not None:
        settings_json[
            'hide_shares_from_unauthorized_users'
        ] = args.hide_shares_from_unauthorized_users
    if args.snapshot_directory_mode is not None:
        settings_json['snapshot_directory_mode'] = args.snapshot_directory_mode.upper()
    if args.bypass_traverse_checking is not None:
        settings_json['bypass_traverse_checking'] = args.bypass_traverse_checking
    if args.signing_required is not None:
        settings_json['signing_required'] = args.signing_required

    if len(settings_json) == 0:
        raise ValueError('Choose one or more settings to modify')

    return settings_json


class SMBModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_modify_settings'
    SYNOPSIS = 'Set SMB server settings'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        add_smb_settings_options(parser)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        settings_json = extract_modify_settings_args(args)
        print(smb.patch_smb_settings(rest_client.conninfo, rest_client.credentials, settings_json))


class SMBGetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_get_settings'
    SYNOPSIS = 'Get SMB settings'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(smb.get_smb_settings(rest_client.conninfo, rest_client.credentials))


class SMBListFileHandlesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_file_handles'
    SYNOPSIS = 'List SMB open file handles'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--page-size', type=int, help='Max files to return per request.')
        parser.add_argument(
            '--file-number',
            type=int,
            default=None,
            required=False,
            help="""
                Limits results to the specified file, as returned from a command like
                fs_file_get_attr or fs_read_dir.
                """,
        )
        parser.add_argument(
            '-p',
            '--resolve-paths',
            action='store_true',
            help='Returns the primary path of the opened file.',
        )
        parser.add_argument('--path', help='Path to file', type=str_decode)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.page_size is not None and args.page_size < 1:
            raise ValueError('Page size must be greater than 0')

        file_number = args.file_number
        if args.path:
            file_attr = fs.get_file_attr(
                rest_client.conninfo, rest_client.credentials, path=args.path
            )
            file_number = file_attr.lookup('file_number')

        resolve_paths = args.resolve_paths or False

        results = smb.list_file_handles(
            rest_client.conninfo,
            rest_client.credentials,
            file_number=file_number,
            limit=args.page_size,
            resolve_paths=resolve_paths,
        )
        request.print_paginated_results(results, 'file_handles')


class SMBCloseFileHandleCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_close_file_handle'
    SYNOPSIS = 'Force-close the specified SMB file handle'
    DESCRIPTION = SYNOPSIS + textwrap.dedent(
        """\n
        Important: This command prevents the client from sending any new requests for this file
        handle, releases all locks, and forces the client to reopen the file. The system will not
        give the client an opportunity to flush cached writes.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--location',
            type=str,
            default=None,
            required=True,
            help='The location of the file handle to close as returned from smb_list_file_handles.',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if type(args.location) is not str:  # noqa: E721
            raise ValueError('location must be a string')
        message = (
            'Are you sure you want to force close this file? '
            "The client's cached writes will be lost."
        )
        if not qumulo.lib.opts.ask(SMBCloseFileHandleCommand.NAME, message):
            return
        smb.close_smb_file(rest_client.conninfo, rest_client.credentials, location=args.location)


class SMBListSessionsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_list_sessions'
    SYNOPSIS = 'List SMB open sessions'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--page-size', type=int, help='Max sessions to return per request')
        parser.add_argument(
            '--identity',
            type=str,
            default=None,
            required=False,
            help="""
                List only the sessions that match the specified user's identity in one of the
                following forms: a name or a SID optionally qualified with a domain prefix (for
                example, "local:name", "S-1-1-0", "name", "world:Everyone", "ldap_user:name",
                "ad:name"), or an ID type (for example, "uid:1001", "auth_id:513", "SID:S-1-1-0").
                """,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.page_size is not None and args.page_size < 1:
            raise ValueError('Page size must be greater than 0')

        results = smb.list_smb_sessions(
            rest_client.conninfo,
            rest_client.credentials,
            limit=args.page_size,
            identity=args.identity,
        )
        request.print_paginated_results(results, 'session_infos')


class SMBCloseSessionsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'smb_close_sessions'
    SYNOPSIS = 'Force close SMB sessions matching one or more of a set of filters.'
    DESCRIPTION = SYNOPSIS + textwrap.dedent(
        """\n
        Important: This flag prevents the client from sending any new requests for this session,
        releases all locks, and forces the client to reauthenticate. The system does not give the
        client an opportunity to flush cached writes.
        """
    )
    BATCH_SIZE = 100

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--identity',
            type=str,
            default=None,
            required=False,
            help="""
                Close only the sessions that match the specified user's identity in one of the
                following forms: a name or a SID optionally qualified with a domain prefix (for
                example, "local:name", "S-1-1-0", "name", "world:Everyone", "ldap_user:name",
                "ad:name"), or an ID type (for example, "uid:1001", "auth_id:513", "SID:S-1-1-0").
                """,
        )
        parser.add_argument(
            '--location',
            type=str,
            default=None,
            required=False,
            help="""
                Use the list of sessions from the smb_list_sessions command to close only the
                session with the specified location.
                """,
        )
        parser.add_argument(
            '--share-name',
            type=str,
            default=None,
            required=False,
            help="""
                Close only the sessions that are connected to the share with the specified
                case-sensitive name. Sessions connected to multiple shares will disconnect from all
                shares using the session.
                """,
        )
        parser.add_argument(
            '--ip',
            type=str,
            default=None,
            required=False,
            help='Close only the sessions that originate from the specified IP address.',
        )

    @staticmethod
    def main(
        rest_client: RestClient,
        args: argparse.Namespace,
        smb_mod: Any = smb,
        opts_mod: Any = qumulo.lib.opts,
    ) -> None:
        if all(a is None for a in (args.identity, args.location, args.ip, args.share_name)):
            raise ValueError('One of identity, location, share name, or IP must be provided')

        sessions = []
        for f in smb_mod.list_smb_sessions(
            rest_client.conninfo, rest_client.credentials, identity=args.identity
        ):
            sessions.extend(f.lookup('session_infos'))

        if args.ip is not None:
            sessions = [i for i in sessions if args.ip == i['originator']]
        if args.location is not None:
            sessions = [i for i in sessions if args.location == i['location']]
        if args.share_name is not None:
            sessions = [i for i in sessions if args.share_name in i['share_names']]
        if not sessions:
            raise ValueError('No sessions found to close')

        message = (
            'About to force close (%d) sessions. Client-side cached writes will be lost. Proceed?'
            % len(sessions)
        )
        if not opts_mod.ask(SMBCloseSessionsCommand.NAME, message):
            return

        # We had a customer who had 340k orphaned smb guest sessions. That
        # caused the API to fail because the request's json size was too large.
        # This simple batching of 100 sessions at a time closed all 340k within
        # a few seconds.
        batch_size = SMBCloseSessionsCommand.BATCH_SIZE
        session_batches = [
            sessions[x : x + batch_size] for x in range(0, len(sessions), batch_size)
        ]
        for batch in session_batches:
            smb_mod.close_smb_sessions(rest_client.conninfo, rest_client.credentials, batch)
