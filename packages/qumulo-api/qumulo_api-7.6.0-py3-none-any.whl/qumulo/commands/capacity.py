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

import qumulo.commands.cluster
import qumulo.lib.opts
import qumulo.lib.util as util

from qumulo.lib.opts import str_decode
from qumulo.rest_client import RestClient


class CapacityLimitGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'capacity_clamp_get'
    SYNOPSIS = (
        'Get the capacity clamp value in bytes, which can be set via PUT API or during'
        ' cluster creation. When the cluster provisions more pstores, it will take this'
        ' value into account. The cluster will not provision new pstores if the usable'
        ' capacity would exceed this value.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        capacity_clamp = rest_client.capacity.get_capacity_clamp()
        if capacity_clamp:
            print(util.humanize(capacity_clamp))
        else:
            print(None)


class CapacityLimitSetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'capacity_clamp_set'
    SYNOPSIS = (
        'Set the capacity clamp value in bytes. This limits the capacity that will be'
        ' provisioned to be no more than the clamp value. A value below the current'
        ' provisioned capacity has no effect. The actual stored value will be a pstore'
        ' count that produces a byte count closest to the requested bytes without going'
        ' over. If the change is applied successfully, quorum will be abandoned and the'
        ' change will appear in the new quorum.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--clamp',
            type=str_decode,
            help='The capacity clamp to set as a human readable byte count (e.g. "10TB").',
        )
        group.add_argument(
            '--disable', action='store_true', help='Remove the capacity clamp on the cluster.'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.disable:
            rest_client.capacity.put_capacity_clamp(None)
        else:
            limit_in_bytes = util.get_bytes(args.clamp)
            rest_client.capacity.put_capacity_clamp(limit_in_bytes)
