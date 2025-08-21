# Copyright (c) 2021 Qumulo, Inc.
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

from typing import Mapping, Sequence

import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.rest.tree_delete as tree_delete

from qumulo.lib.util import humanize, tabulate
from qumulo.rest_client import RestClient


def make_table(jobs: Sequence[Mapping[str, object]]) -> str:
    headers = [
        'id',
        'initial_capacity',
        'remaining_capacity',
        'create_time',
        'initial_path',
        'mode',
        'last_error_message',
    ]
    rows = [[job[header] for header in headers] for job in jobs]
    return tabulate(rows, headers)


class ListCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_list'
    SYNOPSIS = 'Get information about all tree delete jobs'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        results = tree_delete.list_jobs(rest_client.conninfo, rest_client.credentials)
        if args.json:
            print(results)
        else:
            print(make_table(results.data['jobs']))


class CreateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_create'
    SYNOPSIS = 'Create delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('directory', help='Directory id or path')
        parser.add_argument(
            '--force',
            '-f',
            action='store_true',
            help=(
                'Bypass path confirmation. WARNING! Tree delete can be canceled with '
                'tree_delete_cancel, but already deleted items cannot be recovered.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if not args.force:
            # N.B. you can pass an id or path to either the id_ or path arg!
            aggregates = fs.read_dir_aggregates(
                rest_client.conninfo, rest_client.credentials, id_=args.directory
            ).data
            num_files = aggregates['total_files']
            total_capacity = humanize(int(aggregates['total_capacity']))

            message = (
                f'WARNING! Are you sure that you want to delete all {num_files} '
                f'files (total size: {total_capacity}) in directory "{args.directory}"?'
            )

            if not qumulo.lib.opts.ask(CreateCommand.NAME, message):
                return

        tree_delete.create_job(rest_client.conninfo, rest_client.credentials, args.directory)


class GetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_get'
    SYNOPSIS = 'Get information about one delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id')
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        results = tree_delete.get_job(rest_client.conninfo, rest_client.credentials, args.id)
        if args.json:
            print(results)
        else:
            print(make_table([results.data]))


class CancelCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_cancel'
    SYNOPSIS = 'Cancel delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        tree_delete.cancel_job(rest_client.conninfo, rest_client.credentials, args.id)


class RestartCommand(qumulo.lib.opts.Subcommand):
    NAME = 'tree_delete_restart'
    SYNOPSIS = 'Retry errored delete job'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', help='Directory id')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        tree_delete.restart_job(rest_client.conninfo, rest_client.credentials, args.id)
