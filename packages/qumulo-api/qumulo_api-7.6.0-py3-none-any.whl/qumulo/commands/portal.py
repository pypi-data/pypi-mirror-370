# Copyright (c) 2024 Qumulo, Inc.
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
import sys

from typing import List

import qumulo.lib.opts

from qumulo.lib.request import pretty_json, RequestError
from qumulo.lib.util import tabulate
from qumulo.rest.portal import DEFAULT_PORTAL_PORT_NUMBER as PORTAL_PORT
from qumulo.rest.portal import EvictionSettings, HubPortal, SpokePortal
from qumulo.rest_client import RestClient

JSON_HELP = 'Pretty-print JSON'
ADDR_HELP = 'The IP address of a node in the remote cluster'
PORT_HELP = 'The TCP port for portal activity on the remote cluster (3713 by default)'
HUB_ROOT_HELP = (
    'The full path to the prospective directory that will serve as the hub portal root directory'
)
SPOKE_ROOT_HELP = (
    'The full path to the directory that serves as the spoke portal root directory. Qumulo Core'
    ' creates this directory for you automatically. If this directory exists already, the system'
    ' outputs an error.'
)
RO_SPOKE_HELP = (
    'Create a read-only spoke portal. Read-only spoke portals prevent users from creating or'
    ' modifying files or directories under the hub portal root directory.'
    " Important: It isn't possible to change a read-only spoke portal to a read-write portal"
    ' after creating it.'
)
FORCE_DELETE_DETAIL = (
    'Caution: This operation deletes all data from the spoke portal, including any new and'
    ' modified data on the spoke that has not yet synchronized with the hub portal. Data under'
    ' the hub portal root directory is not affected.'
)


def pretty_portal_enum(state: str) -> str:
    return ' '.join([word.title() for word in state.split('_')])


def pretty_spoke_type(spoke_type: str) -> str:
    return {'SPOKE_READ_ONLY': 'RO', 'SPOKE_READ_WRITE': 'RW'}.get(spoke_type, spoke_type)


def format_hub_portals(hubs: List[HubPortal], as_json: bool) -> str:
    if as_json:
        output = []
        for hub in hubs:
            out = hub.to_dict()
            output.append(out)

        return pretty_json(output)

    columns = ['ID', 'State', 'Status', 'Hub Root', 'Spoke Host', 'Spoke Name', 'Spoke Type']

    rows = []
    for hub in hubs:
        addr = f'{hub.spoke_address}:{hub.spoke_port}' if hub.spoke_address else '-'
        root = hub.root_path or 'Deleted'
        row = [
            hub.id,
            pretty_portal_enum(hub.state),
            pretty_portal_enum(hub.status),
            root,
            addr,
            hub.spoke_cluster_name,
            pretty_spoke_type(hub.spoke_type),
        ]
        rows.append(row)

    return tabulate(rows, columns)


def format_spoke_portals(spokes: List[SpokePortal], as_json: bool) -> str:
    if as_json:
        output = []
        for spoke in spokes:
            out = spoke.to_dict()
            output.append(out)

        return pretty_json(output)

    columns = ['ID', 'State', 'Status', 'Type', 'Spoke Root', 'Hub Host', 'Hub Portal ID']
    rows = []

    for spoke in spokes:
        addr = f'{spoke.hub_address}:{spoke.hub_port}' if spoke.hub_address else '-'
        row = [
            spoke.id,
            pretty_portal_enum(spoke.state),
            pretty_portal_enum(spoke.status),
            pretty_spoke_type(spoke.spoke_type),
            spoke.spoke_root_path,
            addr,
            spoke.hub_id or '-',
        ]
        rows.append(row)

    return tabulate(rows, columns)


class CreatePortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_create'
    SYNOPSIS = (
        'Create a spoke portal on the current cluster and propose a hub portal on another cluster'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--spoke-root', required=True, help=SPOKE_ROOT_HELP)
        parser.add_argument('-a', '--hub-address', required=True, help=ADDR_HELP)
        parser.add_argument('-p', '--hub-port', default=PORTAL_PORT, help=PORT_HELP, type=int)
        parser.add_argument('--hub-root', required=True, help=HUB_ROOT_HELP)
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')
        parser.add_argument('-r', '--read-only-spoke', help=RO_SPOKE_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        is_writable_spoke = not args.read_only_spoke
        spoke_id = rest_client.portal.create_portal(args.spoke_root, is_writable_spoke)
        error = None

        try:
            spoke = rest_client.portal.propose_hub_portal(
                spoke_id, args.hub_address, args.hub_port, args.hub_root
            )
        except RequestError as propose_error:
            error = propose_error
        else:
            print(format_spoke_portals([spoke], args.json))
            return

        try:
            rest_client.portal.delete_spoke_portal(spoke_id)
        except RequestError:
            print(
                f'Could not clean up spoke portal with ID {spoke_id}. Please delete it manually.',
                file=sys.stderr,
            )

        print(
            'Could not establish a relationship with the proposed remote cluster.', file=sys.stderr
        )
        raise error


class GetSpokePortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_get_spoke'
    SYNOPSIS = 'Get the configuration and status for a spoke portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Spoke portal ID')
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        spoke = rest_client.portal.get_spoke_portal(args.id)
        print(format_spoke_portals([spoke], args.json))


class GetHubPortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_get_hub'
    SYNOPSIS = 'Get the configuration and status for a hub portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Hub portal ID')
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        hub = rest_client.portal.get_hub_portal(args.id)

        print(format_hub_portals([hub], args.json))


class ModifySpokePortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_modify_spoke'
    SYNOPSIS = 'Change the configuration for a spoke portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Spoke portal ID')
        parser.add_argument('-a', '--hub-address', required=True, help=ADDR_HELP)
        parser.add_argument('-p', '--hub-port', default=PORTAL_PORT, help=PORT_HELP, type=int)
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        spoke = rest_client.portal.modify_spoke_portal(args.id, args.hub_address, args.hub_port)
        print(format_spoke_portals([spoke], args.json))


class DeleteSpokePortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_delete_spoke'
    SYNOPSIS = 'Delete a spoke portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Spoke portal ID')
        parser.add_argument(
            '--force',
            help=f'Force the deletion of the spoke portal. {FORCE_DELETE_DETAIL}',
            action='store_true',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.portal.delete_spoke_portal(args.id, args.force)


class ModifyHubPortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_modify_hub'
    SYNOPSIS = 'Change the configuration for a hub portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Hub portal ID')
        parser.add_argument('-a', '--spoke-address', required=True, help=ADDR_HELP)
        parser.add_argument('-p', '--spoke-port', default=PORTAL_PORT, help=PORT_HELP, type=int)
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        hub = rest_client.portal.modify_hub_portal(args.id, args.spoke_address, args.spoke_port)
        print(format_hub_portals([hub], args.json))


class DeleteHubPortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_delete_hub'
    SYNOPSIS = 'Delete a hub portal on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-i', '--id', type=int, required=True, help='Hub portal ID')
        parser.add_argument(
            '--force',
            help=f'Force the deletion of the hub portal. {FORCE_DELETE_DETAIL}',
            action='store_true',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.portal.delete_hub_portal(args.id, args.force)


class AuthorizeHubPortal(qumulo.lib.opts.Subcommand):
    NAME = 'portal_authorize_hub'
    SYNOPSIS = 'Authorize the specified hub portal to activate the relationship'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-i',
            '--id',
            type=int,
            required=True,
            help='The identifier of the hub portal to authorize',
        )
        parser.add_argument(
            '-a',
            '--spoke-address',
            required=True,
            help='The IP address of a node in the spoke portal host cluster that proposed the '
            'relationship',
        )
        parser.add_argument('-p', '--spoke-port', default=PORTAL_PORT, help=PORT_HELP, type=int)

        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        hub = rest_client.portal.authorize_hub_portal(args.id, args.spoke_address, args.spoke_port)
        print(format_hub_portals([hub], args.json))


