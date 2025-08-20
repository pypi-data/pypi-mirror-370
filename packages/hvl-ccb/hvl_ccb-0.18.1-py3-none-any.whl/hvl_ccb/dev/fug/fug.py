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

import logging
import re
from typing import cast

from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import SingleCommDevice
from hvl_ccb.utils.typing import Number

from .comm import FuGSerialCommunication
from .constants import FuGDigitalVal, FuGProbusIVCommands
from .errors import FuGError, FuGErrorcodes
from .registers import (
    FuGProbusVConfigRegisters,
    FuGProbusVDIRegisters,
    FuGProbusVDORegisters,
    FuGProbusVMonitorRegisters,
    FuGProbusVRegisterGroups,
    FuGProbusVSetRegisters,
)

logger = logging.getLogger(__name__)


@configdataclass
class FuGConfig:
    """
    Device configuration dataclass for FuG power supplies.
    """


class FuGProbusIV(SingleCommDevice):
    """
    FuG Probus IV device class

    Sends basic SCPI commands and reads the answer.
    Only the special commands and PROBUS IV instruction set is implemented.
    """

    def __init__(self, com, dev_config=None) -> None:
        # Call superclass constructor
        super().__init__(com, dev_config)

        # Version of the interface (will be retrieved after com is opened)
        self._interface_version: str = ""

    def __repr__(self) -> str:
        return f"FuGProbus({self._interface_version})"

    @staticmethod
    def default_com_cls():
        return FuGSerialCommunication

    @staticmethod
    def config_cls():
        return FuGConfig

    def start(self) -> None:
        logger.info(f"Starting device {self}")
        super().start()

        self._interface_version = self.command(FuGProbusIVCommands.ID)  # type: ignore[arg-type]
        logger.info(f"Connection to {self._interface_version} established.")

    def stop(self) -> None:
        with self.com.access_lock:
            logger.info(f"Stopping device {self}")
            self.output_off()
            self.reset()
            super().stop()

    def command(self, command: FuGProbusIVCommands, value=None) -> str:
        """

        :param command: one of the commands given within FuGProbusIVCommands
        :param value: an optional value, depending on the command
        :return: a String if a query was performed
        """
        if not (
            (value is None and command.input_type is None)
            or isinstance(value, command.input_type)
        ):
            msg = (
                "Wrong value for data was given. Expected: "
                f"{command.input_type} and given: {value.__class__}"
            )
            raise FuGError(msg)

        # Differentiate between with and without optional value
        if command.input_type is None:
            answer = self.com.query(f"{command.command}")
        else:
            answer = self.com.query(f"{command.command}{value}")
        return cast("str", answer)  # for typing: query of fug never returns None

    # Special commands
    def reset(self) -> None:
        """
        Reset of the interface:
        All setvalues are set to zero
        """
        self.command(FuGProbusIVCommands.RESET)  # type: ignore[arg-type]

    def output_off(self) -> None:
        """
        Switch DC voltage output off.
        """
        self.command(
            FuGProbusIVCommands.OUTPUT,  # type: ignore[arg-type]
            FuGDigitalVal.OFF,
        )


class FuGProbusV(FuGProbusIV):
    """
    FuG Probus V class which uses register based commands to control the power supplies
    """

    def set_register(self, register: str, value: Number | str) -> None:
        """
        generic method to set value to register

        :param register: the name of the register to set the value
        :param value: which should be written to the register
        """

        self.com.query(f">{register} {value}")

    def get_register(self, register: str) -> str:
        """
        get the value from a register

        :param register: the register from which the value is requested
        :returns: the value of the register as a String
        """

        answer = cast("str", self.com.query(f">{register} ?")).split(":")
        # cast for typing: query of fug never returns None

        if answer[0] != register:
            cast("FuGErrorcodes", FuGErrorcodes.E505).raise_()

        return answer[1]


