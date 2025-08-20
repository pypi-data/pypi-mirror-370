#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants, variable names for the BaseCube OPC-connected devices.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, cast

from aenum import Enum, IntEnum
from typing_extensions import Self

from hvl_ccb.utils.enum import ValueEnum, unique
from hvl_ccb.utils.validation import validate_bool

if TYPE_CHECKING:
    from collections.abc import Sequence, Sized

    from hvl_ccb.utils.typing import Number

    from . import BaseCube  # pragma: no cover

logger = logging.getLogger(__name__)


class _BaseGetDescriptor:
    """
    Base Descriptor for attributes that are readonly.
    """

    def __init__(self, number: Number, name: str) -> None:
        self.number = number
        self.name = name

    @abstractmethod
    def __get__(self, instance, owner):  # noqa: ANN204
        pass  # pragma: no cover

    def __set__(self, instance, state) -> None:
        msg = f"It is not possible to set the {self.name}. This parameter is readonly!"
        logger.error(msg)
        raise AttributeError(msg)


@unique
class _CubeOpcEndpoint(ValueEnum):
    """
    OPC Server Endpoint strings for the BaseCube variants.
    """

    PI_CUBE = "PICube"
    BASE_CUBE = "BaseCube"


@unique
class _BreakdownDetection(ValueEnum):
    """
    Node ID strings for the breakdown detection.
    """

    # Boolean read-only variable indicating whether breakdown detection and fast
    # switchoff is enabled in the system or not.
    ACTIVATED = '"DB_Fast_Switch_Off"."sx_breakdownD_active"'

    # Boolean read-only variable telling whether the fast switch-off has triggered.
    # This can also be seen using the safety circuit state, therefore no method is
    # implemented to read this out directly.
    TRIGGERED = '"DB_Fast_Switch_Off"."sx_breakdownD_triggered"'

    # Boolean writable variable to reset the fast switch-off. Toggle to re-enable.
    RESET = '"DB_Fast_Switch_Off"."sx_breakdownD_reset"'


_CEE16 = '"Qx_Allg_Socket_CEE16"'


class _T13Socket:
    """
    Set and get the state of a SEV T13 power socket.
    """

    _SOCKETS: tuple = (1, 2, 3)

    def __init__(self, socket) -> None:
        self._socket = socket
        self._CMD = f'"Qx_Allg_Socket_T13_{socket}"'

    def __get__(self, instance, owner) -> Self | bool:
        if instance is None:
            return self  # pragma: no cover

        value = bool(instance.read(self._CMD))
        state = "ON" if value else "OFF"
        logger.info(f"T13 Power Socket {self._socket} is {state}")
        return value

    def __set__(self, instance, state) -> None:
        validate_bool("state", state, logger)
        instance.write(self._CMD, state)
        state_str = "ON" if state else "OFF"
        logger.info(f"T13 Power Socket {self._socket} is switched {state_str}")


@unique
class _Safety(ValueEnum):
    """
    NodeID strings for the basic safety circuit status
    """

    # Status is a read-only integer containing the state number of the
    # BaseCube-internal state machine. The values correspond to the numbers in
    # :class:`SafetyStatus`.
    STATUS = '"DB_Safety_Circuit"."si_safe_status"'


class SafetyStatus(IntEnum):
    """
    Safety status values that are possible states returned from
    :meth:`hvl_ccb.dev.cube.base.BaseCube.status`. These
    values correspond to the states of the BaseCube's safety circuit statemachine.
    """

    # System is initializing or booting.
    INITIALIZING = 0

    # System is safe, lamps are green and some safety elements are not in place such
    # that it cannot be switched to 'RED_READY' currently.
    GREEN_NOT_READY = 1

    # System is safe and all safety elements are in place to be able to switch to
    # *ready* 'RED_READY'.
    GREEN_READY = 2

    # System is locked in red state and *ready* to go to *operate* ('RED_OPERATE') mode.
    RED_READY = 3

    # System is locked in red state and in *operate* mode, i.e. high voltage on.
    RED_OPERATE = 4

    # Fast turn off triggered and switched off the system. Reset Breakdown Detection
    # to go back to a normal state.
    QUICK_STOP = 5

    # System is in error mode.
    ERROR = 6


