#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Base classes for the PFA-2 filter from Precision Filter Inc..

The PFA-2 filter is a high-precision, low-noise analog filter commonly used in
laboratory instrumentation and signal conditioning setups. It is suitable for
applications requiring clean signal output, such as spectroscopy, low-level
voltage measurements, signal recovery and high-resolution data acquisition.

The class PFA2Filter has been tested with a PFA-2 (with option H) unit.
Verify compatibility with your specific filter variant before use,
especially for units with custom or user-modified settings.

Product information and technical details:
https://pfinc.com/product/precision-pfa-2-filter-amplifier
"""

from typing import Literal

from aenum import StrEnum

from hvl_ccb.comm.base import CommunicationError, SyncCommunicationProtocol
from hvl_ccb.comm.serial import SerialCommunication, SerialCommunicationConfig
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import DeviceError
from hvl_ccb.utils.enum import RangeEnum

N_CHANNELS: int = 2
LPF_FREQUENCY_MIN: int = 5
LPF_FREQUENCY_MAX: int = 127_750
HPF_FREQUENCY_MIN: int = 1
HPF_FREQUENCY_MAX: int = 127_500


class Pfa2FilterCommunicationError(CommunicationError):
    pass


class Pfa2FilterError(DeviceError):
    pass


@configdataclass
class Pfa2FilterSerialCommunicationConfig(SerialCommunicationConfig):
    """
    Specific communication config implementation for for PFA-2 filters
    Predefines device-specific protocol parameters.
    """

    baudrate: int = 57600  # PFA-2 filter uses 57600 baud


class Pfa2FilterSerialCommunication(SerialCommunication, SyncCommunicationProtocol):
    """
    Specific communication protocol implementation for PFA-2 filters.
    Predefines device-specific protocol parameters in config.
    """

    def __init__(self, configuration) -> None:
        super().__init__(configuration)

    @staticmethod
    def config_cls():
        return Pfa2FilterSerialCommunicationConfig


class Pfa2FilterChannelMode(StrEnum):
    """StrEnum for the channel modes"""

    OPERATE = "OPERATE"
    CALIBRATION = "CAL"
    SHORTED = "SHORT"


class Pfa2FilterChannelCoupling(StrEnum):
    """StrEnum for the channel coupling"""

    AC = "AC"
    DC = "DC"


class Pfa2FilterLPFMode(StrEnum):
    """StrEnum for the low pass filter mode"""

    FLAT = "FLAT"
    PULSE = "PULSE"
    OFF = "NONE"


class Pfa2FilterHPFState(StrEnum):
    """StrEnum for the high pass filter state"""

    ON = "ON"
    OFF = "OFF"


class Pfa2FilterPreGain(RangeEnum):
    """RangeEnum for the pre filter gain value"""

    @classmethod
    def unit(cls) -> Literal[""]:
        return ""

    @classmethod
    def is_reversed(cls) -> bool:
        return True

    ONE: float = 1
    TWO: float = 2
    FOUR: float = 4
    EIGHT: float = 8
    SIXTEEN: float = 16
    THIRTY_TWO: float = 32
    SIXTY_FOUR: float = 64
    ONE_HUNDRED_TWENTY_EIGHT: float = 128


class Pfa2FilterPostGain(RangeEnum):
    """RangeEnum for the post filter gain value"""

    @classmethod
    def unit(cls) -> Literal[""]:
        return ""

    @classmethod
    def is_reversed(cls) -> bool:
        return True

    ONE_SIXTEENTH: float = 0.0625
    ONE_EIGHT: float = 0.125
    ONE_QUARTER: float = 0.25
    ONE_HALF: float = 0.5
    ONE: float = 1
    TWO: float = 2
    FOUR: float = 4
    EIGHT: float = 8
    SIXTEEN: float = 16


class Pfa2FilterOverloadMode(StrEnum):
    """StrEnum for the overload handling mode"""

    LATCHING = "LATCHING"
    CONTINUOUS = "CONTINUOUS"


class _Pfa2FilterCommands(StrEnum):
    """StrEnum for the PFA-2 filter commands"""

    COUPLING = "COUPLING"
    MODE = "MODE"
    PREGAIN = "PREGAIN"
    POSTGAIN = "POSTGAIN"
    LPF_TYPE = "LPFILTTYPE"
    LPF_FREQUENCY = "LPFC"
    HPF_STATE = "HPFILT"
    HPF_TYPE = "HPFILTTYPE"
    HPF_FREQUENCY = "HPFC"
    IN_OVERLOAD = "INOVLD"
    OUT_OVERLOAD = "OUTOVLD"
    OVERLOAD_LIMIT = "OUTOVLDLIM"
    OVERLOAD_MODE = "OVLDMODE"
    OVERLOAD_CLEAR = "OVLDCLEAR"

    def build_str(self, channel: int, param: str | None = None) -> str:
        """
        Build a command string for sending to the device.

        getter example: Pfa2FilterCommands.COUPLING.build_str(1)-->"1:COUPLING?"
        setter example: Pfa2FilterCommands.COUPLING.build_str(1, 'AC')-->"1:COUPLING=AC"


        :param param: Command's parameter given as string
        :return: Command's string
        """
        action = "?" if param is None else f"={param}"

        return f"{channel}:{self.value}{action}"
