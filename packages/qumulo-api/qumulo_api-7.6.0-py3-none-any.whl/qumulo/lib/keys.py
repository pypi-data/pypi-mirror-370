# Copyright (c) 2023 Qumulo, Inc.
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

import base64
import binascii

from getpass import getpass
from typing import Callable, Optional

from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePrivateKey

try:
    from cryptography.hazmat.primitives.asymmetric.types import (  # type: ignore[attr-defined]
        PrivateKeyTypes,
    )
except ImportError:
    from cryptography.hazmat.primitives.asymmetric.types import PRIVATE_KEY_TYPES as PrivateKeyTypes

from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    load_der_private_key,
    load_pem_private_key,
    load_ssh_private_key,
    PublicFormat,
)


class KeyOps:
    def __init__(self, private_key_data: str, askpass: Callable[[str], str] = getpass) -> None:
        self._potential_key_data = [private_key_data.encode()]
        try:
            self._potential_key_data.append(base64.b64decode(private_key_data))
        except binascii.Error:
            pass
        self._private_key: Optional[EllipticCurvePrivateKey] = None
        self._askpass = askpass

    def public_bytes_as_base64(self) -> str:
        return base64.b64encode(
            self.private_key.public_key().public_bytes(
                Encoding.DER, PublicFormat.SubjectPublicKeyInfo
            )
        ).decode()

    @property
    def private_key(self) -> EllipticCurvePrivateKey:
        if self._private_key is None:
            for algorithm in [load_der_private_key, load_pem_private_key, load_ssh_private_key]:
                result = self.load_key(algorithm)
                if result is not None:
                    break

            if result is None:
                raise ValueError('Private key must be der or pem encoded')
            if not isinstance(result, EllipticCurvePrivateKey):
                raise ValueError(f'Private key is not an ecdsa key ({type(result).__name__})')
            self._private_key = result

        return self._private_key

    def _load_key_with_password(
        self, load_fn: Callable[[bytes, Optional[bytes]], PrivateKeyTypes], key_data: bytes
    ) -> Optional[PrivateKeyTypes]:
        password = self._askpass('Key Password: ').encode() or None
        while True:
            try:
                return load_fn(key_data, password)
            except (TypeError, ValueError):
                pass

            password = self._askpass('Wrong Password? Try again: ').encode() or None

    def load_key(
        self, load_fn: Callable[[bytes, Optional[bytes]], PrivateKeyTypes]
    ) -> Optional[PrivateKeyTypes]:
        for key_data in self._potential_key_data:
            try:
                if key_data is not None:
                    return load_fn(key_data, None)
            except TypeError as e:
                if e.args[0] == 'Password was not given but private key is encrypted':
                    return self._load_key_with_password(load_fn, key_data)
            except ValueError:
                pass
        return None

    def sign(self, challenge: str) -> str:
        return base64.b64encode(self.private_key.sign(challenge.encode(), ECDSA(SHA256()))).decode()
