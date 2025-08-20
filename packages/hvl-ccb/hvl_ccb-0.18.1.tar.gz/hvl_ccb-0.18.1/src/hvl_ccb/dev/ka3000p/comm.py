#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""Communication protocol for the KA3000P laboratory power supplies"""

import logging

from hvl_ccb.comm.base import SyncCommunicationProtocol
from hvl_ccb.comm.serial import SerialCommunication, SerialCommunicationConfig
from hvl_ccb.dev.ka3000p.base import KA3000PError

logger = logging.getLogger(__name__)


class KA3000PCommunicationConfig(SerialCommunicationConfig): ...


class KA3000PCommunication(SerialCommunication, SyncCommunicationProtocol):
    """Communication Protocol for KA3000P"""

    @staticmethod
    def config_cls():
        return KA3000PCommunicationConfig

    def query_not_none(
        self,
        command: str,
        n_attempts_max: int | None = None,
        attempt_interval_sec: float | None = None,
    ) -> str:
        value = self.query(command, n_attempts_max, attempt_interval_sec)

        if value is None:
            msg = (
                f'Did not recieved any responce on query "{command}", '
                "but expected something"
            )
            logger.error(msg)
            raise KA3000PError(msg)
        return value
