#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants of FuG
"""

from aenum import IntEnum

from hvl_ccb.utils.enum import NameEnum


class FuGDigitalVal(IntEnum):
    """
    Enum for digital values understood by FuG
    """

    OFF = 0
    ON = 1
    YES = 1
    NO = 0


class FuGRampModes(IntEnum):
    """
    Enum for the different ramp modes
    """

    IMMEDIATELY = 0
    """Standard mode: no ramp"""
    FOLLOWRAMP = 1
    """Follow the ramp up- and downwards"""
    RAMPUPWARDS = 2
    """Follow the ramp only upwards, downwards immediately"""
    SPECIALRAMPUPWARDS = 3
    """Follow a special ramp function only upwards"""
    ONLYUPWARDSOFFTOZERO = 4
    """Follow the ramp up- and downwards, if output is OFF set value is zero"""


class FuGReadbackChannels(IntEnum):
    """
    Enum for the readback channels for Trigger-on-Talk
    """

    VOLTAGE = 0
    CURRENT = 1
    STATUSBYTE = 2
    RATEDVOLTAGE = 3
    RATEDCURRENT = 4
    FIRMWARE = 5
    SN = 6


class FuGMonitorModes(IntEnum):
    """
    Enum for the different ADC modes
    """

    T256US = 0
    """14 bit + sign, 256 us integration time"""
    T1MS = 1
    """15 bit + sign, 1 ms integration time"""
    T4MS = 2
    """15 bit + sign, 4 ms integration time"""
    T20MS = 3
    """17 bit + sign, 20 ms integration time"""
    T40MS = 4
    """17 bit + sign, 40 ms integration time"""
    T80MS = 5
    """typ. 18 bit + sign, 80 ms integration time"""
    T200MS = 6
    """typ. 19 bit + sign, 200 ms integration time"""
    T800MS = 7
    """typ. 20 bit + sign, 800 ms integration time"""


class FuGPolarities(IntEnum):
    """
    Enum for the different polarities
    """

    POSITIVE = 0
    NEGATIVE = 1


class FuGTerminators(IntEnum):
    """
    Enum for the terminators of the command strings
    """

    CRLF = 0
    LFCR = 1
    LF = 2
    CR = 3


class FuGProbusIVCommands(NameEnum, init="command input_type"):  # type: ignore[call-arg]
    """
    Enum for the command of the (older) "Probus IV" interface.
    The `input_type` defines the type of a value that can be written.
    """

    ID = "*IDN?", None
    RESET = "=", None
    OUTPUT = "F", (FuGDigitalVal, int)
    VOLTAGE = "U", (int, float)
    CURRENT = "I", (int, float)
    READBACKCHANNEL = "N", (FuGReadbackChannels, int)
    QUERY = "?", None
    ADMODE = "S", (FuGMonitorModes, int)
    POLARITY = "P", (FuGPolarities, int)
    XOUTPUTS = "R", int
    """TODO: the possible values are limited to 0..13"""
    EXECUTEONX = "G", (FuGDigitalVal, int)
    """Wait for "X" to execute pending commands"""
    EXECUTE = "X", None
    TERMINATOR = "Y", (FuGTerminators, int)
