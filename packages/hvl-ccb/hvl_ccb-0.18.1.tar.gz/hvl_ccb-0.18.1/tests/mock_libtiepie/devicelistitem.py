#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock DeviceListItem
"""

import libtiepie as ltp
from libtiepie.devicelistitem import DeviceListItem as LtpDeviceListItem

from hvl_ccb.dev.tiepie import TiePieDeviceType
from mock_libtiepie.const import (  # MOCK_I2CHOST_SERIAL_NUMBER,
    MOCK_DEVICE_SERIAL_NUMBER,
    MOCK_GENERATOR_SERIAL_NUMBER,
    MOCK_OSCILLOSCOPE_SERIAL_NUMBER,
    MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2,
)

from .generator import Generator

# from .i2chost import I2CHost
from .oscilloscope import Oscilloscope
from .server import Server


class DeviceListItem(LtpDeviceListItem):
    """"""

    def __init__(self, serial_number) -> None:
        self._serial_number = serial_number
        self._oscilloscope = Oscilloscope(self._serial_number)
        self._generator = Generator(self._serial_number)
        # self._i2chost = I2CHost(self._serial_number)

    def open_device(self, device_type):
        """Open a device .

        :param device_type: A device type.
        :returns: Instance of :class:`.Oscilloscope`, :class:`.Generator` or
            :class:`.I2CHost`.
        """
        if device_type == ltp.DEVICETYPE_OSCILLOSCOPE:
            return self.open_oscilloscope()

        if device_type == ltp.DEVICETYPE_GENERATOR:
            return self.open_generator()

        # if device_type == ltp.DEVICETYPE_I2CHOST:
        #     return self.open_i2chost()

        return super().open_device(device_type)

    def open_oscilloscope(self):
        """Open an oscilloscope .
        :returns: Instance of :class:`.Oscilloscope`.
        """
        return self._oscilloscope

    def open_generator(self):
        """Open a generator .
        :returns: Instance of :class:`.Generator`.
        """
        return self._generator

    def open_i2chost(self):
        """Open an I2C host .
        :returns: Instance of :class:`.i2chost`.
        """
        return self._i2chost

    def can_open(self, device_type) -> bool:
        """Check whether the listed device can be opened.
        :param device_type: A device type.
        :returns: ``True`` if the device can be opened or ``False`` if not.
        """
        return (
            device_type is TiePieDeviceType.OSCILLOSCOPE.value
            and self._serial_number
            in (
                MOCK_DEVICE_SERIAL_NUMBER,
                MOCK_OSCILLOSCOPE_SERIAL_NUMBER,
                MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2,
            )
        ) or (
            device_type is TiePieDeviceType.GENERATOR.value
            and self._serial_number
            in (
                MOCK_DEVICE_SERIAL_NUMBER,
                MOCK_GENERATOR_SERIAL_NUMBER,
            )
        )

    def _get_name(self):
        """Full name."""
        return "Mocked name for device with serial number " + str(self._serial_number)

    def _get_has_server(self):
        """Check whether the listed device is connected to a server."""
        return True

    def _get_serial_number(self):
        """Serial number."""
        return self._serial_number

    def _get_server(self):
        """Server handle of the server the listed device is connected to."""
        return Server("127.0.0.1")

    def device_type_str(self):
        """Device types."""
        _str = ""
        if self._serial_number == (MOCK_DEVICE_SERIAL_NUMBER):
            _str = "Oscilloscope, Generator, I2CHost"
        if self._serial_number == (MOCK_OSCILLOSCOPE_SERIAL_NUMBER):
            _str = "Oscilloscope"
        if self._serial_number == (MOCK_GENERATOR_SERIAL_NUMBER):
            _str = "Generator"
        # if self._serial_number == (MOCK_I2CHOST_SERIAL_NUMBER):
        #     _str = "I2C Host"
        return _str

    def _get_types(self):
        return 1

    name = property(_get_name)
    has_server = property(_get_has_server)
    serial_number = property(_get_serial_number)
    server = property(_get_server)
    types = property(_get_types)
