#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
DC Laboratory Power Supply Unit "Korad KA3000P"

Interface for the power supply units of "Korad" and their "KA3000P"-series.
This package was developed and tested with "Korad KA3005P".
It might also work with other devices like the ones of the "Korad KA6000P"-series.
"""

from .base import KA3000PError as KA3000PError
from .device import KA3000P as KA3000P
