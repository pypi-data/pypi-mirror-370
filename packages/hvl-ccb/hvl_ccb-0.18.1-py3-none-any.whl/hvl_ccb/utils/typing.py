#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Additional Python typing module utilities
"""

import logging
from typing import TypeAlias

import numpy.typing as npt

logger = logging.getLogger(__name__)


Number: TypeAlias = int | float
"""Typing hint auxiliary for a Python base number types: `int` or `float`."""

ConvertableTypes: TypeAlias = (
    int | float | list[Number] | tuple[Number, ...] | dict[str, Number] | npt.NDArray
)
"""Typing hint for data type that can be used in conversion"""
