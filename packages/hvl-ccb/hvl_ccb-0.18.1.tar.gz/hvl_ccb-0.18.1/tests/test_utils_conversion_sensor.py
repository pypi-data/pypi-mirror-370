#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for Sensor Conversion Utils
"""

import numpy as np
import pytest

from hvl_ccb.utils.conversion import LEM4000S, LMT70A
from hvl_ccb.utils.conversion.utils import GetAttr, SetAttr


def test_lem4000s() -> None:
    lem = LEM4000S()
    assert lem.shunt == 1.2
    lem.shunt = 2
    assert lem.shunt == 2
    with pytest.raises(ValueError):
        lem.shunt = -1
    with pytest.raises(AttributeError):
        lem.CONVERSION = 1
    with pytest.raises(ValueError):
        lem.calibration_factor = 1.5
    lem.shunt = 1.2
    assert lem.convert(1.2) == 5000
    lem.calibration_factor = 1.05
    assert lem.convert(1.2) == 5250
    lem.calibration_factor = -1.05
    assert lem.convert(1.2) == -5250


def test_lmt70a() -> None:
    lmt = LMT70A()
    with pytest.raises(AttributeError):
        lmt.LUT = 1
    with pytest.raises(ValueError):
        lmt.temperature_unit = "R"
    assert lmt.convert(0.943227) == 30
    assert np.isnan(lmt.convert(0.3))


def test_set_attr() -> None:
    class Helper:
        help_attr_1 = SetAttr(0, "help_attr_1", (0, 10), validator=LEM4000S)
        help_attr_2 = GetAttr(10, "help_attr_2")

    a = Helper()
    assert a.help_attr_1 == 0
    with pytest.raises(NotImplementedError):
        a.help_attr_1 = 1

    assert type(Helper.help_attr_2) is GetAttr
