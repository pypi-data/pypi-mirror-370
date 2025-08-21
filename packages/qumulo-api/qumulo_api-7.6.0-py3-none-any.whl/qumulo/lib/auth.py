# Copyright (c) 2012 Qumulo, Inc.
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


import errno
import json
import os
import shutil

from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Mapping, Optional

from dataclasses_json import DataClassJsonMixin

CREDENTIALS_FILENAME = '.qfsd_cred'
CONTENT_TYPE_BINARY = 'application/octet-stream'
CREDENTIALS_VERSION = 1


class CredentialsError(Exception):
    pass


@dataclass
class CredentialsOnDisk(DataClassJsonMixin):
    version: Optional[int] = None
    bearer_token: Optional[str] = None


@dataclass
class Credentials:
    bearer_token: str

    @classmethod
    def from_login_response(cls, obj: Mapping[str, object]) -> 'Credentials':
        bearer_token = obj['bearer_token']
        assert isinstance(bearer_token, str), type(bearer_token)
        return cls(bearer_token)

    @classmethod
    def from_disk(cls, on_disk: CredentialsOnDisk) -> 'Credentials':
        if on_disk.version != CREDENTIALS_VERSION:
            raise CredentialsError(f'expected version {CREDENTIALS_VERSION}, got {on_disk.version}')
        assert isinstance(on_disk.bearer_token, str)
        return cls(on_disk.bearer_token)

    def to_disk(self) -> CredentialsOnDisk:
        return CredentialsOnDisk(CREDENTIALS_VERSION, self.bearer_token)

    METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS')
    BINARY_METHODS = ('PATCH', 'PUT', 'POST')
    NO_CONTENT_METHODS = ('GET', 'DELETE', 'HEAD', 'OPTIONS', 'POST')

    def auth_header(self) -> str:
        return f'Bearer {str(self.bearer_token)}'


def credential_store_filename(
    path_module: Any = None, creds_file_name: str = CREDENTIALS_FILENAME
) -> str:
    if path_module is None:
        path_module = os.path

    if os.path.isabs(creds_file_name):
        return creds_file_name

    home = path_module.expanduser('~')
    if home == '~':
        home = os.environ.get('HOME')

    if home is None or home == '~':
        raise OSError('Could not find home directory for credentials store')

    path = os.path.join(home, creds_file_name)
    if os.path.isdir(path):
        raise OSError('Credentials store is a directory: %s' % path)
    return path


def remove_credentials_store(path: str) -> None:
    try:
        os.unlink(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def set_credentials(login_response: Mapping[str, object], path: str) -> None:
    credentials = Credentials.from_login_response(login_response)
    on_disk_creds = credentials.to_disk().to_json(sort_keys=True)
    cred_pre = os.path.basename(path) + '.'
    cred_dir = os.path.dirname(path)
    cred_tmp = NamedTemporaryFile(prefix=cred_pre, dir=cred_dir, delete=False)
    try:
        os.chmod(cred_tmp.name, 0o600)
        cred_tmp.write((on_disk_creds + '\n').encode())
        cred_tmp.flush()
        # Make sure the file is closed before moving it
        cred_tmp.close()
        shutil.move(cred_tmp.name, path)
    finally:
        # On windows, cred_tmp must be closed before it can be unlinked.
        # Close can safely be called multiple times so we call it again just
        # in case there was an error before it was called above.
        cred_tmp.close()
        if os.path.exists(cred_tmp.name):
            os.unlink(cred_tmp.name)


def get_credentials(path: str) -> Optional[Credentials]:
    if not os.path.isfile(path):
        return None

    with open(path) as store:
        if os.fstat(store.fileno()).st_size == 0:
            return None
        contents = json.load(store)

    return Credentials.from_disk(CredentialsOnDisk.from_dict(contents))
