# Copyright (c) 2020 Qumulo, Inc.
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

from dataclasses import asdict

import qumulo.lib.opts

from qumulo.lib.request import pretty_json
from qumulo.rest.encryption import KmipKeyCreateParams, KmipKeyCreatePost, KmipKeyStoreConfigPut
from qumulo.rest_client import RestClient


class RotateEncryptionKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 'rotate_encryption_keys'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            '--key-id',
            type=str,
            dest='key_id',
            help='The unique ID of the master key for at-rest encryption.',
        )
        group.add_argument(
            '--create-key-with-name',
            type=str,
            dest='key_name',
            help='The name of the key that will be created and used for at-rest encryption.',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if not args.key_name:
            rest_client.encryption.rotate_keys_v2(key_id=args.key_id)
        else:
            key_create_config = KmipKeyCreatePost(key_name=args.key_name, kms_config=None)
            key_id = rest_client.encryption.create_kmip_key(config=key_create_config)
            print('A new KMS key was created with ID ' + key_id)
            rest_client.encryption.rotate_keys_v2(key_id=key_id)
        print('Key rotation complete')


class EncryptionGetStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_status'
    SYNOPSIS = 'Get the status of at-rest encryption.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.get_key_store_status()
        print(pretty_json(resp.to_dict()))


class GetEncryptionKeyStoreCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_key_store'
    SYNOPSIS = 'Get the active at-rest encryption configuration.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.get_key_store_config()
        print(pretty_json(asdict(resp)))


class PutEncryptionKeyStoreCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_set_key_store'
    SYNOPSIS = 'Set the active at-rest encryption configuration.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest='key_store_type', required=True)

        kmip_parser = subparsers.add_parser(
            'kms',
            help=(
                'Configure the cluster to use a Key Management Server to store the master key for'
                ' at-rest encryption.'
            ),
        )
        kmip_parser.add_argument(
            '--client-cert',
            type=str,
            dest='client_cert',
            required=True,
            help=(
                'The path to the client certificate file that Qumulo Core uses to authenticate the'
                ' cluster to a Key Management Server.'
            ),
        )
        kmip_parser.add_argument(
            '--client-private-key',
            type=str,
            dest='client_private_key',
            required=True,
            help=(
                "The path to the file that contains the client's private key that corresponds to"
                ' the client certificate.'
            ),
        )
        kmip_parser.add_argument(
            '--hostname',
            type=str,
            dest='hostname',
            required=True,
            help='The hostname of the Key Management Server.',
        )

        # According to the specification, the port should be 5696 but we allow overriding it for
        # testing and handling non-standard configurations.
        # http://docs.oasis-open.org/kmip/profiles/v1.4/os/kmip-profiles-v1.4-os.html#_Toc491431402
        default_port = '5696'
        kmip_parser.add_argument(
            '--port',
            type=str,
            dest='kmip_server_port',
            required=False,
            default=default_port,
            help='The port number of the Key Management Server, 5696 by default.',
        )

        group = kmip_parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--key-id',
            type=str,
            dest='key_id',
            help='The unique ID of the master key for at-rest encryption.',
        )
        group.add_argument(
            '--create-key-with-name',
            type=str,
            dest='key_name',
            help='The name of the key that will be created and used for at-rest encryption.',
        )

        kmip_parser.add_argument(
            '--server-ca-cert',
            type=str,
            dest='server_ca_cert',
            required=True,
            help=(
                'The path to the file that contains the Certificate Authority certificate that'
                ' Qumulo Core uses to validate the TLS connection to the Key Management Server.'
            ),
        )

        # Local doesn't need any parameters
        subparsers.add_parser('local', help='Use a local master key for at-rest encryption.')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        key_store_config = None
        if args.key_store_type == 'kms':
            client_cert_data = ''
            with open(args.client_cert) as f:
                client_cert_data = f.read()

            client_private_key_data = ''
            with open(args.client_private_key) as f:
                client_private_key_data = f.read()

            server_ca_cert_data = ''
            with open(args.server_ca_cert) as f:
                server_ca_cert_data = f.read()

            if args.key_id is not None:
                key_id = args.key_id
            else:
                key_create_config = KmipKeyCreatePost(
                    key_name=args.key_name,
                    kms_config=KmipKeyCreateParams(
                        client_cert=client_cert_data,
                        client_private_key=client_private_key_data,
                        hostname=args.hostname,
                        port=args.kmip_server_port,
                        server_ca_cert=server_ca_cert_data,
                    ),
                )
                key_id = rest_client.encryption.create_kmip_key(config=key_create_config)
                print('A new KMS key was created with ID ' + key_id)

            key_store_config = KmipKeyStoreConfigPut(
                client_cert=client_cert_data,
                client_private_key=client_private_key_data,
                hostname=args.hostname,
                key_id=key_id,
                port=args.kmip_server_port,
                server_ca_cert=server_ca_cert_data,
            )

        rest_client.encryption.put_key_store_config(config=key_store_config)
