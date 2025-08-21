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
import sys

from typing import Any, Iterable, List, Mapping, Tuple

import qumulo.lib.opts
import qumulo.rest.software_license as software_license

from qumulo.lib.util import TextAligner
from qumulo.rest_client import RestClient


class GetLicenseCommand(qumulo.lib.opts.Subcommand):
    NAME = 'license_get_status'
    SYNOPSIS = 'Fetch the current license state of the cluster.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--json', action='store_true', help='Print JSON representation of license.'
        )

    @staticmethod
    def flatten(d: Mapping[str, Any], prefix: str = '') -> Iterable[Tuple[str, Any]]:
        res: List[Tuple[str, Any]] = []
        for k, v in d.items():
            if isinstance(v, Mapping):
                res.extend(GetLicenseCommand.flatten(v, prefix=f'{prefix}{k}.'))
            else:
                res.append((f'{prefix}{k}', v))
        return res

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        resp = software_license.get_status(rest_client.conninfo, rest_client.credentials)
        if args.json:
            sys.stdout.write(str(resp))
        else:
            aligner = TextAligner()
            aligner.add_wrapped_table(GetLicenseCommand.flatten(resp.data))
            aligner.write(sys.stdout)
