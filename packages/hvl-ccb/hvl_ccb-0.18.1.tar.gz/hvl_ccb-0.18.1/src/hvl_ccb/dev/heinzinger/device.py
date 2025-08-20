#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for Heinzinger Digital Interface I/II and Heinzinger PNC power supply.

The Heinzinger Digital Interface I/II is used for many Heinzinger power units.
Interface Manual:
https://www.heinzinger.com/assets/uploads/downloads/Handbuch_DigitalInterface_2021-12-14-V1.6.pdf

The Heinzinger PNC series is a series of high voltage direct current power supplies.
The class Heinzinger is tested with different PNChp-types.
Check the code carefully before using it with other PNC devices, especially PNC3p
or PNCcap.
Manufacturer homepage:
https://www.heinzinger.com/en/products/pnc-serie
"""

import logging
import re
from time import sleep
from typing import cast

from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import SingleCommDevice
from hvl_ccb.dev.heinzinger.base import HeinzingerSerialCommunication
from hvl_ccb.dev.heinzinger.constants import (
    HeinzingerDeviceNotRecognizedError,
    HeinzingerSetValueError,
    RecordingsEnum,
)
from hvl_ccb.dev.heinzinger.mixin import DeprecatedHeinzingerMixin
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_bool, validate_number

logger = logging.getLogger(__name__)


@configdataclass
class HeinzingerConfig:
    """
    Device configuration dataclass for Heinzinger power supplies.
    """

    #: default number of recordings used in averaging the current
    #  or the voltage [1, 2, 4, 8, 16]
    default_number_of_recordings: int | RecordingsEnum = 1

    #: number of decimals sent for setting the current limit or the voltage, between 1
    #  and 10
    number_of_decimals: int = 6

    #: Time to wait after subsequent commands during stop (in seconds)
    wait_sec_stop_commands: Number = 0.5

    def clean_values(self) -> None:
        if not isinstance(self.default_number_of_recordings, RecordingsEnum):
            self.force_value(  # type: ignore[attr-defined]
                "default_number_of_recordings",
                RecordingsEnum(self.default_number_of_recordings),
            )

        if self.number_of_decimals not in range(1, 11):
            msg = "The number of decimals should be an integer between 1 and 10."
            raise ValueError(msg)

        if self.wait_sec_stop_commands <= 0:
            msg = (
                "Wait time after subsequent commands during stop must be be a "
                "positive value (in seconds)."
            )
            raise ValueError(msg)


class Heinzinger(SingleCommDevice, DeprecatedHeinzingerMixin):
    """
    Heinzinger power supply device class.
    The power supply is controlled over a Heinzinger Digital Interface I/II

    Sends basic SCPI commands and reads the answer.
    Only the standard instruction set from the manual is implemented.
    """

    def __init__(self, com, dev_config=None) -> None:
        # Call superclass constructor
        super().__init__(com, dev_config)

        # Version of the interface (will be retrieved after com is opened)
        self._interface_version = ""

        # Status of the voltage output (it has to be updated via the output = True and
        # output = False because querying it is not supported)
        self._output_status: bool | None = None

        # Serial number of the device (will be retrieved after com is opened)
        self._serial_number: str = ""
        # model of the device (derived from serial number)
        self._model: str = ""
        # maximum output current of the hardware (unit A)
        self._max_current_hardware: Number = 0
        # maximum output voltage of the hardware (unit V)
        self._max_voltage_hardware: Number = 0
        # maximum output current set by user (unit A)
        self._max_current: Number = 0
        # maximum output voltage set by user (unit V)
        self._max_voltage: Number = 0
        # the tolerance value for checking if the set voltage/current is correctly set
        self._epsilon: Number = 1e-3
        # identify voltage range, because unit is always V
        self._voltage_multiplier: Number = 0
        # identify current range, because unit is always A
        self._current_multiplier: Number = 0

    def __repr__(self) -> str:
        return (
            f"HeinzingerPNC({self._serial_number}), with "
            f"HeinzingerDI({self._interface_version})"
        )

    @staticmethod
    def default_com_cls() -> type[HeinzingerSerialCommunication]:
        return HeinzingerSerialCommunication

    @staticmethod
    def config_cls() -> type[HeinzingerConfig]:
        return HeinzingerConfig

    def start(self) -> None:
        """
        Opens the communication protocol and configures the device.

        :raises SerialCommunicationIOError: when communication port cannot be opened.
        """

        logger.info(f"Starting device {self}")
        super().start()

        self._interface_version = self.get_interface_version()

        # find out which type of source this is:
        self.identify_device()
        self.number_of_recordings = self.config.default_number_of_recordings

    def stop(self) -> None:
        """
        Stop the device. Closes also the communication protocol.
        """

        logger.info(f"Stopping device {self}")
        if not self.com.is_open:
            logger.warning(f"Device {self} already stopped")
        else:
            # set the voltage to zero
            self.voltage = 0
            sleep(self.config.wait_sec_stop_commands)
            # switch off the voltage output
            self.output = False
            sleep(self.config.wait_sec_stop_commands)
        super().stop()

    def identify_device(self) -> None:
        """
        Identify the device nominal voltage and current based on its serial number.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        serial_number = self.get_serial_number()
        # regex to find the model of the device
        regex_vc = r"(\d+)-(\d+)"  # voltage-current info
        regex_model = r"PNC.*?" + regex_vc + r"\s?[a-z]{3}"
        result = re.search(regex_model, serial_number)
        if result:
            self._serial_number = serial_number
            model = result.group()
            self._model = model
            # regex to find the nominal voltage and nominal current
            match = cast("re.Match", re.search(regex_vc, model))
            voltage = int(match.group(1))
            current = int(match.group(2))
            # the units of voltage (V) and current (A)
            self._max_voltage_hardware = voltage
            self._max_voltage = voltage
            self._max_current_hardware = current / 1000
            self._max_current = current / 1000
            if self._max_voltage_hardware < 100000:
                self._voltage_multiplier = 1.0
            else:
                self._voltage_multiplier = 1e3

            if self._max_current_hardware < 0.001:
                self._current_multiplier = 1e-6  # I_nenn < 1 mA
            elif self._max_current_hardware > 1:
                self._current_multiplier = 1.0  # I_nenn
            else:
                self._current_multiplier = 1e-3  # I_nenn >= 1 mA & < 1 A
            logger.info(f"Device {model} successfully identified")
        else:
            raise HeinzingerDeviceNotRecognizedError(serial_number)

    def reset_interface(self) -> None:
        """
        Reset of the digital interface; only Digital Interface I:
        Power supply is switched to the Local-Mode (Manual operation)

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        logger.info("Reset of the digital interface")
        self.com.write("*RST")

    def get_interface_version(self) -> str:
        """
        Queries the version number of the digital interface.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        version = self.com.query("VERS?")
        logger.info(f"The interface version of the Heinzinger: {version}")
        return version

    def get_serial_number(self) -> str:
        """
        Ask the device for its serial number and returns the answer as a string.

        :return: string containing the device serial number
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = self.com.query("*IDN?")
        logger.info(f"The identification string of the Heinzinger: {value}")
        return value

    @property
    def max_current_hardware(self) -> Number:
        """Maximal output current the hardware can provide in A"""
        return self._max_current_hardware

    @property
    def max_voltage_hardware(self) -> Number:
        """Maximal output voltage the hardware can provide in V"""
        return self._max_voltage_hardware

    @property
    def max_current(self) -> Number:
        """Maximal settable output current in A"""
        return self._max_current

    @max_current.setter
    def max_current(self, value: Number | None):
        """Maximal settable output current in A"""
        if value is None:
            # Reset the user-defined limit to the hardware limit
            self._max_current = self.max_current_hardware
            return
        validate_number(
            "max_current", value, (0, self.max_current_hardware), logger=logger
        )
        self._max_current = value

    @property
    def max_voltage(self) -> Number:
        """Maximal settable output voltage in V"""
        return self._max_voltage

    @max_voltage.setter
    def max_voltage(self, value: Number | None):
        """Maximal settable output voltage in V"""
        if value is None:
            # Reset the user-defined limit to the hardware limit
            self._max_voltage = self.max_voltage_hardware
            return
        validate_number(
            "max_voltage", value, (0, self.max_voltage_hardware), logger=logger
        )
        self._max_voltage = value

    @property
    def output(self) -> bool | None:
        """
        Switch DC voltage output on and updates the output status.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        return self._output_status

    @output.setter
    def output(self, value: bool) -> None:
        """
        Switch DC voltage output on or off and updates the output status.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises TypeError: if value is not a `bool`
        """
        validate_bool("Enable DC voltage output", value, logger)

        if value:
            self.com.write("OUTP ON")
            self._output_status = True
        else:
            self.com.write("OUTP OFF")
            self._output_status = False
        logger.info(f"DC voltage output is {'ON' if value else 'OFF'}")

    @property
    def number_of_recordings(self) -> int:
        """
        Queries the number of recordings the device is using for average value
        calculation.

        :return: int number of recordings
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = self.com.query("AVER?")
        logger.info(
            "the number of recordings the device is using for "
            f"average value calculation: {value}"
        )
        return int(value)

    @number_of_recordings.setter
    def number_of_recordings(self, value: int | RecordingsEnum) -> None:
        """
        Sets the number of recordings the device is using for average value
        calculation. The possible values are 1, 2, 4, 8 and 16.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = int(RecordingsEnum(value).value)
        # if the input is not 1, 2, 4, 8, or 16, RangeEnum picks a suitable one
        validate_number("number_of_recordings", value, (1, 16), int, logger=logger)
        self.com.write(f"AVER {value}")

    @property
    def voltage(self) -> Number:
        """
        Ask the Device to measure its output voltage and return the measurement
        result in V.

        :return: measured voltage as float in V
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = float(self.com.query("MEAS:VOLT?")) * self._voltage_multiplier
        logger.info(f"Output measured voltage of the Heinzinger PNC: {value} V")
        return value

    @voltage.setter
    def voltage(self, value: Number) -> None:
        """
        Sets the output voltage of the Heinzinger PNC to the given value in V.
        Same as set_voltage.setter

        :param value: voltage expressed in V
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises HeinzingerSetValueError: when the value was not set correctly
        """
        validate_number("voltage", value, (0, self.max_voltage), logger=logger)
        # value_input could be in kV or V depending on self._max_voltage_hardware
        value_command = value / self._voltage_multiplier
        self.com.write(f"VOLT {value_command:.{self.config.number_of_decimals}f}")
        # Validation:
        sleep(self.config.wait_sec_stop_commands)
        set_value = self.set_voltage
        if abs(value - set_value) > self._epsilon * self._max_voltage_hardware:
            msg = (
                f"Tried to set voltage = {value} V, "
                f"but the device did not take the value; the value is = {set_value} V"
            )
            logger.error(msg)
            raise HeinzingerSetValueError(msg)

        logger.info(f"Output voltage of the Heinzinger PNC is set to: {value} V")

    @property
    def set_voltage(self) -> Number:
        """
        Queries the set voltage of the Heinzinger PNC (not the measured voltage!) in V.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = float(self.com.query("VOLT?")) * self._voltage_multiplier
        logger.info(f"Output set voltage of the Heinzinger PNC: {value} V")
        return value

    @set_voltage.setter
    def set_voltage(self, value: Number) -> None:
        """
        Sets the output voltage of the Heinzinger PNC to the given value in V.
        Same as voltage.setter

        :param value: voltage expressed in V
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        self.voltage = value

    @property
    def current(self) -> Number:
        """
        Ask the Device to measure its output current and return the measurement
        result in A.

        :return: measured current as float
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = float(self.com.query("MEAS:CURR?")) * self._current_multiplier
        logger.info(f"Output measured current of the Heinzinger PNC: {value} A")
        return value

    @current.setter
    def current(self, value: Number) -> None:
        """
        Sets the output current of the Heinzinger PNC to the given value in A.
        Same as set_current.setter

        :param value: current expressed in A
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises HeinzingerSetValueError: when the value was not set correctly
        """
        validate_number("current", value, (0, self.max_current), logger=logger)
        # value_input could be in µA, mA, or A depending on self._max_current_hardware
        value_command = value / self._current_multiplier
        self.com.write(f"CURR {value_command:.{self.config.number_of_decimals}f}")
        # Validation:
        sleep(self.config.wait_sec_stop_commands)
        set_value = self.set_current
        if abs(value - set_value) > self._epsilon * self._max_current_hardware:
            msg = (
                f"Tried to set current = {value} A, "
                f"but the device did not take the value; the value is = {set_value} A"
            )
            logger.error(msg)
            raise HeinzingerSetValueError(msg)

        logger.info(f"Output current of the Heinzinger PNC is set to: {value} A")

    @property
    def set_current(self) -> Number:
        """
        Queries the set current of the Heinzinger PNC (not the measured current!) in A.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        value = float(self.com.query("CURR?")) * self._current_multiplier
        logger.info(f"Output set current of the Heinzinger PNC: {value} A")
        return value

    @set_current.setter
    def set_current(self, value: Number) -> None:
        """
        Sets the output current of the Heinzinger PNC to the given value in A.
        Same as current.setter

        :param value: current expressed in A
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        self.current = value
