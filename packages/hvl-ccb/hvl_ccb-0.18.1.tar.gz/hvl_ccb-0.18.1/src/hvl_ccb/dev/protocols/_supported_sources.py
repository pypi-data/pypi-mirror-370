#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
This file is only for type checking, that the `Source`-protocol is fulfilled.
"""

from hvl_ccb.dev.fug import FuG
from hvl_ccb.dev.heinzinger import Heinzinger
from hvl_ccb.dev.ka3000p import KA3000P
from hvl_ccb.dev.technix import Technix

from . import Source

my_source: Source = Heinzinger({})
my_source = Technix({}, {})
my_source = FuG({})
my_source = KA3000P({})
