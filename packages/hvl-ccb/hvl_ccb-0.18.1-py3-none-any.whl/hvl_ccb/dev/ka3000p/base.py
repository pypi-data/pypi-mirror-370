#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

import logging
from typing import NamedTuple

from bitstring import BitArray

from hvl_ccb.dev.base import DeviceError
from hvl_ccb.utils.enum import NameEnum
from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


class KA3000PError(DeviceError):
    """KA3000P related errors."""


class KA3000PTracking(NameEnum):
    SINGLE = 0
    INDEPENDENT = 1
    PARALLEL = 2
    SERIAL = 3


class KA3000PStatus(NamedTuple):
    ch1_cv: bool
    ch2_cv: bool
    tracking: KA3000PTracking
    beep: bool
    ocp: bool
    output: bool
    ovp: bool


def _gen_status(stb_qry: int) -> KA3000PStatus:
    """Converts a sinlge byte into the `KA3000PStatus`

    :param stb_qry: status as single byte
    :return: Status of KA3000P
    """
    validate_number("stb_qry", stb_qry, (0, 255), int, logger=logger)
    stb = BitArray(uint=stb_qry, length=8)
    stb.reverse()
    ch1_cv = bool(stb[0])
    ch2_cv = bool(stb[1])
    tracking = KA3000PTracking(stb[2:4].uint)
    beep = bool(stb[4])
    ocp = bool(stb[5])
    output = bool(stb[6])
    ovp = bool(stb[7])

    return KA3000PStatus(ch1_cv, ch2_cv, tracking, beep, ocp, output, ovp)
