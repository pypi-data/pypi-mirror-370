# Copyright (c) 2025 Qumulo, Inc.
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

from dataclasses import dataclass
from typing import Dict, List

from dataclasses_json import DataClassJsonMixin

import qumulo.lib.request as request


@dataclass
class SsdEndurance(DataClassJsonMixin):
    drive_bay: str
    level: int


class Health:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def ssd_endurance_level(self) -> Dict[int, List[SsdEndurance]]:
        method = 'GET'
        uri = '/v1/health/ssd-endurance'

        response = self.client.send_request(method, uri).data

        return {
            int(key): [SsdEndurance.from_dict(entry) for entry in value]
            for key, value in response.items()
        }
