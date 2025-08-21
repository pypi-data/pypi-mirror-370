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
import http.client as httplib
import json
import os
import random
import socket
import ssl
import struct
import sys
import textwrap
import time

from collections import OrderedDict
from io import BytesIO
from typing import (
    Any,
    AnyStr,
    Callable,
    cast,
    Dict,
    Generic,
    IO,
    Iterator,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from qumulo.lib import log
from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder

Body = Union[Sequence[object], Mapping[str, object]]

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_BINARY = 'application/octet-stream'
CONTENT_TYPE_SSE_STREAM = 'text/event-source'

DEFAULT_CHUNKED = False

# Chosen as a sweet spot for performance. Minimizes chunk and SSL overhead without being wasteful
# with memory. It's 10% faster than 64KiB and 20000% faster than 1KiB. Somewhere around 1MiB perf
# starts to decrease again.
DEFAULT_CHUNK_SIZE_BYTES = 1024 * 128

NEED_LOGIN_MESSAGE = 'Need to log in first to establish credentials.'

PRIV_PORT_BEG = 900
PRIV_PORT_END = 1024

LOCALHOSTS = frozenset(['localhost', 'ip6-localhost', '127.0.0.1', '::1'])


# Order of evaluation is important. If host is not local, don't check
# uid at all, which is not available on all platforms.
def user_is_local_root(host: Optional[str]) -> bool:
    return (host is None or host in LOCALHOSTS) and os.geteuid() == 0


# N.B. The `Any` specified below doesn't actually get passed through as the return type of the
# decorated function by mypy. It's able to see what the return type is based on the decorator
# implementation.
RequestFunction = TypeVar('RequestFunction', bound=Callable[..., 'Any'])


# Decorator for request methods
def request(fn: RequestFunction) -> RequestFunction:
    setattr(fn, 'request', True)
    return fn


def pretty_json(obj: object, sort_keys: bool = True, indent: Optional[int] = 4) -> str:
    return json.dumps(obj, sort_keys=sort_keys, indent=indent, ensure_ascii=False)


def stream_writer(conn: IO[bytes], file_: IO[bytes]) -> None:
    chunk_size = 128 * 1024
    while True:
        data = conn.read(chunk_size)
        if len(data) == 0:
            return
        file_.write(data)


# We set various TCP socket options for HTTPS connections by overriding
# httplib.HTTPSConnection. When/if Qumulo Core supports http (vs. https) we need to do
# the same for httplib.HTTPConnection. The options set here are consistent with those
# set on socket in the product.
class HTTPSConnectionWithSocketOptions(httplib.HTTPSConnection):
    # Default TCP keepalive settings consistent with net/stream_socket.h
    DEFAULT_KEEPALIVE_IDLE_TIME = 60  # seconds before sending keepalive probes
    DEFAULT_KEEPALIVE_PROBE_COUNT = 3  # keepalive probes before giving up
    DEFAULT_KEEPALIVE_PROBE_INTERVAL = 10  # seconds between probes
    DEFAULT_TCP_USER_TIMEOUT = 90 * 1000  # ms timeout on unacked transmits

    _context: ssl.SSLContext

    def connect(self) -> None:
        # Create a TCP socket connection without applying the SSL context.
        httplib.HTTPConnection.connect(self)

        # QFS-14181: httplib doesn't set TCP_NODELAY on sockets. Set it here to reduce request
        # latency.
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Enable TCP keepalive to ensure that dead connections are detected more quickly. This fixes
        # an issue in automation where a dropped connection can cause REST calls to hang. Apply the
        # keepalive socket option before creating the SSL socket which automatically performs an SSL
        # handshake during which the peer could go away.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Versions of Windows prior to Windows 10 1709 did not support TCP_KEEP* options, so check
        # for them before setting them.
        if (
            hasattr(socket, 'TCP_KEEPIDLE')
            and hasattr(socket, 'TCP_KEEPCNT')
            and hasattr(socket, 'TCP_KEEPINTVL')
        ):
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.DEFAULT_KEEPALIVE_IDLE_TIME
            )
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.DEFAULT_KEEPALIVE_PROBE_COUNT
            )
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.DEFAULT_KEEPALIVE_PROBE_INTERVAL
            )
        elif hasattr(socket, 'SIO_KEEPALIVE_VALS'):
            # Windows uses this ioctl to set keepalive parameters
            self.sock.ioctl(  # type: ignore[union-attr]
                getattr(socket, 'SIO_KEEPALIVE_VALS'),
                (
                    1,  # enable
                    self.DEFAULT_KEEPALIVE_IDLE_TIME * 1000,  # idle time in ms
                    self.DEFAULT_KEEPALIVE_PROBE_INTERVAL * 1000,  # interval in ms
                ),
            )

        # Set the TCP user timeout, if available. Versions of Python before 3.6 didn't have this
        # constant, so we have to check for it.
        if hasattr(socket, 'TCP_USER_TIMEOUT'):
            self.sock.setsockopt(
                socket.SOL_TCP, getattr(socket, 'TCP_USER_TIMEOUT'), self.DEFAULT_TCP_USER_TIMEOUT
            )
        elif sys.platform.startswith('linux'):
            # For Python < 3.6 running on Linux, we'd still like to set the TCP user timeout, so
            # we'll just grab the value explicitly from /usr/include/linux/tcp.h
            self.sock.setsockopt(socket.SOL_TCP, 18, self.DEFAULT_TCP_USER_TIMEOUT)

        # Wrap the existing TCP socket with an SSL socket with socket options applied.
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


