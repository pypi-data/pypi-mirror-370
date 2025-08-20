#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for the PFA-2 filter from Precision Filter Inc..

The PFA-2 filter is a high-precision, low-noise analog filter commonly used in
laboratory instrumentation and signal conditioning setups. It is suitable for
applications requiring clean signal output, such as spectroscopy, low-level
voltage measurements, signal recovery and high-resolution data acquisition.

The class PFA2Filter has been tested with a PFA-2 (with option H) unit.
Verify compatibility with your specific filter variant before use,
especially for units with custom or user-modified settings.

Product information and technical details:
https://pfinc.com/product/precision-pfa-2-filter-amplifier
"""

from .base import (  # noqa: F401
    Pfa2FilterChannelCoupling,
    Pfa2FilterChannelMode,
    Pfa2FilterHPFState,
    Pfa2FilterLPFMode,
    Pfa2FilterOverloadMode,
    Pfa2FilterPostGain,
    Pfa2FilterPreGain,
    Pfa2FilterSerialCommunication,
    Pfa2FilterSerialCommunicationConfig,
)
from .device import (  # noqa: F401
    Pfa2Filter,
)
