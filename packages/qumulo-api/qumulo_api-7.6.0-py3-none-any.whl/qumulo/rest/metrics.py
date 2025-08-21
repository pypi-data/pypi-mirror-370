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


import io

from qumulo.lib.request import SendRequestObject


class Metrics:
    def __init__(self, client: SendRequestObject):
        self.client = client

    def get(self) -> str:
        """
        Get all customer-facing metrics for the cluster.
        """

        method = 'GET'
        uri = '/v2/metrics/endpoints/default/data'

        # rest_request assumes all data returned from the server should be json
        # loaded unless a response_file is provided. Use an in memory buffer as
        # a file to get around this problem.
        contents = io.BytesIO()
        self.client.send_request(method, uri, response_file=contents)

        return contents.getvalue().decode()

    def get_internal(self) -> str:
        """
        Get all metrics for the cluster, including the internal ones.
        """

        method = 'GET'
        uri = '/v2/metrics/endpoints/internal/data'

        # rest_request assumes all data returned from the server should be json
        # loaded unless a response_file is provided. Use an in memory buffer as
        # a file to get around this problem.
        contents = io.BytesIO()
        self.client.send_request(method, uri, response_file=contents)

        return contents.getvalue().decode()
