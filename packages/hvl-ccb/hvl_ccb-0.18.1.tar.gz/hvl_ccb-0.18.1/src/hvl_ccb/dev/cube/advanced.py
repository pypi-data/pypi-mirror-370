#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
The very special "AdvancedCube" with its two single implementations "SynthCube" and
"FPCSCube".
"""

import logging
from collections.abc import Iterator

from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.enum import BoolEnum
from hvl_ccb.utils.typing import Number

from .base import BaseCube, BaseCubeConfiguration
from .constants import SafetyStatus, _Door
from .errors import (
    AdvancedCubeModuleError,
    ChargerSwitchError,
    DischargeError,
    ShortCircuitError,
)
from .switches import SwitchOperation, _Switch

logger = logging.getLogger(__name__)


class ActivationStatus(BoolEnum):
    """
    Boolean activation status of an advanced cube output bit
    """

    ACTIVATED = True
    DEACTIVATED = False


class PressurizationStatus(BoolEnum):
    """
    Boolean status of an advanced cube pressure sensor
    """

    PRESSURIZED = True
    DEPRESSURIZED = False


class _DischargeSwitch(_Switch):
    """
    Discharge switch within a module of the advanced cube.
    """

    _ERROR_CLS = DischargeError
    _STATES_FOR_SWITCHING = (
        SafetyStatus.RED_READY,
        SafetyStatus.RED_OPERATE,
    )

    def __init__(self, handle, module_number: int) -> None:
        super().__init__(handle, device_name=f"Discharge Switch {module_number}")
        self._CMD_STATUS = (
            f'"DB_Safety_Circuit"."Module_{module_number}".'
            '"Discharge_Circuit"."si_HMI_Status"'
        )
        self._CMD_OPERATING_STATUS = (
            f'"DB_Safety_Circuit"."Module_{module_number}"."sx_able_to_discharge"'
        )
        self._CMD_MANUAL = (
            f'"DB_Safety_Circuit"."Module_{module_number}"."sx_discharge"'
        )


class _ShortCircuitSwitch(_Switch):
    """
    Short-circuit switch within a module of the advanced cube.
    """

    _ERROR_CLS = ShortCircuitError

    def __init__(self, handle, module_number: int) -> None:
        identifier = (
            "Central_Earthing" if module_number == 0 else f"Module_{module_number}"
        )
        super().__init__(handle, device_name=f"Short-Circuit Switch {identifier}")
        identifier_extended = (
            identifier if module_number == 0 else identifier + '"."Short_Circuit'
        )
        self._CMD_STATUS = (
            f'"DB_Safety_Circuit"."{identifier_extended}"."si_HMI_Status"'
        )
        self._CMD_OPERATING_STATUS = (
            f'"DB_Safety_Circuit"."{identifier}"."sx_able_to_short_circuit"'
        )
        self._CMD_MANUAL = None


class _ChargerSwitch(_Switch):
    """
    Charger switch within a module of the advanced cube.
    """

    _ERROR_CLS = ChargerSwitchError
    _STATES_FOR_SWITCHING = (SafetyStatus.RED_OPERATE,)

    def __init__(self, handle, module_number: int) -> None:
        identifier = (
            "Central_Charger" if module_number == 0 else f"Module_{module_number}"
        )
        super().__init__(handle, device_name=f"Charger Switch {identifier}")
        identifier_extended = (
            identifier if module_number == 0 else identifier + '"."Charger_Circuit'
        )
        self._CMD_STATUS = (
            f'"DB_Safety_Circuit"."{identifier_extended}"."si_HMI_Status"'
        )
        self._CMD_OPERATING_STATUS = (
            f'"DB_Safety_Circuit"."{identifier}"."sx_able_to_charge"'
        )
        self._CMD_MANUAL = f'"DB_Safety_Circuit"."{identifier}"."sx_charge"'


class _Module:
    """
    Module level interface between AdvancedCube and current sources.
    """

    _ACTIVATABLE_STATES = (
        SafetyStatus.GREEN_NOT_READY,
        SafetyStatus.GREEN_READY,
    )

    def __init__(self, handle, index: int) -> None:
        self._handle: AdvancedCube = handle
        self._index: int = index
        self.discharge_switch: _DischargeSwitch = _DischargeSwitch(handle, index)
        self.short_circuit_switch: _ShortCircuitSwitch = _ShortCircuitSwitch(
            handle, index
        )
        self.charger_switch: _ChargerSwitch = _ChargerSwitch(handle, index)
        self._CMD_ACTIVE: str = f'"DB_Safety_Circuit"."Module_{index}"."sx_dial"'
        self._CMD_VOLTAGE: str = f'"DB_Safety_Circuit"."Module_{index}"."si_voltage"'
        self._CMD_MAX_SC_SWITCHING_VOLTAGE: str = (
            f'"DB_Safety_Circuit"."Module_{index}".'
            '"Ir_max_short_circuit_switching_voltage"'
        )

    def __repr__(self) -> str:
        return f"Module {self._index}"

    @property
    def active(self) -> ActivationStatus:
        """
        Module activation status

        :return: boolean module activation status
        """
        activation_status = ActivationStatus(self._handle.read(self._CMD_ACTIVE))
        logger.info(f"Module {self._index} is {activation_status.name}")
        return activation_status

    @active.setter
    def active(self, new_activation_status: ActivationStatus):
        new_activation_status = ActivationStatus(new_activation_status)
        if self._handle.status in self._ACTIVATABLE_STATES:
            self._handle.write(self._CMD_ACTIVE, new_activation_status)
            logger.info(f"Module {self._index} set to {new_activation_status.name}")
        else:
            msg = (
                f"Tried to set Module {self._index} to {new_activation_status.name}. "
                "Safety circuit must be in green state to change the activation "
                f"status of a module, but is in {self._handle.status.name}"
            )
            logger.error(msg)
            raise AdvancedCubeModuleError(msg)

    @property
    def voltage(self) -> int:
        """
        Measured voltage of a module.

        :return: measured voltage in V
        """
        voltage = int(self._handle.read(self._CMD_VOLTAGE))
        logger.info(f"Module {self._index} voltage: {voltage} V")
        return voltage

    @property
    def max_short_circuit_switching_voltage(self) -> int:
        """
        Maximum switching voltage of a module.

        :return: maximum switching voltage in V
        """
        voltage = int(self._handle.read(self._CMD_MAX_SC_SWITCHING_VOLTAGE))
        logger.info(
            f"Maximum short-circuit switching voltage of Module {self._index}"
            f" is set to {voltage} V"
        )
        return voltage


class _Pneumatics:
    """
    Pneumatic circuit of a current source controlled by an AdvancedCube
    """

    _CMD_STATUS = '"Ix_Allg_pressure_ok"'
    _CMD_ACTIVE = '"Qx_Allg_Main_Pressure"'

    def __init__(self, handle) -> None:
        self._handle: AdvancedCube = handle

    @property
    def status(self) -> PressurizationStatus:
        """
        Pneumatic circuit pressure status

        :return: boolean pressurization status
        """
        status = PressurizationStatus(self._handle.read(self._CMD_STATUS))
        logger.info(f"Pneumatic circuit is {status.name}")
        return status

    @property
    def active(self) -> ActivationStatus:
        """
        Pressure valve activation status

        :return: boolean pressure valve activation status
        """
        activation_status = ActivationStatus(self._handle.read(self._CMD_ACTIVE))
        logger.info(f"Main pressure valve is {activation_status.name}")
        return activation_status

    @active.setter
    def active(self, new_activation_status: ActivationStatus):
        new_activation_status = ActivationStatus(new_activation_status)
        self._handle.write(self._CMD_ACTIVE, new_activation_status)
        logger.info(f"Main pressure valve {new_activation_status.name}")


class _Siren:
    """
    Acoustic alert device controlled by an AdvancedCube
    """

    def __init__(self, handle, index: int, name: str) -> None:
        self._handle: AdvancedCube = handle
        self._name = name
        self._CMD_ACTIVE: str = f'"Qx_Allg_Acoustic_{index}"'

    @property
    def active(self) -> ActivationStatus:
        """
        Siren activation status

        :return: boolean siren activation status
        """
        active = ActivationStatus(self._handle.read(self._CMD_ACTIVE))
        logger.info(f"{self._name} siren is {active.name}")
        return active

    @active.setter
    def active(self, active: ActivationStatus):
        active = ActivationStatus(active)
        self._handle.write(self._CMD_ACTIVE, active)
        logger.info(f"{self._name} siren has been {active.name}")


@configdataclass
class AdvancedCubeConfiguration(BaseCubeConfiguration):
    """Adaption of base configuration to accept longer time to wait for a discharge"""

    timeout_status_change: Number = 20


class AdvancedCube(BaseCube):
    """
    The AdvancedCube is the template for its two special implementations
    """

    _N_MODULES: int | None = None

    def __init__(self, com, dev_config=None) -> None:
        super().__init__(com, dev_config)
        self.modules: dict[int, _Module] = {}
        self.pneumatics: _Pneumatics | None = None
        self.charging_siren: _Siren | None = None
        self.triggering_siren: _Siren | None = None

    @staticmethod
    def config_cls():
        return AdvancedCubeConfiguration

    @property
    def number_of_modules(self) -> int:
        """
        Queries the number of installed modules (active plus inactive)
        """
        if self._N_MODULES is None:
            msg = "No number of modules was set in implementation."
            logger.error(msg)
            raise AdvancedCubeModuleError(msg)

        val = self._N_MODULES
        logger.info(f"{self.__class__.__name__} has {val} modules installed.")
        return val

    def start(self) -> None:
        """
        Start the connection to the AdvancedCube and set up the modules
        """
        super().start()

        try:
            _ = self.number_of_modules
        except AdvancedCubeModuleError:
            self.stop()
            raise

        for ii in range(self.number_of_modules):
            self.modules[ii + 1] = _Module(self, ii + 1)

        self.pneumatics = _Pneumatics(self)
        self.charging_siren = _Siren(self, 1, name="Charging")
        self.triggering_siren = _Siren(self, 2, name="Triggering")

    @property
    def active_modules(self) -> Iterator[_Module]:
        """
        Iterator for all active modules
        """
        for module in self.modules.values():
            if module.active == ActivationStatus.ACTIVATED:
                yield module

    @property
    def operate_discharge_switches(self) -> list[SwitchOperation]:
        """
        Property to query all discharge switches of the installed/active modules

        :return: `list[SwitchOperation]` of the individual discharge switches
        """
        return [module.discharge_switch.operate for module in self.active_modules]

    @operate_discharge_switches.setter
    def operate_discharge_switches(self, operation: SwitchOperation) -> None:
        """
        Operate all discharge switches of the installed/active modules

        :param operation: a `SwitchOperation` to `OPEN` or `CLOSE`
        """
        for module in self.active_modules:
            module.discharge_switch.operate = operation


class SynthCube(AdvancedCube):
    """
    The SynthCube is the special Cube for the Synthetic Circuit
    """

    _N_MODULES = 4

    def __init__(self, com, dev_config=None) -> None:
        super().__init__(com, dev_config)
        self.hcc_loop_1: _Module | None = None
        self.hcc_loop_2: _Module | None = None
        self.hcc_loop_3: _Module | None = None
        self.cic: _Module | None = None

    def start(self) -> None:
        super().start()
        self.hcc_loop_1 = self.modules[1]
        self.hcc_loop_2 = self.modules[2]
        self.hcc_loop_3 = self.modules[3]
        self.cic = self.modules[4]

    @property
    def active_hcc_loops(self) -> Iterator[_Module]:
        """
        Iterator for all active high-current modules
        """
        for module in self.active_modules:
            if module in (self.hcc_loop_1, self.hcc_loop_2, self.hcc_loop_3):
                yield module


class FPCSCube(AdvancedCube):
    """
    The FPCSCube is the special Cube for the FPCS
    """

    _N_MODULES = 8

    door_fpcs_status = _Door("FPCS", "door status")

    def __init__(self, com, dev_config=None) -> None:
        super().__init__(com, dev_config)
        self.central_earthing: _ShortCircuitSwitch | None = None
        self.central_charger: _ChargerSwitch | None = None
        self.module: dict[str, _Module] = {}

    def start(self) -> None:
        super().start()
        for ii in range(self._N_MODULES):
            self.module[chr(ord("A") + ii)] = self.modules[ii + 1]
            self.module[chr(ord("a") + ii)] = self.modules[ii + 1]
        self.central_charger = _ChargerSwitch(self, 0)
        self.central_earthing = _ShortCircuitSwitch(self, 0)
