#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
This module establishes methods for interfacing with the Highland Technology T560-2
via its ethernet adapter with a TCP communication protocol.

The T560 is a small digital delay & pulse generator.
It outputs up to four individually timed pulses with 10-ps precision,
given an internal or external trigger.

This module introduces methods for configuring channels, gating, and triggering.
Further documentation and a more extensive command list may be obtained from:

https://www.highlandtechnology.com/DSS/T560DS.shtml
"""

from .base import (  # noqa: F401
    AutoInstallMode,
    GateMode,
    Polarity,
    T560Communication,
    T560CommunicationConfig,
    T560Error,
    TriggerMode,
)
from .device import T560, T560Config  # noqa: F401
