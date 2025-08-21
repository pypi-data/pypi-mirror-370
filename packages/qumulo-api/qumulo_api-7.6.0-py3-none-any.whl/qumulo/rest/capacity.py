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


from typing import Optional

import qumulo.lib.request as request

CAPACITY_URI = '/v1/capacity/clamp'


class Capacity:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def get_capacity_clamp(self) -> Optional[int]:
        response = self.client.send_request('GET', CAPACITY_URI)
        capacity_clamp = response.data['capacity_clamp']
        return int(capacity_clamp) if capacity_clamp else None

    def put_capacity_clamp(self, capacity_clamp: Optional[int]) -> None:
        body = {'capacity_clamp': capacity_clamp}
        self.client.send_request('PUT', CAPACITY_URI, body=body)
