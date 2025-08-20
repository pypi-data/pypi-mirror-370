#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants, Heinzinger Digital Interface I/II and Heinzinger PNC power supply.
Descriptors for errors
"""

import logging

from hvl_ccb.dev.base import DeviceError
from hvl_ccb.utils.enum import RangeEnum

logger = logging.getLogger(__name__)


class HeinzingerError(DeviceError):
    """
    General error with the Heinzinger PNC voltage source.
    """


class HeinzingerDeviceNotRecognizedError(HeinzingerError):
    """
    Error indicating that the serial number of the device is not recognized.
    """


class HeinzingerSetValueError(HeinzingerError):
    """
    Error indicating that the value (current, voltage, ...) is not set correctly
    """


class RecordingsEnum(RangeEnum):
    @classmethod
    def unit(cls) -> str:
        return ""

    ONE = 1
    TWO = 2
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