class FuG(FuGProbusV):
    """
    FuG power supply device class.

    The power supply is controlled over a FuG ADDA Interface with the PROBUS V protocol
    """

    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for configuring the power supply.

        :param com:
        :param dev_config:
        """

        # Call superclass constructor
        super().__init__(com, dev_config)

        self._id_string: str = ""
        """ID String of the device (will be retrieved after com is opened) contains
        Serial number and model"""

        # Serial number of the device (will be retrieved after com is opened)
        self._serial_number: str = ""
        # model class of the device (derived from serial number)
        self._model: str = ""
        # maximum output current of the hardware
        self._max_current_hardware: Number = 0
        # maximum output charging power of the hardware
        self._max_power_hardware: Number = 0
        # maximum output voltage of the hardware
        self._max_voltage_hardware: Number = 0

        self._voltage = FuGProbusVSetRegisters(
            self, FuGProbusVRegisterGroups("SETVOLTAGE")
        )
        self._current = FuGProbusVSetRegisters(
            self, FuGProbusVRegisterGroups("SETCURRENT")
        )
        self._out_x0 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX0"))
        self._out_x1 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX1"))
        self._out_x2 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX2"))
        self._out_xcmd = FuGProbusVDORegisters(
            self, FuGProbusVRegisterGroups("OUTPUTXCMD")
        )
        self._output = FuGProbusVDORegisters(
            self, FuGProbusVRegisterGroups("OUTPUTONCMD")
        )
        self._voltage_monitor = FuGProbusVMonitorRegisters(
            self, FuGProbusVRegisterGroups("MONITOR_V")
        )
        self._current_monitor = FuGProbusVMonitorRegisters(
            self, FuGProbusVRegisterGroups("MONITOR_I")
        )
        self._di = FuGProbusVDIRegisters(self, FuGProbusVRegisterGroups("INPUT"))
        self._config_status = FuGProbusVConfigRegisters(
            self, FuGProbusVRegisterGroups("CONFIG")
        )

    def __repr__(self) -> str:
        return f"{self._id_string}"

    def start(self, max_voltage=0, max_current=0) -> None:
        """
        Opens the communication protocol and configures the device.

        :param max_voltage: Configure here the maximal permissible voltage which is
            allowed in the given experimental setup
        :param max_current: Configure here the maximal permissible current which is
            allowed in the given experimental setup
        """

        # starting FuG Probus Interface
        super().start()

        self._voltage._max_setvalue = max_voltage
        self._current._max_setvalue = max_current

        # find out which type of source this is:
        self.identify_device()

    @property
    def voltage(self) -> Number:
        """
        Return the measured output voltage in V
        """
        return self.voltage_monitor.value

    @voltage.setter
    def voltage(self, value: Number) -> None:
        """
        Set the output voltage in V

        :param value: voltage in V
        """
        self._voltage.setvalue = value

    @property
    def current(self) -> Number:
        """
        Return the measured output current in A
        """
        return self.current_monitor.value

    @current.setter
    def current(self, value: Number) -> None:
        """
        Set the output current

        :param value: Current in A
        """
        self._current.setvalue = value

    @property
    def set_voltage(self) -> Number:
        """
        Return the set voltage (may differ from actual voltage) in V
        """
        return self._voltage.setvalue

    @set_voltage.setter
    def set_voltage(self, value: Number) -> None:
        """Set the output voltage"""
        self.voltage = value

    @property
    def set_current(self) -> Number:
        """Return the set current (may differ from actual value) in A"""
        return self._current.setvalue

    @set_current.setter
    def set_current(self, value: Number) -> None:
        """Set the output current"""
        self.current = value

    @property
    def max_voltage(self) -> Number:
        """
        Returns the maximal voltage which could provided within the test setup

        :return: max voltage in V
        """
        return self._voltage._max_setvalue

    @property
    def max_voltage_hardware(self) -> Number:
        """
        Returns the maximal voltage which could provided with the power supply

        :return:
        """
        return self._max_voltage_hardware

    @property
    def max_current(self) -> Number:
        """
        Returns the maximal current which could provided within the test setup

        :return: max current in A
        """
        return self._current._max_setvalue

    @property
    def max_current_hardware(self) -> Number:
        """
        Returns the maximal current which could provided with the power supply

        :return:
        """
        return self._max_current_hardware

    # Output stage
    @property
    def output(self) -> bool | None:
        """State of the high voltage output"""
        return self._output.status == FuGDigitalVal.ON

    @output.setter
    def output(self, value: bool) -> None:
        """
        Activates the output of the source

        :param value: `True` for activation, `False` for deactivation
        """
        self._output.out = FuGDigitalVal.ON if value else FuGDigitalVal.OFF

    # Utility Registers (Not implementing `Source`-protocol)
    @property
    def voltage_register(self) -> FuGProbusVSetRegisters:
        """
        Returns the registers for the voltage output
        """
        return self._voltage

    @property
    def current_register(self) -> FuGProbusVSetRegisters:
        """
        Returns the registers for the current output
        """
        return self._current

    @property
    def out_x0(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X0

        :return: FuGProbusVDORegisters
        """
        return self._out_x0

    @property
    def out_x1(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X1

        :return: FuGProbusVDORegisters
        """
        return self._out_x1

    @property
    def out_x2(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X2

        :return: FuGProbusVDORegisters
        """
        return self._out_x2

    @property
    def out_xcmd(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital outputX-CMD

        :return: FuGProbusVDORegisters
        """
        return self._out_xcmd

    @property
    def output_register(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the output switch to turn the output on or off

        :return: FuGProbusVDORegisters
        """
        return self._output

    @property
    def voltage_monitor(self) -> FuGProbusVMonitorRegisters:
        """
        Returns the registers for the voltage monitor.

        A typically usage will be "self.voltage_monitor.value" to measure the output
        voltage

        :return:
        """
        return self._voltage_monitor

    @property
    def current_monitor(self) -> FuGProbusVMonitorRegisters:
        """
        Returns the registers for the current monitor.

        A typically usage will be "self.current_monitor.value" to measure the output
        current

        :return:
        """
        return self._current_monitor

    @property
    def di(self) -> FuGProbusVDIRegisters:
        """
        Returns the registers for the digital inputs

        :return: FuGProbusVDIRegisters
        """
        return self._di

    @property
    def config_status(self) -> FuGProbusVConfigRegisters:
        """
        Returns the registers for the registers with the configuration and status values

        :return: FuGProbusVConfigRegisters
        """
        return self._config_status

    def identify_device(self) -> None:
        """
        Identify the device nominal voltage and current based on its model number.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        id_string = str(self.command(FuGProbusIVCommands("ID")))
        # "'FUG HCK
        # 800
        # - 20 000
        # MOD 17022-01-01'"
        # regex to find the model of the device
        regex_model = (
            "FUG (?P<model>[A-Z]{3})"
            " (?P<power>[0-9 ]+)"
            " - (?P<voltage>[0-9 ]+)"
            " MOD (?P<sn>[0-9-]+)"
        )

        result = re.search(regex_model, id_string)
        if not result:
            msg = (
                f'The device with the ID string "{id_string}" could not be recognized.'
            )
            raise FuGError(msg)

        self._id_string = id_string
        results = result.groupdict()
        self._model = str(results.get("model"))
        self._max_power_hardware = int(results.get("power").replace(" ", ""))  # type: ignore[union-attr]
        self._max_voltage_hardware = int(results.get("voltage").replace(" ", ""))  # type: ignore[union-attr]
        self._max_current_hardware = (
            2 * self._max_power_hardware / self._max_voltage_hardware
        )
        self._serial_number = str(results.get("sn"))

        logger.info(f"Device {id_string} successfully identified:")
        logger.info(f"Model class: {self._model}")
        logger.info(f"Maximal voltage: {self._max_voltage_hardware} V")
        logger.info(f"Maximal current: {self._max_current_hardware} A")
        logger.info(f"Maximal charging power: {self._max_power_hardware} J/s")
        logger.info(f"Serial number: {self._serial_number}")

        # if limits for test setup were not predefined, set them to hardware limits
        # or if the previous limits were to high, limit them to the hardware limits
        if self.max_voltage == 0:
            self._voltage._max_setvalue = self.max_voltage_hardware
        elif self.max_voltage > self.max_voltage_hardware:
            logger.warning(
                "FuG power source should supply up to "
                f"{self.max_voltage} V, but the hardware only goes up "
                f"to {self.max_voltage_hardware} V."
            )
            self._voltage._max_setvalue = self.max_voltage_hardware
        logger.info(
            "For this setup the maximal output voltage of the power "
            f"supply is limited to {self.max_voltage} V."
        )

        if self.max_current == 0:
            self._current._max_setvalue = self.max_current_hardware
        elif self.max_current > self.max_current_hardware:
            logger.warning(
                "FuG power source should supply up to "
                f"{self.max_current} A, but the hardware only goes up "
                f"to {self.max_current_hardware} A."
            )
            self._current._max_setvalue = self.max_current_hardware
        logger.info(
            "For this setup the maximal output current of the power "
            f"supply is limited to {self.max_current} A."
        )
