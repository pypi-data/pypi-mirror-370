#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication and auxiliary classes for Technix
"""

import logging
from abc import ABC
from typing import NamedTuple, TypeAlias

from hvl_ccb import configdataclass
from hvl_ccb.comm import SyncCommunicationProtocol, SyncCommunicationProtocolConfig
from hvl_ccb.comm.serial import SerialCommunication, SerialCommunicationConfig
from hvl_ccb.comm.tcp import TcpCommunication, TcpCommunicationConfig
from hvl_ccb.dev import DeviceError
from hvl_ccb.utils.enum import ValueEnum
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


class TechnixError(DeviceError):
    """
    Technix related errors.
    """


class TechnixFaultError(TechnixError):
    """
    Raised when the fault flag was detected while the interlock is closed
    """


@configdataclass
class _TechnixCommunicationConfig(SyncCommunicationProtocolConfig):
    #: The terminator is CR
    terminator: bytes = b"\r"


class _TechnixCommunication(SyncCommunicationProtocol, ABC):
    """
    Generic communication class for Technix, which can be implemented via
    `TechnixSerialCommunication` or `TechnixTcpCommunication`
    """

    def query(
        self,
        command: str,
        n_attempts_max: int | None = None,
        attempt_interval_sec: Number | None = None,
    ) -> str:
        """
        Send a command to the interface and handle the status message.
        Possibly raises an error.

        :param command: Command to send
        :param n_attempts_max: Amount of attempts how often a non-empty text is tried to
            be read as answer
        :param attempt_interval_sec: time between the reading attempts
        :raises TechnixError: if the connection is broken
        :return: Answer from the interface
        """

        with self.access_lock:
            logger.debug(f"TechnixCommunication, send: '{command}'")
            answer: str | None = super().query(
                command,
                n_attempts_max=n_attempts_max,
                attempt_interval_sec=attempt_interval_sec,
            )  # string or None
            logger.debug(f"TechnixCommunication, receive: '{answer}'")
            if answer is None:
                msg = f"TechnixCommunication did get no answer on command: '{command}'"
                logger.error(msg)
                raise TechnixError(msg)
            return answer


@configdataclass
class TechnixSerialCommunicationConfig(
    _TechnixCommunicationConfig, SerialCommunicationConfig
):
    """
    Configuration for the serial communication for Technix
    """


class TechnixSerialCommunication(_TechnixCommunication, SerialCommunication):
    """
    Serial communication for Technix
    """

    @staticmethod
    def config_cls():
        return TechnixSerialCommunicationConfig


@configdataclass
class TechnixTcpCommunicationConfig(
    _TechnixCommunicationConfig, TcpCommunicationConfig
):
    """
    Configuration for the TCP communication for Technix
    """

    #: Port at which Technix is listening
    port: int = 4660


class TechnixTcpCommunication(TcpCommunication, _TechnixCommunication):
    """
    TCP communication for Technix
    """

    @staticmethod
    def config_cls():
        return TechnixTcpCommunicationConfig

    def open(self) -> None:
        super().open()

        while data := self.read_bytes():
            msg = f"Read telnet data at the beginning: {data!r}"
            logger.debug(msg)


_TechnixCommunicationClasses: TypeAlias = type[  # noqa: PYI047
    TechnixSerialCommunication | TechnixTcpCommunication
]


class _SetRegisters(ValueEnum):
    VOLTAGE = "d1"  # Output Voltage programming
    CURRENT = "d2"  # Output Current programming
    HVON = "P5"  # HV on
    HVOFF = "P6"  # HV off
    LOCAL = "P7"  # Local/remote mode
    INHIBIT = "P8"  # Inhibit


class _GetRegisters(ValueEnum):
    VOLTAGE = "a1"  # Output Voltage Monitor
    CURRENT = "a2"  # Output Current Monitor
    STATUS = "E"  # Image of the power supply logical status


class _Status(NamedTuple):
    """
    Container for the different statuses of the device. It can also handle the most
    recent reading of the voltage and current at the output.
    """

    inhibit: bool
    remote: bool
    hv_off: bool
    hv_on: bool
    output: bool
    open_interlock: bool
    fault: bool
    voltage_regulation: bool

    voltage: Number | None
    current: Number | None
