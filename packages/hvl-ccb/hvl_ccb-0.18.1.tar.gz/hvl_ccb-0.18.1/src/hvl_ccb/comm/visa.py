#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol for VISA. Makes use of the pyvisa library.
The backend can be NI-Visa or pyvisa-py.

Information on how to install a VISA backend can be found here:
https://pyvisa.readthedocs.io/en/master/getting_nivisa.html

So far only TCPIP SOCKET and TCPIP INSTR interfaces are supported.
"""

import logging
from collections.abc import Callable
from ipaddress import IPv4Address, IPv6Address
from time import sleep
from typing import TYPE_CHECKING, cast

import pyvisa as visa
from pyvisa_py.protocols.rpc import (  # type: ignore[import-untyped,import-not-found]
    RPCError,
)

from hvl_ccb.comm import CommunicationError
from hvl_ccb.comm.base import SyncCommunicationProtocol, SyncCommunicationProtocolConfig
from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.enum import AutoNumberNameEnum
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_and_resolve_host, validate_tcp_port

if TYPE_CHECKING:
    from pyvisa.resources import MessageBasedResource


logger = logging.getLogger(__name__)


class VisaCommunicationError(IOError, CommunicationError):
    """
    Base class for VisaCommunication errors.
    """


@configdataclass
class VisaCommunicationConfig(SyncCommunicationProtocolConfig):
    """
    `VisaCommunication` configuration dataclass.
    """

    class InterfaceType(AutoNumberNameEnum, init="value"):  # type: ignore[call-arg]
        """
        Supported VISA Interface types.
        """

        #: VISA-RAW protocol
        TCPIP_SOCKET = ((),)

        #: VXI-11 protocol
        TCPIP_INSTR = ((),)

        def address(
            self, host: str, port: int | None = None, board: int | None = None
        ) -> str:
            """
            Address string specific to the VISA interface type.

            :param host: host IP address
            :param port: optional TCP port
            :param board: optional board number
            :return: address string
            """

            if self.name == VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET:
                return f"TCPIP{board}::{host}::{port}::SOCKET"
            if self.name == VisaCommunicationConfig.InterfaceType.TCPIP_INSTR:
                return f"TCPIP::{host}::INSTR"
            msg = f"{self.name} is unknown InterfaceType."
            raise VisaCommunicationError(msg)

    # IP address of the VISA device.
    host: str | IPv4Address | IPv6Address = ""

    #: Interface type of the VISA connection, being one of :class:`InterfaceType`.
    interface_type: str | InterfaceType = ""

    #: Board number is typically 0 and comes from old bus systems.
    board: int = 0

    #: TCP port, standard is 5025.
    port: int = 5025

    #: Timeout for commands in milli seconds.
    timeout: int = 5000

    #: Chunk size is the allocated memory for read operations. The standard is 20kB,
    #: and is increased per default here to 200kB. It is specified in bytes.
    chunk_size: int = 204800

    #: Timeout for opening the connection, in milli seconds.
    open_timeout: int = 1000

    #: The terminator will be used to set `write_termination` and `read_termination`
    terminator: bytes = b"\n"

    visa_backend: str = ""
    """
    Specifies the path to the library to be used with PyVISA as a backend. Defaults
    to None, which is NI-VISA (if installed), or pyvisa-py (if NI-VISA is not found).
    To force the use of pyvisa-py, specify '@py' here.
    """

    def clean_values(self) -> None:
        # in principle, host is allowed to be IP or FQDN. However, we only allow IP:
        self.force_value("host", validate_and_resolve_host(self.host, logger))  # type: ignore[attr-defined]
        validate_tcp_port(self.port, logger)

        if not isinstance(self.interface_type, self.InterfaceType):
            self.force_value("interface_type", self.InterfaceType(self.interface_type))  # type: ignore[attr-defined]

        if self.board < 0:
            msg = "Board number has to be >= 0."
            raise ValueError(msg)

        if self.timeout < 0:
            msg = "Timeout has to be >= 0."
            raise ValueError(msg)

        if self.open_timeout < 0:
            msg = "Open Timeout has to be >= 0."
            raise ValueError(msg)

        allowed_terminators = (b"\n", b"\r", b"\r\n")
        if self.terminator not in allowed_terminators:
            msg = "Terminator has to be \\n, \\r or \\r\\n as `byte`."
            raise ValueError(msg)

    @property
    def address(self) -> str:
        """
        Address string depending on the VISA protocol's configuration.

        :return: address string corresponding to current configuration
        """

        return self.interface_type.address(  # type: ignore[union-attr]
            cast("str", self.host),
            port=self.port,
            board=self.board,
        )


def has_instrument(func: Callable) -> Callable:
    """
    Decorator to check if `self._instrument is not None`.
    """

    def decorator(*args, **kwargs):
        self = args[0]
        if self._instrument is None:
            msg = (
                f'Could not execute "{func.__name__}" of VISA connection, it was not'
                " started."
            )
            logger.error(msg)
            raise VisaCommunicationError(msg)
        return func(*args, **kwargs)

    return decorator


class VisaCommunication(SyncCommunicationProtocol):
    """
    Implements the Communication Protocol for VISA / SCPI.
    """

    #: The maximum of commands that can be sent in one round is 5 according to the
    #: VISA standard.
    MULTI_COMMANDS_MAX = 5

    #: The character to separate two commands is ; according to the VISA standard.
    MULTI_COMMANDS_SEPARATOR = ";"

    #: Small pause in seconds to wait after write operations, allowing devices to
    #: really do what we tell them before continuing with further tasks.
    WAIT_AFTER_WRITE = 0.08  # seconds to wait after a write is sent

    def __init__(self, configuration) -> None:
        """
        Constructor for VisaCommunication.
        """

        super().__init__(configuration)

        # create a new resource manager
        if self.config.visa_backend == "":
            self._resource_manager = visa.ResourceManager()
        else:
            self._resource_manager = visa.ResourceManager(self.config.visa_backend)

        self._instrument: MessageBasedResource | None = None

    @staticmethod
    def config_cls() -> type[VisaCommunicationConfig]:
        return VisaCommunicationConfig

    def open(self) -> None:
        """
        Open the VISA connection and create the resource.
        """

        logger.info("Open the VISA connection.")

        with self.access_lock:
            try:
                self._instrument = cast(
                    "MessageBasedResource",
                    self._resource_manager.open_resource(
                        self.config.address,
                        open_timeout=self.config.open_timeout,
                    ),
                )
                self._instrument.chunk_size = self.config.chunk_size
                self._instrument.timeout = self.config.timeout
                self._instrument.write_termination = self.config.terminator.decode()
                self._instrument.read_termination = self.config.terminator.decode()

            except visa.VisaIOError as e:
                logger.exception("Error of VISA Communication", exc_info=e)
                if e.error_code != 0:
                    raise VisaCommunicationError from e

            except (
                RPCError,
                ConnectionRefusedError,
                BrokenPipeError,
            ) as e:
                # if pyvisa-py is used as backend, this RPCError can come. As it is
                # difficult to import (hyphen in package name), we "convert" it here to
                # a VisaCommunicationError. Apparently on the Linux runners,
                # a ConnectionRefusedError is raised on fail, rather than an RPCError.
                # On macOS the BrokenPipeError error is raised (from
                # pyvisa-py/protocols/rpc.py:320), with puzzling log message from
                # visa.py: "187 WARNING  Could not close VISA connection, was not
                # started."
                logger.exception("Error of VISA Communication", exc_info=e)
                raise VisaCommunicationError from e

            if self._instrument is not None:
                try:
                    # enable keep-alive of the connection. Seems not to work always, but
                    # using the status poller a keepalive of the connection is also
                    # satisfied. Unsupported on RTO 1022 devices.
                    value = visa.constants.VI_TRUE
                    if isinstance(
                        self._instrument.get_visa_attribute(
                            visa.constants.ResourceAttribute.tcpip_keepalive
                        ),
                        bool,
                    ):
                        value = True
                    self._instrument.set_visa_attribute(
                        visa.constants.ResourceAttribute.tcpip_keepalive, value
                    )

                except visa.VisaIOError as e:
                    if e.abbreviation == "VI_ERROR_NSUP_ATTR":
                        logger.warning(
                            "Error of VISA Communication: 'VI_ERROR_NSUP_ATTR'",
                            exc_info=e,
                        )
                    else:
                        logger.exception("Error of VISA Communication", exc_info=e)
                        if e.error_code != 0:
                            raise VisaCommunicationError from e

    def close(self) -> None:
        """
        Close the VISA connection and invalidates the handle.
        """

        if self._instrument is None:
            logger.warning("Could not close VISA connection, was not started.")
            return

        try:
            with self.access_lock:
                self._instrument.close()
        except visa.InvalidSession as e:
            logger.warning(
                "Could not close VISA connection, session invalid.", exc_info=e
            )

    @has_instrument
    def read_bytes(self) -> bytes:
        return cast("MessageBasedResource", self._instrument).read_raw()

    @has_instrument
    def write_bytes(self, data: bytes) -> int:
        return cast("MessageBasedResource", self._instrument).write_raw(data)

    @has_instrument
    def read(self) -> str:
        return cast("MessageBasedResource", self._instrument).read()

    @has_instrument
    def write(self, text: str) -> None:
        cast("MessageBasedResource", self._instrument).write(text)

    def read_all(
        self,
        _n_attempts_max: int | None = None,
        _attempt_interval_sec: Number | None = None,
    ) -> str | None:
        msg = "The 'read_all'-feature is not supported by visa."
        raise NotImplementedError(msg)

    @has_instrument
    def query(
        self,
        command: str,
        _n_attempts_max: int | None = None,
        _attempt_interval_sec: Number | None = None,
    ) -> str | None:
        with self.access_lock:
            return cast("MessageBasedResource", self._instrument).query(command)

    @has_instrument
    def write_multiple(self, *commands: str) -> None:
        """
        Write commands. No answer is read or expected.

        :param commands: one or more commands to send
        :raises VisaCommunicationError: when connection was not started
        """
        with self.access_lock:
            cast("MessageBasedResource", self._instrument).write(
                self._generate_cmd_string(commands)
            )

            # sleep small amount of time to not overload device
            sleep(self.WAIT_AFTER_WRITE)

    @has_instrument
    def query_multiple(self, *commands: str) -> str | tuple[str, ...]:
        """
        A combination of write(message) and read.

        :param commands: list of commands
        :return: list of values
        :raises VisaCommunicationError: when connection was not started, or when trying
            to issue too many commands at once.
        """
        cmd_string = self._generate_cmd_string(commands)
        with self.access_lock:
            return_string = cast("MessageBasedResource", self._instrument).query(
                cmd_string
            )

        if len(commands) == 1:
            return return_string

        return tuple(return_string.split(self.MULTI_COMMANDS_SEPARATOR))

    @classmethod
    def _generate_cmd_string(cls, command_list: tuple[str, ...]) -> str:
        """
        Generate the command string out of a tuple of strings.

        :param command_list: is the tuple containing multiple commands
        :return: the command string that can be sent via the protocol
        """

        if len(command_list) <= cls.MULTI_COMMANDS_MAX:
            return cls.MULTI_COMMANDS_SEPARATOR.join(command_list)

        msg = (
            f"Too many commands at once ({len(command_list)}). Max allowed: "
            f"{cls.MULTI_COMMANDS_MAX}."
        )
        raise VisaCommunicationError(msg)

    @has_instrument
    def spoll(self) -> int:
        """
        Execute serial poll on the device. Reads the status byte register STB. This
        is a fast function that can be executed periodically in a polling fashion.

        :return: integer representation of the status byte
        :raises VisaCommunicationError: when connection was not started
        """

        interface_type = self.config.interface_type

        if interface_type == VisaCommunicationConfig.InterfaceType.TCPIP_INSTR:
            with self.access_lock:
                return cast("MessageBasedResource", self._instrument).read_stb()

        if interface_type == VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET:
            return int(self.query("*STB?"))

        msg = "Forgot to cover interface_type case?"
        raise VisaCommunicationError(msg)