class _SafetyStatusTransition(Enum, init="source target command"):  # type: ignore[call-arg]
    """
    NodeID strings for the transition between "ready" and "operate" and
    the corresponding source and target states.
    """

    #: Writable boolean for switching to Red Ready (locked, HV off) state.
    SWITCH_TO_READY = (
        SafetyStatus.GREEN_READY,
        SafetyStatus.RED_READY,
        '"DB_Safety_Circuit"."sx_safe_switch_to_ready"',
    )
    #: Writable boolean for switching to Red Operate (locket, HV on) state.
    SWITCH_TO_OPERATE = (
        SafetyStatus.RED_READY,
        SafetyStatus.RED_OPERATE,
        '"DB_Safety_Circuit"."sx_safe_switch_to_operate"',
    )


STOP_SAFETY_STATUSES: tuple[SafetyStatus, ...] = (
    cast("SafetyStatus", SafetyStatus.GREEN_NOT_READY),
    cast("SafetyStatus", SafetyStatus.GREEN_READY),
)
"""
BaseCube's safety statuses required to close the connection to the device.
"""


@unique
class _Power(ValueEnum):
    """
    Variable NodeID strings concerning power data.
    """

    # Primary voltage in volts, measured by the power inverter at its output.
    # (read-only)
    VOLTAGE_PRIMARY = '"DB_Datamanagement"."si_output_SC_voltage"'

    # Primary current in ampere, measured by the power inverter. (read-only)
    CURRENT_PRIMARY = '"DB_Datamanagement"."si_output_SC_current"'

    # Power setup that is configured using the BaseCube HMI. The value corresponds to
    # the ones in :class:`PowerSetup`. (read-only)
    SETUP = '"DB_Safety_Circuit"."si_power_setup"'

    # Voltage slope in V/s or kV/s (depends on Power Setup).
    VOLTAGE_SLOPE = '"DB_Powercontrol"."si_set_dUdT"'

    # Target voltage setpoint in V or kV (depends on Power Setup).
    VOLTAGE_TARGET = '"DB_Powercontrol"."si_set_voltage"'

    # Maximum voltage allowed by the current experimental setup in V or kV
    # (depends on Power Setup).. (read-only)
    VOLTAGE_MAX = '"DB_Powercontrol"."si_voltage_limit_panel"'

    # Power inverter output frequency. (read-only)
    FREQUENCY = '"DB_Datamanagement"."si_converter_frequency"'

    # Polarity of the output if a DC PowerSetup (7 or 8) is used.
    # Returns True if positive
    POLARITY = '"DB_Powercontrol"."sx_set_polarity"'

    # actual measured output voltage in V or kV (depends on Power Setup).
    VOLTAGE_ACTUAL = '"DB_Measurements"."si_actual_voltage"'


class Polarity(IntEnum):
    NEGATIVE = 0
    POSITIVE = 1


class PowerSetup(IntEnum, init="value slope_min slope_max scale unit"):  # type: ignore[call-arg]
    """
    Possible power setups corresponding to the value of variable :attr:`Power.setup`.
    The values for slope_min are experimentally defined, below these values the slope
    is more like a staircase

    The name of the first argument needs to be 'value', otherwise the IntEnum is
    not working correctly.
    """

    # No safety switches, uses only safety components (doors, fence, earthing...)
    # without any power source.
    NO_SOURCE = 0, 0, 0, 1, ""

    # For PICube: External power supply fed through blue 25A power plug input using
    # isolation transformer and safety switches of the PICube
    # For BaseCube: Use of an external safety switch attached to the BaseCube.
    EXTERNAL_SOURCE = 1, 0, 0, 1, ""

    # AC setup with one MWB transformer set to 50 kV maximum voltage.
    AC_50KV = 2, 100, 6000, 1e-3, "kV"

    # AC setup with one MWB transformer set to 100 kV maximum voltage.
    AC_100KV = 3, 100, 15000, 1e-3, "kV"

    # AC setup with two MWB transformers, one configured to a output voltage
    # of 100 kV and the other to 50 kV, resulting in a total maximum voltage of 150 kV.
    AC_150KV = 4, 200, 15000, 1e-3, "kV"

    # AC setup with two MWB transformers both configured to a output voltage
    # of 100 kV, resulting in a total maximum voltage of 200kV.
    AC_200KV = 5, 200, 15000, 1e-3, "kV"

    # Direct control of the internal power inverter, controlling of the primary voltage
    # output of the PICube itself. The maximum voltage at the output of the PICube
    # is 200 V. No feedback loop with a measurement transformer is used.
    POWER_INVERTER_220V = 6, 0.2, 15, 1, "V"

    # DC setup with one AC transformer configured to 100 kV and a rectifier circuit.
    # The maximum DC voltage is 140 kV.
    DC_140KV = 7, 300, 15000, 1e-3, "kV"

    # DC setup with one AC transformer configured to 100 kV and a Greinacher
    # voltage doubler circuit.
    # OR a DC setup with two AC transformers both configured to 100 kV and a rectifier
    # circuit. Both setup are resulting in DC voltage of 280 kV.
    DC_280KV = 8, 300, 15000, 1e-3, "kV"

    # Impulse setup with one AC transformer configured to 100 kV and a rectifier
    # circuit, which results in a maximum DC voltage of 140 kV. The impulse is
    # triggered with a spark gap.
    IMPULSE_140KV = 9, 300, 15000, 1e-3, "kV"


