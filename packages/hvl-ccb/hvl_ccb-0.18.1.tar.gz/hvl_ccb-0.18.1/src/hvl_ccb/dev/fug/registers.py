#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Registers of FuG
"""

import logging
from typing import cast

from hvl_ccb.utils.enum import NameEnum
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

from .constants import (
    FuGDigitalVal,
    FuGMonitorModes,
    FuGPolarities,
    FuGRampModes,
    FuGReadbackChannels,
    FuGTerminators,
)
from .errors import FuGErrorcodes

logger = logging.getLogger(__name__)


class FuGProbusVRegisterGroups(NameEnum):
    """
    Enum for the register groups
    """

    SETVOLTAGE = "S0"
    SETCURRENT = "S1"
    OUTPUTX0 = "B0"
    OUTPUTX1 = "B1"
    OUTPUTX2 = "B2"
    OUTPUTXCMD = "BX"
    OUTPUTONCMD = "BON"
    MONITOR_V = "M0"
    MONITOR_I = "M1"
    INPUT = "D"
    CONFIG = "K"


class FuGProbusVSetRegisters:
    """
    Setvalue control acc. 4.2.1 for the voltage and the current output
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups) -> None:
        self._fug = fug

        _super_register = super_register.value

        self._setvalue: str = _super_register
        self.__max_setvalue: float = 0
        self._actualsetvalue: str = _super_register + "A"
        self._ramprate: str = _super_register + "R"
        self._rampmode: str = _super_register + "B"
        self._rampstate: str = _super_register + "S"
        self._high_resolution: str = _super_register + "H"

    @property
    def _max_setvalue(self) -> float:
        return self.__max_setvalue

    @_max_setvalue.setter
    def _max_setvalue(self, value: Number):
        self.__max_setvalue = float(value)

    @property
    def setvalue(self) -> float:
        """
        For the voltage or current output this setvalue was programmed.

        :return: the programmed setvalue
        """
        return float(self._fug.get_register(self._setvalue))

    @setvalue.setter
    def setvalue(self, value: Number):
        """
        This sets the value for the voltage or current output

        :param value: value in V or A
        """
        validate_number("", value, (0, self._max_setvalue), logger=logger)
        self._fug.set_register(self._setvalue, value)

    @property
    def actualsetvalue(self) -> float:
        """
        The actual valid set value, which depends on the ramp function.

        :return: actual valid set value
        """
        return float(self._fug.get_register(self._actualsetvalue))

    @actualsetvalue.setter
    def actualsetvalue(self, value: Number):
        validate_number("", value, (0, self._max_setvalue), logger=logger)
        self._fug.set_register(self._actualsetvalue, value)

    @property
    def ramprate(self) -> float:
        """
        The set ramp rate in V/s.

        :return: ramp rate in V/s
        """
        return float(self._fug.get_register(self._ramprate))

    @ramprate.setter
    def ramprate(self, value: Number):
        """
        The ramp rate can be set in V/s.

        :param value: ramp rate in V/s
        """
        self._fug.set_register(self._ramprate, value)

    @property
    def rampmode(self) -> FuGRampModes:
        """
        The set ramp mode to control the setvalue.

        :return: the mode of the ramp as instance of FuGRampModes
        """
        return FuGRampModes(int(self._fug.get_register(self._rampmode)))

    @rampmode.setter
    def rampmode(self, value: int | FuGRampModes):
        """
        Sets the ramp mode.

        :param value: index for the ramp mode from FuGRampModes
        :raise FuGError: if a wrong ramp mode is chosen
        """
        try:
            self._fug.set_register(self._rampmode, FuGRampModes(value))
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E125).raise_()

    @property
    def rampstate(self) -> FuGDigitalVal:
        """
        Status of ramp function.

        :return 0: if final setvalue is reached
        :return 1: if still ramping up
        """
        return FuGDigitalVal(int(self._fug.get_register(self._rampstate)))

    @rampstate.setter
    def rampstate(self, _):
        """
        The rampstate is only an output. Writing data to this register will raise an
        error

        :raise FuGError: if something is written to this attribute
        """
        cast("FuGErrorcodes", FuGErrorcodes.E106).raise_()

    @property
    def high_resolution(self) -> FuGDigitalVal:
        """
        Status of the high resolution mode of the output.

        :return 0: normal operation
        :return 1: High Res. Mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._high_resolution)))

    @high_resolution.setter
    def high_resolution(self, value: int | FuGDigitalVal):
        """
        Enables/disables the high resolution mode of the output.

        :param value: FuGDigitalVal
        :raise FuGError: if not a FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.ON:
                self._fug.set_register(self._high_resolution, FuGDigitalVal.ON)
            else:
                self._fug.set_register(self._high_resolution, FuGDigitalVal.OFF)
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E115).raise_()


