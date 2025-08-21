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


import argparse

import qumulo.lib.opts
import qumulo.rest.shutdown as shutdown

from qumulo.rest_client import RestClient


def ask_for_shutdown(command: str, target: str) -> bool:
    message = f'Are you sure you want to {command} the {target}'
    return qumulo.lib.opts.ask(command, message)


class HaltClusterCommand(qumulo.lib.opts.Subcommand):
    NAME = 'halt_cluster'
    SYNOPSIS = 'Halt the cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.force or ask_for_shutdown('halt', 'cluster'):
            shutdown.halt_cluster(rest_client.conninfo, rest_client.credentials)
            print('The cluster is halting.')


class RebootStartCommand(qumulo.lib.opts.Subcommand):
    NAME = 'reboot_start'
    SYNOPSIS = 'Start a cluster-wide reboot'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--rolling',
            dest='is_rolling',
            action='store_true',
            help=(
                'Reboot nodes one set at a time, depending on the number of node failures '
                'configured in the protection system'
            ),
        )
        parser.add_argument(
            '--num-nodes',
            dest='num_nodes_to_reboot',
            action='store',
            type=int,
            required=False,
            help=(
                'Using the --rolling flag lets you specify the number of nodes to reboot at a '
                'time. The number of nodes must be greater than 0 and less than or equal to the '
                'number of node failures that your cluster permits. By default, this value is the '
                'number of permitted node failures minus 1 (1 node minimum).'
            ),
        )
        parser.add_argument('--force', action='store_true', dest='force', help='Do not prompt')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if not args.is_rolling and args.num_nodes_to_reboot:
            raise ValueError('argument --num-nodes only allowed with argument --rolling')
        if args.force or ask_for_shutdown('reboot', 'cluster'):
            shutdown.reboot_start(
                rest_client.conninfo,
                rest_client.credentials,
                args.is_rolling,
                args.num_nodes_to_reboot,
            )
            print('The cluster is rebooting.')


class RebootPauseCommand(qumulo.lib.opts.Subcommand):
    NAME = 'reboot_pause'
    SYNOPSIS = 'Pause a cluster-wide reboot'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        shutdown.reboot_pause(rest_client.conninfo, rest_client.credentials)


class RebootResumeCommand(qumulo.lib.opts.Subcommand):
    NAME = 'reboot_resume'
    SYNOPSIS = 'Resume a cluster-wide reboot'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        shutdown.reboot_resume(rest_client.conninfo, rest_client.credentials)


class RebootStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'reboot_status'
    SYNOPSIS = 'Retrieve status of reboot manager'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(shutdown.reboot_status(rest_client.conninfo, rest_client.credentials))


class ContainerRestartCommand(qumulo.lib.opts.Subcommand):
    NAME = 'container_restart'
    SYNOPSIS = 'Restart the qcore container'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--node-id',
            required=False,
            type=int,
            help=('Restart the container on the specified node. Defaults to the current node.'),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.node_id is not None:
            shutdown.container_restart_node(
                rest_client.conninfo, rest_client.credentials, args.node_id
            )
        else:
            shutdown.container_restart(rest_client.conninfo, rest_client.credentials)

        print('The container is restarting.')
