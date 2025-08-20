#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for controlling a MBW 973 SF6 Analyzer over a serial connection.

The MBW 973 is a gas analyzer designed for gas insulated switchgear and measures
humidity, SF6 purity and SO2 contamination in one go.
Manufacturer homepage: https://www.mbw.ch/products/sf6-gas-analysis/973-sf6-analyzer/
"""

from .mbw973 import (  # noqa: F401
    MBW973,
    MBW973Config,
    MBW973ControlRunningError,
    MBW973Error,
    MBW973PumpRunningError,
    MBW973SerialCommunication,
    MBW973SerialCommunicationConfig,
)
