#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Alarms of the different "Cubes".
"""

from aenum import IntEnum

from hvl_ccb.utils.enum import ValueEnum, unique

from .constants import _PrefixedNumbersEnumBase

NUMBER_OF_ALARMS = 152


class _AlarmEnumBase(_PrefixedNumbersEnumBase):
    """
    Base class for enums with "Alarm{n}" instance names, where n=1..N.
    """

    @classmethod
    def _prefix(cls) -> str:
        return "ALARM_"

    @classmethod
    def alarm(cls, number: int):  # noqa: ANN206
        """
        Get the enum instance for a given alarm number.

        :param number: the alarm number (1..N)
        :return: the enum instance for the alarm number.
        :raises ValueError: when alarm number is not in the 1..N range
        """
        return cls.get(number)


_Alarms = unique(
    _AlarmEnumBase(
        "Alarms",
        {
            f"{_AlarmEnumBase._prefix()}{n}": f'"DB_Alarm_HMI"."Alarm{n}"'
            for n in range(1, NUMBER_OF_ALARMS)
        },
    )
)
"""
Alarms enumeration containing all variable NodeID strings for the alarm array.
"""


class _AlarmStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1


class _AlarmsOverview:
    """
    Stores the status of all alarms / messages
    """

    def __init__(self) -> None:
        for i in _Alarms.range():
            setattr(type(self), f"alarm_{i}", _AlarmStatus.INACTIVE)


class _AlarmLevel(IntEnum):
    """
    Alarm Level for OPC alarms, the level is similar to the corresponding logging level.
    """

    NOT_DEFINED = 10
    MESSAGE = 20
    WARNING = 30
    STOP = 35


class _AlarmText(ValueEnum, init="level coming going"):  # type: ignore[call-arg]
    """
    This enumeration contains the message for coming and going alarms of the BaseCube
    system.
    The corresponding AlarmLevel is also stored.
    Use the :meth:`AlarmText.get_level`
    method to retrieve the alarm level of an alarm number.
    Use the :meth:`AlarmText.get_coming_message`
    method to retrieve the going message of an alarm number.
    Use the :meth:`AlarmText.get_going_message`
    method to retrieve the coming message of an alarm number.
    """

    # Safety elements
    ALARM_1 = (
        _AlarmLevel.STOP,
        "Emergency Stop 1 triggered",
        "Emergency Stop 1 released",
    )
    ALARM_2 = (
        _AlarmLevel.STOP,
        "Emergency Stop 2 triggered",
        "Emergency Stop 2 released",
    )
    ALARM_3 = (
        _AlarmLevel.STOP,
        "Emergency Stop 3 triggered",
        "Emergency Stop 3 released",
    )
    ALARM_4 = _AlarmLevel.STOP, "Safety Switch 1 Error", "Safety Switch 1 Error solved"
    ALARM_5 = _AlarmLevel.STOP, "Safety Switch 2 Error", "Safety Switch 2 Error solved"
    ALARM_6 = _AlarmLevel.STOP, "Door 1 Lock Failure", "Door 1 Lock Failure solved"
    ALARM_7 = _AlarmLevel.STOP, "Door 2 Lock Failure", "Door 2 Lock Failure solved"
    ALARM_8 = _AlarmLevel.STOP, "Door 3 Lock Failure", "Door 3 Lock Failure solved"
    ALARM_9 = (
        _AlarmLevel.STOP,
        "Earthing Stick 1 Error while opening",
        "Earthing Stick 1 Error while opening solved",
    )
    ALARM_10 = (
        _AlarmLevel.STOP,
        "Earthing Stick 2 Error while opening",
        "Earthing Stick 2 Error while opening solved",
    )
    ALARM_11 = (
        _AlarmLevel.STOP,
        "Earthing Stick 3 Error while opening",
        "Earthing Stick 3 Error while opening solved",
    )
    ALARM_12 = (
        _AlarmLevel.STOP,
        "Earthing Stick 4 Error while opening",
        "Earthing Stick 4 Error while opening solved",
    )
    ALARM_13 = (
        _AlarmLevel.STOP,
        "Earthing Stick 5 Error while opening",
        "Earthing Stick 5 Error while opening solved",
    )
    ALARM_14 = (
        _AlarmLevel.STOP,
        "Earthing Stick 6 Error while opening",
        "Earthing Stick 6 Error while opening solved",
    )
    ALARM_15 = (
        _AlarmLevel.STOP,
        "Earthing Stick 1 Error while closing",
        "Earthing Stick 1 Error while closing solved",
    )
    ALARM_16 = (
        _AlarmLevel.STOP,
        "Earthing Stick 2 Error while closing",
        "Earthing Stick 2 Error while closing solved",
    )
    ALARM_17 = (
        _AlarmLevel.STOP,
        "Earthing Stick 3 Error while closing",
        "Earthing Stick 3 Error while closing solved",
    )
    ALARM_18 = (
        _AlarmLevel.STOP,
        "Earthing Stick 4 Error while closing",
        "Earthing Stick 4 Error while closing solved",
    )
    ALARM_19 = (
        _AlarmLevel.STOP,
        "Earthing Stick 5 Error while closing",
        "Earthing Stick 5 Error while closing solved",
    )
    ALARM_20 = (
        _AlarmLevel.STOP,
        "Earthing Stick 6 Error while closing",
        "Earthing Stick 6 Error while closing solved",
    )
    ALARM_21 = _AlarmLevel.STOP, "Safety Fence 1 not closed", "Safety Fence 1 closed"
    ALARM_22 = _AlarmLevel.STOP, "Safety Fence 2 not closed", "Safety Fence 2 closed"
    ALARM_23 = _AlarmLevel.STOP, "OPC Connection Error", "OPC Connection Error is gone"
    ALARM_24 = _AlarmLevel.STOP, "Grid Power Failure", "Grid Power Failure is gone"
    ALARM_25 = _AlarmLevel.STOP, "UPS Failure", "UPS Failure is gone"
    ALARM_26 = _AlarmLevel.STOP, "24V PSU Failure", "24V PSU Failure is gone"

    # Power unit
    ALARM_27 = (
        _AlarmLevel.STOP,
        "Power Setup and Power Switch Position are not matching",
        "Power Setup and Power Switch Position are matching again",
    )
    ALARM_28 = (
        _AlarmLevel.STOP,
        "Power Inverter Failure",
        "Power Inverter Failure solved",
    )
    ALARM_29 = (
        _AlarmLevel.STOP,
        "Control Loop Response Failure",
        "Control Loop Response Failure solved",
    )
    ALARM_30 = (
        _AlarmLevel.STOP,
        "'Set Polarity' does not match with Measured Voltage",
        "'Set Polarity' matches with Measured Voltage",
    )

    # Doors
    ALARM_41 = (
        _AlarmLevel.WARNING,
        "Door 1: Use Earthing Rod!",
        "Door 1: Earthing Rod used.",
    )
    ALARM_42 = (
        _AlarmLevel.MESSAGE,
        "Door 1: Earthing Rod is still in Experiment.",
        "Door 1: Earthing Rod is removed from Experiment.",
    )
    ALARM_43 = (
        _AlarmLevel.WARNING,
        "Door 2: Use Earthing Rod!",
        "Door 2: Earthing Rod used.",
    )
    ALARM_44 = (
        _AlarmLevel.MESSAGE,
        "Door 2: Earthing Rod is still in Experiment.",
        "Door 2: Earthing Rod is removed from Experiment.",
    )
    ALARM_45 = (
        _AlarmLevel.WARNING,
        "Door 3: Use Earthing Rod!",
        "Door 3: Earthing Rod used.",
    )
    ALARM_46 = (
        _AlarmLevel.MESSAGE,
        "Door 3: Earthing Rod is still in Experiment.",
        "Door 3: Earthing Rod is removed from Experiment.",
    )

    # General
    ALARM_47 = _AlarmLevel.MESSAGE, "UPS Charge < 85%", "UPS Charge >= 85%"
    ALARM_48 = _AlarmLevel.MESSAGE, "UPS running on Battery", "UPS running on Grid"
    ALARM_49 = (
        _AlarmLevel.WARNING,
        "Remove PD-Calibrator from the Circuit",
        "PD-Calibrator removed from the Circuit",
    )
    ALARM_50 = _AlarmLevel.MESSAGE, "OPC Connection active", "OPC Connection not active"
    ALARM_57 = (
        _AlarmLevel.MESSAGE,
        "Breakdown Detection Unit triggered",
        "Breakdown Detection Unit is reset",
    )

    # Earthing Stick
    ALARM_51 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 1: Manual earthing enabled",
        "Earthing Stick 1: Manual earthing disabled",
    )
    ALARM_52 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 2: Manual earthing enabled",
        "Earthing Stick 2: Manual earthing disabled",
    )
    ALARM_53 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 3: Manual earthing enabled",
        "Earthing Stick 3: Manual earthing disabled",
    )
    ALARM_54 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 4: Manual earthing enabled",
        "Earthing Stick 4: Manual earthing disabled",
    )
    ALARM_55 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 5: Manual earthing enabled",
        "Earthing Stick 5: Manual earthing disabled",
    )
    ALARM_56 = (
        _AlarmLevel.MESSAGE,
        "Earthing Stick 6: Manual earthing enabled",
        "Earthing Stick 6: Manual earthing disabled",
    )

    # generic not defined alarm text
    NOT_DEFINED = (
        _AlarmLevel.NOT_DEFINED,
        "NO ALARM TEXT DEFINED",
        "NO ALARM TEXT DEFINED",
    )

    @classmethod
    def get_level(cls, alarm: int) -> _AlarmLevel:
        """
        Get the alarm level of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the alarm level for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").level
        except AttributeError:
            return cls.NOT_DEFINED.level  # type: ignore[attr-defined]

    @classmethod
    def get_coming_message(cls, alarm: int) -> str:
        """
        Get the coming message of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the coming alarm message for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").coming
        except AttributeError:
            return cls.NOT_DEFINED.coming  # type: ignore[attr-defined]

    @classmethod
    def get_going_message(cls, alarm: int) -> str:
        """
        Get the going message of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the going alarm message for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").going
        except AttributeError:
            return cls.NOT_DEFINED.going  # type: ignore[attr-defined]
