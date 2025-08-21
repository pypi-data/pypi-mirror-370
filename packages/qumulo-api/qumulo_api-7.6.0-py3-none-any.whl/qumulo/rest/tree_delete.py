# Copyright (c) 2021 Qumulo, Inc.
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


import time

from typing import Optional

import qumulo.lib.request as request
import qumulo.rest.fs

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


@request.request
def list_jobs(
    conninfo: request.Connection, _credentials: Optional[Credentials]
) -> request.RestResponse:
    uri = UriBuilder(path='/v1/tree-delete/jobs').append_slash()
    method = 'GET'
    return conninfo.send_request(method, str(uri))


@request.request
def create_job(
    conninfo: request.Connection, _credentials: Optional[Credentials], directory: str
) -> request.RestResponse:
    """Start asynchronous tree_delete jobs on directory path or ID."""
    uri = UriBuilder(path='/v1/tree-delete/jobs').append_slash()
    method = 'POST'
    body = {'id': directory}
    return conninfo.send_request(method, str(uri), body=body)


@request.request
def get_job(
    conninfo: request.Connection, _credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = UriBuilder(path=f'/v1/tree-delete/jobs/{dir_id}')
    return conninfo.send_request(method, str(uri))


@request.request
def cancel_job(
    conninfo: request.Connection, _credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    method = 'DELETE'
    uri = UriBuilder(path=f'/v1/tree-delete/jobs/{dir_id}')
    return conninfo.send_request(method, str(uri))


@request.request
def wait_for_job(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    dir_id: str,
    exit_on_error: bool = False,
) -> None:
    while True:
        try:
            job = get_job(conninfo, credentials, dir_id)
            if exit_on_error and job.data['last_error_message'] is not None:
                return
        except request.RequestError as e:
            if e.error_class == 'http_not_found_error':
                return
            raise
        time.sleep(1.0)


@request.request
def run_job_sync(
    conninfo: request.Connection, credentials: Optional[Credentials], id_or_path: str
) -> None:
    if '/' in id_or_path:
        dir_id = qumulo.rest.fs.get_file_attr(conninfo, credentials, path=id_or_path).lookup('id')
        assert isinstance(dir_id, str)
    else:
        dir_id = id_or_path

    create_job(conninfo, credentials, dir_id)
    wait_for_job(conninfo, credentials, dir_id=dir_id)


@request.request
def restart_job(
    conninfo: request.Connection, _credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    method = 'POST'
    uri = UriBuilder(path=f'/v1/tree-delete/jobs/restart/{dir_id}')
    return conninfo.send_request(method, str(uri))
