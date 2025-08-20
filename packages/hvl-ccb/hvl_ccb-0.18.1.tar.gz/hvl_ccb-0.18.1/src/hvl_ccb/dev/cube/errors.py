#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Errors of the different "Cubes".
"""

from hvl_ccb.dev import DeviceError


class CubeError(DeviceError):
    pass


class CubeStatusChangeError(CubeError):
    pass


class CubeStopError(CubeError):
    pass


class CubeRemoteControlError(CubeError):
    pass


class SwitchOperationError(CubeError):
    pass


class CubeEarthingStickOperationError(SwitchOperationError):
    pass


class DischargeError(SwitchOperationError):
    pass


class ShortCircuitError(SwitchOperationError):
    pass


class ChargerSwitchError(SwitchOperationError):
    pass


class PICubeTestParameterError(CubeError):
    pass


class AdvancedCubeModuleError(CubeError):
    pass
