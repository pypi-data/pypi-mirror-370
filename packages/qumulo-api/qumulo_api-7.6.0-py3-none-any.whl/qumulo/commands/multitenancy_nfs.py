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

from typing import Optional

import qumulo.lib.opts
import qumulo.rest.multitenancy_nfs as multitenancy_nfs

from qumulo.commands.nfs import add_nfs_settings_options
from qumulo.lib.request import RequestError
from qumulo.rest_client import RestClient

#   ____ _       _           _    ____      _
#  / ___| | ___ | |__   __ _| |  / ___| ___| |_
# | |  _| |/ _ \| '_ \ / _` | | | |  _ / _ \ __|
# | |_| | | (_) | |_) | (_| | | | |_| |  __/ |_
#  \____|_|\___/|_.__/ \__,_|_|  \____|\___|\__|
#  ____       _   _   _
# / ___|  ___| |_| |_(_)_ __   __ _ ___
# \___ \ / _ \ __| __| | '_ \ / _` / __|
#  ___) |  __/ |_| |_| | | | | (_| \__ \
# |____/ \___|\__|\__|_|_| |_|\__, |___/
#                             |___/
#  FIGLET: Global Get Settings
#


class MultitenancyNFSGetGlobalSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_get_global_settings'
    SYNOPSIS = 'Retrieve global default NFS settings'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'These settings apply to the NFS for any tenants for which tenant-specific NFS settings '
        'have not been defined.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(multitenancy_nfs.get_global_settings(rest_client.conninfo, rest_client.credentials))


#   ____ _       _           _   __  __           _ _  __
#  / ___| | ___ | |__   __ _| | |  \/  | ___   __| (_)/ _|_   _
# | |  _| |/ _ \| '_ \ / _` | | | |\/| |/ _ \ / _` | | |_| | | |
# | |_| | | (_) | |_) | (_| | | | |  | | (_) | (_| | |  _| |_| |
#  \____|_|\___/|_.__/ \__,_|_| |_|  |_|\___/ \__,_|_|_|  \__, |
#                                                         |___/
#  ____       _   _   _
# / ___|  ___| |_| |_(_)_ __   __ _ ___
# \___ \ / _ \ __| __| | '_ \ / _` / __|
#  ___) |  __/ |_| |_| | | | | (_| \__ \
# |____/ \___|\__|\__|_|_| |_|\__, |___/
#                             |___/
#  FIGLET: Global Modify Settings
#


class MultitenancyNFSModifyGlobalSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_modify_global_settings'
    SYNOPSIS = 'Modify global default NFS settings'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'These settings apply to the NFS for any tenants for which tenant-specific NFS settings '
        'have not been defined.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        add_nfs_settings_options(parser)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(
            multitenancy_nfs.modify_global_settings(
                rest_client.conninfo,
                rest_client.credentials,
                v4_enabled=args.v4_enabled,
                krb5_enabled=args.krb5_enabled,
                krb5p_enabled=args.krb5p_enabled,
                krb5i_enabled=args.krb5i_enabled,
                auth_sys_enabled=args.auth_sys_enabled,
            )
        )


#  _     _     _     ____       _   _   _
# | |   (_)___| |_  / ___|  ___| |_| |_(_)_ __   __ _ ___
# | |   | / __| __| \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |___| \__ \ |_   ___) |  __/ |_| |_| | | | | (_| \__ \
# |_____|_|___/\__| |____/ \___|\__|\__|_|_| |_|\__, |___/
#                                               |___/
#  FIGLET: List Settings
#


class MultitenancyNFSListSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_list_settings'
    SYNOPSIS = 'Retrieve NFS settings for all tenant that have tenant-specific settings configured'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Only returns the NFS settings if the tenant has had tenant-specific settings configured. '
        'If a tenant is using the global settings, that tenant will not appear here.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(multitenancy_nfs.list_settings(rest_client.conninfo, rest_client.credentials))


