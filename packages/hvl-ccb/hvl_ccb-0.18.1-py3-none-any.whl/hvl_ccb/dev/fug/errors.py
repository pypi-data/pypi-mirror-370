#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Errors and their codes of FuG
"""

import logging

from hvl_ccb.dev.base import DeviceError
from hvl_ccb.utils.enum import NameEnum

logger = logging.getLogger(__name__)


class FuGError(DeviceError):
    """
    Error with the FuG voltage source.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.errorcode: str = kwargs.pop("errorcode", "")
        """
        Errorcode from the Probus, see documentation of Probus V chapter 5.
        Errors with three-digit errorcodes are thrown by this python module.
        """
        super().__init__(*args, **kwargs)


class FuGErrorcodes(NameEnum, init="description possible_reason"):  # type: ignore[call-arg]
    """
    The power supply can return an errorcode. These errorcodes are handled by this
    class. The original errorcodes from the source are with one or two digits,
    see documentation of Probus V chapter 5.
    All three-digit errorcodes are from this python module.
    """

    E0 = "no error", "standard response on each command"
    E1 = (
        "no data available",
        (
            "Customer tried to read from GPIB but there were no data prepared. "
            "(IBIG50 sent command ~T2 to ADDA)"
        ),
    )
    E2 = "unknown register type", "No valid register type after '>'"
    E4 = (
        "invalid argument",
        "The argument of the command was rejected .i.e. malformed number",
    )
    E5 = "argument out of range", "i.e. setvalue higher than type value"
    E6 = (
        "register is read only",
        "Some registers can only be read but not written to. (i.e. monitor registers)",
    )
    E7 = "Receive Overflow", "Command string was longer than 50 characters."
    E8 = (
        "EEPROM is write protected",
        (
            "Write attempt to calibration data while the write protection switch was"
            " set to write protected."
        ),
    )
    E9 = (
        "address error",
        (
            "A non addressed command was sent to ADDA while it was in addressable mode "
            "(and vice versa)."
        ),
    )
    E10 = "unknown SCPI command", "This SCPI command is not implemented"
    E11 = (
        "not allowed Trigger-on-Talk",
        (
            "Not allowed attempt to Trigger-on-Talk (~T1) while ADDA was in addressable"
            " mode."
        ),
    )
    E12 = "invalid argument in ~Tn command", "Only ~T1 and ~T2 is implemented."
    E13 = (
        "invalid N-value",
        (
            "Register > K8 contained an invalid value. Error code is output on an"
            " attempt to query data with ? or ~T1"
        ),
    )
    E14 = "register is write only", "Some registers can only be writte to (i.e.> H0)"
    E15 = "string too long", "i.e.serial number string too long during calibration"
    E16 = (
        "wrong checksum",
        (
            "checksum over command string was not correct, refer also to 4.4 of the "
            "Probus V documentation"
        ),
    )
    E100 = (
        "Command is not implemented",
        "You tried to execute a command, which is not implemented or does not exist",
    )
    E106 = (
        "The rampstate is a read-only register",
        (
            "You tried to write data to the register, which can only give "
            "you the status of the ramping."
        ),
    )
    E206 = (
        "This status register is read-only",
        (
            "You tried to write data to this "
            "register, which can only give you "
            "the actual status of the "
            "corresponding digital output."
        ),
    )
    E306 = (
        "The monitor register is read-only",
        "You tried to write data to a monitor, which can only give you measured data.",
    )
    E115 = (
        "The given index to select a digital value is out of range",
        "Only integer values between 0 and 1 are allowed.",
    )
    E125 = (
        "The given index to select a ramp mode is out of range",
        "Only integer values between 0 and 4 are allowed.",
    )
    E135 = (
        "The given index to select the readback channel is out of range",
        "Only integer values between 0 and 6 are allowed.",
    )
    E145 = (
        "The given value for the AD-conversion is unknown",
        'Valid values for the ad-conversion are integer values from "0" to "7".',
    )
    E155 = (
        "The given value to select a polarity is out range.",
        "The value should be 0 or 1.",
    )
    E165 = "The given index to select the terminator string is out of range", ""
    E504 = "Empty string as response", "The connection is broken."
    E505 = (
        "The returned register is not the requested.",
        "Maybe the connection is overburden.",
    )
    E666 = (
        (
            "You cannot overwrite the most recent error in the interface of the power"
            " supply. But, well: You created an error anyway..."
        ),
        "",
    )

    def raise_(self) -> None:
        """
        Evaluate the error code and raise a `FuGError` if the error code is not `E0`
        """
        if self is FuGErrorcodes.E0:
            logger.debug('Communication with FuG successful, errorcode "E0" received.')
            return
        logger.debug(f"A FuGError with the errorcode {self.name} was detected.")
        msg = f"{self.description}. Possible reason: {self.possible_reason}"
        logger.exception(msg)
        raise FuGError(msg, errorcode=self.name)
