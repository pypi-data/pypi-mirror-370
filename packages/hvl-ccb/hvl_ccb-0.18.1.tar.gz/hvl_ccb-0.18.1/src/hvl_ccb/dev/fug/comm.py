#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
SerialCommunication for FuG
"""

import logging
from typing import cast

from hvl_ccb.comm.base import SyncCommunicationProtocol
from hvl_ccb.comm.serial import (
    SerialCommunication,
    SerialCommunicationBytesize,
    SerialCommunicationConfig,
    SerialCommunicationParity,
    SerialCommunicationStopbits,
)
from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.typing import Number

from .errors import FuGError, FuGErrorcodes

logger = logging.getLogger(__name__)


@configdataclass
class FuGSerialCommunicationConfig(SerialCommunicationConfig):
    """
    Configuration dataclass for :class:`FuGSerialCommunication`.
    """

    #: Baudrate for FuG power supplies is 9600 baud
    baudrate: int = 9600

    #: FuG does not use parity
    parity: str | SerialCommunicationParity = SerialCommunicationParity.NONE

    #: FuG uses one stop bit
    stopbits: int | SerialCommunicationStopbits = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: int | SerialCommunicationBytesize = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is LF
    terminator: bytes = b"\n"

    #: use 3 seconds timeout as default
    timeout: Number = 3

    #: default time to wait between attempts of reading a non-empty text
    wait_sec_read_text_nonempty: Number = 0.5

    #: default number of attempts to read a non-empty text
    default_n_attempts_read_text_nonempty: int = 10


class FuGSerialCommunication(SerialCommunication, SyncCommunicationProtocol):
    """
    Specific communication protocol implementation for
    FuG power supplies.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return FuGSerialCommunicationConfig

    def query(
        self,
        command: str,
        n_attempts_max: int | None = None,
        attempt_interval_sec: Number | None = None,
    ) -> str | None:
        """
        Send a command to the interface and handle the status message.
        Raises an error, if the answer starts with "E".

        :param command: Command to send
        :raises FuGError: if the connection is broken or the error from the power
            source itself
        :return: Answer from the interface or empty string
        """

        with self.access_lock:
            logger.debug(f"FuG communication, send: {command}")
            answer: str | None = super().query(
                command, n_attempts_max, attempt_interval_sec
            )
            logger.debug(f"FuG communication, receive: {answer}")
            if not answer:
                cast("FuGErrorcodes", FuGErrorcodes.E504).raise_()
            try:
                FuGErrorcodes(cast("str", answer)).raise_()
            except ValueError as exc:
                logger.exception(
                    "ValueError at finding the correct FuGErrorcode", exc_info=exc
                )
                if cast("str", answer).startswith("E"):
                    msg = f'The unknown errorcode "{answer}" was detected.'
                    raise FuGError(msg) from exc
                return answer
            else:
                return ""
