#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device class for Newport SMC100PP stepper motor controller with serial communication.

The SMC100PP is a single axis motion controller/driver for stepper motors up to 48 VDC
at 1.5 A rms. Up to 31 controllers can be networked through the internal RS-485
communication link.

Manufacturer homepage:
https://www.newport.com/f/smc100-single-axis-dc-or-stepper-motion-controller
"""

from .newport import (  # noqa: F401
    NewportConfigCommands,
    NewportControllerError,
    NewportMotorError,
    NewportMotorPowerSupplyWasCutError,
    NewportSerialCommunicationError,
    NewportSMC100PP,
    NewportSMC100PPConfig,
    NewportSMC100PPSerialCommunication,
    NewportSMC100PPSerialCommunicationConfig,
    NewportStates,
    NewportUncertainPositionError,
)
