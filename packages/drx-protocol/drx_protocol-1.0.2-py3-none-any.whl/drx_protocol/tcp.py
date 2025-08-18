"""DrX TCP connection"""

import logging
from socket import AF_INET, SHUT_RDWR, SOCK_STREAM, socket

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT
from .exceptions import DrxConnectionError, DrxTimeoutError

_LOGGER = logging.getLogger(__name__)


class drx_tcp:
    """DrX TCP connection class."""

    def __init__(
        self,
        host: str,
        serial: str,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._host = host
        self._serial = serial
        self._port = port
        self._timeout = timeout

        self._socket: socket | None = None

    def _connect(self) -> None:
        """Connect to the DrX device"""
        if self._socket is not None:
            return

        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        try:
            self._socket.connect((self._host, self._port))
        except TimeoutError as err:
            self.close()
            raise DrxConnectionError(f"DrX {self._serial}, {self._host}: Connection timeout") from err
        _LOGGER.debug("DrX %s, %s: TCP connected", self._serial, self._host)

    def close(self) -> None:
        """Disconnect from the DrX device"""
        if self._socket is None:
            return

        try:
            self._socket.shutdown(SHUT_RDWR)
        except OSError:
            pass
        self._socket.close()
        self._socket = None
        _LOGGER.debug("DrX %s, %s: TCP closed", self._serial, self._host)

    def send(self, data: bytes) -> None:
        """Send data to the DrX device and receive the response"""
        self._connect()
        assert self._socket is not None
        try:
            self._socket.sendall(data)
        except TimeoutError as err:
            raise DrxTimeoutError(f"DrX {self._serial}, {self._host}: send timeout") from err

    def receive(self, n_bytes: int) -> bytes:
        """Send data to the DrX device and receive the response"""
        if self._socket is None:
            raise DrxConnectionError(f"DrX {self._serial}, {self._host}: " "Can not receive when not connected to the device")

        buffer = b""
        previous_buffer_len = 0
        buffer_len = 0

        # keep receiving data in a loop untill the requested n_bytes have been received
        while True:
            try:
                buffer += self._socket.recv(n_bytes - len(buffer))
            except TimeoutError as err:
                raise DrxTimeoutError(f"DrX {self._serial}, {self._host}: " f"timeout after receiving {len(buffer)} of {n_bytes} bytes") from err

            buffer_len = len(buffer)
            if buffer_len >= n_bytes:
                break  # Done, all bytes received

            # if no extra bytes are received the TCP connection was disconnected
            if buffer_len == previous_buffer_len:
                self.close()
                raise DrxConnectionError(f"DrX {self._serial}, {self._host}: device disconnected while " f"only having received {len(buffer)} of {n_bytes} bytes")
            previous_buffer_len = buffer_len

            _LOGGER.debug(
                "DrX %s, %s: received %s of %s bytes, waiting for the rest...",
                self._serial,
                self._host,
                len(buffer),
                n_bytes,
            )

        return buffer
