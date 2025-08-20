#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Ranges, RangeEnum for Fluke8845a device
"""

from typing import Literal

from hvl_ccb.utils.enum import RangeEnum


class DCVoltageRange(RangeEnum):
    """
    possible measurement ranges for DC voltage with unit volt
    """

    ONE_HUNDRED_MILLI_VOLT = 0.1
    ONE_VOLT = 1
    TEN_VOLT = 10
    HUNDRED_VOLT = 100
    ONE_THOUSAND_VOLT = 1000

    @classmethod
    def unit(cls) -> Literal["V"]:
        return "V"


class ACVoltageRange(RangeEnum):
    """
    possible measurement ranges for AC voltage with unit volt
    """

    ONE_HUNDRED_MILLI_VOLT = 0.1
    ONE_VOLT = 1
    TEN_VOLT = 10
    HUNDRED_VOLT = 100
    SEVEN_HUNDRED_FIFTY_VOLT = 750

    @classmethod
    def unit(cls) -> Literal["V"]:
        return "V"


class DCCurrentRange(RangeEnum):
    """
    possible measurement ranges for DC current with unit Ampere
    """

    ONE_HUNDRED_MICRO_AMPERE = 1e-4
    ONE_MILLI_AMPERE = 1e-3
    TEN_MILLI_AMPERE = 1e-2
    ONE_HUNDRED_MILLI_AMPERE = 0.1
    FOUR_HUNDRED_MILLI_AMPERE = 0.4
    ONE_AMPERE = 1
    THREE_AMPERE = 3
    TEN_AMPERE = 10

    @classmethod
    def unit(cls) -> Literal["A"]:
        return "A"


class ACCurrentRange(RangeEnum):
    """
    possible measurement ranges for AC current with unit Ampere
    """

    TEN_MILLI_AMPERE = 0.01
    ONE_HUNDRED_MILLI_AMPERE = 0.1
    FOUR_HUNDRED_MILLI_AMPERE = 0.4
    ONE_AMPERE = 1
    THREE_AMPERE = 3
    TEN_AMPERE = 10

    @classmethod
    def unit(cls) -> Literal["A"]:
        return "A"


class ResistanceRange(RangeEnum):
    """
    possible measurement ranges for resistance with unit Ohm
    """

    # Two-wire resistance (RES) and four-wire resistance (FRES)
    ONE_HUNDRED_OHM = 1e2
    ONE_THOUSAND_OHM = 1e3
    TEN_THOUSAND_OHM = 1e4
    ONE_HUNDRED_THOUSAND_OHM = 1e5
    ONE_MILLION_OHM = 1e6
    TEN_MILLION_OHM = 1e7
    ONE_HUNDRED_MILLION_OHM = 1e8

    @classmethod
    def unit(cls) -> Literal["Ω"]:
        return "Ω"


class ApertureRange(RangeEnum):
    """
    Page 46

    .. code-block:: rst

        Sets the gate time for the frequency/period function to the value
        10ms = 4 1/2 digits
        100ms = 5 1/2 digits
        1s = 6 1/2 digits
    """

    TEN_MILLI_SECOND = 0.01
    ONE_HUNDRED_MILLI_SECOND = 0.1
    ONE_SECOND = 1

    @classmethod
    def unit(cls) -> Literal["s"]:
        return "s"


class FilterRange(RangeEnum):
    """
    Page 47

    .. code-block:: rst

        Sets the appropriate filter for the frequency specified by <n>
        High pass filter
        For `VOLTAGE_AC`: <n> Hz to 300 kHz
        For `CURRENT_AC`: <n> Hz to 10 kHz
        parameters <n> = 3 slow filter
                        20 medium filter
                        200 fast filter
        For `CURRENT_AC` and `VOLTAGE_AC`
    """

    SLOW_FILTER = 3
    MEDIUM_FILTER = 20
    FAST_FILTER = 200

    @classmethod
    def unit(cls) -> Literal[""]:
        return ""
