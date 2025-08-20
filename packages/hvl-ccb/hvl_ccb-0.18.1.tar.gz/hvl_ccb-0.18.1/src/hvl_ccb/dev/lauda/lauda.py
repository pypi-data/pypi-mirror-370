#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for controlling a Lauda PRO RP245E, circulation chiller over TCP.
"""

import logging
import time
from enum import IntEnum

from hvl_ccb.comm.tcp import TcpCommunication, TcpCommunicationConfig
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import DeviceError, SingleCommDevice
from hvl_ccb.utils.enum import ValueEnum
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


class LaudaProRp245eCommand(ValueEnum):
    """
    Commands for Lauda PRO RP245E Chiller
    Command strings most often need to be complimented with a parameter
    (attached as a string) before being sent to the device.
    Commands implemented as defined in "Lauda Betriebsanleitung fuer
    PRO Badthermostate und Umwaelzthermostate" pages 42 - 49
    """

    #: Pass on external controlled temperature
    EXTERNAL_TEMP = "OUT_PV_05_"
    #: Define temperature set point
    TEMP_SET_POINT = "OUT_SP_00_"
    #: Define pump level 1-8
    PUMP_LEVEL = "OUT_SP_01_"
    #: Define operation mode
    OPERATION_MODE = "OUT_SP_02_"
    #: Define upper temp limit
    UPPER_TEMP = "OUT_SP_04_"
    #: Define lower temp limit
    LOWER_TEMP = "OUT_SP_05_"
    #: Define communication time out
    COM_TIME_OUT = "OUT_SP_08_"
    #: Set control mode 1=internal, 2=ext. analog, 3=ext. serial, 4=USB, 5=ethernet
    CONT_MODE = "OUT_MODE_01_"
    #: Start temp control (pump and heating/cooling)
    START = "START"
    #: Stop temp control (pump and heating/cooling)
    STOP = "STOP"
    #: Select a ramp program (target for all further ramp commands)
    RAMP_SELECT = "RMP_SELECT_"
    #: Start a selected ramp program
    RAMP_START = "RMP_START"
    #: Pause a selected ramp program
    RAMP_PAUSE = "RMP_PAUSE"
    #: Continue a paused ramp program
    RAMP_CONTINUE = "RMP_CONT"
    #: Stop a running ramp program
    RAMP_STOP = "RMP_STOP"
    #: Reset a selected ramp program
    RAMP_DELETE = "RMP_RESET"
    #: Define how often a ramp program should be iterated
    RAMP_ITERATIONS = "RMP_OUT_02_"
    #: Define parameters of a selected ramp program
    RAMP_SET = "RMP_OUT_00_"
    #: Request internal bath temperature
    BATH_TEMP = "IN_PV_00"
    #: Request external PT100 temperature
    EXTERNAL_PT100_TEMP = "IN_PV_03"
    #: Request device type
    DEVICE_TYPE = "TYPE"


class LaudaProRp245eError(DeviceError):
    """Errors from Lauda Devices"""


class LaudaProRp245eCommandError(LaudaProRp245eError):
    """
    Error raised when an error is returned upon a command.
    """


@configdataclass
class LaudaProRp245eTcpCommunicationConfig(TcpCommunicationConfig):
    """
    Configuration dataclass for :class:`LaudaProRp245eTcpCommunication`.
    """

    #: Delay time between commands in seconds
    wait_sec_pre_read_or_write: float = 0.005

    def clean_values(self) -> None:
        # host, raises ValueError on its own if not suitable
        super().clean_values()
        validate_number(
            "wait_sec_pre_read_or_write",
            self.wait_sec_pre_read_or_write,
            (0.001, None),
            logger=logger,
        )

        valid_terminators = {b"", b"\n", b"\r", b"\r\n"}
        if self.terminator not in valid_terminators:
            msg = f'Unknown terminator: "{self.terminator!r}"'
            logger.error(msg)
            raise ValueError(msg)


class LaudaProRp245eTcpCommunication(TcpCommunication):
    """
    Implements the Communication Protocol for Lauda PRO RP245E TCP connection.
    """

    config: LaudaProRp245eTcpCommunicationConfig

    def __init__(self, configuration) -> None:
        """Constructor for socket"""
        super().__init__(configuration)

    @staticmethod
    def config_cls() -> type[LaudaProRp245eTcpCommunicationConfig]:
        return LaudaProRp245eTcpCommunicationConfig

    def write_command(self, command: LaudaProRp245eCommand | str, param: str) -> None:
        """
        Send command function.

        :param command: first part of command string, defined in `LaudaProRp245eCommand`
        :param param: second part of command string, parameter
        :return: None
        """
        try:
            command = LaudaProRp245eCommand(command)
        except ValueError as exc:
            err_msg = f"Unknown command: '{command}///{param}'"
            logger.exception(err_msg)
            raise LaudaProRp245eCommandError(err_msg) from exc

        time.sleep(LaudaProRp245eTcpCommunicationConfig.wait_sec_pre_read_or_write)
        with self.access_lock:
            self.write(f"{command}{param}")

    def read_processed(self) -> str:
        """
        Receive value function.

        :return: reply from device as a string, the terminator, as well as the 'OK'
            stripped from the reply to make it directly useful as a value (e.g. in case
            the internal bath temperature is requested)
        """
        time.sleep(self.config.wait_sec_pre_read_or_write)
        with self.access_lock:
            return self.read().strip().replace("OK", "")

    def query_command(
        self, command: LaudaProRp245eCommand | str, param: str = ""
    ) -> str:
        """
        Send and receive function. E.g. to be used when setting/changing device setting.

        :param command: first part of command string, defined in `LaudaProRp245eCommand`
        :param param: second part of command string, parameter (by default '')
        :return: None
        """
        with self.access_lock:
            self.write_command(command, param)
            reply = self.read_processed()
        if "ERR" in reply:
            msg = f"Error in reply to a command: '{command}///{param}' => '{reply}'"
            logger.error(msg)
            raise LaudaProRp245eCommandError(msg)
        return reply

    def open(self) -> None:
        """
        Open the Lauda PRO RP245E TCP connection.
        """

        # open the port

        with self.access_lock:
            super().open()

    def close(self) -> None:
        """
        Close the Lauda PRO RP245E TCP connection.
        """

        with self.access_lock:
            # Set Lauda control mode to internal
            self.write_command(
                LaudaProRp245eCommand.CONT_MODE,
                str(LaudaProRp245eConfig.ExtControlModeEnum.INTERNAL.value),
            )
            # Stop currently running processes
            self.write_command(LaudaProRp245eCommand.STOP, "")
            # Close connection to Lauda
            super().close()


@configdataclass
class LaudaProRp245eConfig:
    """
    Configuration for the Lauda RP245E circulation chiller.
    """

    class OperationModeEnum(IntEnum):
        """Operation Mode (Cooling OFF/Cooling On/AUTO - set to AUTO)"""

        COOLOFF = 0
        COOLON = 1
        #: Automatically select heating/cooling
        AUTO = 2

    class ExtControlModeEnum(IntEnum):
        """
        Source for definition of external, controlled temperature (option 2, 3 and 4
        are not available with current configuration of the Lauda RP245E,
        add-on hardware would required)
        """

        INTERNAL = 0
        EXPT100 = 1
        ANALOG = 2
        SERIAL = 3
        USB = 4
        ETH = 5

    #: Default temperature set point
    temp_set_point_init: Number = 20.0
    #: Default pump Level
    pump_init: int = 6
    #: Upper temperature limit (safe for Galden HT135 cooling liquid)
    upper_temp: Number = 202.0
    #: Lower temperature limit (safe for Galden HT135 cooling liquid)
    lower_temp: Number = -55.0
    #: Communication time out (0 = OFF)
    com_time_out: Number = 0
    #: Highest pump level of the chiller
    max_pump_level: int = 8
    #: Maximum number of ramp programs that can be stored in the memory of the chiller
    max_pr_number: int = 5

    operation_mode: int | OperationModeEnum = OperationModeEnum.AUTO

    control_mode: int | ExtControlModeEnum = ExtControlModeEnum.INTERNAL

    def clean_values(self) -> None:
        if not isinstance(self.operation_mode, self.OperationModeEnum):
            self.force_value(  # type: ignore[attr-defined]
                "operation_mode", self.OperationModeEnum(self.operation_mode)
            )
        if not isinstance(self.control_mode, self.ExtControlModeEnum):
            self.force_value(  # type: ignore[attr-defined]
                "control_mode", self.ExtControlModeEnum(self.control_mode)
            )
        validate_number("upper_temp", self.upper_temp, (25, 202), logger=logger)
        validate_number("lower_temp", self.lower_temp, (-55, 25), logger=logger)


class LaudaProRp245e(SingleCommDevice):
    """
    Lauda RP245E circulation chiller class.
    """

    com: LaudaProRp245eTcpCommunication
    config: LaudaProRp245eConfig

    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for Lauda.

        :param com: object to use as communication protocol.
        """

        # Call superclass constructor
        super().__init__(com, dev_config)

    @staticmethod
    def default_com_cls() -> type[LaudaProRp245eTcpCommunication]:
        return LaudaProRp245eTcpCommunication

    @staticmethod
    def config_cls() -> type[LaudaProRp245eConfig]:
        return LaudaProRp245eConfig

    def _validate_pump_level(self, level: int) -> None:
        """
        Validates pump level. Raises ValueError, if pump level is incorrect.

        :param level: pump level, integer
        """
        if level > self.config.max_pump_level:
            err_msg = f"maximum pump level is {self.config.max_pump_level}"
            raise ValueError(err_msg)

    def start(self) -> None:
        """
        Start this device.

        """

        logger.info(f"Starting device {self}")

        super().start()

        self.get_device_type()
        # Defaults of things to be changed at runtime
        # safe temperature set point
        self.set_temp_set_point(self.config.temp_set_point_init)
        # standard pump level
        self.set_pump_level(self.config.pump_init)
        # Defaults set only here, not required at runtime
        self.com.query_command(
            LaudaProRp245eCommand.OPERATION_MODE, str(self.config.operation_mode)
        )
        self.com.query_command(
            LaudaProRp245eCommand.UPPER_TEMP, str(self.config.upper_temp)
        )
        self.com.query_command(
            LaudaProRp245eCommand.LOWER_TEMP, str(self.config.lower_temp)
        )
        self.com.query_command(
            LaudaProRp245eCommand.COM_TIME_OUT, str(self.config.com_time_out)
        )

    def stop(self) -> None:
        """
        Stop this device. Disables access and
        closes the communication protocol.

        """

        logger.info(f"Stopping device {self}")
        super().stop()

    def pause(self) -> str:
        """
        Stop temperature control and pump.

        :return: reply of the device to the last call of "query"
        """
        return self.com.query_command(LaudaProRp245eCommand.STOP)

    def run(self) -> str:
        """
        Start temperature control & pump.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.START)

    def set_external_temp(self, external_temp: float = 20.00) -> str:
        """
        Pass value of external controlled temperature. Should be done every second,
        when control of external temperature is active. Has to be done right before
        control of external temperature is activated.

        :param external_temp: current value of external temperature to be controlled.
        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(
            LaudaProRp245eCommand.EXTERNAL_TEMP, f"{external_temp:.2f}"
        )

    def set_temp_set_point(self, temp_set_point: float = 20.00) -> str:
        """
        Define temperature set point

        :param temp_set_point: temperature set point.
        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(
            LaudaProRp245eCommand.TEMP_SET_POINT, f"{temp_set_point:.2f}"
        )

    def set_pump_level(self, pump_level: int = 6) -> str:
        """
        Set pump level
        Raises ValueError, if pump level is invalid.

        :param pump_level: pump level.
        :return: reply of the device to the last call of "query"
        """

        self._validate_pump_level(pump_level)
        return self.com.query_command(LaudaProRp245eCommand.PUMP_LEVEL, str(pump_level))

    def set_control_mode(
        self,
        mod: int
        | LaudaProRp245eConfig.ExtControlModeEnum = LaudaProRp245eConfig.ExtControlModeEnum.INTERNAL,  # noqa: E501
    ) -> str:
        """
        Define control mode. 0 = INTERNAL (control bath temp), 1 = EXPT100 (pt100
        attached to chiller), 2 = ANALOG, 3 = SERIAL, 4 = USB, 5 = ETH (to be used
        when passing the ext. temp. via ethernet) (temperature then needs to be
        passed every second, when not using options 3, 4, or 5)

        :param mod: temp control mode (control internal temp or external temp).
        :return: reply of the device to the last call of "query"
            ("OK", if command was recognized")
        """

        mod_enum = LaudaProRp245eConfig.ExtControlModeEnum(mod)
        return self.com.query_command(
            LaudaProRp245eCommand.CONT_MODE, str(mod_enum.value)
        )

    def set_ramp_program(self, program: int = 1) -> str:
        """
        Define ramp program for following ramp commands.
        Raises ValueError if maximum number of ramp programs (5) is exceeded.

        :param program: Number of ramp program to be activated for following commands.
        :return: reply of the device to the last call of "query"
        """

        if program > self.config.max_pr_number:
            err_msg = f"Maximum number of ramp programs is {self.config.max_pr_number}."
            raise ValueError(err_msg)
        return self.com.query_command(LaudaProRp245eCommand.RAMP_SELECT, str(program))

    def start_ramp(self) -> str:
        """
        Start current ramp program.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_START)

    def pause_ramp(self) -> str:
        """
        Pause current ramp program.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_PAUSE)

    def continue_ramp(self) -> str:
        """
        Continue current ramp program.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_CONTINUE)

    def stop_ramp(self) -> str:
        """
        Stop current ramp program.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_STOP)

    def reset_ramp(self) -> str:
        """
        Delete all segments from current ramp program.

        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_DELETE)

    def set_ramp_iterations(self, num: int = 1) -> str:
        """
        Define number of ramp program cycles.

        :param num: number of program cycles to be performed.
        :return: reply of the device to the last call of "query"
        """

        return self.com.query_command(LaudaProRp245eCommand.RAMP_ITERATIONS, str(num))

    def set_ramp_segment(
        self, temp: float = 20.00, dur: int = 0, tol: float = 0.00, pump: int = 6
    ) -> str:
        """
        Define segment of current ramp program - will be attached to current program.
        Raises ValueError, if pump level is invalid.

        :param temp: target temperature of current ramp segment
        :param dur: duration in minutes, in which target temperature should be reached
        :param tol: tolerance at which target temperature should be reached (for 0.00,
            next segment is started after dur has passed).
        :param pump: pump level to be used for this program segment.
        :return: reply of the device to the last call of "query"
        """
        self._validate_pump_level(pump)
        segment = f"{temp:.2f}_{dur}_{tol:.2f}_{pump}"
        return self.com.query_command(LaudaProRp245eCommand.RAMP_SET, segment)

    def get_bath_temp(self) -> float:
        """
        Retuns the bath temperature

        :return: float value of measured lauda bath temp in °C
        """
        rep = self.com.query_command(LaudaProRp245eCommand.BATH_TEMP)
        return float(rep)

    def get_external_temp(self) -> float:
        """
        Returns the external temperature

        :return: float value of measured external PT100 temp in °C
        """
        rep = self.com.query_command(LaudaProRp245eCommand.EXTERNAL_PT100_TEMP)
        return float(rep)

    def get_device_type(self) -> str:
        """
        Returns the device type

        :return: Connected Lauda device type (for connection/com test)
        """
        device_type = self.com.query_command(LaudaProRp245eCommand.DEVICE_TYPE)
        if "PRO" not in device_type:
            msg = "Could not connect to Lauda RP 245 E PRO. Check IP address."
            logger.error(msg)
            raise LaudaProRp245eCommandError(msg)

        return device_type
