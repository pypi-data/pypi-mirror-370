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

from qumulo.rest_client import RestClient


class ObjectStorageGetURIsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'get_object_storage_uris'
    SYNOPSIS = (
        'Get the list of object storage uris configured on the cluster. These object storage uris '
        'store the persisted pstore data for an object-backed cluster. For a cluster that is not '
        'backed by objects, the returned list is always empty.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(rest_client.object_storage.get_uris())


class ObjectStorageAddURIsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'add_object_storage_uris'
    SYNOPSIS = (
        "Add object storage URIs for configuring the cluster's data persistence. As the system "
        'provisions additional storage capacity on the cluster (which increases together with the '
        'clamp increase functionality), the file system recognizes and uses any new object storage '
        'URIs. Ensure that the new URIs point to empty S3 buckets or storage accounts and that the '
        'nodes on the cluster have sufficient permissions to perform LIST, PUT, GET, and DELETE '
        'operations on these buckets or accounts. Performing this action on a cluster not backed '
        'by objects results in an error.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--uris', nargs='+', default=[], help='The new URIs to add to the cluster.'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.object_storage.add_uris(args.uris)
