#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mixin class for Heinzinger's deprecated methods.Raise DeprecationWarning, will be
removed in the next release
"""

import logging

logger = logging.getLogger(__name__)


class DeprecatedHeinzingerMixin:
    @staticmethod
    def output_on() -> None:
        msg = (
            "output_on will be deprecated in the next release; "
            "use property instead: device.output = True"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)

    @staticmethod
    def output_off() -> None:
        msg = (
            "output_off will be deprecated in the next release; "
            "use property instead: device.output = False"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)

    @staticmethod
    def get_number_of_recordings() -> None:
        msg = (
            "get_number_of_recordings will be deprecated in the next release; "
            "use property instead: device.number_of_recordings"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)

    @staticmethod
    def set_number_of_recordings() -> None:
        msg = (
            "set_number_of_recordings will be deprecated in the next release; "
            "use property instead: device.number_of_recordings = value"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)

    @staticmethod
    def measure_voltage() -> None:
        msg = (
            "measure_voltage will be deprecated in the next release; "
            "use property instead: device.voltage"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)

    @staticmethod
    def measure_current() -> None:
        msg = (
            "measure_current will be deprecated in the next release; "
            "use property instead: device.current"
        )
        logger.error(msg)
        raise DeprecationWarning(msg)
