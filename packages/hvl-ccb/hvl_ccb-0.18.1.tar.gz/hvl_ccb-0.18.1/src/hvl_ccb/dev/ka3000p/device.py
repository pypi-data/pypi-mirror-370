#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

import contextlib
import logging
import re
from collections.abc import Generator
from time import sleep
from typing import Any

from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import SingleCommDevice
from hvl_ccb.utils.validation import validate_bool, validate_number

from .base import KA3000PError, KA3000PStatus, _gen_status
from .comm import KA3000PCommunication

logger = logging.getLogger(__name__)


@configdataclass
class KA3000PConfig:
    """Device configuration class for a KA3000P power supply"""

    time_to_wait_before_save_settings: float = 0.1


class KA3000P(SingleCommDevice):
    """Class to controll a KA3000P power supply"""

    com: KA3000PCommunication
    config: KA3000PConfig

    @staticmethod
    def default_com_cls():
        return KA3000PCommunication

    @staticmethod
    def config_cls():
        return KA3000PConfig

    def __init__(self, com, dev_config=None) -> None:
        super().__init__(com, dev_config)
        self._brand: str = ""
        self._comm_version: str = ""
        self._serial_number: str = ""
        # maximum output voltage of the hardware (unit V)
        self._max_voltage_hardware: float = 0
        # maximum output current of the hardware (unit A)
        self._max_current_hardware: float = 0

    def start(self) -> None:
        super().start()
        try:
            self.idenify_device()
        except KA3000PError as exc:
            self.stop()
            msg = (
                "Error during identifying the device. "
                "Either the device is unknown or the connection is not stable."
            )
            logger.exception(msg)
            raise KA3000PError(msg) from exc

    def idenify_device(self) -> None:
        identification: str = self.com.query_not_none("*IDN?")
        logger.debug(f'Identified device: "{identification}"')
        # Result: KORAD KA3005P V5.9 SN:02738566
        regex_model = (
            r"(?P<brand>[A-Z]+) "  # KORAD
            r"KA(?P<voltage>\d{2})(?P<current>\d{2})P "  # KA3005P
            r"V(?P<version>[.0-9]+) "  # V5.9
            r"SN:(?P<sn>[0-9]+)"  # SN:02738566
        )
        m_obj: re.Match[str] | None = re.match(regex_model, identification)
        if m_obj is None:
            msg = f"Cannot identify device with identification: {identification}"
            logger.error(msg)
            raise KA3000PError(msg)
        device_values: dict[str, str] = m_obj.groupdict()
        self._brand = device_values["brand"]
        self._max_voltage_hardware = float(device_values["voltage"])
        self._max_current_hardware = float(device_values["current"])
        self._comm_version = f"V{device_values['version']}"
        self._serial_number = device_values["sn"]

    # Static information
    @property
    def brand(self) -> str:
        """Brand of the connected device

        :return: Band
        """
        return self._brand

    @property
    def comm_version(self) -> str:
        """Version of the communication protocol

        :return: Version number
        """
        return self._comm_version

    @property
    def serial_number(self) -> str:
        """Serial number of the connected device

        :return: Serial number
        """
        return self._serial_number

    @property
    def status(self) -> KA3000PStatus:
        with self.com.access_lock:
            self.com.write("STATUS?")
            stb_qry = self.com.read_bytes()

        # A somehow "manual" strip of a single byte, as the result can be a byte which
        # could be interpreted as whitespace
        if len(stb_qry) == 0:
            msg = "Queried status and did not get an answer"
            logger.error(msg)
            raise KA3000PError(msg)
        if len(stb_qry) > 1 and len(stb_qry[1:].strip()) != 0:
            msg = f"Queried status and answer was not a single byte ({stb_qry!r})"
            logger.error(msg)
            raise KA3000PError(msg)
        return _gen_status(stb_qry[0])

    # Voltage and current values
    @property
    def voltage(self) -> float:
        """Return the measured output voltage in V"""
        value = float(self.com.query_not_none("VOUT1?"))
        logger.debug(f"Voltage at Output 1 of KA3000P: {value} V")
        return value

    @voltage.setter
    def voltage(self, value: float) -> None:
        """Set the output voltage"""
        validate_number("voltage", value, (0, self.max_voltage), logger=logger)
        value_str = f"VSET1:{value:.2f}"
        logger.debug(f'Set output voltage ({value} V) with: "{value_str}"')
        self.com.write(value_str)

    @property
    def current(self) -> float:
        """Return the measured output current in A"""
        value = float(self.com.query_not_none("IOUT1?"))
        logger.debug(f"Current at Output 1 of KA3000P: {value} A")
        return value

    @current.setter
    def current(self, value: float) -> None:
        """Set the output current"""
        validate_number("current", value, (0, self.max_current), logger=logger)
        value_str = f"ISET1:{value:.3f}"
        logger.debug(f'Set output current ({value} A) with: "{value_str}"')
        self.com.write(value_str)

    @property
    def set_voltage(self) -> float:
        """Return the set voltage (may differ from actual value) in V"""
        value = float(self.com.query_not_none("VSET1?"))
        logger.debug(f"Set Voltage at Output 1 of KA3000P: {value} V")
        return value

    @set_voltage.setter
    def set_voltage(self, value: float) -> None:
        """Set the output voltage"""
        self.voltage = value

    @property
    def set_current(self) -> float:
        """Return the set current (may differ from actual value) in A"""
        value = float(self.com.query_not_none("ISET1?"))
        logger.debug(f"Set Current at Output 1 of KA3000P: {value} A")
        return value

    @set_current.setter
    def set_current(self, value: float) -> None:
        """Set the output current"""
        self.current = value

    @property
    def max_voltage(self) -> float:
        """Maximal output voltage of the hardware in V,
        but user can reset to a lower value"""
        return self._max_voltage_hardware

    @property
    def max_current(self) -> float:
        """Maximal output current of the hardware in A,
        but user can reset to a lower value"""
        return self._max_current_hardware

    # Output stage
    @property
    def output(self) -> bool | None:
        """State of the high voltage output"""
        return self.status.output

    @output.setter
    def output(self, value: bool) -> None:
        """
        Activates the output of the source

        :param value: `True` for activation, `False` for deactivation
        """
        validate_bool("output", value, logger=logger)
        value_str = f"OUT{1 if value else 0}"
        logger.debug(f'Set output ({"ON" if value else "OFF"}) with: "{value_str}"')
        self.com.write(value_str)

    # Beep
    @property
    def beep(self) -> bool:
        """State of the beep"""
        return self.status.beep

    @beep.setter
    def beep(self, value: bool) -> None:
        """
        Activates the beep of the source

        :param value: `True` for activation, `False` for deactivation
        """
        validate_bool("beep", value, logger=logger)
        value_str = f"BEEP{1 if value else 0}"
        logger.debug(f'Set beep ({"ON" if value else "OFF"}) with: "{value_str}"')
        self.com.write(value_str)

    # Lock Screen
    @property
    def lock(self) -> bool:
        """State of the button lock"""
        msg = "The state of the button lock cannot be read. It is write-only..."
        logger.error(msg)
        raise NotImplementedError(msg)

    @lock.setter
    def lock(self, value: bool) -> None:
        """Lock or unlock the hardware buttons at the front panel

        :param value: `True` to lock the buttons, `False` to enable the manuel buttons
        """
        validate_bool("lock", value, logger=logger)
        value_str = f"LOCK{1 if value else 0}"
        logger.debug(f'Set lock ({"ON" if value else "OFF"}) with: "{value_str}"')
        self.com.write(value_str)

    # Controlled Voltage or Current
    @property
    def controlled_voltage(self) -> bool:
        """If the power supply operates at voltage limiting mode.
        Opposite to `controlled_current`.

        :return: Output is voltage limited
        """

        return self.status.ch1_cv

    @property
    def controlled_current(self) -> bool:
        """If the power supply operates at current limiting mode.
        Opposite to `controlled_voltage`.

        :return: Output is current limited
        """

        return not self.status.ch1_cv

    # Save and Recall settings (unfortunately, also write-only)
    @property
    def save(self) -> int:
        """Save a setting"""
        msg = "The save the settings cannot be read. It is write-only..."
        logger.error(msg)
        raise NotImplementedError(msg)

    @save.setter
    def save(self, value: int) -> None:
        """Save the panel settings to a given slot. Available slot: 1...5

        :param value: `int` between 1 and 5 to select the slot
        """
        validate_number("save", value, (1, 5), number_type=int, logger=logger)
        value_str = f"SAV{value}"
        logger.debug(f'Save settings to slot {value} with: "{value_str}"')
        self.com.write(value_str)

    @property
    def recall(self) -> int:
        """Recall a setting"""
        msg = "The recall a setting cannot be read. It is write-only..."
        logger.error(msg)
        raise NotImplementedError(msg)

    @recall.setter
    def recall(self, value: int) -> None:
        """Recall the panel settings from a given slot. Available slot: 1...5

        :param value: `int` between 1 and 5 to select the slot
        """
        validate_number("recall", value, (1, 5), number_type=int, logger=logger)
        value_str = f"RCL{value}"
        logger.debug(f'Recall a setting from slot {value} with: "{value_str}"')
        self.com.write(value_str)

    @contextlib.contextmanager
    def save_settings_to(self, slot: int) -> Generator[None, Any, None]:
        """Method to save settings to a slot.

        Use this method with a `with`-block. It will recall a slot and save the settings
        to it.

        Example:

        .. code-block:: python

            slot = 3
            with ka3005p.save_settings_to(slot):
                ka3005p.voltage = 2.5
                ka3005p.current = 0.75

        :param slot: Slot 1...5

        """
        self.recall = slot
        yield
        sleep(self.config.time_to_wait_before_save_settings)
        self.save = slot

    # OCP
    @property
    def ocp(self) -> bool:
        """State of the over current protection"""
        return self.status.ocp

    @ocp.setter
    def ocp(self, value: bool) -> None:
        """
        Activates the over current protection

        :param value: `True` for activation, `False` for deactivation
        """
        validate_bool("ocp", value, logger=logger)
        value_str = f"OCP{1 if value else 0}"
        logger.debug(
            f"Set over current protection ({'ON' if value else 'OFF'}) "
            f'with: "{value_str}"'
        )
        self.com.write(value_str)

    # OVP
    @property
    def ovp(self) -> bool:
        """State of the over voltage protection"""
        return self.status.ovp

    @ovp.setter
    def ovp(self, value: bool) -> None:
        """
        Activates the over voltage protection

        :param value: `True` for activation, `False` for deactivation
        """
        validate_bool("ovp", value, logger=logger)
        value_str = f"OVP{1 if value else 0}"
        logger.debug(
            f"Set over voltage protection ({'ON' if value else 'OFF'}) "
            f'with: "{value_str}"'
        )
        self.com.write(value_str)