#   ____      _     ____       _   _   _
#  / ___| ___| |_  / ___|  ___| |_| |_(_)_ __   __ _ ___
# | |  _ / _ \ __| \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |_| |  __/ |_   ___) |  __/ |_| |_| | | | | (_| \__ \
#  \____|\___|\__| |____/ \___|\__|\__|_|_| |_|\__, |___/
#                                              |___/
#  FIGLET: Get Settings
#


class MultitenancyNFSGetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_get_settings'
    SYNOPSIS = 'Retrieve NFS settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'If tenant-specific NFS settings have not yet been defined for a tenant, use '
        '`multitenancy_nfs_get_global_settings` to retrieve the global settings, or '
        '`multitenancy_nfs_modify_settings` to define settings for the tenant.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of tenant to get settings for'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(
            multitenancy_nfs.get_settings(
                rest_client.conninfo, rest_client.credentials, args.tenant_id
            )
        )


#  __  __           _ _  __         ____       _   _   _
# |  \/  | ___   __| (_)/ _|_   _  / ___|  ___| |_| |_(_)_ __   __ _ ___
# | |\/| |/ _ \ / _` | | |_| | | | \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |  | | (_) | (_| | |  _| |_| |  ___) |  __/ |_| |_| | | | | (_| \__ \
# |_|  |_|\___/ \__,_|_|_|  \__, | |____/ \___|\__|\__|_|_| |_|\__, |___/
#                           |___/                              |___/
#  FIGLET: Modify Settings
#


class MultitenancyNFSModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_modify_settings'
    SYNOPSIS = 'Modify NFS settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Set tenant-specific NFS settings for a tenant to override the default global settings.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of tenant to modify settings for'
        )
        add_nfs_settings_options(parser)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        try:
            print(
                multitenancy_nfs.modify_settings(
                    rest_client.conninfo,
                    rest_client.credentials,
                    args.tenant_id,
                    v4_enabled=args.v4_enabled,
                    krb5_enabled=args.krb5_enabled,
                    krb5p_enabled=args.krb5p_enabled,
                    krb5i_enabled=args.krb5i_enabled,
                    auth_sys_enabled=args.auth_sys_enabled,
                )
            )
        except RequestError as e:
            if e.error_class != 'api_nfs_tenant_settings_do_not_exist_error':
                raise

            global_settings = multitenancy_nfs.get_global_settings(
                rest_client.conninfo, rest_client.credentials
            ).data

            def merge_settings(args_enabled: Optional[bool], default_enabled: bool) -> bool:
                return default_enabled if args_enabled is None else args_enabled

            print(
                multitenancy_nfs.set_settings(
                    rest_client.conninfo,
                    rest_client.credentials,
                    args.tenant_id,
                    v4_enabled=merge_settings(args.v4_enabled, global_settings['v4_enabled']),
                    krb5_enabled=merge_settings(args.krb5_enabled, global_settings['krb5_enabled']),
                    krb5p_enabled=merge_settings(
                        args.krb5p_enabled, global_settings['krb5p_enabled']
                    ),
                    krb5i_enabled=merge_settings(
                        args.krb5i_enabled, global_settings['krb5i_enabled']
                    ),
                    auth_sys_enabled=merge_settings(
                        args.auth_sys_enabled, global_settings['auth_sys_enabled']
                    ),
                )
            )


#  ____       _      _         ____       _   _   _
# |  _ \  ___| | ___| |_ ___  / ___|  ___| |_| |_(_)_ __   __ _ ___
# | | | |/ _ \ |/ _ \ __/ _ \ \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |_| |  __/ |  __/ ||  __/  ___) |  __/ |_| |_| | | | | (_| \__ \
# |____/ \___|_|\___|\__\___| |____/ \___|\__|\__|_|_| |_|\__, |___/
#                                                         |___/
#  FIGLET: Delete Settings
#


class MultitenancyNFSDeleteSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_nfs_delete_settings'
    SYNOPSIS = 'Delete NFS settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Removing the tenant-specific NFS settings for a tenant restores the global default '
        'settings for the tenant.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of the tenant to delete settings for'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        multitenancy_nfs.delete_settings(
            rest_client.conninfo, rest_client.credentials, args.tenant_id
        )
