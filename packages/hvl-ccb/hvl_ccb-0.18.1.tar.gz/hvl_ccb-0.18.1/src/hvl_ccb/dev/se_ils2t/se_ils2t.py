#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for controlling a Schneider Electric ILS2T stepper drive over modbus TCP.
"""

import logging
import struct
import sys
from datetime import timedelta
from enum import Flag, IntEnum
from time import sleep, time
from typing import Any, ClassVar, cast

import aenum
from bitstring import BitArray
from pymodbus.client import ModbusTcpClient

from hvl_ccb.comm.modbus_tcp import (
    ModbusTcpCommunication,
    ModbusTcpCommunicationConfig,
    ModbusTcpConnectionFailedError,
)
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import DeviceError, SingleCommDevice
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


class ILS2TError(DeviceError):
    """
    Error to indicate problems with the SE ILS2T stepper motor.
    """


class IoScanningModeValueError(ILS2TError):
    """
    Erorr to indicate that the selected IO scanning mode is invalid.
    """


class ScalingFactorValueError(ILS2TError):
    """
    Error to indicate that a scaling factor value is invalid.
    """


@configdataclass
class ILS2TModbusTcpCommunicationConfig(ModbusTcpCommunicationConfig):
    """
    Configuration dataclass for Modbus/TCP communciation specific for the Schneider
    Electric ILS2T stepper motor.
    """

    #: The unit has to be 255 such that IO scanning mode works.
    unit: int = 255


class ILS2TModbusTcpCommunication(ModbusTcpCommunication):
    """
    Specific implementation of Modbus/TCP for the Schneider Electric ILS2T stepper
    motor.
    """

    @staticmethod
    def config_cls():
        return ILS2TModbusTcpCommunicationConfig


@configdataclass
class ILS2TConfig:
    """
    Configuration for the ILS2T stepper motor device.
    """

    #: initial maximum RPM for the motor, can be set up to 3000 RPM. The user is
    #: allowed to set a new max RPM at runtime using :meth:`ILS2T.set_max_rpm`,
    #: but the value must never exceed this configuration setting.
    rpm_max_init: int = 1500
    wait_sec_post_enable: Number = 1
    wait_sec_max_disable: Number = 10
    wait_sec_post_cannot_disable: Number = 1
    wait_sec_post_relative_step: Number = 2
    wait_sec_post_absolute_position: Number = 2

    def clean_values(self) -> None:
        if not 0 < self.rpm_max_init <= 3000:
            msg = "Maximum RPM for the motor must be integer number between 1 and 3000."
            raise ValueError(msg)
        if self.wait_sec_post_enable <= 0:
            msg = "Wait time post motor enabling must be a positive value (in seconds)."
            raise ValueError(msg)
        if self.wait_sec_max_disable < 0:
            msg = (
                "Maximal wait time for attempting to disable motor must be a "
                "non-negative value (in seconds)."
            )
            raise ValueError(msg)
        if self.wait_sec_post_cannot_disable <= 0:
            msg = (
                "Wait time post failed motor disable attempt must be a positive value "
                "(in seconds)."
            )
            raise ValueError(msg)
        if self.wait_sec_post_relative_step <= 0:
            msg = (
                "Wait time post motor relative step must be a positive value "
                "(in seconds)."
            )
            raise ValueError(msg)
        if self.wait_sec_post_absolute_position <= 0:
            msg = (
                "Wait time post motor absolute position change must be a positive "
                "value (in seconds)."
            )
            raise ValueError(msg)


class ILS2TRegDatatype(aenum.Enum, init="min max"):  # type: ignore[call-arg]
    """
    Modbus Register Datatypes for Schneider Electric ILS2T stepper drive.

    From the manual of the drive:

    =========== =========== ============== =============
    datatype    byte        min            max
    =========== =========== ============== =============
    INT8        1 Byte      -128           127
    UINT8       1 Byte      0              255
    INT16       2 Byte      -32_768        32_767
    UINT16      2 Byte      0              65_535
    INT32       4 Byte      -2_147_483_648 2_147_483_647
    UINT32      4 Byte      0              4_294_967_295
    BITS        just 32bits N/A            N/A
    =========== =========== ============== =============

    """

    INT32 = -2_147_483_648, 2_147_483_647

    def is_in_range(self, value: int) -> bool:
        return self.min <= value <= self.max


class ILS2TRegAddr(IntEnum):
    """
    Modbus Register Adresses for for Schneider Electric ILS2T stepper drive.
    """

    POSITION = 7706  # INT32 position of the motor in user defined units
    IO_SCANNING = 6922  # BITS start register for IO scanning control
    # and status
    TEMP = 7200  # INT16 temperature of motor
    VOLT = 7198  # UINT16 dc voltage of motor
    SCALE = 1550  # INT32 user defined steps per revolution
    ACCESS_ENABLE = 282  # BITS not documented register
    # to enable access via IO scanning
    JOGN_FAST = 10506  # UINT16 revolutions per minute for fast Jog (1 to 3000)
    JOGN_SLOW = 10504  # UINT16 revolutions per minute
    # for slow Jog (1 to 3000)

    RAMP_TYPE = 1574  # INT16 ramp type, 0: linear / -1: motor optimized
    RAMP_ACC = 1556  # UINT32 acceleration
    RAMP_DECEL = 1558  # UINT32 deceleration
    RAMP_N_MAX = 1554  # UINT16 max rpm
    FLT_INFO = 15362  # 22 registers, code for error
    FLT_MEM_RESET = 15114  # UINT16 reset fault memory
    FLT_MEM_DEL = 15112  # UINT16 delete fault memory


class ILS2T(SingleCommDevice):
    """
    Schneider Electric ILS2T stepper drive class.
    """

    RegDatatype = ILS2TRegDatatype
    """Modbus Register Datatypes
    """
    RegAddr = ILS2TRegAddr
    """Modbus Register Adresses
    """

    class Mode(IntEnum):
        """
        ILS2T device modes
        """

        PTP = 3  # point to point
        JOG = 1

    class ActionsPtp(IntEnum):
        """
        Allowed actions in the point to point mode (`ILS2T.Mode.PTP`).
        """

        ABSOLUTE_POSITION = 0
        RELATIVE_POSITION_TARGET = 1
        RELATIVE_POSITION_MOTOR = 2

    ACTION_JOG_VALUE = 0
    """
    The single action value for `ILS2T.Mode.JOG`
    """

    # Note: don't use IntFlag here - it allows other then enumerated values
    # The behaviour changed with py311
    if sys.version_info < (3, 11):

        class Ref16Jog(Flag):
            """
            Allowed values for ILS2T ref_16 register (the shown values are the integer
            representation of the bits), all in Jog mode = 1
            """

            NONE = 0
            POS = 1
            NEG = 2
            FAST = 4
            # allowed combinations
            POS_FAST = POS | FAST
            NEG_FAST = NEG | FAST
    else:
        from enum import STRICT

        class Ref16Jog(Flag, boundary=STRICT):
            """
            Allowed values for ILS2T ref_16 register (the shown values are the integer
            representation of the bits), all in Jog mode = 1
            """

            NONE = 0
            POS = 1
            NEG = 2
            FAST = 4
            # allowed combinations
            POS_FAST = POS | FAST
            NEG_FAST = NEG | FAST

    class State(IntEnum):
        """
        State machine status values
        """

        QUICKSTOP = 7
        READY = 4
        ON = 6

    DEFAULT_IO_SCANNING_CONTROL_VALUES: ClassVar[dict[str, Any]] = {
        "action": ActionsPtp.RELATIVE_POSITION_MOTOR.value,
        "mode": Mode.PTP.value,
        "disable_driver_di": 0,
        "enable_driver_en": 0,
        "quick_stop_qs": 0,
        "fault_reset_fr": 0,
        "execute_stop_sh": 0,
        "reset_stop_ch": 0,
        "continue_after_stop_cu": 0,
        "ref_16": ILS2TConfig.rpm_max_init,
        "ref_32": 0,
    }
    """
    Default IO Scanning control mode values
    """

    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for ILS2T.

        :param com: object to use as communication protocol.
        """

        # Call superclass constructor
        super().__init__(com, dev_config)

        # toggle reminder bit
        self._mode_toggle_mt = 0

        self.flt_list: list[dict[int, dict[str, Any]]] = []

    @staticmethod
    def default_com_cls():
        return ILS2TModbusTcpCommunication

    @staticmethod
    def config_cls():
        return ILS2TConfig

    def start(self) -> None:
        """
        Start this device.
        """

        logger.info(f"Starting device {self}")
        try:
            # try opening the port
            super().start()
        except ModbusTcpConnectionFailedError:
            logger.exception("Error with ModbusTCP Connection")
            raise

        # writing 1 to register ACCESS_ENABLE allows to use the IO scanning mode.
        #  This is not documented in the manual!
        self.com.write_registers(self.RegAddr.ACCESS_ENABLE.value, [0, 1])

        # set maximum RPM from init config
        self.set_max_rpm(self.config.rpm_max_init)

    def stop(self) -> None:
        """
        Stop this device. Disables the motor (applies brake), disables access and
        closes the communication protocol.
        """

        logger.info(f"Stopping device {self}")
        self.disable()
        self.com.write_registers(self.RegAddr.ACCESS_ENABLE.value, [0, 0])
        super().stop()

    def get_status(self) -> dict[str, int | list[bool]]:
        """
        Perform an IO Scanning read and return the status of the motor.

        :return: dict with status information.
        """

        registers = self.com.read_holding_registers(self.RegAddr.IO_SCANNING.value, 8)
        return self._decode_status_registers(registers)

    def do_ioscanning_write(self, **kwargs: int) -> None:
        """
        Perform a write operation using IO Scanning mode.

        :param kwargs:
            Keyword-argument list with options to send, remaining are taken
            from the defaults.
        """

        self._toggle()
        values = self._generate_control_registers(**kwargs)
        self.com.write_registers(self.RegAddr.IO_SCANNING.value, values)

    def _generate_control_registers(self, **kwargs: int) -> list[int]:
        """
        Generates the control registers for the IO scanning mode.
        It is necessary to write all 64 bit at the same time, so a list of 4 registers
        is generated.

        :param kwargs: Keyword-argument list with options different than the defaults.
        :return: List of registers for the IO scanning mode.
        """

        cleaned_io_scanning_mode = self._clean_ioscanning_mode_values(kwargs)

        action_bits = f"{cleaned_io_scanning_mode['action']:03b}"
        mode_bits = f"{cleaned_io_scanning_mode['mode']:04b}"
        builder = []

        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=[
                    # add the first byte: Drive control
                    cleaned_io_scanning_mode["disable_driver_di"],
                    cleaned_io_scanning_mode["enable_driver_en"],
                    cleaned_io_scanning_mode["quick_stop_qs"],
                    cleaned_io_scanning_mode["fault_reset_fr"],
                    0,  # has to be 0 per default, no meaning
                    cleaned_io_scanning_mode["execute_stop_sh"],
                    cleaned_io_scanning_mode["reset_stop_ch"],
                    cleaned_io_scanning_mode["continue_after_stop_cu"],
                    # add the second byte: Mode control
                    int(mode_bits[3]),
                    int(mode_bits[2]),
                    int(mode_bits[1]),
                    int(mode_bits[0]),
                    int(action_bits[2]),
                    int(action_bits[1]),
                    int(action_bits[0]),
                    self._mode_toggle_mt,
                ],
                data_type=ModbusTcpClient.DATATYPE.BITS,
                word_order="big",
            )
        )

        # add the third and fourth byte:
        # Ref_16 (either JOG direction/speed, or RPM...)
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=cleaned_io_scanning_mode["ref_16"],
                data_type=ModbusTcpClient.DATATYPE.UINT16,
                word_order="big",
            )
        )

        # add 4 bytes Ref_32, Target position
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=cleaned_io_scanning_mode["ref_32"],
                data_type=ModbusTcpClient.DATATYPE.INT32,
                word_order="big",
            )
        )
        return builder

    def _clean_ioscanning_mode_values(
        self, io_scanning_values: dict[str, int]
    ) -> dict[str, int]:
        """
        Checks if the constructed mode is valid.

        :param io_scanning_values: Dictionary with register values to check
        :return: Dictionary with cleaned register values
        :raises ValueError: if `io_scanning_values` has unrecognized keys
        :raises IoScanningModeValueError: if either `'mode'` or either of corresponding
            `'action'`, `'ref_16'`, or `'ref_32'` keys of `io_scanning_values` has
            an invalid value.
        """

        # check if there are too much keys that are not recognized
        io_scanning_keys = set(io_scanning_values.keys())
        all_keys = set(self.DEFAULT_IO_SCANNING_CONTROL_VALUES.keys())
        superfluous_keys = io_scanning_keys.difference(all_keys)
        if superfluous_keys:
            msg = f"Unrecognized mode keys: {list(superfluous_keys)}"
            raise ValueError(msg)

        # fill up io_scanning_values with defaults, if they are not set
        for mode_key, default_value in self.DEFAULT_IO_SCANNING_CONTROL_VALUES.items():
            if mode_key not in io_scanning_values:
                io_scanning_values[mode_key] = cast("int", default_value)

        # perform checks depending on mode
        # JOG mode
        if io_scanning_values["mode"] == self.Mode.JOG:
            io_scanning_value = io_scanning_values["action"]
            if io_scanning_value != self.ACTION_JOG_VALUE:
                msg = f"Wrong action: {io_scanning_value}"
                raise IoScanningModeValueError(msg)

            io_scanning_value = io_scanning_values["ref_16"]
            try:
                self.Ref16Jog(io_scanning_value)
            except ValueError as exc:
                msg = f"Wrong value in ref_16 ({io_scanning_value})"
                logger.exception(msg)
                raise IoScanningModeValueError(msg) from exc

            io_scanning_value = io_scanning_values["ref_32"]
            if io_scanning_value != 0:
                msg = f"Wrong value in ref_32 ({io_scanning_value})"
                raise IoScanningModeValueError(msg)

            return io_scanning_values

        # PTP mode
        if io_scanning_values["mode"] == self.Mode.PTP:
            io_scanning_value = io_scanning_values["action"]
            try:
                self.ActionsPtp(io_scanning_value)
            except ValueError as exc:
                msg = f"Wrong action: {io_scanning_value}"
                logger.exception(msg)
                raise IoScanningModeValueError(msg) from exc

            io_scanning_value = io_scanning_values["ref_16"]
            if not self._is_valid_rpm(io_scanning_value):
                msg = f"Wrong value in ref_16 ({io_scanning_value})"
                raise IoScanningModeValueError(msg)

            io_scanning_value = io_scanning_values["ref_32"]
            if not self._is_int32(io_scanning_value):
                msg = f"Wrong value in ref_32 ({io_scanning_value})"
                raise IoScanningModeValueError(msg)

            return io_scanning_values

        # default
        msg = f"Wrong mode: {io_scanning_values['mode']}"
        raise IoScanningModeValueError(msg)

    def _is_valid_rpm(self, num: int) -> bool:
        """
        Checks whether `num` is a valid RPM value.

        :param num: RPM value to check
        :return: `True` if `num` is a valid RPM value, `False` otherwise
        """

        return isinstance(num, int) and 0 < num <= self.config.rpm_max_init

    @classmethod
    def _is_int32(cls, num: int) -> bool:
        """
        Checks whether a number fits in a signed 32-bit integer.

        :param num: is the number to check.
        :return: check result.
        """
        return isinstance(num, int) and cast(
            "ILS2TRegDatatype", ILS2TRegDatatype.INT32
        ).is_in_range(num)

    @staticmethod
    def _decode_status_registers(registers: list[int]) -> dict[str, int | list[bool]]:
        """
        Decodes the the status of the stepper drive, derived from IOscanning.
        register 1 is decoded into "ref_16" (16-bit int)
        register 2 and 3 together into "ref_32" (32-bit int)
        the others are decoded into bit lists

        :param registers: List of 8 registers (6922-6930)
        :return: dict
        """
        decoded = {}

        bit_list_registers = {
            0: ("drive_control", "mode_control"),
            4: ("drive_status_1", "drive_status_2"),
            5: ("mode_status", "drive_input"),
            6: ("action_word_1", "action_word_2"),
            7: ("special_function_1", "special_function_2"),
        }

        for idx, keys in bit_list_registers.items():
            reg_bytes = registers[idx].to_bytes(2, byteorder="big")
            bit_lists = [
                [bool((byte >> bit_position) & 1) for bit_position in range(8)]
                for byte in reg_bytes
            ]
            decoded[keys[0]], decoded[keys[1]] = bit_lists

        # > means big-endian and h signed short int 2 bytes
        decoded["ref_16"] = struct.unpack(">h", struct.pack(">h", registers[1]))[0]

        # Combine register 2 and 3 into a 32-bit integer
        # HH: two unsigned short int 2 bytes, I: big-endian unsigned int 4 bytes
        byte_data = struct.pack(">HH", registers[2], registers[3])
        decoded["ref_32"] = struct.unpack(">I", byte_data)[0]

        return {
            "mode": BitArray(decoded["mode_status"][3::-1]).int,
            "action": BitArray(decoded["mode_control"][6:3:-1]).int,
            "ref_16": decoded["ref_16"],
            "ref_32": decoded["ref_32"],
            "state": BitArray(decoded["drive_status_2"][3::-1]).int,
            "fault": decoded["drive_status_2"][6],
            "warn": decoded["drive_status_2"][7],
            "halt": decoded["drive_status_1"][0],
            "motion_zero": decoded["action_word_2"][6],
            "turning_positive": decoded["action_word_2"][7],
            "turning_negative": decoded["action_word_1"][0],
        }

    def _toggle(self) -> None:
        """
        To activate a command it is necessary to toggle the MT bit first.
        """

        self._mode_toggle_mt = 0 if self._mode_toggle_mt else 1

    def write_relative_step(self, steps: int) -> None:
        """
        Write instruction to turn the motor the relative amount of steps. This function
        does not enable or disable the motor automatically.

        :param steps: Number of steps to turn the motor.
        """
        max_step = self.RegDatatype.INT32.max  # type: ignore[attr-defined]
        # use _is_int32 instead?
        if not abs(steps) < max_step:
            logger.warning(f"number of steps is too big: {steps}")

        logger.info(f"Perform number of steps: {steps}")

        self.do_ioscanning_write(
            enable_driver_en=1,
            mode=self.Mode.PTP.value,
            action=self.ActionsPtp.RELATIVE_POSITION_MOTOR.value,
            ref_32=steps,
        )

    def write_absolute_position(self, position: int) -> None:
        """
        Write instruction to turn the motor until it reaches the absolute position.
        This function does not enable or disable the motor automatically.

        :param position: absolute position of motor in user defined steps.
        """

        max_position = self.RegDatatype.INT32.max  # type: ignore[attr-defined]
        # use _is_int32 instead?
        if not abs(position) < max_position:
            logger.warning(f"position is out of range: {position}")

        logger.info(f"Absolute position: {position}")

        self.do_ioscanning_write(
            enable_driver_en=1,
            mode=self.Mode.PTP.value,
            action=self.ActionsPtp.ABSOLUTE_POSITION.value,
            ref_32=position,
        )

    def _is_position_as_expected(
        self, position_expected: int, position_actual: int, err_msg: str
    ) -> bool:
        """
        Check if actual drive position is a expected. If expectation is not met,
        check for possible drive error and log the given error message with appropriate
        level of severity. Do not raise error; instead, return `bool` stating if
        expectation was met.

        :param position_expected: Expected drive position.
        :param position_actual: Actual drive position.
        :param err_msg: Error message to log if expectation is not met.
        :return: `True` if actual position is as expected, `False` otherwise.
        """
        as_expected = position_expected == position_actual
        if not as_expected:
            flt_dict = self.get_error_code()
            self.flt_list.append(flt_dict)
            if "empty" in flt_dict[0]:
                logger.warning(
                    "no error in drive, something different must have gone wrong"
                )
                logger.warning(err_msg)
            else:
                logger.critical("error in drive, drive is know maybe locked")
                logger.critical(err_msg)
        return as_expected

    def execute_relative_step(self, steps: int) -> bool:
        """
        Execute a relative step, i.e. enable motor, perform relative steps,
        wait until done and disable motor afterwards.

        Check position at the end if wrong do not raise error; instead just log and
        return check result.

        :param steps: Number of steps.
        :return: `True` if actual position is as expected, `False` otherwise.
        """
        logger.info(f"Motor steps requested: {steps}")

        with self.com.access_lock:
            position_before = self.get_position()

            self.enable()
            sleep(self.config.wait_sec_post_enable)
            self.write_relative_step(steps)
            sleep(self.config.wait_sec_post_relative_step)
            self.disable(log_warn=False)

            # check if steps were made
            position_after = self.get_position()
            return self._is_position_as_expected(
                position_before + steps,
                position_after,
                "The position does not align with the requested step number. "
                f"Before: {position_before}, after: {position_after}, "
                f"requested: {steps}, "
                f"real difference: {position_after - position_before}.",
            )

    def execute_absolute_position(self, position: int) -> bool:
        """
        Execute a absolute position change, i.e. enable motor, perform absolute
        position change, wait until done and disable motor afterwards.

        Check position at the end if wrong do not raise error; instead just log and
        return check result.

        :param position: absolute position of motor in user defined steps.
        :return: `True` if actual position is as expected, `False` otherwise.
        """
        logger.info(f"absolute position requested: {position}")

        with self.com.access_lock:
            position_before = self.get_position()

            self.enable()
            sleep(self.config.wait_sec_post_enable)
            self.write_absolute_position(position)
            sleep(self.config.wait_sec_post_absolute_position)
            self.disable(log_warn=False)

            # check if steps were made
            position_after = self.get_position()
            return self._is_position_as_expected(
                position,
                position_after,
                "The position does not align with the requested absolute position."
                f"Before: {position_before}, after: {position_after}, "
                f"requested: {position}.",
            )

    def disable(
        self,
        log_warn: bool = True,
        wait_sec_max: int | None = None,
    ) -> bool:
        """
        Disable the driver of the stepper motor and enable the brake.

        Note: the driver cannot be disabled if the motor is still running.

        :param log_warn: if log a warning in case the motor cannot be disabled.
        :param wait_sec_max: maximal wait time for the motor to stop running and to
            disable it; by default, with `None`, use a config value
        :return: `True` if disable request could and was sent, `False` otherwise.
        """
        if wait_sec_max is None:
            wait_sec_max = self.config.wait_sec_max_disable

        try_disable = True
        elapsed_time = 0.0
        start_time = time()
        while try_disable:
            can_disable = bool(self.get_status()["motion_zero"])
            if can_disable:
                logger.info("Disable motor, brake.")
                self.do_ioscanning_write(enable_driver_en=0, disable_driver_di=1)
            elif log_warn:
                logger.warning("Cannot disable motor, still running!")
            elapsed_time += time() - start_time

            try_disable = not can_disable and elapsed_time < wait_sec_max
            if try_disable:
                sleep(self.config.wait_sec_post_cannot_disable)

        return can_disable

    def enable(self) -> None:
        """
        Enable the driver of the stepper motor and disable the brake.
        """

        self.do_ioscanning_write(enable_driver_en=1, disable_driver_di=0)
        logger.info("Enable motor, disable brake.")

    def get_position(self) -> int:
        """
        Read the position of the drive and store into status.

        :return: Position step value
        """

        value = self.com.read_input_registers(self.RegAddr.POSITION.value, 2)
        return self._decode_32bit(value, True)

    def get_temperature(self) -> int:
        """
        Read the temperature of the motor.

        :return: Temperature in degrees Celsius.
        """

        value = self.com.read_input_registers(self.RegAddr.TEMP.value, 2)
        return self._decode_32bit(value, True)

    def get_dc_volt(self) -> float:
        """
        Read the DC supply voltage of the motor.

        :return: DC input voltage.
        """

        value = self.com.read_input_registers(self.RegAddr.VOLT.value, 2)
        return self._decode_32bit(value, True) / 10

    @staticmethod
    def _decode_32bit(registers: list[int], signed: bool = True) -> int:
        """
        Decode two 16-bit ModBus registers to a 32-bit integer.

        :param registers: list of two register values
        :param signed: True, if register containes a signed value
        :return: integer representation of the 32-bit register
        """

        if signed:
            return ModbusTcpClient.convert_from_registers(
                registers=registers, data_type=ModbusTcpClient.DATATYPE.INT32
            )

        return ModbusTcpClient.convert_from_registers(
            registers=registers, data_type=ModbusTcpClient.DATATYPE.UINT32
        )

    def user_steps(self, steps: int = 16384, revolutions: int = 1) -> None:
        """
        Define steps per revolution.
        Default is 16384 steps per revolution.
        Maximum precision is 32768 steps per revolution.

        :param steps: number of steps in `revolutions`.
        :param revolutions: number of revolutions corresponding to `steps`.
        """

        if not self._is_int32(revolutions):
            err_msg = f"Wrong scaling factor: revolutions = {revolutions}"
            logger.error(err_msg)
            raise ScalingFactorValueError(err_msg)

        if not self._is_int32(steps):
            err_msg = f"Wrong scaling factor: steps = {steps}"
            logger.error(err_msg)
            raise ScalingFactorValueError(err_msg)

        builder = []
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=steps,
                data_type=ModbusTcpClient.DATATYPE.INT32,
                word_order="big",
            )
        )
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=revolutions,
                data_type=ModbusTcpClient.DATATYPE.INT32,
                word_order="big",
            )
        )
        self.com.write_registers(self.RegAddr.SCALE.value, builder)

    def quickstop(self) -> None:
        """
        Stops the motor with high deceleration rate and falls into error state. Reset
        with `reset_error` to recover into normal state.
        """

        logger.warning("Motor QUICK STOP.")
        self.do_ioscanning_write(quick_stop_qs=1)

    def reset_error(self) -> None:
        """
        Resets the motor into normal state after quick stop or another error occured.
        """

        logger.info("Reset motor after fault or quick stop.")
        self.do_ioscanning_write(fault_reset_fr=1)

    def jog_run(self, direction: bool = True, fast: bool = False) -> None:
        """
        Slowly turn the motor in positive direction.
        """

        status = self.get_status()

        if status["mode"] != self.Mode.JOG and not status["motion_zero"]:
            logger.error("Motor is not in Jog mode or standstill, abort.")
            return

        if status["state"] != self.State.ON:
            # need to enable first
            logger.error("Motor is not enabled or in error state. Try .enable()")
            return

        ref_16 = self.Ref16Jog.NONE

        if direction:
            ref_16 = ref_16 | self.Ref16Jog.POS
            logger.info("Jog mode in positive direction enabled.")
        else:
            ref_16 = ref_16 | self.Ref16Jog.NEG
            logger.info("Jog mode in negative direction enabled.")

        if fast:
            ref_16 = ref_16 | self.Ref16Jog.FAST

        self.do_ioscanning_write(
            mode=self.Mode.JOG.value,
            action=self.ACTION_JOG_VALUE,
            enable_driver_en=1,
            ref_16=ref_16.value,
        )

    def jog_stop(self) -> None:
        """
        Stop turning the motor in Jog mode.
        """

        logger.info("Stop in Jog mode.")

        self.do_ioscanning_write(
            mode=self.Mode.JOG.value,
            action=self.ACTION_JOG_VALUE,
            enable_driver_en=1,
            ref_16=0,
        )

    def set_jog_speed(self, slow: int = 60, fast: int = 180) -> None:
        """
        Set the speed for jog mode. Default values correspond to startup values of
        the motor.

        :param slow: RPM for slow jog mode.
        :param fast: RPM for fast jog mode.
        """

        logger.info(f"Setting Jog RPM. Slow = {slow} RPM, Fast = {fast} RPM.")
        self.com.write_registers(self.RegAddr.JOGN_SLOW.value, [0, slow])
        self.com.write_registers(self.RegAddr.JOGN_FAST.value, [0, fast])

    def get_error_code(self) -> dict[int, dict[str, Any]]:
        """
        Read all messages in fault memory.
        Will read the full error message and return the decoded values.
        At the end the fault memory of the motor will be deleted.
        In addition, reset_error is called to re-enable the motor for operation.

        :return: Dictionary with all information
        """

        ret_dict = {}
        self.com.write_registers(self.RegAddr.FLT_MEM_RESET.value, [0, 1])
        for i in range(10):
            registers = self.com.read_input_registers(self.RegAddr.FLT_INFO.value, 22)
            decoded = {
                "ignored0": None,
                "error_code": ModbusTcpClient.convert_from_registers(
                    registers=registers[1:2],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored1": None,
                "error_class": ModbusTcpClient.convert_from_registers(
                    registers=registers[3:4],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "error_time": ModbusTcpClient.convert_from_registers(
                    registers=registers[4:6],
                    data_type=ModbusTcpClient.DATATYPE.UINT32,
                    word_order="big",
                ),
                "ignored2": None,
                "error_addition": ModbusTcpClient.convert_from_registers(
                    registers=registers[7:8],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored3": None,
                "error_no_cycle": ModbusTcpClient.convert_from_registers(
                    registers=registers[9:10],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored4": None,
                "error_after_enable": ModbusTcpClient.convert_from_registers(
                    registers=registers[11:12],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored5": None,
                "error_voltage_dc": ModbusTcpClient.convert_from_registers(
                    registers=registers[13:14],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored6": None,
                "error_rpm": ModbusTcpClient.convert_from_registers(
                    registers=registers[15:16],
                    data_type=ModbusTcpClient.DATATYPE.INT16,
                    word_order="big",
                ),
                "ignored7": None,
                "error_current": ModbusTcpClient.convert_from_registers(
                    registers=registers[17:18],
                    data_type=ModbusTcpClient.DATATYPE.UINT16,
                    word_order="big",
                ),
                "ignored8": None,
                "error_amplifier_temperature": ModbusTcpClient.convert_from_registers(
                    registers=registers[19:20],
                    data_type=ModbusTcpClient.DATATYPE.INT16,
                    word_order="big",
                ),
                "ignored9": None,
                "error_device_temperature": ModbusTcpClient.convert_from_registers(
                    registers=registers[21:22],
                    data_type=ModbusTcpClient.DATATYPE.INT16,
                    word_order="big",
                ),
            }
            flt_dict = {
                "error_code": hex(decoded["error_code"])[2:],
                "error_class": decoded["error_class"],
                "error_time": timedelta(seconds=decoded["error_time"]),
                "error_addition": decoded["error_addition"],
                "error_no_cycle": decoded["error_no_cycle"],
                "error_after_enable": timedelta(seconds=decoded["error_after_enable"]),
                "error_voltage_dc": decoded["error_voltage_dc"] / 10,
                "error_rpm": decoded["error_rpm"],
                "error_current": decoded["error_current"] / 100,
                "error_amplifier_temperature": decoded["error_amplifier_temperature"],
                "error_device_temperature": decoded["error_device_temperature"],
            }
            ret_dict[i] = flt_dict
            if flt_dict["error_code"] == "0":
                flt_dict = {"empty": None}
                ret_dict = {i: flt_dict}
                break
        self.com.write_registers(self.RegAddr.FLT_MEM_DEL.value, [0, 1])
        self.reset_error()
        return ret_dict

    def set_max_rpm(self, rpm: int) -> None:
        """
        Set the maximum RPM.

        :param rpm: revolution per minute ( 0 < rpm <= RPM_MAX)
        :raises ILS2TError: if RPM is out of range
        """

        if self._is_valid_rpm(rpm):
            self.DEFAULT_IO_SCANNING_CONTROL_VALUES["ref_16"] = rpm
            self.com.write_registers(self.RegAddr.RAMP_N_MAX.value, [0, rpm])
        else:
            msg = f"RPM out of range: {rpm} not in (0, {self.config.rpm_max_init}]"
            raise ILS2TError(msg)

    def set_ramp_type(self, ramp_type: int = -1) -> None:
        """
        Set the ramp type. There are two options available:
            0:  linear ramp
            -1: motor optimized ramp

        :param ramp_type: 0: linear ramp | -1: motor optimized ramp
        """

        self.com.write_registers(self.RegAddr.RAMP_TYPE.value, [0, ramp_type])

    def set_max_acceleration(self, rpm_minute: int) -> None:
        """
        Set the maximum acceleration of the motor.

        :param rpm_minute: revolution per minute per minute
        """

        builder = []
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=rpm_minute,
                data_type=ModbusTcpClient.DATATYPE.UINT32,
                word_order="big",
            )
        )
        self.com.write_registers(self.RegAddr.RAMP_ACC.value, builder)

    def set_max_deceleration(self, rpm_minute: int) -> None:
        """
        Set the maximum deceleration of the motor.

        :param rpm_minute: revolution per minute per minute
        """

        builder = []
        builder.extend(
            ModbusTcpClient.convert_to_registers(
                value=rpm_minute,
                data_type=ModbusTcpClient.DATATYPE.UINT32,
                word_order="big",
            )
        )
        self.com.write_registers(self.RegAddr.RAMP_DECEL.value, builder)
