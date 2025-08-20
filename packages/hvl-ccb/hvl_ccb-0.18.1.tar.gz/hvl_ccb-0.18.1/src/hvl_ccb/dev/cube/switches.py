#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Switches of the different "Cubes".
"""

import logging
from abc import ABC
from typing import TYPE_CHECKING

from aenum import IntEnum

from hvl_ccb.utils.enum import BoolEnum

from .constants import SafetyStatus
from .errors import SwitchOperationError

if TYPE_CHECKING:
    from . import BaseCube  # pragma: no cover

logger = logging.getLogger(__name__)


class SwitchStatus(IntEnum):
    """
    Status of a switch. These are the possible values in the status integer
    e.g. in :attr:`_Switch.status`.
    """

    # Switch is deselected and not enabled in safety circuit. To get out of
    # this state, the earthing has to be enabled in the BaseCube HMI setup.
    INACTIVE = 0

    # Earthing is closed (safe).
    CLOSED = 1

    # Earthing is open (not safe).
    OPEN = 2

    # Earthing is in error, e.g. when the stick did not close correctly or could not
    # open.
    ERROR = 3


class SwitchOperatingStatus(IntEnum):
    """
    Operating Status of a switch. Switch can be in auto or manual mode.
    """

    AUTO = 0
    MANUAL = 1


class SwitchOperation(BoolEnum):
    """
    Operation of a switch in manual operating mode. Can be closed or opened.
    """

    OPEN = False
    CLOSE = True


class _Switch(ABC):  # noqa: B024
    """
    Switch with status, operating status (manual and auto) and manual operate.
    """

    # TODO: re-write `_Switch` to not be an `ABC`  # noqa: FIX002
    # https://gitlab.com/ethz_hvl/hvl_ccb/-/issues/381

    _ERROR_CLS = SwitchOperationError
    _SWITCHABLE_AT_STATES: tuple[SafetyStatus] | None = None

    def __init__(self, handle, device_name: str) -> None:
        self._handle: BaseCube = handle
        self._device_name: str = device_name
        self._CMD_STATUS: str | None = None
        self._CMD_OPERATING_STATUS: str | None = None
        self._CMD_MANUAL: str | None = None

    @property
    def status(self) -> SwitchStatus:
        """
        Position status of a switch.

        :return: Status of the switch.
        """
        if self._CMD_STATUS is None:
            msg = (
                f"Tried to query position status of {self._device_name}, "
                f"but {self._device_name} does not have a position status feedback."
            )
            logger.error(msg)
            raise self._ERROR_CLS(msg)

        value = SwitchStatus(self._handle.read(self._CMD_STATUS))
        logger.info(f"Status of {self._device_name} is {value.name}")
        return value

    @property
    def operating_status(self) -> SwitchOperatingStatus:
        """
        Switch operating status, if 'manual' the stick can be controlled by the
        user.

        :return: Switch operating status, can be either auto or manual
        """
        if self._CMD_OPERATING_STATUS is None:
            msg = (
                f"Tried to query operating status of {self._device_name}, "
                f"but {self._device_name} does not have an operating status."
            )
            logger.error(msg)
            raise self._ERROR_CLS(msg)

        value = SwitchOperatingStatus(self._handle.read(self._CMD_OPERATING_STATUS))
        logger.info(f"Operating Status of {self._device_name} is {value.name}")
        return value

    def operation_conditions_fulfilled(self) -> None:
        """
        Method to be called before an operation is performed. It will raise an
        exception if not
        """
        if (
            self._SWITCHABLE_AT_STATES
            and self._handle.status not in self._SWITCHABLE_AT_STATES
        ):
            switchable_states = " or ".join(
                [f'"{_}"' for _ in self._SWITCHABLE_AT_STATES]
            )
            msg = (
                f"Cube needs to be in state {switchable_states} "
                f"to operate {self._device_name} manually, "
                f'but is in "{self._handle.status.name}".'
            )
            logger.error(msg)
            raise self._ERROR_CLS(msg)

        if self.operating_status != SwitchOperatingStatus.MANUAL:
            msg = (
                f"Operation of the {self._device_name} is not possible, "
                "as the feature is not activated in the Cube Setup."
            )
            logger.error(msg)
            raise self._ERROR_CLS(msg)

    @property
    def operate(self) -> SwitchOperation:
        """
        Operation of a switch which has a manual operating status.

        :return: Switch operation setting, can be open or close
        """
        if self._CMD_MANUAL is None:
            msg = (
                f"Tried to query manual operation setting of {self._device_name}, "
                f"but {self._device_name} cannot be operated manually."
            )
            logger.error(msg)
            raise self._ERROR_CLS(msg)

        value = SwitchOperation(self._handle.read(self._CMD_MANUAL))
        logger.info(f"Manual operation status of {self._device_name} is {value}")
        return value

    @operate.setter
    def operate(self, operation: SwitchOperation) -> None:
        """
        Operation of a switch which has a manual operating status.

        :param operation: switch operation setting (close or open)
        :raises SwitchOperationError: when the operation conditions of the switch
        are not fulfilled, or if the switch is not allowed to be manually operated
        """
        self.operation_conditions_fulfilled()

        if self._CMD_MANUAL is None:
            msg = (  # pragma: no cover
                f"Tried to operate {self._device_name}, "
                f"but {self._device_name} cannot"
                "be operated manually."
            )
            logger.error(msg)  # pragma: no cover
            raise self._ERROR_CLS(msg)  # pragma: no cover

        operation = SwitchOperation(operation)
        self._handle.write(self._CMD_MANUAL, operation)
        logger.info(f"{self._device_name} is set to {operation}")
