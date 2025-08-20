#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock OscilloscopeChannelTriggerHystereses
"""

from libtiepie.oscilloscopechanneltriggerhystereses import (
    OscilloscopeChannelTriggerHystereses as LtpOscilloscopeChannelTriggerHystereses,
)


class OscilloscopeChannelTriggerHystereses(LtpOscilloscopeChannelTriggerHystereses):
    def __init__(self) -> None:
        self.items = [1, 2, 3]

    def __getitem__(self, index) -> float:
        return self.items[index]

    def __setitem__(self, index, value) -> None:
        self.items[index] = value

    def __len__(self) -> int:
        return self.count

    def _get_count(self):
        return len(self.items)

    count = property(_get_count)