class ListPortals(qumulo.lib.opts.Subcommand):
    NAME = 'portal_list'
    SYNOPSIS = 'List a summary of configuration and status for all portals on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        hubs = rest_client.portal.list_hub_portals()
        spokes = rest_client.portal.list_spoke_portals()

        if args.json:
            result = {
                'hubs': [hub.to_dict() for hub in hubs],
                'spokes': [spoke.to_dict() for spoke in spokes],
            }
            print(pretty_json(result))
            return

        columns = ['Role', 'ID', 'State', 'Status', 'Type', 'Local Root', 'Remote Host']
        rows = []

        for hub in hubs:
            addr = f'{hub.spoke_address}:{hub.spoke_port}' if hub.spoke_address else '-'
            root = hub.root_path or 'Deleted'
            row = [
                'Hub',
                hub.id,
                pretty_portal_enum(hub.state),
                pretty_portal_enum(hub.status),
                pretty_spoke_type(hub.spoke_type),
                root,
                addr,
            ]
            rows.append(row)

        for spoke in spokes:
            addr = f'{spoke.hub_address}:{spoke.hub_port}' if spoke.hub_address else '-'
            row = [
                'Spoke',
                spoke.id,
                pretty_portal_enum(spoke.state),
                pretty_portal_enum(spoke.status),
                pretty_spoke_type(spoke.spoke_type),
                spoke.spoke_root_path,
                addr,
            ]
            rows.append(row)

        print(tabulate(rows, columns))


class ListHubPortals(qumulo.lib.opts.Subcommand):
    NAME = 'portal_list_hubs'
    SYNOPSIS = 'List the configuration and status of all hub portals on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        hubs = rest_client.portal.list_hub_portals()

        print(format_hub_portals(hubs, args.json))


class ListSpokePortals(qumulo.lib.opts.Subcommand):
    NAME = 'portal_list_spokes'
    SYNOPSIS = 'List the configuration and status of all spoke portals on the current cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-j', '--json', help=JSON_HELP, action='store_true')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        spokes = rest_client.portal.list_spoke_portals()
        print(format_spoke_portals(spokes, args.json))


class GetEvictionSettings(qumulo.lib.opts.Subcommand):
    NAME = 'portal_get_eviction_settings'
    SYNOPSIS = 'Retrieve the configuration for automated removal of cached data'

    @staticmethod
    def main(rest_client: RestClient, _: argparse.Namespace) -> None:
        settings = rest_client.portal.get_eviction_settings()
        print(pretty_json(settings.data.to_dict()))


class SetEvictionSettings(qumulo.lib.opts.Subcommand):
    NAME = 'portal_set_eviction_settings'
    SYNOPSIS = 'Configure the automated removal of cached data'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-f',
            '--free-threshold',
            type=float,
            required=True,
            help=(
                'The threshold of remaining free capacity on a cluster, as a decimal number '
                'between 0 and 1, that triggers the automated removal of cached data. For example, '
                'if you set this value to 0.05, the system begins to remove cached data from spoke '
                'portals when the cluster is 95%% full.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        config = EvictionSettings(free_threshold=args.free_threshold)
        settings = rest_client.portal.set_eviction_settings(config)
        print(pretty_json(settings.data.to_dict()))


class ListFileSystems(qumulo.lib.opts.Subcommand):
    NAME = 'portal_list_file_systems'
    SYNOPSIS = 'Retrieve portal information for all file systems'

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        file_systems = rest_client.portal.list_file_systems()
        print(pretty_json([fs.to_dict() for fs in file_systems]))


class GetFileSystem(qumulo.lib.opts.Subcommand):
    NAME = 'portal_get_file_system'
    SYNOPSIS = 'Retrieve portal information for a specific file system'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--uuid', type=str, required=True, help='File System UUID')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        file_system = rest_client.portal.get_file_system(args.uuid)
        print(pretty_json(file_system.to_dict()))