class FuGProbusVDORegisters:
    """
    Digital outputs acc. 4.2.2
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups) -> None:
        self._fug = fug

        _super_register = super_register.value

        self._out = _super_register
        self._status = _super_register + "A"

    @property
    def out(self) -> int | FuGDigitalVal:
        """
        Status of the output according to the last setting. This can differ from the
        actual state if output should only pulse.

        :return: FuGDigitalVal
        """
        return FuGDigitalVal(int(self._fug.get_register(self._out)))

    @out.setter
    def out(self, value: int | FuGDigitalVal):
        """
        Set the output ON or OFF. If pulsing is enabled, it only pulses.

        :param value: FuGDigitalVal
        :raise FuGError: if a non FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.ON:
                self._fug.set_register(self._out, FuGDigitalVal.ON)
            else:
                self._fug.set_register(self._out, FuGDigitalVal.OFF)
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E115).raise_()

    @property
    def status(self) -> FuGDigitalVal:
        """
        Returns the actual value of output. This can differ from the set value if
        pulse function is used.

        :return: FuGDigitalVal
        """
        return FuGDigitalVal(int(self._fug.get_register(self._status)))

    @status.setter
    def status(self, _):
        """
        The status is only an output. Writing data to this register will raise an
        error

        :raise FuGError: read only
        """
        cast("FuGErrorcodes", FuGErrorcodes.E206).raise_()


