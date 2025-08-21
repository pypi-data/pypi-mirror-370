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


import contextlib

from datetime import timedelta
from typing import Any, Iterator, Optional

import qumulo.lib.request as request

from qumulo.lib.duration import Duration

WEB_UI_SETTINGS_URI = '/v1/web-ui/settings'


# XXX jon: should be implemented using a dataclass, once that's supported in the bindings.
class WebUiSettings:
    def __init__(self, inactivity_timeout: Optional[timedelta], login_banner: Optional[str]):
        self.inactivity_timeout = inactivity_timeout
        self.login_banner = login_banner

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebUiSettings):
            return False

        return (
            self.inactivity_timeout == other.inactivity_timeout
            and self.login_banner == other.login_banner
        )

    @classmethod
    def from_dict(cls, response_data: Any) -> 'WebUiSettings':
        timeout_decoder = (  # noqa: E731
            lambda val: Duration.from_dict(val).delta if val is not None else None
        )
        return WebUiSettings(
            inactivity_timeout=timeout_decoder(response_data['inactivity_timeout']),
            login_banner=response_data['login_banner'],
        )

    def to_dict(self) -> Any:
        timeout_encoder = (  # noqa: E731
            lambda val: Duration(delta=val).to_dict() if val is not None else None
        )
        return {
            'inactivity_timeout': timeout_encoder(self.inactivity_timeout),
            'login_banner': self.login_banner,
        }


class WebUi:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def get_settings(self) -> request.ResponseWithEtag[WebUiSettings]:
        method = 'GET'

        response = self.client.send_request(method, WEB_UI_SETTINGS_URI)
        assert response.etag is not None

        return request.ResponseWithEtag(WebUiSettings.from_dict(response.data), response.etag)

    def set_settings(
        self, settings: WebUiSettings, etag: Optional[str] = None
    ) -> request.ResponseWithEtag[WebUiSettings]:
        """
        Replace the Web UI settings.

        :param settings: The new Web UI settings to use.
        :param etag: Optional ETag for optimistic concurrency.
        """
        method = 'PUT'

        response = self.client.send_request(
            method, WEB_UI_SETTINGS_URI, body=settings.to_dict(), if_match=etag
        )
        assert response.etag is not None

        return request.ResponseWithEtag(WebUiSettings.from_dict(response.data), response.etag)

    @contextlib.contextmanager
    def modify_settings(self, ignore_etag: bool = False) -> Iterator[WebUiSettings]:
        response = self.get_settings()
        yield response.data
        etag = None if ignore_etag else response.etag
        self.set_settings(response.data, etag)
