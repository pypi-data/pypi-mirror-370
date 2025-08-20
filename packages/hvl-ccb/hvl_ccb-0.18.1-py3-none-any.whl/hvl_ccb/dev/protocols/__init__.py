#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
This module has some common protocols to interface similar device with the same
methods. The benefit is to be able to switch between different devices with less
effort of change the code and also to keep the same "look-and-feel".
"""

from .sources import Source  # noqa: F401