DC_POWER_SETUPS: tuple[PowerSetup, ...] = (
    cast("PowerSetup", PowerSetup.DC_140KV),
    cast("PowerSetup", PowerSetup.DC_280KV),
)

AC_POWER_SETUPS: tuple[PowerSetup, ...] = (
    cast("PowerSetup", PowerSetup.AC_50KV),
    cast("PowerSetup", PowerSetup.AC_100KV),
    cast("PowerSetup", PowerSetup.AC_150KV),
    cast("PowerSetup", PowerSetup.AC_200KV),
)


class _MeasurementChannel:
    """
    Measurement Channel with properties for the value and the ratio.
    """

    def __init__(self, handle, number: int, input_noise: Number) -> None:
        self._handle: BaseCube = handle
        self._number: int = number
        self._input_noise: Number = input_noise
        self._CMD_SCALE: str = f'"DB_Measurements"."sx_volts_input_{number}"'
        self._CMD_VOLTAGE: str = f'"DB_Measurements"."si_scaled_Voltage_Input_{number}"'
        self._CMD_RATIO: str = f'"DB_Measurements"."si_Divider_Ratio_{number}"'

    @property
    def voltage(self) -> float:
        """
        Measured voltage of the measurement channel.

        :return: in V
        """
        value = float(self._handle.read(self._CMD_VOLTAGE))
        scale_unit = self._handle.read(self._CMD_SCALE)
        if scale_unit:
            value_return = value * 1e3
            unit = "kV"
        else:
            value_return = value
            unit = "V"
        logger.info(
            f"Measurement Voltage of Channel {self._number} is {value:_.2f} {unit}"
        )
        return value_return

    @property
    def ratio(self) -> float:
        """
        Set ratio for the measurement channel.

        :return: in 1
        """
        value = float(self._handle.read(self._CMD_RATIO))
        logger.info(f"Measurement Ratio of Channel {self._number} is {value}")
        return value

    @property
    def noise_level(self) -> Number:
        return self._input_noise


@unique
class _Errors(ValueEnum):
    """
    Variable NodeID strings for information regarding error, warning and message
    handling.
    """

    #: Boolean read-only variable telling if a message is active.
    MESSAGE = '"DB_Message_Buffer"."Info_active"'

    #: Boolean read-only variable telling if a warning is active.
    WARNING = '"DB_Message_Buffer"."Warning_active"'

    #: Boolean read-only variable telling if a stop is active.
    STOP = '"DB_Message_Buffer"."Stop_active"'

    #: Writable boolean for the error quit button.
    QUIT = '"DB_Message_Buffer"."Reset_button"'


class DoorStatus(IntEnum):
    """
    Possible status values for doors.
    """

    #: not enabled in BaseCube HMI setup, this door is not supervised.
    INACTIVE = 0

    #: Door is open.
    OPEN = 1

    #: Door is closed, but not locked.
    CLOSED = 2

    #: Door is closed and locked (safe state).
    LOCKED = 3

    #: Door has an error or was opened in locked state (either with emergency stop or
    #: from the inside).
    ERROR = 4


class _Door(_BaseGetDescriptor):
    """
    Get the status of a safety fence door. See :class:`constants.DoorStatus` for
    possible returned door statuses.
    """

    def __init__(self, number, name) -> None:
        super().__init__(number, name)
        self._CMD = f'"DB_Safety_Circuit"."Door_{number}"."si_HMI_status"'

    def __get__(self, instance, owner) -> Self | DoorStatus:
        """
        :return: the door status
        """
        if instance is None:
            return self  # pragma: no cover

        value = DoorStatus(instance.read(self._CMD))
        logger.info(f"Door {self.number} is {value.name}")
        return value