class FuGProbusVMonitorRegisters:
    """
    Analog monitors acc. 4.2.3
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups) -> None:
        self._fug = fug
        _super_register = super_register.value

        self._value = _super_register
        self._value_raw = _super_register + "R"
        self._adc_mode = _super_register + "I"

    @property
    def value(self) -> float:
        """
        Value from the monitor.

        :return: a float value in V or A
        """
        return float(self._fug.get_register(self._value))

    @value.setter
    def value(self, _):
        """
        Monitor is read-only!

        :raise FuGError: read-only
        """
        cast("FuGErrorcodes", FuGErrorcodes.E306).raise_()

    @property
    def value_raw(self) -> float:
        """
        uncalibrated raw value from AD converter

        :return: float value from ADC
        """
        return float(self._fug.get_register(self._value_raw))

    @value_raw.setter
    def value_raw(self, _):
        """
        Monitor is read-only!

        :raise FuGError: read-only
        """
        cast("FuGErrorcodes", FuGErrorcodes.E306).raise_()

    @property
    def adc_mode(self) -> FuGMonitorModes:
        """
        The programmed resolution and integration time of the AD converter

        :return: FuGMonitorModes
        """
        return FuGMonitorModes(int(self._fug.get_register(self._adc_mode)))

    @adc_mode.setter
    def adc_mode(self, value: int | FuGMonitorModes):
        """
        Sets the resolution and integration time of the AD converter with the given
        settings in FuGMonitorModes.

        :param value: index of the monitor mode from FuGMonitorModes
        :raise FuGError: if index is not in FuGMonitorModes
        """
        try:
            self._fug.set_register(self._adc_mode, FuGMonitorModes(value))
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E145).raise_()


class FuGProbusVDIRegisters:
    """
    Digital Inputs acc. 4.2.4
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups) -> None:
        self._fug = fug

        _super_register = super_register.value

        self._cv_mode = _super_register + "VR"
        self._cc_mode = _super_register + "IR"
        self._reg_3 = _super_register + "3R"
        self._x_stat = _super_register + "X"
        self._on = _super_register + "ON"
        self._digital_control = _super_register + "SD"
        self._analog_control = _super_register + "SA"
        self._calibration_mode = _super_register + "CAL"

    @property
    def cv_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in CV mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._cv_mode)))

    @property
    def cc_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in CC mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._cc_mode)))

    @property
    def reg_3(self) -> FuGDigitalVal:
        """
        For special applications.

        :return: input from bit 3-REG
        """
        return FuGDigitalVal(int(self._fug.get_register(self._reg_3)))

    @property
    def x_stat(self) -> FuGPolarities:
        """

        :return: polarity of HVPS with polarity reversal
        """
        return FuGPolarities(int(self._fug.get_register(self._x_stat)))

    @property
    def on(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply ON
        """
        return FuGDigitalVal(int(self._fug.get_register(self._on)))

    @property
    def digital_control(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is digitally controlled
        """
        return FuGDigitalVal(int(self._fug.get_register(self._digital_control)))

    @property
    def analog_control(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is controlled by the analog interface
        """
        return FuGDigitalVal(int(self._fug.get_register(self._analog_control)))

    @property
    def calibration_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in calibration mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._calibration_mode)))


class FuGProbusVConfigRegisters:
    """
    Configuration and Status values, acc. 4.2.5
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups) -> None:
        self._fug = fug

        _super_register = super_register.value

        self._terminator = _super_register + "T"
        self._status = _super_register + "S"
        self._srq_status = _super_register + "QS"
        self._srq_mask = _super_register + "QM"
        self._execute_on_x = _super_register + "X"
        self._readback_data = _super_register + "N"
        self._most_recent_error = _super_register + "E"

    @property
    def terminator(self) -> FuGTerminators:
        """
        Terminator character for answer strings from ADDA

        :return: FuGTerminators
        """
        return FuGTerminators(int(self._fug.get_register(self._terminator)))

    @terminator.setter
    def terminator(self, value: int | FuGTerminators):
        """
        Sets the terminator character for answer string from ADDA

        :param value: index from FuGTerminators
        :raise FuGError: if index is not in FuGTerminators
        """
        try:
            self._fug.set_register(self._terminator, FuGTerminators(value))
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E165).raise_()

    @property
    def status(self) -> str:
        """
        Statusbyte as a string of 0/1. Combined status (compatibel to Probus IV),
        MSB first:
        Bit 7: I-REG
        Bit 6: V-REG
        Bit 5: ON-Status
        Bit 4: 3-Reg
        Bit 3: X-Stat (polarity)
        Bit 2: Cal-Mode
        Bit 1: unused
        Bit 0: SEL-D

        :return: string of 0/1
        """
        return self._fug.get_register(self._status)

    @status.setter
    def status(self, _):
        """
        Stautsbyte is read-only

        :raise FuGError: read-only
        """
        cast("FuGErrorcodes", FuGErrorcodes.E206).raise_()

    @property
    def srq_status(self) -> str:
        """
        SRQ-Statusbyte output as a decimal number:
        Bit 2: PS is in CC mode
        Bit 1: PS is in CV mode

        :return: representative string
        """
        return self._fug.get_register(self._srq_status)

    @srq_status.setter
    def srq_status(self, _):
        """
        SRQ-Statusbyte is read-only

        :raise FuGError: read-only
        """
        cast("FuGErrorcodes", FuGErrorcodes.E206).raise_()

    @property
    def srq_mask(self) -> int:
        """
        SRQ-Mask, Service-Request
        Enable status bits for SRQ
        0: no SRQ
        Bit 2: SRQ on change of status to CC
        Bit 1: SRQ on change to CV

        :return: representative integer value
        """
        return int(float(self._fug.get_register(self._srq_mask)))

    @srq_mask.setter
    def srq_mask(self, value: int):
        """
        Sets the SRQ-Mask

        :param value: representative integer value
        """
        self._fug.set_register(self._srq_mask, value)

    @property
    def execute_on_x(self) -> FuGDigitalVal:
        """
        status of Execute-on-X

        :return: FuGDigitalVal of the status
        """
        return FuGDigitalVal(int(self._fug.get_register(self._execute_on_x)))

    @execute_on_x.setter
    def execute_on_x(self, value: int | FuGDigitalVal):
        """
        Enable/disable the Execute-on-X-mode
        0: immediate execution
        1: execution pending until X-command

        :param value: FuGDigitalVal
        :raise FuGError: if a non FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.YES:
                self._fug.set_register(self._execute_on_x, FuGDigitalVal.YES)
            else:
                self._fug.set_register(self._execute_on_x, FuGDigitalVal.NO)
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E115).raise_()

    @property
    def readback_data(self) -> FuGReadbackChannels:
        """
        Preselection of readout data for Trigger-on-Talk

        :return: index for the readback channel
        """
        return FuGReadbackChannels(int(self._fug.get_register(self._readback_data)))

    @readback_data.setter
    def readback_data(self, value: int | FuGReadbackChannels):
        """
        Sets the readback channel according to the index given within the
        FuGReadbackChannels

        :param value: index of readback channel
        :raise FuGError: if index in not in FuGReadbackChannels
        """
        try:
            self._fug.set_register(self._readback_data, FuGReadbackChannels(value))
        except ValueError:
            cast("FuGErrorcodes", FuGErrorcodes.E135).raise_()

    @property
    def most_recent_error(self) -> FuGErrorcodes:
        """
        Reads the Error-Code of the most recent command

        :return FuGError:
        :raise FuGError: if code is not "E0"
        """
        return FuGErrorcodes(self._fug.get_register(self._most_recent_error))

    @most_recent_error.setter
    def most_recent_error(self, _):
        cast("FuGErrorcodes", FuGErrorcodes.E666).raise_()