class UnixHTTPConnection(httplib.HTTPConnection):
    """HTTPConnection subclass that uses a Unix domain socket instead of TCP"""

    def __init__(self, unix_socket_path: str, **kwargs: Any):
        super().__init__('localhost', 0, **kwargs)
        self.unix_socket_path = unix_socket_path

    def connect(self) -> None:
        # Create a Unix socket connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if self.timeout is not None:
            sock.settimeout(self.timeout)

        # Connect to the Unix socket path
        sock.connect(self.unix_socket_path)

        # Set the socket directly - no SSL wrapping needed for Unix sockets
        self.sock = sock


class RealConnectionFactory:
    def __init__(
        self,
        host: str,
        port: int,
        timeout: Optional[int] = None,
        time_fn: Callable[[], float] = time.time,
        socket_path: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self._timeout = timeout
        self.time_fn = time_fn
        self.socket_path = socket_path

    def timeout(self) -> Optional[int]:
        return self._timeout

    def get_connection(
        self, source_port: Optional[int] = None
    ) -> Union[HTTPSConnectionWithSocketOptions, UnixHTTPConnection]:
        # If a Unix socket path is provided, use plain HTTP over the Unix socket
        if self.socket_path is not None:
            return UnixHTTPConnection(unix_socket_path=self.socket_path, timeout=self.timeout())

        # For regular connections, use HTTPS with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Many Qumulo clusters use self-signed certificates which will cause certificate validation
        # to fail, so disable certificate validation.
        # XXX patrick: Turning off certificate validation should really be an option to qq.
        # Presumably, most users would assume that this library is performing certificate
        # validation.
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        kwargs: Dict[str, Any] = {'context': context, 'timeout': self.timeout()}
        if source_port is not None:
            kwargs['source_address'] = (self.host, source_port)

        return HTTPSConnectionWithSocketOptions(self.host, self.port, **kwargs)

    def _try_connect_priv_port(
        self, source_port: int, last_try: bool, deadline: Optional[float]
    ) -> Optional[HTTPSConnectionWithSocketOptions]:
        # This method is only used for TCP backdoor connections, never for Unix sockets
        try:
            # We know this returns HTTPSConnectionWithSocketOptions (we're not using socket_path)
            conn = cast(HTTPSConnectionWithSocketOptions, self.get_connection(source_port))
            conn.connect()
            # Set SO_LINGER on backdoor sockets created for root-initiated
            # connections to localhost to force an immediate RST on close.
            # We have a very limited number of privileged ports available
            # to bind to and short-lived REST connections can otherwise
            # easily exhaust those with TIME_WAIT connections.
            conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
            return conn
        except OSError as e:
            # Looking for a port that isn't in use. Either there's no ports left
            # to try, or this is some other kind of error, so don't try again:
            if last_try or e.errno != errno.EADDRINUSE:
                raise
            elif deadline and self.time_fn() > deadline:
                # out of time
                raise
            else:
                return None

    def get_backdoor_connection(self) -> HTTPSConnectionWithSocketOptions:
        source_ports = list(range(PRIV_PORT_BEG, PRIV_PORT_END))
        random.shuffle(source_ports)

        deadline = None
        if self._timeout:
            deadline = self.time_fn() + self._timeout

        for i, source_port in enumerate(source_ports):
            last_try = i + 1 == len(source_ports)
            conn = self._try_connect_priv_port(source_port, last_try, deadline)
            if conn:
                return conn

        # Last _try_connect_priv_port should have raised if it failed
        raise AssertionError('Unreachable')


class Connection:
    def __init__(
        self,
        host: Optional[str],
        port: int,
        credentials: Optional[Credentials],
        chunk_size: int = DEFAULT_CHUNK_SIZE_BYTES,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        socket_path: Optional[str] = None,
    ):
        self.run_on_local_node = host is None
        self.backdoor = user_is_local_root(host)
        if host is None:
            host = 'localhost'
        self.chunk_size = chunk_size
        self.conn: Optional[Union[HTTPSConnectionWithSocketOptions, UnixHTTPConnection]] = None
        self.connection_factory = RealConnectionFactory(
            host, port, timeout, socket_path=socket_path
        )
        self.credentials = credentials
        self.host = host
        self.port = port
        self.scheme = 'http' if socket_path is not None else 'https'
        self.timeout = self.connection_factory.timeout()
        self.user_agent = user_agent
        self.socket_path = socket_path

    def is_connected(self) -> bool:
        return self.conn is not None

    def get_or_create_connection(
        self
    ) -> Union[HTTPSConnectionWithSocketOptions, UnixHTTPConnection]:
        if self.conn is None:
            if self.run_on_local_node and self.socket_path is not None:
                # For Unix sockets, always use direct HTTP connection
                self.conn = self.connection_factory.get_connection()
            elif self.backdoor:
                # For backdoor connections over TCP
                self.conn = self.connection_factory.get_backdoor_connection()
            else:
                # Normal HTTPS connections
                self.conn = self.connection_factory.get_connection()

        return self.conn

    def close(self) -> None:
        """
        Close the underlying network connection.

        An explicit close() should not strictly be necessary, as refcount GC
        will also ensure the connection gets closed. This provides a stronger
        guarantee or tighter control if desired (e.g. it might be useful when a
        long lived instance has long idle periods).
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def send_request(
        self,
        method: str,
        uri: str,
        body: Optional[Body] = None,
        body_file: Optional[IO[Any]] = None,
        if_match: Optional[str] = None,
        request_content_type: Optional[str] = None,
        response_file: Optional[IO[bytes]] = None,
        headers: Optional[Mapping[str, str]] = None,
        chunked: bool = False,
    ) -> 'RestResponse':
        try:
            rest = APIRequest(
                conninfo=self,
                method=method,
                uri=uri,
                chunked=chunked,
                chunk_size=self.chunk_size,
                body=body,
                body_file=body_file,
                if_match=if_match,
                request_content_type=request_content_type,
                response_file=response_file,
                headers=headers,
            )
            rest.send_request()

            rest.get_response()
        except (ConnectionError, httplib.IncompleteRead):
            # If the connection has received an error, it can no longer be reused. Close it so that
            # the next request will open a new connection.
            self.close()
            raise

        return RestResponse(rest.response_obj, rest.response_etag)


class APIException(Exception):
    """
    Unusual errors when sending request or receiving response.
    """


class RequestError(Exception):
    """
    An error response to an invalid REST request. A combination of HTTP status code,
    HTTP status message and REST error response.
    """

    def __init__(
        self, status_code: int, status_message: str, json_error: Optional[Mapping[str, Any]] = None
    ):
        self.status_code = status_code
        self.status_message = str(status_message)

        json_error = {} if json_error is None else json_error

        module = json_error.get('module', 'qumulo.lib.request')
        self.module = str(module)

        error_class = json_error.get('error_class', 'unknown')
        self.error_class = str(error_class)

        if 'description' in json_error:
            self.description = json_error['description']
        elif status_code == 401:
            self.description = NEED_LOGIN_MESSAGE
        else:
            self.description = 'Dev error: No json error response.'

        self.stack = json_error.get('stack', [])
        self.user_visible = json_error.get('user_visible', False)

        inner = json_error.get('inner', None)
        self.inner: Optional[RequestError] = None
        if inner is not None:
            self.inner = RequestError(status_code, status_message, inner)

        message = (
            f'Error {self.status_code}: {self.error_class}: {self.description}\n'
            f'Backtrace:\n{self.render_backtrace()}'
        )
        super().__init__(message)

    def render_backtrace(self, is_inner_error: bool = False) -> str:
        backtrace = '\n'.join(' ' * 4 + frame for frame in self.stack)
        backtrace = backtrace or '    (no backtrace)'

        if self.inner is not None:
            return (
                f'{self.inner.render_backtrace(is_inner_error=True)}\n\n'
                f'{self.error_class}: {self.description}\n'
                f'{backtrace}'
            )
        else:
            # we already print the error_class and description of the outermost error in the message
            error_metadata = f'{self.error_class}: {self.description}\n' if is_inner_error else ''
            return error_metadata + str(backtrace)

    def pretty_str(self) -> str:
        """
        This formatting of the error is used by QQ to display the error nicely
        to a user.
        """
        return f'Error {self.status_code}: {self.error_class}: {self.description}'


#  ____                            _
# |  _ \ ___  __ _ _   _  ___  ___| |_
# | |_) / _ \/ _` | | | |/ _ \/ __| __|
# |  _ <  __/ (_| | |_| |  __/\__ \ |_
# |_| \_\___|\__, |\__,_|\___||___/\__|
#               |_|


class APIRequest:
    """REST API request class."""

    def __init__(
        self,
        conninfo: Connection,
        method: str,
        uri: str,
        chunked: bool,
        chunk_size: int,
        body: Optional[Body] = None,
        body_file: Optional[IO[AnyStr]] = None,
        if_match: Optional[str] = None,
        request_content_type: Optional[str] = None,
        response_file: Optional[IO[bytes]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ):
        if request_content_type is None:
            request_content_type = CONTENT_TYPE_JSON

        self.conninfo = conninfo
        self.method = method
        self.uri = uri
        self.chunked = chunked
        self.chunk_size = chunk_size
        self.response: Optional[httplib.HTTPResponse] = None
        self.response_etag: Optional[str] = None
        self._response_data: Optional[bytes] = None
        self.response_obj: Union[Dict[str, object], List[object], httplib.HTTPResponse, None] = None
        self._headers: Dict[str, Any] = OrderedDict()
        self._headers.update(headers or {})
        if if_match is not None:
            self._headers['If-Match'] = if_match
        if self.conninfo.user_agent:
            self._headers['User-Agent'] = self.conninfo.user_agent

        # Request type defaults to JSON. If overridden, body_file is required.
        self.request_content_type = request_content_type
        if request_content_type != CONTENT_TYPE_JSON:
            assert body_file is not None, 'Binary request requires body_file'

        self.response_file = response_file

        self.body_file: Optional[Union[IO[str], IO[bytes]]] = None
        self.body_text = None
        self.body_length = 0
        if body_file is not None:
            self.body_file = body_file

            # Most http methods want to overwrite fully, so seek to 0.
            if not method == 'PATCH':
                try:
                    body_file.seek(0, 0)
                except OSError:
                    # file is a stream, and therefore can't be seeked.
                    pass

            if not self.chunked:
                current_pos = body_file.tell()
                body_file.seek(0, 2)
                self.body_length = body_file.tell() - current_pos
                body_file.seek(current_pos, 0)

        elif body is not None:
            self.body_text = body
            json_blob = json.dumps(body, ensure_ascii=True)
            self.body_file = BytesIO(json_blob.encode())
            # json_blob will only contain ascii characters so its length is the
            # same as its size in bytes.
            self.body_length = len(json_blob)

        # We expect only the first call to get_or_create_connection to connect if needed.
        # Afterwards, there should be no APIRequests closing the connection in parallel.
        self.conn = self.conninfo.get_or_create_connection()

    def _log_headers(
        self, category: str, headers: Union[Mapping[str, str], httplib.HTTPMessage]
    ) -> None:
        log.debug(f'{category} HEADERS:')
        for header, value in headers.items():
            log.debug(f'    {header}: {value}')

    def send_request(self) -> None:
        self._headers['Content-Type'] = self.request_content_type

        if self.chunked:
            assert self.method in ('PUT', 'POST', 'PATCH'), self.method
            self._headers['Transfer-Encoding'] = 'chunked'
        else:
            self._headers['Content-Length'] = self.body_length

        if self.conninfo.credentials:
            self._headers['Authorization'] = self.conninfo.credentials.auth_header()

        if self.conninfo.socket_path is not None:
            log.debug(
                'REQUEST: {method} {scheme}+unix://{socket_path}{uri}'.format(
                    method=self.method,
                    scheme=self.conninfo.scheme,
                    socket_path=self.conninfo.socket_path,
                    uri=self.uri,
                )
            )
        else:
            log.debug(
                'REQUEST: {method} {scheme}://{host}:{port}{uri}'.format(
                    method=self.method,
                    scheme=self.conninfo.scheme,
                    host=self.conninfo.host,
                    port=self.conninfo.port,
                    uri=self.uri,
                )
            )

        self._log_headers('REQUEST', self._headers)

        if self.body_length > 0:
            log.debug('REQUEST BODY:')
            if self.request_content_type == CONTENT_TYPE_BINARY:
                log.debug(
                    '\tContent elided. File info: %s (%d bytes)'
                    % (self.body_file, self.body_length)
                )
            else:
                log.debug(self.body_text)
                assert self.body_file
                self.body_file.seek(0)

        try:
            self.conn.putrequest(self.method, self.uri)

            for name, value in self._headers.items():
                self.conn.putheader(name, value)

            self.conn.endheaders()

            # Chunked transfer encoding. Details:
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.6.1
            # On our server side chunks are processed by chunked_xfer_istream.h
            if self.chunked:
                if self.body_file is not None:
                    while True:
                        chunk = self.body_file.read(self.chunk_size)
                        chunk_bytes = chunk if isinstance(chunk, bytes) else chunk.encode()
                        chunk_size = len(chunk_bytes)
                        if chunk_size == 0:
                            break
                        msg = f'{chunk_size:x}\r\n'.encode()
                        msg += chunk_bytes
                        msg += b'\r\n'
                        self.conn.send(msg)

                self.conn.send(b'0\r\n\r\n')
            elif self.body_file is not None:
                self.conn.send(self.body_file)  # type: ignore[arg-type]

        except OSError as e:
            # Allow EPIPE, server probably sent us a response before breaking
            if e.errno != errno.EPIPE:
                raise

    def get_response(self) -> None:
        self.response = self.conn.getresponse()
        self.response_etag = self.response.getheader('etag')

        log.debug('RESPONSE STATUS: %d' % self.response.status)

        length = self.response.getheader('content-length')

        content_type = self.response.getheader('content-type')

        if content_type == CONTENT_TYPE_SSE_STREAM and self._success():
            self.response_obj = self.response
        elif self.response_file is None or not self._success():
            self._response_data = self.response.read()
        else:
            self._log_headers('RESPONSE', self.response.headers)
            stream_writer(self.response, self.response_file)

        # Close connection here if the server asks us nicely
        if self.response.getheader('Connection') == 'close':
            self.conninfo.close()

        if not self._success():
            log.debug('Server replied: %d %s' % (self._status(), self._reason()))

        if self._response_data and length != '0':
            try:
                self.response_obj = json.loads(self._response_data.decode())
            except ValueError as e:
                if self._response_data:
                    raise APIException('Error loading data: %s' % str(e))
            else:
                log.debug('RESPONSE:')
                log.debug(self.response.msg)
                if self.response_obj is not None:
                    log.debug(self.response_obj)

        if not self._success():
            json_error = cast(Dict[str, object], self.response_obj)
            raise RequestError(self._status(), self._reason(), json_error)

    def _status(self) -> int:
        assert self.response
        return self.response.status

    def _success(self) -> bool:
        return self._status() >= 200 and self._status() < 300

    def _reason(self) -> str:
        assert self.response
        return self.response.reason


#  ____
# |  _ \ ___  ___ _ __   ___  _ __  ___  ___
# | |_) / _ \/ __| '_ \ / _ \| '_ \/ __|/ _ \
# |  _ <  __/\__ \ |_) | (_) | | | \__ \  __/
# |_| \_\___||___/ .__/ \___/|_| |_|___/\___|
#                |_|


class RestResponse(NamedTuple):
    data: Any
    etag: Optional[str]

    def __str__(self) -> str:
        return self.to_str()

    def to_str(self, sort_keys: bool = True) -> str:
        # qq commands usually make one REST API call and simply print the response.
        # Many APIs do not return any data in the response. Avoid printing a confusing 'null'.
        return pretty_json(self.data, sort_keys) if self.data is not None else ''

    def lookup(self, key: str) -> object:
        if self.data is not None and key in self.data:
            return self.data[key]
        else:
            raise AttributeError(key)


class SendRequestObject(Protocol):
    def send_request(
        self,
        method: str,
        uri: str,
        body: Optional[Body] = None,
        body_file: Optional[IO[AnyStr]] = None,
        if_match: Optional[str] = None,
        request_content_type: Optional[str] = None,
        response_file: Optional[IO[bytes]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> RestResponse:
        ...


T = TypeVar('T')


# XXX jon: should be implemented using dataclasses, but is blocked on us ending python 3.6 support.
class ResponseWithEtag(Generic[T]):
    """
    Used for our new-style, explicitly typed python bindings.
    """

    def __init__(self, data: T, etag: str):
        self._data = data
        self._etag = etag

    def __repr__(self) -> str:
        return f'ResponseWithEtag({self.data!r}, {self.etag!r})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResponseWithEtag):
            return False
        return self._data == other._data and self._etag == other._etag

    @property
    def data(self) -> T:
        return self._data

    @property
    def etag(self) -> str:
        return self._etag


#  ____             _
# |  _ \ __ _  __ _(_)_ __   __ _
# | |_) / _` |/ _` | | '_ \ / _` |
# |  __/ (_| | (_| | | | | | (_| |
# |_|   \__,_|\__, |_|_| |_|\__, |
#             |___/         |___/
#


class PagingIterator:
    def __init__(
        self,
        path: str,
        fn: Callable[[UriBuilder], RestResponse],
        page_size: Optional[int] = None,
        query_params: Optional[Dict['str', Any]] = None,
    ):
        self.path = path
        self.rest_request = fn
        self.page_size = page_size
        self.query_params = query_params

        self.uri = UriBuilder(path=self.path, rstrip_slash=False)

        if query_params is not None:
            for k, v in query_params.items():
                self.uri.add_query_param(k, v)

        if page_size is not None:
            self.uri.add_query_param('limit', page_size)

    def __iter__(self) -> Iterator[RestResponse]:
        return self

    def __next__(self) -> RestResponse:
        if self.uri in ('', None):
            raise StopIteration
        result = self.rest_request(self.uri)
        self.uri = result.data['paging']['next']

        return result


P = TypeVar('P')


class TypedPagingIterator(Generic[P]):
    def __init__(
        self,
        initial_url: str,
        request_fn: Callable[[UriBuilder], RestResponse],
        convert_fn: Callable[[RestResponse], P],
        page_size: Optional[int] = None,
    ):
        self.initial_url = initial_url
        self.rest_request = request_fn
        self.convert_response = convert_fn
        self.page_size = page_size

        self.uri = UriBuilder(path=initial_url, rstrip_slash=False)
        if page_size is not None:
            self.uri.add_query_param('limit', page_size)

    def __iter__(self) -> Iterator[P]:
        return self

    def __next__(self) -> P:
        if self.uri in ('', None):
            raise StopIteration
        response = self.rest_request(self.uri)
        self.uri = response.data['paging']['next']
        return self.convert_response(response)


def print_paginated_results(results: PagingIterator, key: str) -> None:
    print('{')
    print(f'    "{key}": [')
    i = j = -1

    for i, result in enumerate(results):
        for j, handle in enumerate(result.data[key]):
            if i + j > 0:
                print(',')
            print(textwrap.indent(pretty_json(handle), ' ' * 8), end='')

    if i + j >= 0:
        # No extra newline if there weren't any results
        print('')

    print('    ]')
    print('}')