class EarthingRodStatus(IntEnum):
    """
    Possible status values for earthing rods.
    """

    #: earthing rod is somewhere in the experiment
    #: and blocks the start of the experiment
    EXPERIMENT_BLOCKED = 0

    #: earthing rod is hanging next to the door, experiment is ready to operate
    EXPERIMENT_READY = 1


class _EarthingRod(_BaseGetDescriptor):
    """
    Get the status of a earthing rod. See :class:`constants.EarthingRodStatus` for
    possible returned earthing rod statuses.
    """

    def __init__(self, number, name) -> None:
        super().__init__(number, name)
        self._CMD = f'"DB_Safety_Circuit"."Door_{number}"."Ix_earthingrod"'

    def __get__(self, instance, owner) -> Self | EarthingRodStatus:
        """
        :return: the earthing rod status
        """
        if instance is None:
            return self  # pragma: no cover

        value = EarthingRodStatus(instance.read(self._CMD))
        status = "NOT " if value == EarthingRodStatus.EXPERIMENT_READY else ""
        logger.info(f"Earthing Rod {self.number} is {status}blocking the Experiment")
        return value


class _PrefixedNumbersEnumBase(ValueEnum):
    """
    Base class for enums with "{prefix}{n}" instance names, where n=1..N.
    """

    @classmethod
    def range(cls) -> Sequence[int]:
        """
        Integer range of all channels.

        :return: sequence of channel numbers
        """
        return range(1, len(cast("Sized", cls)) + 1)

    @classmethod
    def _validate_number(cls, number: int) -> None:
        """
        Validate enum instance number.

        :param number: the enum instance number (1..N)
        :raises ValueError: when enum instance number is not in 1..N range
        """
        if number not in cls.range():
            msg = f"{cls._prefix()} number must be one of {list(cls.range())}"
            raise ValueError(msg)

    @classmethod
    def _prefix(cls) -> str:
        """
        Enum instances name prefix: "{prefix}{n}"

        :return: enum instances prefix string
        """
        msg = "Implement in subclass"
        raise NotImplementedError(msg)  # pragma: no cover

    @property
    def number(self) -> int:
        """
        Get corresponding enum instance number.

        :return: enum instance number (1..N)
        """
        return self.name.removeprefix(self._prefix())

    # no type return as it would be a arguably too complex/obscure;
    # cf. https://github.com/python/typing/issues/58#issuecomment-326240794
    @classmethod
    def get(cls, number: int) -> _PrefixedNumbersEnumBase:
        """
        Get the enum instance for a given number.

        :param number: the instance number (1..N)
        :return: the enum instance for the given number.
        :raises ValueError: when instance number is not in the 1..N range
        """
        cls._validate_number(number)
        return getattr(cls, f"{cls._prefix()}{number}")


class _OpcControl(ValueEnum):
    """
    Variable NodeID strings for supervision of the OPC connection from the
    controlling workstation to the BaseCube.
    """

    # writable boolean to enable OPC remote control and display a message window on
    # the BaseCube HMI.
    ACTIVE = '"DB_OPC_Connection"."sx_OPC_active"'
    LIVE = '"DB_OPC_Connection"."sx_OPC_lifebit"'
    TIME = '"DB_OPC_Connection"."st_system_time"'


NUMBER_OF_LINES = 16


class _LineEnumBase(_PrefixedNumbersEnumBase):
    """
    Base class for enums with "input_{n}" instance names, where n=1..N.
    """

    @classmethod
    def _prefix(cls) -> str:
        return "LINE_"

    @classmethod
    def line(cls, number: int) -> _LineEnumBase:
        """
        Get the enum instance for a given line number.

        :param number: the line number (1..M)
        :return: the enum instance for the given line number.
        :raises ValueError: when line number is not in the 1..N range
        """
        return cls.get(number)


MessageBoard = unique(
    _LineEnumBase(
        "MessageBoard",
        {
            f"{_LineEnumBase._prefix()}{n}": f'"DB_OPC_Connection"."Is_status_Line_{n}"'
            for n in range(1, NUMBER_OF_LINES)
        },
    )
)
"""
Variable NodeID strings for message board lines.
"""
