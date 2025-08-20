#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
EarthingStick of the different "Cubes".
"""

import logging

from .constants import SafetyStatus
from .errors import CubeEarthingStickOperationError
from .switches import (  # noqa: F401
    SwitchOperatingStatus,
    SwitchOperation,
    SwitchStatus,
    _Switch,
)

logger = logging.getLogger(__name__)


class _EarthingStick(_Switch):
    """
    Earthing sticks with status, operating status (manual and auto) and manual operate.
    """

    _STICKS: tuple = (1, 2, 3, 4, 5, 6)
    _ERROR_CLS = CubeEarthingStickOperationError
    _SWITCHABLE_AT_STATES = (  # type: ignore[assignment]
        SafetyStatus.RED_READY,
        SafetyStatus.RED_OPERATE,
    )

    def __init__(self, handle, number: int) -> None:
        super().__init__(handle, device_name=f"Earthing Stick {number}")

        self._CMD_STATUS: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."si_HMI_Status"'
        )
        self._CMD_OPERATING_STATUS: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."sx_manual_control_active"'
        )
        self._CMD_MANUAL: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."sx_earthing_manually"'
        )
