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
import sys

from collections import namedtuple
from datetime import timedelta
from enum import Enum
from typing import Dict, List, Optional, Sequence, TypeVar

import qumulo.lib.opts
import qumulo.lib.util as util

from qumulo.rest.web_ui import WebUiSettings
from qumulo.rest_client import RestClient

T = TypeVar('T')


def update_value(
    current_value: Optional[T], input_value: Optional[T], clear_value: bool
) -> Optional[T]:
    if clear_value:
        return None

    if input_value is None:
        return current_value

    return input_value


class SettingsField(Enum):
    INACTIVITY_TIMEOUT = 'Inactivity timeout'
    LOGIN_BANNER = 'Login banner'


SettingsFieldArgumentConfig = namedtuple(
    'SettingsFieldArgumentConfig', 'set_arg set_dest clear_arg clear_dest'
)

INACTIVITY_CONFIG = SettingsFieldArgumentConfig(
    set_arg='--inactivity-timeout',
    set_dest='inactivity_timeout',
    clear_arg='--disable-inactivity-timeout',
    clear_dest='inactivity_timeout_clear',
)

LOGIN_BANNER_CONFIG = SettingsFieldArgumentConfig(
    set_arg='--login-banner',
    set_dest='login_banner_file',
    clear_arg='--disable-login-banner',
    clear_dest='login_banner_clear',
)

SETTINGS_FIELD_ARGUMENT_CONFIGS = [INACTIVITY_CONFIG, LOGIN_BANNER_CONFIG]

PUBLIC_SETTINGS_FIELD_ARGUMENT_CONFIGS = [INACTIVITY_CONFIG, LOGIN_BANNER_CONFIG]

DEFAULT_SETTINGS_TO_DISPLAY = (SettingsField.INACTIVITY_TIMEOUT, SettingsField.LOGIN_BANNER)


# Format the Web UI settings to be human-readable
class SettingsForDisplay:
    def __init__(
        self, settings: WebUiSettings, fields: Sequence[SettingsField] = DEFAULT_SETTINGS_TO_DISPLAY
    ):
        self.settings: Dict[SettingsField, str] = {}

        if settings.inactivity_timeout is not None:
            inactivity_timeout_minutes = int(settings.inactivity_timeout / timedelta(minutes=1))
            self.settings[
                SettingsField.INACTIVITY_TIMEOUT
            ] = f'{inactivity_timeout_minutes} minutes'

        if settings.login_banner is not None:
            self.settings[SettingsField.LOGIN_BANNER] = settings.login_banner

        self.fields = fields

    def __str__(self) -> str:
        return util.tabulate(
            list(
                map(
                    lambda field: [f'{field.value}:', self.settings.get(field, 'Not set')],
                    self.fields,
                )
            )
        )


class GetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'web_ui_get_settings'
    SYNOPSIS = 'Get configuration options for the Web UI'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        command_group = parser.add_mutually_exclusive_group()

        command_group.add_argument(
            '--inactivity-timeout',
            help='Gets the inactivity timeout',
            action='store_const',
            const=SettingsField.INACTIVITY_TIMEOUT,
            dest='field',
        )
        command_group.add_argument(
            '--login-banner',
            help='Gets the configuration for the login banner',
            action='store_const',
            const=SettingsField.LOGIN_BANNER,
            dest='field',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        settings = rest_client.web_ui.get_settings()
        if args.field:
            print(SettingsForDisplay(settings.data, [args.field]))
        else:
            print(SettingsForDisplay(settings.data))


class ModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'web_ui_modify_settings'
    SYNOPSIS = 'Modify configuration options for the Web UI'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        inactivity_group = parser.add_mutually_exclusive_group(required=False)
        inactivity_group.add_argument(
            INACTIVITY_CONFIG.set_arg,
            help='Sets the inactivity timeout',
            metavar='MINUTES',
            dest=INACTIVITY_CONFIG.set_dest,
            type=int,
        )
        inactivity_group.add_argument(
            INACTIVITY_CONFIG.clear_arg,
            help='Disables the inactivity timeout',
            action='store_const',
            const=True,
            dest=INACTIVITY_CONFIG.clear_dest,
        )

        login_banner_group = parser.add_mutually_exclusive_group(required=False)
        login_banner_group.add_argument(
            LOGIN_BANNER_CONFIG.set_arg,
            help='Sets the login banner',
            metavar='BANNER_MARKDOWN_FILE',
            dest=LOGIN_BANNER_CONFIG.set_dest,
            type=str,
        )
        login_banner_group.add_argument(
            LOGIN_BANNER_CONFIG.clear_arg,
            help='Disables the login banner',
            action='store_const',
            const=True,
            dest=LOGIN_BANNER_CONFIG.clear_dest,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        args_dict = vars(args)

        def args_populated_for_field(config: SettingsFieldArgumentConfig) -> bool:
            return args_dict[config.set_dest] or args_dict[config.clear_dest]

        args_populated_for_any_field = any(
            list(map(args_populated_for_field, SETTINGS_FIELD_ARGUMENT_CONFIGS))
        )

        if not args_populated_for_any_field:
            required_args: List[str] = []
            for config in PUBLIC_SETTINGS_FIELD_ARGUMENT_CONFIGS:
                required_args.append(config.set_arg)
                required_args.append(config.clear_arg)
            required_arg_str = ', '.join(required_args)
            sys.stderr.write(
                'error: at least one of the following arguments is required:'
                f' [{required_arg_str}]\n'
            )
            sys.exit(1)

        parsed_inactivity_timeout = None
        if args_dict[INACTIVITY_CONFIG.set_dest]:
            parsed_inactivity_timeout = timedelta(
                minutes=int(args_dict[INACTIVITY_CONFIG.set_dest])
            )

        login_banner_file_contents = None
        if args_dict[LOGIN_BANNER_CONFIG.set_dest]:
            with open(args_dict[LOGIN_BANNER_CONFIG.set_dest]) as f:
                login_banner_file_contents = f.read()

        with rest_client.web_ui.modify_settings() as settings:
            settings.inactivity_timeout = update_value(
                current_value=settings.inactivity_timeout,
                input_value=parsed_inactivity_timeout,
                clear_value=args_dict[INACTIVITY_CONFIG.clear_dest],
            )
            settings.login_banner = update_value(
                current_value=settings.login_banner,
                input_value=login_banner_file_contents,
                clear_value=args_dict[LOGIN_BANNER_CONFIG.clear_dest],
            )
