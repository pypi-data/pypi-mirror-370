# Copyright (c) 2025 Qumulo, Inc.
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

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap

from typing import Dict, Optional

import qumulo.lib.opts

from qumulo.commands.network import parse_comma_deliminated_args
from qumulo.lib.request import pretty_json
from qumulo.rest.network_v3 import AddressesKind
from qumulo.rest_client import RestClient


class GetClusterNetworkConfig(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_get_config'
    ALIASES = ['network_v3_get_config']
    SYNOPSIS = 'Retrieve the cluster-wide network config'
    DESCRIPTION = textwrap.dedent(
        """\
        Retrieve the cluster-wide network config.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-o',
            '--output',
            type=str,
            help='The file to which the network config should be written.',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        config = pretty_json(rest_client.network_v3.get_config_raw().data, sort_keys=False)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(config)
        else:
            print(config)


WELL_KNOWN_EDITORS = ['editor', 'vim', 'vi']


def find_default_editor() -> str:
    editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
    if editor:
        return editor

    for e in WELL_KNOWN_EDITORS:
        path = shutil.which(e)
        if path is not None:
            return path

    raise FileNotFoundError(
        'Unable to find a text editor on this system. '
        'Consider setting your $EDITOR environment variable'
    )


def yes_or_no(message: str) -> bool:
    responses = {'': True, 'y': True, 'yes': True, 'n': False, 'no': False}
    while True:
        line = input(message)
        answer = responses.get(line.lower().strip(), None)
        if answer is not None:
            return answer


HELPER_MESSAGE = r"""
 _____ _____ __  __ ____  _        _  _____ _____ ____
|_   _| ____|  \/  |  _ \| |      / \|_   _| ____/ ___|
  | | |  _| | |\/| | |_) | |     / _ \ | | |  _| \___ \
  | | | |___| |  | |  __/| |___ / ___ \| | | |___ ___) |
  |_| |_____|_|  |_|_|   |_____/_/   \_\_| |_____|____/

To communicate with the API endpoint, you can use the following JSON templates based on typical
network configurations. Use these examples to structure your JSON and adjust the values to fit
your configuration needs.

Add a vlan interface over the frontend bond:
"frontend_vlan_configs": [
    ...
    {
        "vlan_id": <1-4094>,
        "mtu": <u32, optional>,
        "network_id": <u32>,
        "second_network_id": <u32, optional>
    }
]

Add a DHCP network config:
"frontend_networks": [
    ...
    {
        "id": <u32>,
        "name": <str>,
        "tenant_id": <u32, optional>,
        "addresses": {
            "type": "DHCP",
            "dhcp_addresses": {
                "floating_ip_ranges": [<IP ranges, "1.1.1.1-4">]
            }
        }
    }
]

Add a STATIC network config:
"frontend_networks": [
    ...
    {
        "id": <u32>,
        "name": <str>,
        "tenant_id": <u32, optional>,
        "addresses": {
            "type": "STATIC",
            "static_addresses": {
                "default_gateway": <IP addr, "1.1.1.1", empty-able>,
                "ip_ranges": [<IP ranges, "1.1.1.1-4">],
                "floating_ip_ranges": [<IP ranges, "1.1.1.1-4">],
                "netmask": <Ip addr or CIDR format, "255.0.0.0", "aa:bb::/64">
            }
        }
    }
]

