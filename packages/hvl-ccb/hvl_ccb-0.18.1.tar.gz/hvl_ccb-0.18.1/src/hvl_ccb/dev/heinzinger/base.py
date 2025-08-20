#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Base classes for Heinzinger Digital Interface I/II and Heinzinger PNC power supply.

The Heinzinger Digital Interface I/II is used for many Heinzinger power units.
Interface Manual:
https://www.heinzinger.com/assets/uploads/downloads/Handbuch_DigitalInterface_2021-12-14-V1.6.pdf

The Heinzinger PNC series is a series of high voltage direct current power supplies.
The class HeinzingerPNC is tested with two PNChp 60000-1neg and a PNChp 1500-1neg.
Check the code carefully before using it with other PNC devices, especially PNC3p
or PNCcap.
Manufacturer homepage:
https://www.heinzinger.com/en/products/pnc-serie
"""

import logging

from hvl_ccb.comm import SyncCommunicationProtocol
from hvl_ccb.comm.serial import (
    SerialCommunication,
    SerialCommunicationBytesize,
    SerialCommunicationConfig,
    SerialCommunicationParity,
    SerialCommunicationStopbits,
)
from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


@configdataclass
class HeinzingerSerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for Heinzinger power supplies is 9600 baud
    baudrate: int = 9600

    #: Heinzinger does not use parity
    parity: str | SerialCommunicationParity = SerialCommunicationParity.NONE

    #: Heinzinger uses one stop bit
    stopbits: int | SerialCommunicationStopbits = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: int | SerialCommunicationBytesize = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is LF
    terminator: bytes = b"\n"

    #: use 3 seconds timeout as default
    timeout: Number = 3

    #: default time to wait between attempts of reading a non-empty text
    wait_sec_read_text_nonempty: Number = 0.5

    #: increased to 40 default number of attempts to read a non-empty text
    default_n_attempts_read_text_nonempty: int = 40


class HeinzingerSerialCommunication(SerialCommunication, SyncCommunicationProtocol):
    """
    Specific communication protocol implementation for
    Heinzinger power supplies.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return HeinzingerSerialCommunicationConfig
