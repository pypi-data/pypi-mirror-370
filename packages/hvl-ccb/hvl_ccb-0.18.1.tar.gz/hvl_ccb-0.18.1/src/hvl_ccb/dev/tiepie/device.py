#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
TiePie devices.
"""

import logging

from .generator import TiePieGeneratorMixin

# from .i2c import TiePieI2CHostMixin
from .oscilloscope import TiePieOscilloscope

logger = logging.getLogger(__name__)


# class TiePieWS5(TiePieI2CHostMixin, TiePieGeneratorMixin, TiePieOscilloscope):
class TiePieWS5(TiePieGeneratorMixin, TiePieOscilloscope):
    """
    TiePie WS5 device.
    """


# class TiePieHS5(TiePieI2CHostMixin, TiePieGeneratorMixin, TiePieOscilloscope):
class TiePieHS5(TiePieGeneratorMixin, TiePieOscilloscope):
    """
    TiePie HS5 device.
    """


class TiePieHS6(TiePieOscilloscope):
    """
    TiePie HS6 DIFF device.
    """
