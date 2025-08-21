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


import json
import sys
import textwrap

from argparse import ArgumentParser, FileType, Namespace, RawDescriptionHelpFormatter, SUPPRESS

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.dns as dns

from qumulo.commands.network import parse_comma_deliminated_args
from qumulo.rest.dns import ApiDnsClearCache, ApiDnsConfigPatch
from qumulo.rest_client import RestClient


class ResolveIpAddressesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_resolve_ips'
    SYNOPSIS = 'Resolve IP addresses to hostnames'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--ips', required=True, nargs='+', help='IP addresses to resolve')
        # XXX DNS Config ID is part of the not yet released Multi-AD feature
        parser.add_argument('--dns-config-id', required=False, type=int, help=SUPPRESS)

    @staticmethod
    def main(rest_client: RestClient, args: Namespace) -> None:
        print(
            dns.resolve_ips_to_names(
                rest_client.conninfo,
                rest_client.credentials,
                args.ips,
                dns_config_id=args.dns_config_id,
            )
        )


class ResolveHostnamesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_resolve_hostnames'
    SYNOPSIS = 'Resolve hostnames to IP addresses'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--hosts', required=True, nargs='+', help='Hostnames to resolve')
        # XXX DNS Config ID is part of the not yet released Multi-AD feature
        parser.add_argument('--dns-config-id', required=False, type=int, help=SUPPRESS)

    @staticmethod
    def main(rest_client: RestClient, args: Namespace) -> None:
        print(
            dns.resolve_names_to_ips(
                rest_client.conninfo,
                rest_client.credentials,
                args.hosts,
                dns_config_id=args.dns_config_id,
            )
        )


class ClearDnsCacheCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_clear_cache'
    SYNOPSIS = 'Clear the local DNS cache'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        # XXX DNS Config ID is part of the not yet released Multi-AD feature
        parser.add_argument(
            '--dns-config-id', required=False, type=int, default=None, help=SUPPRESS
        )

        skip_args = parser.add_mutually_exclusive_group(required=False)

        skip_args.add_argument(
            '--skip-reverse-cache',
            action='store_true',
            help='When this flag is set, the reverse lookup cache is not cleared.',
        )

        skip_args.add_argument(
            '--skip-forward-cache',
            action='store_true',
            help='When this flag is set, the forward lookup cache is not cleared.',
        )

    @staticmethod
    def main(rest_client: RestClient, args: Namespace) -> None:
        options = ApiDnsClearCache(
            dns_config_id=args.dns_config_id,
            skip_forward_cache=args.skip_forward_cache,
            skip_reverse_cache=args.skip_reverse_cache,
        )
        dns.clear_cache(rest_client.conninfo, rest_client.credentials, options)


#  _             _
# | | ___   ___ | | ___   _ _ __
# | |/ _ \ / _ \| |/ / | | | '_ \
# | | (_) | (_) |   <| |_| | |_) |
# |_|\___/ \___/|_|\_\\__,_| .__/____
#                          |_| |_____|
#                           _     _
#   _____   _____ _ __ _ __(_) __| | ___  ___
#  / _ \ \ / / _ \ '__| '__| |/ _` |/ _ \/ __|
# | (_) \ V /  __/ |  | |  | | (_| |  __/\__ \
#  \___/ \_/ \___|_|  |_|  |_|\__,_|\___||___/
#  FIGLET: lookup_overrides
#


class DNSLookupOverridesGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_get_lookup_overrides'
    SYNOPSIS = 'List the configured set of DNS lookup overrides.'
    DESCRIPTION = textwrap.dedent(
        """\
        List the configured set of DNS lookup overrides.

        These rules override any lookup results from the configured DNS servers
        and serve as static mappings between IP address and hostname."""
    )

    @staticmethod
    def main(rest_client: RestClient, _args: Namespace) -> None:
        print(dns.lookup_overrides_get(rest_client.conninfo, rest_client.credentials))


class DNSLookupOverridesSetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_set_lookup_overrides'
    SYNOPSIS = 'Replace the configured set of DNS lookup overrides.'
    DESCRIPTION = textwrap.dedent(
        """\
        Replace the configured set of DNS lookup overrides.

        These rules override any lookup results from the configured DNS
        servers and serve as static mappings between IP address and hostname.
        The provided overrides document should have the following structure:

        {
          "lookup_overrides": [
              {"ip_address": "1.2.3.4", "aliases": ["foo.com", "www.foo.com"]},
              {"ip_address": "2.3.4.5", "aliases": ["bar.com", "www.bar.com"]}
          ]
        }

        The first hostname in the "aliases" list is what will be resolved
        when doing reverse lookups from IP address to hostname."""
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.formatter_class = RawDescriptionHelpFormatter
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--file', help='JSON-encoded file containing overrides.', type=FileType('rb')
        )
        group.add_argument(
            '--stdin',
            action='store_const',
            const=sys.stdin,
            dest='file',
            help='Read JSON-encoded overrides from stdin',
        )

    @staticmethod
    def main(rest_client: RestClient, args: Namespace) -> None:
        overrides = json.load(args.file)
        dns.lookup_overrides_set(rest_client.conninfo, rest_client.credentials, overrides)


#                _                       _                              __ _
#  ___ _   _ ___| |_ ___ _ __ ___     __| |_ __  ___    ___ ___  _ __  / _(_) __ _
# / __| | | / __| __/ _ \ '_ ` _ \   / _` | '_ \/ __|  / __/ _ \| '_ \| |_| |/ _` |
# \__ \ |_| \__ \ ||  __/ | | | | | | (_| | | | \__ \ | (_| (_) | | | |  _| | (_| |
# |___/\__, |___/\__\___|_| |_| |_|  \__,_|_| |_|___/  \___\___/|_| |_|_| |_|\__, |
#      |___/                                                                 |___/
#  FIGLET: system dns config
#


class DnsSystemConfigGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_get_system_config'
    SYNOPSIS = "Get the system's DNS configuration."
    DESCRIPTION = textwrap.dedent(
        """\
        Get the system's DNS configuration.

        This is the configuration that's applied to the operating system via
        /etc/resolv.conf and /etc/hosts.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def main(rest_client: RestClient, _args: Namespace) -> None:
        print(dns.system_config_get(rest_client.conninfo, rest_client.credentials))


class DnsSystemConfigModifyCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_modify_system_config'
    SYNOPSIS = "Modify the system's DNS configuration."
    DESCRIPTION = textwrap.dedent(
        """\
        Modify the system's DNS servers and search domains. Overrides can be set
        using dns_set_lookup_overrides.

        WARNING: This is a preview command, and is subject to changes without warning.
        """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        args_group = parser.add_mutually_exclusive_group()
        args_group.add_argument(
            '--dns-servers',
            nargs='+',
            default=[],
            action='append',
            metavar='<address-or-range>',
            help=(
                'List of DNS Server IP addresses. Can be a'
                ' single address or multiple comma separated addresses.'
                ' eg. 10.1.1.10 or 10.1.1.10,10.1.1.15'
            ),
        )

        args_group.add_argument(
            '--clear-dns-servers', action='store_true', help='Clear the DNS servers'
        )

        args_domain_group = parser.add_mutually_exclusive_group()
        args_domain_group.add_argument(
            '--dns-search-domains',
            nargs='+',
            default=[],
            action='append',
            metavar='<search-domain>',
            help=(
                'List of DNS Search Domains to replace the current domains. Can be a single domain '
                'or multiple comma separated domains. eg. my.domain.com or '
                'my.domain.com,your.domain.com'
            ),
        )

        args_domain_group.add_argument(
            '--clear-dns-search-domains', action='store_true', help='Clear the DNS search domains'
        )

    @staticmethod
    def main(rest_client: RestClient, args: Namespace) -> None:
        config = dict()
        dns_servers_input = getattr(args, 'dns_servers', None)
        if dns_servers_input:
            config['dns_servers'] = parse_comma_deliminated_args(dns_servers_input)
        dns_search_domains_input = getattr(args, 'dns_search_domains', None)
        if dns_search_domains_input:
            config['dns_search_domains'] = parse_comma_deliminated_args(dns_search_domains_input)

        if args.clear_dns_servers:
            config['dns_servers'] = []
        if args.clear_dns_search_domains:
            config['dns_search_domains'] = []

        print(
            dns.system_config_modify(
                rest_client.conninfo, rest_client.credentials, ApiDnsConfigPatch.from_dict(config)
            )
        )
