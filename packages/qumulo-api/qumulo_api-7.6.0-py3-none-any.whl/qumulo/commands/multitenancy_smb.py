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

import qumulo.lib.opts
import qumulo.rest.multitenancy_smb as multitenancy_smb

from qumulo.commands.smb import add_smb_settings_options, extract_modify_settings_args
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


class MultitenancySMBGetGlobalSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_get_global_settings'
    SYNOPSIS = 'Retrieve global default SMB settings'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'These settings apply to the SMB for any tenants for which tenant-specific SMB settings '
        'have not been defined.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(multitenancy_smb.get_global_settings(rest_client.conninfo, rest_client.credentials))


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


class MultitenancySMBModifyGlobalSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_modify_global_settings'
    SYNOPSIS = 'Modify global default SMB settings'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'These settings apply to the SMB for any tenants for which tenant-specific SMB settings '
        'have not been defined.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        add_smb_settings_options(parser)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        settings_json = extract_modify_settings_args(args)
        print(
            multitenancy_smb.modify_global_settings(
                rest_client.conninfo, rest_client.credentials, settings_json
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


class MultitenancySMBListSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_list_settings'
    SYNOPSIS = 'Retrieve SMB settings for all tenant that have tenant-specific settings configured'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Only returns the SMB settings if the tenant has had tenant-specific settings configured. '
        'If a tenant is using the global settings, that tenant will not up here.'
    )

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(multitenancy_smb.list_settings(rest_client.conninfo, rest_client.credentials))


#   ____      _     ____       _   _   _
#  / ___| ___| |_  / ___|  ___| |_| |_(_)_ __   __ _ ___
# | |  _ / _ \ __| \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |_| |  __/ |_   ___) |  __/ |_| |_| | | | | (_| \__ \
#  \____|\___|\__| |____/ \___|\__|\__|_|_| |_|\__, |___/
#                                              |___/
#  FIGLET: Get Settings
#


class MultitenancySMBGetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_get_settings'
    SYNOPSIS = 'Retrieve SMB settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'If tenant-specific SMB settings have not yet been defined for a tenant, use '
        '`multitenancy_smb_get_global_settings` to retrieve the global settings instead, or '
        '`multitenancy_smb_modify_settings` to define settings for the tenant.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of tenant to get settings for'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        print(
            multitenancy_smb.get_settings(
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


class MultitenancySMBModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_modify_settings'
    SYNOPSIS = 'Modify SMB settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Set tenant-specific SMB settings for a tenant to override the default global '
        'settings.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of tenant to modify settings for'
        )
        add_smb_settings_options(parser)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        settings_json = extract_modify_settings_args(args)

        try:
            print(
                multitenancy_smb.modify_settings(
                    rest_client.conninfo, rest_client.credentials, args.tenant_id, settings_json
                )
            )
        except RequestError as e:
            if e.error_class != 'api_multitenancy_smb_tenant_settings_do_not_exist_error':
                raise

            global_settings = multitenancy_smb.get_global_settings(
                rest_client.conninfo, rest_client.credentials
            ).data

            for key, setting_field in settings_json.items():
                global_settings[key] = setting_field

            print(
                multitenancy_smb.set_settings(
                    rest_client.conninfo, rest_client.credentials, args.tenant_id, global_settings
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


class MultitenancySMBDeleteSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'multitenancy_smb_delete_settings'
    SYNOPSIS = 'Delete SMB settings for a tenant'
    DESCRIPTION = (
        f'{SYNOPSIS}\n\n'
        'Removing the tenant-specific SMB settings for a tenant restores the global default '
        'settings for the tenant.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--tenant-id', required=True, type=int, help='ID of the tenant to delete settings for'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        multitenancy_smb.delete_settings(
            rest_client.conninfo, rest_client.credentials, args.tenant_id
        )
