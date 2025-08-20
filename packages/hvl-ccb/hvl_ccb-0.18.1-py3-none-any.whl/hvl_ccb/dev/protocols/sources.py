#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
from typing import Protocol, runtime_checkable

from hvl_ccb.utils.typing import Number


@runtime_checkable
class Source(Protocol):
    """
    Protocol for a voltage/current source

    (Future) Implementations:
        - `ea_psi9000.PSI9000`
        - `fug.Fug`
        - `heinzinger.HeinzingerPNC`
        - `technix.Technix`
        - `ka3000p.KA3000P`
    """

    # maximum output voltage of the hardware
    _max_voltage_hardware: Number
    # maximum output current of the hardware
    _max_current_hardware: Number

    # Voltage and current values
    @property
    def voltage(self) -> Number:
        """Return the measured output voltage in V"""
        return 0

    @voltage.setter
    def voltage(self, value: Number) -> None:
        """Set the output voltage"""

    @property
    def current(self) -> Number:
        """Return the measured output current in A"""
        return 0

    @current.setter
    def current(self, value: Number) -> None:
        """Set the output current"""

    @property
    def set_voltage(self) -> Number:
        """Return the set voltage (may differ from actual value) in V"""
        return 0

    @set_voltage.setter
    def set_voltage(self, value: Number) -> None:
        """Set the output voltage"""
        self.voltage = value

    @property
    def set_current(self) -> Number:
        """Return the set current (may differ from actual value) in A"""
        return 0

    @set_current.setter
    def set_current(self, value: Number) -> None:
        """Set the output current"""
        self.current = value

    @property
    def max_voltage(self) -> Number:
        """Maximal output voltage of the hardware in V,
        but user can reset to a lower value"""
        return self._max_voltage_hardware

    @property
    def max_current(self) -> Number:
        """Maximal output current of the hardware in A,
        but user can reset to a lower value"""
        return self._max_current_hardware

    # Output stage
    @property
    def output(self) -> bool | None:
        """State of the high voltage output"""
        return False

    @output.setter
    def output(self, value: bool) -> None:
        """
        Activates the output of the source

        :param value: `True` for activation, `False` for deactivation
        """
