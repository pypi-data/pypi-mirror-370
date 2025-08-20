#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
TCP communication protocol. Makes use of the socket library.
"""

import logging
import socket
import warnings
from ipaddress import IPv4Address, IPv6Address
from typing import cast

from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.validation import (
    validate_and_resolve_host,
    validate_number,
    validate_tcp_port,
)

from .base import (
    AsyncCommunicationProtocol,
    AsyncCommunicationProtocolConfig,
    CommunicationError,
)

logger = logging.getLogger(__name__)


class TcpCommunicationError(CommunicationError):
    """Error of the TcpCommunication"""


@configdataclass
class TcpCommunicationConfig(AsyncCommunicationProtocolConfig):
    """
    Configuration dataclass for :class:`TcpCommunication`.
    """

    # Host is the IP address of the connected device.
    host: str | IPv4Address | IPv6Address | None = None
    # TCP port
    port: int = 54321
    # TCP receiving buffersize
    bufsize: int = 1024
    # TCP timeout
    timeout: float | None = 0.2

    def clean_values(self) -> None:
        # if necessary, converts host to a valid IP address
        super().clean_values()
        # Host
        self.force_value("host", validate_and_resolve_host(self.host, logger))  # type: ignore[attr-defined]
        # Port
        validate_tcp_port(self.port, logger)
        # Buffer size
        validate_number("bufsize", self.bufsize, (1, None), int, logger=logger)
        # Timeout
        validate_number("timeout", self.timeout, (0, None), logger=logger)


class TcpCommunication(AsyncCommunicationProtocol):
    """
    Tcp Communication Protocol.
    """

    config: TcpCommunicationConfig

    def __init__(self, configuration) -> None:
        """Constructor socket"""
        super().__init__(configuration)

        # create the communication port specified in the configuration
        logger.debug(
            "Create socket TcpClient with host: "
            f'"{self.config.host}", Port: "{self.config.port}"'
        )
        self._sock: socket.socket | None = None

    @staticmethod
    def config_cls() -> type[TcpCommunicationConfig]:
        return TcpCommunicationConfig

    @property
    def is_open(self) -> bool:
        """
        Is the connection open?

        :return: True for an open connection
        """
        return self._sock is not None

    def open(self) -> None:
        """
        Open TCP connection.
        """
        if self.is_open:
            logger.warning(
                "Tried to open the TCP Communication, but it is already open"
            )
            return

        # open the port
        logger.debug("Open TCP Port.")

        with self.access_lock:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.config.host, self.config.port))
            self._sock.settimeout(self.config.timeout)

    def close(self) -> None:
        """
        Close TCP connection.
        """
        if not self.is_open:
            logger.warning(
                "Tried to close the TCP Communication, but it is already closed"
            )
            return

        # close the port
        logger.debug("Close TCP Port.")

        with self.access_lock:
            sock: socket.socket = cast("socket.socket", self._sock)
            sock.close()
            self._sock = None

    def write_bytes(self, data: bytes) -> int:
        """
        Write data as `bytes` to the TcpCommunication.

        This method uses `self.access_lock` to ensure thread-safety.

        :param data: data as `bytes`-string to be written
        :return: number of bytes written
        """
        if not self.is_open:
            msg = "Tried to write to the TCP Communication, but it is closed"
            logger.error(msg)
            raise TcpCommunicationError(msg)

        with self.access_lock:
            sock: socket.socket = cast("socket.socket", self._sock)
            return sock.send(data)

    def read_bytes(self) -> bytes:
        """
        Read a single line as `bytes` from the TcpCommunication.

        This method uses `self.access_lock` to ensure thread-safety.

        :return: a single line as `bytes` containing the terminator, which can also be
            empty b""
        """
        if not self.is_open:
            msg = "Tried to read from the TCP Communication, but it is closed"
            logger.error(msg)
            raise TcpCommunicationError(msg)

        with self.access_lock:
            sock: socket.socket = cast("socket.socket", self._sock)
            try:
                return sock.recv(self.config.bufsize)
            except TimeoutError:
                msg = "Timeout during reading from TCP, return empty bytes"
                logger.debug(msg)
                return b""


class Tcp(TcpCommunication):
    """Old name :class:`Tcp` for :class:`TcpCommunication` for keeping this import
    backwards compatibile"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        warnings.warn(
            "The 'Tcp' class is deprecated, use 'TcpCommunication' instead",
            DeprecationWarning,
            stacklevel=2,
        )
