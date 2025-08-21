# Copyright (c) 2015 Qumulo, Inc.
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

# Update warning settings before anything else to filter warnings thrown at import time.
import sys

if not sys.warnoptions:
    import warnings

    # Allow DeprecationWarnings to be printed when using qq.
    warnings.simplefilter('default', DeprecationWarning)

import argparse
import logging
import os

from typing import Callable, Optional, Protocol, Sequence

import qumulo
import qumulo.commands
import qumulo.lib.auth
import qumulo.lib.opts as opts
import qumulo.lib.request

from qumulo.lib import log
from qumulo.lib.auth import Credentials
from qumulo.rest_client import DEFAULT_REST_PORT, RestClient

USER_AGENT = 'qq'

OsExists = Callable[[str], bool]


def host_options(parser: argparse.ArgumentParser, host_required: bool, os_exists: OsExists) -> None:
    arg_group = parser.add_argument_group('Target Host Options')

    # If the user is on one of the clusters nodes, they can use localhost, otherwise the user
    # must specify host.
    on_qumulo_node = os_exists('/opt/qumulo/lib')
    if on_qumulo_node:
        arg_group.add_argument('--host', default=None)
    else:
        arg_group.add_argument('--host', required=host_required)

    has_socket_path = os_exists('/run/qfsd/rest.sock')
    if has_socket_path:
        arg_group.add_argument(
            '--socket-path', type=str, default='/run/qfsd/rest.sock', help=argparse.SUPPRESS
        )
    else:
        arg_group.add_argument('--socket-path', type=str, default=None, help=argparse.SUPPRESS)
    arg_group.add_argument('--abstract-socket-path', type=str, default=None, help=argparse.SUPPRESS)

    arg_group.add_argument('--port', type=int, default=DEFAULT_REST_PORT)


def main_options(parser: argparse.ArgumentParser) -> None:
    arg_group = parser.add_argument_group('Target Namespace Options')
    arg_group.add_argument(
        '--chunked',
        action='store_true',
        default=qumulo.lib.request.DEFAULT_CHUNKED,
        help=argparse.SUPPRESS,
    )
    arg_group.add_argument(
        '--chunk-size',
        type=int,
        default=qumulo.lib.request.DEFAULT_CHUNK_SIZE_BYTES,
        help=argparse.SUPPRESS,
    )
    arg_group.add_argument(
        '--credentials-store',
        default=None,
        help='Read and writes credentials to a custom path (default: ~/.qfsd_cred)',
    )
    arg_group.add_argument('--debug', action='store_true')
    arg_group.add_argument('-v', '--verbose', action='count', default=0)
    arg_group.add_argument('--version', action='version', version=f'%(prog)s {qumulo.__version__}')
    arg_group.add_argument(
        '--timeout', type=int, default=None, help='Time (in seconds) to wait for response'
    )


class RestClientFactoryProtocol(Protocol):
    def __call__(
        self,
        args: argparse.Namespace,
        credentials: Optional[Credentials] = None,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ) -> RestClient:
        ...


def rest_client_factory(
    args: argparse.Namespace,
    credentials: Optional[Credentials] = None,
    timeout: Optional[int] = None,
    user_agent: Optional[str] = None,
) -> RestClient:
    socket_path = args.socket_path
    if args.abstract_socket_path is not None:
        socket_path = '\x00' + args.abstract_socket_path
        # Pad to 108 bytes
        socket_path = socket_path + (108 - len(socket_path)) * '\x00'
    return RestClient(
        args.host,
        args.port,
        credentials=credentials,
        timeout=timeout,
        user_agent=user_agent,
        socket_path=socket_path,
    )


def main(args: argparse.Namespace, rest_client_factory: RestClientFactoryProtocol) -> None:
    if not logging.root.handlers:
        logging.basicConfig(format='%(message)s')

    if args.debug or args.verbose > 1:
        log.setLevel(level=logging.DEBUG)
    elif args.verbose == 1:
        log.setLevel(level=logging.INFO)

    if args.credentials_store is None:
        credentials_store_path = qumulo.lib.auth.credential_store_filename()
    else:
        credentials_store_path = args.credentials_store

    credentials = qumulo.lib.auth.get_credentials(credentials_store_path)
    rest_client = rest_client_factory(
        args=args, credentials=credentials, timeout=args.timeout, user_agent=USER_AGENT
    )

    # XXX: The typing here isn't right and we're only saved because run_subcommand currently is
    # un-typed. We want to have the return type of rest_client_factory have a type that matches what
    # the command takes. Public commands take a qumulo.rest_client.RestClient, while private
    # commands take a qinternal.api.client.rest_client.RestClient, which is a subclass of
    # qumulo.rest_client.RestClient.
    opts.run_subcommand(args.subcommand, rest_client, args)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Qumulo CLI', add_help=True)
    host_options(parser, host_required=True, os_exists=os.path.exists)
    main_options(parser)
    return parser


def parse_args(parser: argparse.ArgumentParser, argv: Sequence[str]) -> argparse.Namespace:
    args = opts.parse_options(parser, argv)
    assert args is not None

    # If no subcommand is specified, the Namespace object is returned but it is
    # missing the subcommand attribute. See https://bugs.python.org/issue9253
    if not hasattr(args, 'subcommand'):
        parser.print_usage()
        print('qq: error: too few arguments; try --help to find a list of usable subcommands.')
        sys.exit(1)

    return args


def qq_main(
    argv: Sequence[str],
    parser: argparse.ArgumentParser,
    rest_client_factory: RestClientFactoryProtocol,
) -> int:
    try:
        args = parse_args(parser, argv)
        main(args, rest_client_factory)

    except KeyboardInterrupt:
        print('\nCommand interrupted')
        return 1

    except qumulo.lib.request.RequestError as e:
        # When using QQ RequestError is common and expected. Only print out a
        # terse message about the error by calling pretty_str.
        print(e.pretty_str())
        return 1

    except ValueError as e:
        if os.getenv('DEBUG_CLI') or (args is not None and args.debug):
            print('Command error: %s' % str(e))
            raise

        print('Command error: %s' % str(e))
        return 1

    except OSError as e:
        print('Connection error: %s' % str(e))
        return 1

    return 0


def qq_main_PYTHON_ARGCOMPLETE_OK() -> int:
    """
    The entry point called when `qq` is installed with the Python SDK whl (i.e. installed via `pip`).

    Why the strange name? When a user installs `qq` from a whl file, the `qq` executable they invoke
    is a short, autogenerated Python script which invokes an entry point specified by us.

    Python-argcomplete < 1.10.1 requires the magic string PYTHON_ARGCOMPLETE_OK to be within the
    first 1024 bytes of an executable to perform completion. The easiest way to inject that string
    into the auto-generated `qq` executable is by including it in the entry point name.

    python-argcomplete 1.10.1 is able to traverse through the entry point call to find an annotation
    in the original source (e.g. here), but most OS's ship older versions (e.g. Ubuntu 20.04 ships
    1.8.1).
    """  # noqa: E501
    return qq_main(sys.argv[1:], make_parser(), rest_client_factory=rest_client_factory)
