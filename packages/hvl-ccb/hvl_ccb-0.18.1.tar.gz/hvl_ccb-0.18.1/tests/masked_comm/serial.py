#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Masked version of SerialCommunication for testing purposes.
"""

from queue import Queue

from hvl_ccb.comm.serial import SerialCommunication
from hvl_ccb.dev.crylas import CryLasLaserSerialCommunication
from hvl_ccb.dev.fug.comm import FuGSerialCommunication
from hvl_ccb.dev.heinzinger import HeinzingerSerialCommunication
from hvl_ccb.dev.ka3000p.comm import KA3000PCommunication
from hvl_ccb.dev.newport import NewportSMC100PPSerialCommunication
from hvl_ccb.dev.pfa2_filter import Pfa2FilterSerialCommunication
from hvl_ccb.dev.pfeiffer_tpg import PfeifferTPGSerialCommunication
from hvl_ccb.dev.sst_luminox import LuminoxSerialCommunication
from hvl_ccb.dev.technix import TechnixSerialCommunication


class LoopSerialCommunication(SerialCommunication):
    """
    Serial communication for the tests with "loop://" port. Masks `write` method
    and adds `put_text` method to put actual values for the serial communication
    protocol to read with the `read_text` method.
    """

    def __init__(self, configuration) -> None:
        super().__init__(configuration)

        self._write_buffer = Queue()

    def write(
        self,
        text: str,
    ) -> None:
        self._write_buffer.put(text)

    def put_text(self, text: str) -> None:
        # super().write(text)
        super().write_bytes(
            text.encode(encoding=self.config.encoding) + self.config.terminator
        )

    def write_bytes(self, data: bytes) -> None:
        self._write_buffer.put(data)

    def put_bytes(self, data: bytes) -> None:
        super().write_bytes(data)

    def get_written(self):
        return self._write_buffer.get() if not self._write_buffer.empty() else None


class CryLasLaserLoopSerialCommunication(
    CryLasLaserSerialCommunication, LoopSerialCommunication
):
    pass


class FuGLoopSerialCommunication(FuGSerialCommunication, LoopSerialCommunication):
    pass


class HeinzingerLoopSerialCommunication(
    HeinzingerSerialCommunication, LoopSerialCommunication
):
    pass


class LuminoxLoopSerialCommunication(
    LuminoxSerialCommunication, LoopSerialCommunication
):
    pass


class NewportLoopSerialCommunication(
    NewportSMC100PPSerialCommunication, LoopSerialCommunication
):
    pass


class Pfa2FilterLoopSerialCommunication(
    Pfa2FilterSerialCommunication, LoopSerialCommunication
):
    pass


class PfeifferTPGLoopSerialCommunication(
    PfeifferTPGSerialCommunication, LoopSerialCommunication
):
    pass


class TechnixLoopSerialCommunication(
    TechnixSerialCommunication, LoopSerialCommunication
):
    pass


class KA3000PLoopCommunication(KA3000PCommunication, LoopSerialCommunication):
    pass
