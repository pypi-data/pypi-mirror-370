#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for a SST Luminox Oxygen sensor. This device can measure the oxygen
concentration between 0 % and 25 %.

Furthermore, it measures the barometric pressure and internal temperature.
The device supports two operating modes: in streaming mode the device measures all
parameters every second, in polling mode the device measures only after a query.

Technical specification and documentation for the device can be found a the
manufacturer's page:
https://www.sstsensing.com/product/luminox-optical-oxygen-sensors-2/
"""

from .sst_luminox import (  # noqa: F401
    Luminox,
    LuminoxConfig,
    LuminoxMeasurementType,
    LuminoxMeasurementTypeError,
    LuminoxOutputMode,
    LuminoxOutputModeError,
    LuminoxSerialCommunication,
    LuminoxSerialCommunicationConfig,
)
