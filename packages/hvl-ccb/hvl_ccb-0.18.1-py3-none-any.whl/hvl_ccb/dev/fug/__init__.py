#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for "Probus V - ADDAT30" Interfaces which are used to control power
supplies from FuG Elektronik GmbH

This interface is used for many FuG power units.
Manufacturer homepage:
https://www.fug-elektronik.de

The Professional Series of Power Supplies from FuG is a series of low, medium and high
voltage direct current power supplies as well as capacitor chargers.
The class FuG is tested with a HCK 800-20 000 in Standard Mode.
The addressable mode is not implemented.
Check the code carefully before using it with other devices.
Manufacturer homepage:
https://www.fug-elektronik.de/netzgeraete/professional-series/

The documentation of the interface from the manufacturer can be found here:
https://www.fug-elektronik.de/wp-content/uploads/download/de/SOFTWARE/Probus_V.zip

The provided classes support the basic and some advanced commands.
The commands for calibrating the power supplies are not implemented, as they are only
for very special porpoises and should not used by "normal" customers.
"""

from .errors import FuGError  # noqa: F401
from .fug import FuG  # noqa: F401
