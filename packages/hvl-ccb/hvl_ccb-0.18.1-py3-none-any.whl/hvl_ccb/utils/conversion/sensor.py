#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

"""
Sensors that are used by the devices implemented in the CCB
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import cast

import numpy as np
import numpy.typing as npt

from hvl_ccb.utils.typing import ConvertableTypes
from hvl_ccb.utils.validation import validate_number

from .unit import Temperature
from .utils import GetAttr, SetAttr, convert_value_to_str, preserve_type

logger = logging.getLogger(__name__)


class Sensor(ABC):
    @abstractmethod
    @preserve_type
    def convert(self, value: ConvertableTypes) -> ConvertableTypes:
        pass  # pragma: no cover


@dataclass
class LEM4000S(Sensor):
    CONVERSION = GetAttr(5000, "CONVERSION")
    shunt = SetAttr(1.2, "shunt", limits=(1e-6, None), validator=validate_number)
    calibration_factor = SetAttr(
        1,
        "calibration_factor",
        limits=(0.9, 1.1),
        absolut=True,
        validator=validate_number,
    )

    @preserve_type
    def convert(self, value: ConvertableTypes) -> ConvertableTypes:
        value = cast("npt.NDArray", value)
        conversion = cast("int", self.CONVERSION) * cast(
            "float", self.calibration_factor
        )
        value_ret = value / self.shunt * conversion
        value_str, value_ret_str = convert_value_to_str(value, value_ret)
        logger.info(
            f"LEM400S: Convert a secondary current of {value_str} A to a "
            f"primary current of {value_ret_str} A."
        )
        return value_ret


@dataclass
class LMT70A(Sensor):
    """
    Converts the output voltage (V) to the measured temperature (default °C)
    when using a TI Precision Analog Temperature Sensor LMT70(A)

    """

    temperature_unit = SetAttr(
        Temperature.CELSIUS, "temperature_unit", limits=None, validator=Temperature
    )

    # look up table from datasheet
    # first column: temperature in degree celsius
    # second column: voltage in volt
    # https://www.ti.com/lit/ds/symlink/lmt70a.pdf?ts=1631590373860
    LUT = GetAttr(
        np.array(
            [
                [-55.0, 1.375219],
                [-50.0, 1.350441],
                [-40.0, 1.300593],
                [-30.0, 1.250398],
                [-20.0, 1.199884],
                [-10.0, 1.14907],
                [0.0, 1.097987],
                [10.0, 1.046647],
                [20.0, 0.99505],
                [30.0, 0.943227],
                [40.0, 0.891178],
                [50.0, 0.838882],
                [60.0, 0.78636],
                [70.0, 0.733608],
                [80.0, 0.680654],
                [90.0, 0.62749],
                [100.0, 0.574117],
                [110.0, 0.520551],
                [120.0, 0.46676],
                [130.0, 0.412739],
                [140.0, 0.358164],
                [150.0, 0.302785],
            ]
        ),
        "LUT",
    )

    @preserve_type
    def convert(self, value: ConvertableTypes) -> ConvertableTypes:
        """
        NaN is returned for values that are not covered by the look up table
        :param value: output voltage of the sensor.
        :raise TypeError: for non convertable data types
        :return: measured temperature (default °C)
        """
        # cast necessary because of wrapper, which changes the type of value
        value = cast("npt.NDArray", value)
        try:
            validate_number(
                "value",
                value,
                (
                    cast("npt.NDArray", self.LUT)[-1, 1],
                    cast("npt.NDArray", self.LUT)[0, 1],
                ),
                logger=logger,
            )
        except ValueError:
            mask = np.any(
                [
                    value < cast("npt.NDArray", self.LUT)[-1, 1],
                    value > cast("npt.NDArray", self.LUT)[0, 1],
                ],
                axis=0,
            )
            value[mask] = np.nan
        logger.info(
            "LMT70A: Use linear interpolation of lookup table provided "
            "in datasheet of LMT70A"
        )
        value_ret = np.interp(
            value,
            cast("npt.NDArray", self.LUT)[::-1, 1],
            cast("npt.NDArray", self.LUT)[::-1, 0],
        )
        value_ret = Temperature.convert(
            value_ret, source=Temperature.CELSIUS, target=self.temperature_unit
        )
        value_str, value_ret_str = convert_value_to_str(value, value_ret)
        logger.info(
            f"LMT70A: Convert a voltage of {value_str} V to "
            f"a temperature of {value_ret_str} "
            f"{cast('Temperature', self.temperature_unit).name}."
        )
        return value_ret
