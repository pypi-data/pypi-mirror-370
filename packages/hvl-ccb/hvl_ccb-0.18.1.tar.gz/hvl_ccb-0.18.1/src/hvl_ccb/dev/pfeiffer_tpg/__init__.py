#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for Pfeiffer TPG controllers.

The Pfeiffer TPG control units are used to control Pfeiffer Compact Gauges.
Models: TPG 251 A, TPG 252 A, TPG 256A, TPG 261, TPG 262, TPG 361, TPG 362 and TPG 366.

Manufacturer homepage:
https://www.pfeiffer-vacuum.com/en/products/measurement-analysis/
measurement/activeline/controllers/
"""

from .pfeiffer_tpg import (  # noqa: F401
    PfeifferTPG,
    PfeifferTPGConfig,
    PfeifferTPGError,
    PfeifferTPGSerialCommunication,
    PfeifferTPGSerialCommunicationConfig,
)
