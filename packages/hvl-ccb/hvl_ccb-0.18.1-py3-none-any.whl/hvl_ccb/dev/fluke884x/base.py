#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Python module for the Fluke8845a Multimeter.
The communication to the device is through TCP.
8845A/8846A Programmers Manual is available in the following link.
All page numbers mentioned in this script refer to this manual.
https://download.flukecal.com/pub/literature/8845A___pmeng0300.pdf
"""

import logging
from typing import cast

from hvl_ccb.comm import SyncCommunicationProtocol
from hvl_ccb.comm.tcp import TcpCommunication, TcpCommunicationConfig
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev import SingleCommDevice
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

from .constants import (
    Fluke8845aCheckError,
    Fluke8845aError,
    Fluke8845aUnknownCommandError,
    MeasurementFunction,
    TriggerSource,
    _ApertureDescriptor,
    _FilterDescriptor,
    _RangeDescriptor,
)

logger = logging.getLogger(__name__)


@configdataclass
class Fluke8845aCommunicationConfig(TcpCommunicationConfig):
    #: Port at which Fluke 8845a is listening
    port: int = 3490
    #: The terminator is CR
    terminator: bytes = b"\r"


class Fluke8845aCommunication(TcpCommunication, SyncCommunicationProtocol):
    @staticmethod
    def config_cls():
        return Fluke8845aCommunicationConfig

    def query(
        self,
        command: str,
        n_attempts_max: int | None = None,
        attempt_interval_sec: Number | None = None,
    ) -> str:
        """
        Send a command to the interface and handle the status message.
        Eventually raises an error.

        :param command: Command to send
        :param n_attempts_max: Amount of attempts how often a non-empty text is tried to
            be read as answer
        :param attempt_interval_sec: time between the reading attempts
        :raises Fluke8845aError: if the connection is broken
        :return: Answer from the interface
        """

        with self.access_lock:
            logger.debug(f"Fluke8845aCommunication, send: '{command}'")
            answer: str | None = super().query(
                command,
                n_attempts_max=n_attempts_max,
                attempt_interval_sec=attempt_interval_sec,
            )  # string or None
            logger.debug(f"Fluke8845aCommunication, receive: '{answer}'")
            if answer is None:
                msg = (
                    f"Fluke8845aCommunication did get no answer on command: '{command}'"
                )
                logger.error(msg)
                raise Fluke8845aError(msg)
            return answer


@configdataclass
class Fluke8845aConfig:
    """
    Config for Fluke8845a

    name: the name of the device
    """

    name: str = "Fluke 1"


class Fluke8845a(SingleCommDevice):
    """
    Device class to control Fluke8845a
    """

    DISPLAY_MAX_LENGTH = 12

    def __init__(self, com, dev_config=None) -> None:
        # Call superclass constructor
        super().__init__(com, dev_config)
        logger.debug(f"{self} {self.config.name} initialised.")

    def __str__(self) -> str:
        return "Fluke8845a"

    @staticmethod
    def default_com_cls() -> type[Fluke8845aCommunication]:
        return Fluke8845aCommunication

    @staticmethod
    def config_cls() -> type[Fluke8845aConfig]:
        return Fluke8845aConfig

    def start(self) -> None:
        """
        Start this device as recommended by the manual
        """

        logger.info(f"Starting device: {self} {self.config.name}")
        # try opening the port
        super().start()
        self.activate_remote_mode()
        self.reset()
        self.clear_error_queue()
        logger.info(f"Device {self} {self.config.name} started successfully")

    def stop(self) -> None:
        """
        Stop this device. Disables access and closes the communication protocol.
        """

        logger.info(f"Stopping device: {self} {self.config.name}")
        super().stop()
        logger.info(f"Device {self} {self.config.name} stopped successfully")

    def activate_remote_mode(self) -> None:
        """
        Page 66

        Places the Meter in the remote mode for RS-232 or Ethernet remote
        control. All front-panel keys, except the local key, are disabled.
        """

        logger.debug("Enable remote mode")
        self.com.write("SYST:REM")

    def reset(self) -> None:
        """
        Page 60

        resets the meter to its power-up configuration
        """

        logger.debug("Resets the meter to power-up configuration")
        self.com.write("*RST")

    def clear_error_queue(self) -> None:
        """
        Page 62

        Sets all bits to zero in the Meter's status byte register and all event
        registers. Also clears the error queue
        """

        logger.debug("Clear the error queue")
        self.com.write("*CLS")

    @property
    def identification(self) -> str:
        """
        Page 60

        Queries `"*IDN?"` and returns the identification string of the connected device.

        :return: the identification string of the connected device
            e.g. `"FLUKE, 8845A, 2540017, 08/02/10-11:53"`
        """

        value = self.com.query("*IDN?")
        logger.info(f"The identification string of the Fluke 8845a: {value}")
        return value

    def initiate_trigger(self) -> None:
        """
        Set trigger system to wait-for-trigger
        """

        logger.debug("Set trigger system to wait-for-trigger")
        self.com.write("INIT")

    def trigger(self) -> None:
        """
        Causes the meter to trigger a measurement when paused
        """

        logger.debug("Causes the meter to trigger a measurement when paused")
        self.com.write("*TRG")

    def fetch(self) -> float:
        """
        Page 36

        Transfer stored readings to output buffer
        """

        logger.debug("Transfer stored readings to output buffer")
        return float(self.com.query("FETC?"))

    def measure(self) -> float:
        """
        Page 42

        Taking measurement

        Once the Meter has been configured for a measurement, the INITiate command
        causes the Meter to take a measurement when the trigger condition have been met.
        To process readings from the Meter's internal memory to the output buffer, send
        the Meter a FETCh? command.
        """

        self.initiate_trigger()
        self.trigger()
        measurement_unit = self.measurement_function._range().unit()
        measure_value = self.fetch()
        logger.info(f"measured value {measure_value} {measurement_unit}")
        return measure_value

    @property
    def measurement_function(self) -> MeasurementFunction:
        """
        input_function getter, query what the input function is

        :raises Fluke8845aUnknownCommandError: if the input function is unknown
        """

        # When query "FUNC?", return example '"CURR"'
        # use strip to remove the quotation mark
        measurement_function = self.com.query("FUNC?").strip('"')
        try:
            return MeasurementFunction(measurement_function)
        except ValueError as exc:
            msg = (
                f"Function '{measurement_function}' "
                "not yet implemented or not a valid function."
            )
            logger.exception(msg)
            raise Fluke8845aUnknownCommandError(msg) from exc

    @measurement_function.setter
    def measurement_function(self, input_function: str | MeasurementFunction):
        """
        input_funtion setter, set the input function

        :param input_function: string or MeasurementFunction Enum,
            for example: "CURR", "PER", or MeasurementFunction.CURRENT_AC...
        :raises Fluke8845aUnknownCommandError: if the input function is unknown
        :raises Fluke8845aCheckError: if setting failed
        """

        try:
            input_function = MeasurementFunction(input_function)
        except ValueError as exc:
            msg = (
                "Fluke function not yet implemented; "
                f"Possible functions are {list(MeasurementFunction)}"
            )
            logger.exception(msg, exc_info=exc)
            raise Fluke8845aUnknownCommandError(msg) from exc
        self.com.write(f"CONF:{input_function}")
        function = self.measurement_function
        if function == input_function:
            logger.info(f"Input function is successfully set to '{input_function}'")
        else:
            msg = (
                "Input function setting failed: "
                f"should be '{input_function}' but is now '{function}'"
            )
            logger.error(msg)
            raise Fluke8845aCheckError(msg)

    @property
    def trigger_source(self) -> TriggerSource:
        """
        input_trigger_source getter, query what the input trigger source is

        :raise Fluke8845aUnknownCommandError: if the input trigger source is unknown
        """

        input_trigger_source_checked = self.com.query("TRIG:SOUR?")
        try:
            return TriggerSource(input_trigger_source_checked)
        except ValueError as exc:
            msg = f"Fluke trigger source not valid: '{input_trigger_source_checked}'"
            logger.exception(msg, exc_info=exc)
            raise Fluke8845aUnknownCommandError(msg) from exc

    @trigger_source.setter
    def trigger_source(self, input_trigger_source: str | TriggerSource):
        """
        Page 57

        input_trigger_source setter, set the input trigger source

        :param input_trigger_source: string or TriggerSource Enum,
        :raises Fluke8845aUnknownCommandError: if the input trigger source is unknown
        :raises Fluke8845aCheckError: if setting failed
        """

        try:
            input_trigger_source = TriggerSource(input_trigger_source)
        except ValueError as exc:
            msg = (
                f"Unknown trigger source; Possible functions are {list(TriggerSource)}"
            )
            logger.exception(msg, exc_info=exc)
            raise Fluke8845aUnknownCommandError(msg) from exc

        self.com.write(f"TRIG:SOUR {input_trigger_source}")
        trigger_source = self.trigger_source
        if trigger_source == input_trigger_source:
            logger.info(
                f"input trigger source is successfully set to '{input_trigger_source}'"
            )
        else:
            msg = (
                "input trigger source setting failed: "
                f"should be '{input_trigger_source}' but is now '{trigger_source}'"
            )
            logger.error(msg)
            raise Fluke8845aCheckError(msg)

    @property
    def trigger_delay(self) -> int:
        """
        input_trigger_delay getter, query what the input trigger delay is in second
        answer format from Fluke: string, '+1.00000000E+00', so convert to float
        and then to int

        :return: input trigger delay in second
        """

        trigger_delay = int(float(self.com.query("TRIG:DEL?")))
        logger.info(f"Trigger delay is set to {trigger_delay}s")
        return trigger_delay

    @trigger_delay.setter
    def trigger_delay(self, input_trigger_delay: int):
        """
        Page 57

        input_trigger_delay setter, sets the delay between receiving a trigger and the
        beginning of measurement cycle
        input_trigger_delay should be between 0 and 3600 seconds

        :param input_trigger_delay: int, input trigger delay in second
        :raises Fluke8845aCheckError: if setting failed
        """

        validate_number(
            "input trigger delay", input_trigger_delay, (0, 3600), int, logger=logger
        )
        self.com.write(f"TRIG:DEL {input_trigger_delay}")
        trigger_delay = self.trigger_delay
        if trigger_delay == input_trigger_delay:
            logger.info(
                f"input trigger delay is successfully set to {input_trigger_delay}s"
            )
        else:
            msg = (
                "input trigger delay setting failed: "
                f"should be {input_trigger_delay}s but is now {trigger_delay}s"
            )
            logger.error(msg)
            raise Fluke8845aCheckError(msg)

    @property
    def display_enable(self) -> bool:
        """
        Page 59

        get if the display is enabled or not
        fluke answer string "1" for ON and "0" for off
        bool(int("1")) = 1 and bool(int("0")) = 0

        :return: bool enabled = True, else False
        """

        display_enable = bool(int(self.com.query("DISP?")))
        status = "ON" if display_enable else "OFF"
        logger.info(f"Display is {status}")
        return display_enable

    @display_enable.setter
    def display_enable(self, display_enable: bool):
        """
        Page 59

        Enables or disables the Meter's display.

        :param display_enable: bool, enable display or not
        :raises Fluke8845aCheckError: if setting failed
        """

        status = "ON" if display_enable else "OFF"
        self.com.write(f"DISP {status}")
        if bool(int(self.com.query("DISP?"))) == display_enable:
            logger.info(f"Display is successfully switched {status}")
        else:
            msg = f"Display could not be switched {status}"
            logger.error(msg)
            raise Fluke8845aCheckError(msg)

    def clear_display_message(self) -> None:
        """
        Page 59

        Clears the displayed message on the Meter's display.
        """

        self.com.write("DISP:TEXT:CLE")
        logger.info("Clear message from display")

    @property
    def display_message(self) -> str:
        """
        Page 59

        Retrieves the text sent to the Meter's display.
        """

        display_message = self.com.query("DISP:TEXT?")
        logger.info(f"Display message is {display_message}")
        return display_message

    @display_message.setter
    def display_message(self, display_message: str):
        """
        Page 59

        Displays a message on the Meter's display. The Meter must be remote before
        executing this command. Display string is up to 12 characters. Additional
        characters are truncated. Quotation mark is needed when sending displayed string

        :param display_message: message as string to display up to 12 characters
        :raises Fluke8845aCheckError: if setting failed
        """

        if len(display_message) > self.DISPLAY_MAX_LENGTH:
            display_message = display_message[: self.DISPLAY_MAX_LENGTH]
            logger.warning(
                f"Desired message has {len(display_message)} characters; "
                f"only the first {self.DISPLAY_MAX_LENGTH} is displayed; "
                "additional characters are truncated."
                f"The displayed text is '{display_message}'"
            )
        #  fluke display example: DISP:TEXT "hello", quotation mark is needed
        self.com.write(f'DISP:TEXT "{display_message}"')
        if self.com.query("DISP:TEXT?") == f'"{display_message}"':
            logger.info(f'The text "{display_message}" is displayed successfully')
        else:
            msg = "The text displayed failed"
            logger.error(msg)
            raise Fluke8845aCheckError(msg)

    dc_voltage_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.VOLTAGE_DC)
    )
    ac_voltage_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.VOLTAGE_AC)
    )
    dc_current_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.CURRENT_DC)
    )
    ac_current_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.CURRENT_AC)
    )
    two_wire_resistance_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.TWO_WIRE_RESISTANCE)
    )
    four_wire_resistance_range = _RangeDescriptor(
        cast("MeasurementFunction", MeasurementFunction.FOUR_WIRE_RESISTANCE)
    )
    voltage_filter = _FilterDescriptor(
        cast("MeasurementFunction", MeasurementFunction.VOLTAGE_AC)
    )
    current_filter = _FilterDescriptor(
        cast("MeasurementFunction", MeasurementFunction.CURRENT_AC)
    )
    frequency_aperture = _ApertureDescriptor(
        cast("MeasurementFunction", MeasurementFunction.FREQUENCY)
    )
    period_aperture = _ApertureDescriptor(
        cast("MeasurementFunction", MeasurementFunction.PERIOD)
    )
