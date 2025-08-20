#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Supports of the different "Cubes".
"""

import logging
from typing import TYPE_CHECKING

from hvl_ccb.utils.validation import validate_bool

if TYPE_CHECKING:
    from . import BaseCube  # pragma: no cover

logger = logging.getLogger(__name__)


class _SupportPort:
    """
    class to collect outputs and inputs of support ports.
    """

    _PORTS: tuple = (1, 2, 3, 4, 5, 6)
    _CONTACTS: tuple = (1, 2)
    _IOS: tuple = ("Q", "I")

    def __init__(self, handle, number: int) -> None:
        self._handle: BaseCube = handle
        self._number: int = number

    def _cmd(self, io: str, contact: int) -> str:
        return f'"{io}x_Allg_Support{self._number}_{contact}"'

    @property
    def output_1(self) -> bool:
        """
        Output 1 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("Q", 1)))
        self._log_msg(value, "Output", 1, "")
        return value

    @output_1.setter
    def output_1(self, value: bool) -> None:
        """
        Output 1 of support port.

        :param value: `True` for high output, `False` for low
        """
        validate_bool("state", value, logger)
        self._handle.write(self._cmd("Q", 1), value)
        self._log_msg(value, "Output", 1, "set to ")

    @property
    def output_2(self) -> bool:
        """
        Output 2 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("Q", 2)))
        self._log_msg(value, "Output", 2, "")
        return value

    @output_2.setter
    def output_2(self, value: bool) -> None:
        """
        Output 2 of support port.

        :param value: `True` for high output, `False` for low
        """
        validate_bool("state", value, logger)
        self._handle.write(self._cmd("Q", 2), value)
        self._log_msg(value, "Output", 2, "set to ")

    @property
    def input_1(self) -> bool:
        """
        Input 1 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("I", 1)))
        self._log_msg(value, "Input", 1, "")
        return value

    @property
    def input_2(self) -> bool:
        """
        Input 2 of support port

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("I", 2)))
        self._log_msg(value, "Input", 2, "")
        return value

    def _log_msg(self, value, name, contact, action) -> None:
        value_str = "HIGH" if value else "LOW"
        logger.info(
            f"Support {name} Port {self._number} Contact {contact} "
            f"is {action}{value_str}"
        )
