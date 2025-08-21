# Copyright (c) 2022 Qumulo, Inc.
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

from datetime import datetime, timezone
from typing import Sequence

from dateutil import parser as dateutil_parser

import qumulo.lib.opts

from qumulo.lib.auth import Credentials
from qumulo.lib.identity_util import Identity
from qumulo.lib.util import tabulate
from qumulo.rest.access_tokens import AccessTokenMetadata
from qumulo.rest_client import RestClient


def utc_datetime(arg: str) -> datetime:
    return dateutil_parser.parse(arg).astimezone(timezone.utc)


class CreateAccessTokenCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_create_access_token'
    SYNOPSIS = 'Create a long-lived access token'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        identity = parser.add_mutually_exclusive_group(required=False)
        identity.add_argument(
            '--self',
            action='store_true',
            help=('Create an access key that targets the currently logged in user.'),
        )
        identity.add_argument(
            'identifier',
            type=Identity,
            nargs='?',
            help=(
                'An auth_id, SID, or name optionally qualified with a domain prefix (e.g '
                '"local:name", "ad:name", "AD\\name") or an ID type (e.g. "auth_id:513", '
                '"SID:S-1-1-0"). Groups are not supported for access tokens, must be a user.'
            ),
        )

        parser.add_argument(
            '--expiration-time',
            type=utc_datetime,
            help=(
                'The expiration time of the access token. After this time, the token will no '
                'longer be usable for authentication. For example, "Jan 20 2024", "1/20/2024", '
                'or "2024-01-20 12:00", with times interpreted in UTC timezone.'
            ),
        )

        parser.add_argument(
            '--file',
            '-f',
            metavar='PATH',
            help=(
                'File to store the access token credential. That file can be passed to the '
                '--credentials-store argument to authenticate using the created access token.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.self:
            identity = Identity({'auth_id': rest_client.auth.who_am_i()['id']})
        else:
            identity = Identity(args.identifier)

        access_token = rest_client.access_tokens.create(
            identity, expiration_time=args.expiration_time
        )

        if args.file is not None:
            credentials = Credentials(access_token.bearer_token)
            with open(args.file, 'w') as f:
                f.write(credentials.to_disk().to_json())

        print(access_token.to_json(sort_keys=True, indent=4))


class GetAccessTokenCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_get_access_token'
    SYNOPSIS = 'Get metadata for the specified access token'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', type=str, help='The unique ID of the access token.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(rest_client.access_tokens.get(args.id).to_json(sort_keys=True, indent=4))


class ModifyAccessTokenCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_modify_access_token'
    SYNOPSIS = 'Modify the specified access token'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'id', type=str, help='The unique ID of the access token to be modified.'
        )

        parser.add_argument(
            '--expiration-time',
            type=utc_datetime,
            help=(
                'The expiration time of the access token. After this time, the token will no '
                'longer be usable for authentication. For example, "Jan 20 2024", "1/20/2024", '
                'or "2024-01-20 12:00", with times interpreted in UTC timezone.'
            ),
        )

        parser.add_argument(
            '--enable',
            '-e',
            action='store_const',
            const=True,
            dest='enabled',
            help='Enable the access token.',
        )
        parser.add_argument(
            '--disable',
            '-d',
            action='store_const',
            const=False,
            dest='enabled',
            help=(
                'Disable the access token. It can no longer be used to authenticate until it is'
                ' enabled.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        metadata = rest_client.access_tokens.modify(
            args.id, expiration_time=args.expiration_time, enabled=args.enabled
        )
        print(metadata.to_json(sort_keys=True, indent=4))


class DeleteAccessTokenCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_delete_access_token'
    SYNOPSIS = 'Delete the specified access token'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('id', type=str, help='The unique ID of the access token to be deleted.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.access_tokens.delete(args.id)


def make_access_keys_table(access_tokens: Sequence[AccessTokenMetadata]) -> str:
    headers = ['id', 'user', 'creator', 'creation time', 'expiration time', 'enabled']
    rows = []
    for access_token in access_tokens:
        row = []
        row.append(access_token.id)
        row.append(str(Identity(access_token.user)))
        row.append(str(Identity(access_token.creator)))
        row.append(access_token.creation_time)
        row.append(access_token.expiration_time or '')
        # Prior to 5.3.3, access tokens could not be disabled.
        row.append(str(access_token.enabled if access_token.enabled is not None else True))
        rows.append(row)

    return tabulate(rows, headers)


class ListAccessTokensCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_list_access_tokens'
    SYNOPSIS = 'List metadata for all access tokens'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')
        identity = parser.add_mutually_exclusive_group(required=False)
        identity.add_argument(
            '--user',
            type=Identity,
            help=(
                'Show access tokens belonging to a specific user. Use an auth_id, SID, or name'
                ' optionally qualified with a domain prefix (e.g "local:name", "ad:name",'
                ' "AD\\name") or an ID type (e.g. "auth_id:513", "SID:S-1-1-0"). Groups are not'
                ' supported for access tokens, must be a user.'
            ),
        )
        identity.add_argument(
            '--self', action='store_true', help=('List only access keys that target yourself.')
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        user = args.user
        if args.self:
            user = Identity({'auth_id': rest_client.auth.who_am_i()['id']})

        responses = rest_client.access_tokens.list(user=user)
        entries = [entry for response in responses for entry in response.entries]
        if args.json:
            tokens = [entry.to_dict() for entry in entries]
            print(json.dumps(tokens, indent=4))
        else:
            print(make_access_keys_table(entries))
