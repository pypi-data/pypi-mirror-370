#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
VISA masked communication protocol module.
"""

from collections import defaultdict
from queue import Queue

from hvl_ccb.comm.visa import VisaCommunication
from hvl_ccb.utils.typing import Number


class MaskedVisaCommunication(VisaCommunication):
    """
    Masked version of VisaCommunication to simulate messages.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._read_buffer = defaultdict(Queue)
        self._write_buffer = Queue()

        self.stb = 0

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def write(self, text: str) -> None:
        if text == "*OPC":
            self.put_name("*ESR?", "1")

        self._write_buffer.put(text)

    def write_multiple(self, *commands: str) -> None:
        if "*OPC" in commands:
            # operation complete request set, immediately reply
            self.put_name("*ESR?", "1")

        for command in commands:
            self._write_buffer.put(command)

    def query(
        self,
        command: str,
        _n_attempts_max: int | None = None,
        _attempt_interval_sec: Number | None = None,
    ) -> str | None:
        return (
            self._read_buffer[command].get()
            if not self._read_buffer[command].empty()
            else "0"
        )

    def query_multiple(self, *commands: str) -> str | tuple[str, ...]:
        out = [
            (
                self._read_buffer[command].get()
                if not self._read_buffer[command].empty()
                else "0"
            )
            for command in commands
        ]

        return out[0] if len(out) == 1 else tuple(out)

    def spoll(self) -> int:
        return self.stb

    def put_name(self, command: str, string: str) -> None:
        self._read_buffer[command].put(string)

    def get_written(self) -> str | None:
        return self._write_buffer.get() if not self._write_buffer.empty() else None
