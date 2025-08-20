#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants, ValueEnum: MeasurementFunction and TriggerSoruce
Descriptors for range, filter and aperture

TODO: Fix typing
"""

import logging

from hvl_ccb.dev import DeviceError
from hvl_ccb.dev.fluke884x.ranges import (
    ACCurrentRange,
    ACVoltageRange,
    ApertureRange,
    DCCurrentRange,
    DCVoltageRange,
    FilterRange,
    ResistanceRange,
)
from hvl_ccb.utils.enum import ValueEnum
from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


class Fluke8845aError(DeviceError):
    pass


class Fluke8845aCheckError(Fluke8845aError):
    pass


class Fluke8845aUnknownCommandError(Fluke8845aError):
    pass


class MeasurementFunction(ValueEnum):
    """
    Page 40

    Sets the Meter function. This command must be followed by the INIT and FETCh?
    commands to cause the meter to take a measurement.
    """

    CURRENT_AC = "CURR:AC"
    CURRENT_DC = "CURR"
    VOLTAGE_AC = "VOLT:AC"
    VOLTAGE_DC = "VOLT"
    FOUR_WIRE_RESISTANCE = "FRES"
    TWO_WIRE_RESISTANCE = "RES"
    FREQUENCY = "FREQ"
    PERIOD = "PER"
    DIODE = "DIOD"

    def _range(self):
        if self == MeasurementFunction.VOLTAGE_AC:
            return ACVoltageRange
        if self == MeasurementFunction.VOLTAGE_DC:
            return DCVoltageRange
        if self == MeasurementFunction.CURRENT_AC:
            return ACCurrentRange
        if self == MeasurementFunction.CURRENT_DC:
            return DCCurrentRange
        if self in (
            MeasurementFunction.TWO_WIRE_RESISTANCE,
            MeasurementFunction.FOUR_WIRE_RESISTANCE,
        ):
            return ResistanceRange
        return None

    def _filter(self):
        if self in (MeasurementFunction.VOLTAGE_AC, MeasurementFunction.CURRENT_AC):
            return FilterRange
        return None

    def _aperture(self):
        if self in (MeasurementFunction.FREQUENCY, MeasurementFunction.PERIOD):
            return ApertureRange
        return None


class TriggerSource(ValueEnum):
    """
    Page 57

    .. code-block:: rst

        BUS: Sets the Meter to expect a trigger through the IEEE-488 bus or
        upon execution of a *TRG command
        IMM: Selects Meter's internal triggering system
        EXT: Sets the Meter to sense triggers through the trigger jack on the rear
        panel of the Meter
    """

    BUS = "BUS"
    IMMEDIATE = "IMM"
    EXTERNAL = "EXT"


class _BaseDescriptor:
    def __init__(self, cmd_enum):  # noqa: ANN204
        self._cmd_enum = cmd_enum
        self._query_cmd = None
        self._write_cmd = None
        self._range_enum = None
        self._value_min = None
        self._value_max = None

    def __get__(self, instance, owner=None):  # noqa: ANN204
        voltage_range = float(instance.com.query(self._query_cmd))
        return self._range_enum(voltage_range)

    def __set__(self, instance, input_range):  # noqa: ANN204
        if not isinstance(input_range, self._range_enum):
            validate_number(
                "input range",
                input_range,
                (self._value_min, self._value_max),
                logger=logger,
            )
        input_range = self._range_enum(input_range)
        instance.com.write(f"{self._write_cmd} {input_range}")
        if self.__get__(instance) == float(input_range.value):
            logger.info(
                f"{self._write_cmd} is successfully set "
                f"to {input_range} {self._range_enum.unit()}."
            )
        else:
            msg = f"{self._cmd_enum} setting failed."
            logger.error(msg)
            raise Fluke8845aCheckError(msg)


class _RangeDescriptor(_BaseDescriptor):
    def __init__(self, cmd_enum):  # noqa: ANN204
        super().__init__(cmd_enum)
        self._query_cmd = f"{self._cmd_enum}:RANG?"
        self._write_cmd = f"{self._cmd_enum}:RANG"
        self._range_enum = cmd_enum._range()
        self._value_min = 0
        self._value_max = max(self._range_enum)

    def __set__(self, instance, input_range):  # noqa: ANN204
        super().__set__(instance, input_range)


class _FilterDescriptor(_BaseDescriptor):
    def __init__(self, cmd_enum):  # noqa: ANN204
        super().__init__(cmd_enum)
        self._query_cmd = f"{self._cmd_enum}:BAND?"
        self._write_cmd = f"{self._cmd_enum}:BAND"
        self._range_enum = cmd_enum._filter()
        self._value_min = min(self._range_enum)
        self._value_max = max(self._range_enum)


class _ApertureDescriptor(_BaseDescriptor):
    def __init__(self, cmd_enum):  # noqa: ANN204
        super().__init__(cmd_enum)
        self._query_cmd = f"{self._cmd_enum}:APER?"
        self._write_cmd = f"{self._cmd_enum}:APER"
        self._range_enum = cmd_enum._aperture()
        self._value_min = min(self._range_enum)
        self._value_max = max(self._range_enum)