Add a HOST network config:
"frontend_networks": [
    ...
    {
        "id": <u32>,
        "name": <str>,
        "tenant_id": <u32, optional>,
        "addresses": {
            "type": "HOST",
            "host_addresses": {
                "floating_ip_ranges": [<IP ranges, "1.1.1.1-4">],
                "netmask": <Ip addr or CIDR format, "255.0.0.0", "aa:bb::/64">
            }
        }
    }
]
"""


def trim_comments(s: str) -> str:
    trimmed_one_line_comments = re.sub(r'(#|//).*', '', s, flags=re.MULTILINE)
    trimmed_block_comments = re.sub(r'/\*.*?\*/', '', trimmed_one_line_comments, flags=re.DOTALL)
    return trimmed_block_comments


class ValidateOrPutClusterNetworkConfig(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_put_config'
    ALIASES = ['network_v3_put_config']
    SYNOPSIS = 'Validate or overwrite the cluster-wide network configuration.'
    DESCRIPTION = textwrap.dedent(
        """\
        Validate or overwrite the cluster-wide network configuration.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate a new cluster-wide network config without writing it to disk.',
            default=False,
        )
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            '--file',
            type=str,
            help='The path to the JSON file that contains your new cluster-wide network config.',
        )
        input_group.add_argument(
            '--modify',
            action='store_true',
            help='Open the current cluster-wide network config in your default editor. '
            'After saving and closing your editor, the modified config will be validated.',
        )
        input_group.add_argument(
            '--templates',
            action='store_true',
            help='Print out the templates for configuring the API endpoint.',
            default=False,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.templates:
            print(HELPER_MESSAGE)
            return

        # XXX SQUALL-564: Figure out the best way to display the error backtrace to
        # make it easier to debug API errors.

        def execute(config: Dict[str, object], if_match: Optional[str] = None) -> None:
            if args.dry_run:
                rest_client.network_v3.validate(config, if_match)
            else:
                print(rest_client.network_v3.put_config(config, if_match))

        if args.file:
            with open(args.file) as file:
                contents = trim_comments(file.read())
                config: Dict[str, object] = json.loads(contents)
            execute(config)

        elif args.modify:
            current_config = rest_client.network_v3.get_config_raw()
            current_config_str = pretty_json(current_config.data, sort_keys=False)
            with tempfile.NamedTemporaryFile() as f:
                f.write(current_config_str.encode())
                f.write(('\n\n/*' + HELPER_MESSAGE + '*/').encode())
                f.flush()

                stop = False
                while not stop:
                    try:
                        subprocess.call([find_default_editor(), f.name])
                        f.seek(0)
                        contents = trim_comments(f.read().decode())
                        config = json.loads(contents)

                        execute(config, current_config.etag)

                        stop = True
                    except (json.decoder.JSONDecodeError, qumulo.lib.request.RequestError) as e:
                        if isinstance(e, json.decoder.JSONDecodeError):
                            print(str(e))
                        else:
                            print(e.pretty_str())

                        stop = not yes_or_no('\nContinue editing [Y/n]: ')
                        if stop:
                            print('Stop editing the configuration.')
                            return

        if args.dry_run:
            print('Proposed cluster-wide network configuration is valid!')
        else:
            print('Successfully updated the cluster-wide network configuration!')


class NetworkStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_status'
    ALIASES = ['network_v3_status']
    SYNOPSIS = 'Retrieve the comprehensive network status'
    DESCRIPTION = textwrap.dedent(
        """\
        Retrieve the comprehensive network status.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--node-id', type=int, help='Node ID')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.node_id is not None:
            print(
                pretty_json(
                    rest_client.network_v3.get_network_status(args.node_id), sort_keys=False
                )
            )
        else:
            # sort the output by node id, to provide a less confusing and deterministic output.
            output = rest_client.network_v3.list_network_statuses()
            output.sort(key=lambda x: int(x['node_id']))

            print(pretty_json(output, sort_keys=False))


class FrontendInterfacesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_frontend_interfaces'
    ALIASES = ['network_v3_frontend_interfaces']
    SYNOPSIS = 'Retrieve the list of frontend interfaces for every node in the cluster.'
    DESCRIPTION = textwrap.dedent(
        """\
        Retrieve the list of frontend interfaces for every node in the cluster.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        output = rest_client.network_v3.get_cluster_frontend_interfaces()

        print(pretty_json(output))


class BackendInterfacesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_backend_interfaces'
    ALIASES = ['network_v3_backend_interfaces']
    SYNOPSIS = 'Retrieve the list of backend interfaces for every node in the cluster.'
    DESCRIPTION = textwrap.dedent(
        """\
        Retrieve the list of backend interfaces for every node in the cluster.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        output = rest_client.network_v3.get_cluster_backend_interfaces()

        print(pretty_json(output))


class AddNetworkCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_add_network'
    ALIASES = ['network_v3_add_network']
    SYNOPSIS = 'Add a network to the cluster-wide network config.'
    DESCRIPTION = textwrap.dedent(
        """\
        Add a network to the cluster-wide network config.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--network-id', type=int, required=True, help='Network ID')

        parser.add_argument('--name', required=True, help='Network name')

        parser.add_argument(
            '--tenant-id',
            type=int,
            help=(
                'The tenant that the network will be assigned to. If only one tenant exists, the '
                'network will default to that tenant. Otherwise, not specifying the tenant will '
                'create the network unassigned.'
            ),
        )

        subparsers = parser.add_subparsers(
            dest='assigned_by', required=True, help='The kind of network you want to add.'
        )

        host = subparsers.add_parser(
            'host_managed', help='Assign floating IPs to an interface not managed by Qumulo Core.'
        )
        host.set_defaults(run=AddNetworkCommand.host_network)
        host.add_argument(
            '--netmask',
            metavar='<netmask-or-subnet>',
            help='IPv4 or IPv6 Netmask or Subnet CIDR eg. 255.255.255.0 or 10.1.1.0/24',
        )
        host.add_argument(
            '--floating-ip-ranges',
            nargs='+',
            default=[],
            action='append',
            metavar='<address-or-range>',
            help=(
                'List of floating IP ranges to replace the'
                ' current ranges. Can be single addresses or ranges,'
                ' comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21'
            ),
        )

    @staticmethod
    def host_network(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.network_v3.modify_config(
            lambda old_config: old_config.add_network(
                network_id=args.network_id,
                name=args.name,
                addresses_kind=AddressesKind.HOST,
                tenant_id=args.tenant_id,
                netmask=args.netmask,
                floating_ip_ranges=parse_comma_deliminated_args(args.floating_ip_ranges),
            )
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        args.run(rest_client, args)


class DeleteNetworkCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_preview_delete_network'
    ALIASES = ['network_v3_delete_network']
    SYNOPSIS = 'Delete a network from the cluster-wide network config.'
    DESCRIPTION = textwrap.dedent(
        """\
        Delete a network from the cluster-wide network config.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--network-id', type=int, required=True, help='Network to delete')

        parser.add_argument(
            '--delete-orphaned-vlans',
            default=False,
            action='store_true',
            help=(
                'Delete the vlan associated with the specified network'
                ' if it is the only network on the VLAN.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.network_v3.modify_config(
            lambda old_config: old_config.delete_network(
                network_id=args.network_id, delete_orphaned_vlans=args.delete_orphaned_vlans
            )
        )
