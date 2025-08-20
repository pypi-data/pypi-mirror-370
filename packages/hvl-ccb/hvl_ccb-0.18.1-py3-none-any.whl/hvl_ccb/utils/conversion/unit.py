#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

"""
Unit conversion, within in the same group of units, for example Kelvin <-> Celsius
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, cast

from .utils import preserve_type

if TYPE_CHECKING:
    import numpy.typing as npt

    from hvl_ccb.utils.typing import ConvertableTypes


logger = logging.getLogger(__name__)


class Unit(Enum):
    @classmethod
    @abstractmethod
    @preserve_type
    def convert(cls, value: ConvertableTypes, source, target) -> ConvertableTypes:
        pass  # pragma: no cover


class Temperature(Unit):
    K = "K"
    C = "C"
    F = "F"
    KELVIN = K
    CELSIUS = C
    FAHRENHEIT = F

    @classmethod
    @preserve_type
    def convert(
        cls,
        value: ConvertableTypes,
        source: str | Temperature = KELVIN,
        target: str | Temperature = CELSIUS,
    ) -> ConvertableTypes:
        value_: npt.NDArray = cast("npt.NDArray", value)
        try:
            source = Temperature(source)
            target = Temperature(target)
        except ValueError as exc:
            logger.warning(
                "One unit or both units for source and / or target temperature "
                "are not valid.",
                exc_info=exc,
            )
            raise ValueError from exc
        if source == target:
            return value_

        # convert source to kelvin
        if source == cls.CELSIUS:
            value_ = value_ + 273.15
        elif source == cls.FAHRENHEIT:
            value_ = (value_ - 32) / 1.8 + 273.15

        # convert kelvin to target
        if target == cls.CELSIUS:
            value_ = value_ - 273.15
        elif target == cls.FAHRENHEIT:
            value_ = (value_ - 273.15) * 1.8 + 32
        return value_


class Pressure(Unit):
    PA = "Pa"
    BAR = "bar"
    ATM = "atm"
    PSI = "psi"
    MMHG = "mmHg"
    TORR = "torr"
    PASCAL = PA
    ATMOSPHERE = ATM
    POUNDS_PER_SQUARE_INCH = PSI
    MILLIMETER_MERCURY = MMHG

    @classmethod
    @preserve_type
    def convert(
        cls,
        value: ConvertableTypes,
        source: str | Pressure = BAR,
        target: str | Pressure = PASCAL,
    ) -> ConvertableTypes:
        value_: npt.NDArray = cast("npt.NDArray", value)
        try:
            source = Pressure(source)
            target = Pressure(target)
        except ValueError as exc:
            err_msg = (
                "One unit or both units for source and / "
                "or target pressure are not valid."
            )
            logger.exception(err_msg, exc_info=exc)
            raise ValueError(err_msg) from exc
        if source == target:
            return value_
        # convert source to Pascal
        if source == cls.BAR:
            value_ = value_ * 1e5
        elif source == cls.ATMOSPHERE:
            value_ = value_ * 101_325
        elif source == cls.TORR:
            value_ = value_ * 101_325 / 760
        elif source == cls.MMHG:
            value_ = value_ * 101_325 / 760 * 1.000_000_142_466
        elif source == cls.PSI:
            value_ = value_ * 6_894.75728

        # convert from Pascal to target
        if target == cls.BAR:
            value_ = value_ / 1e5
        elif target == cls.ATMOSPHERE:
            value_ = value_ / 101_325
        elif target == cls.TORR:
            value_ = value_ / 101_325 * 760
        elif target == cls.MMHG:
            value_ = value_ / 101_325 * 760 / 1.000_000_142_466
        elif target == cls.PSI:
            value_ = value_ / 6_894.75728
        return value_
