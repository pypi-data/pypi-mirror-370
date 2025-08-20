#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock Oscilloscope
"""

from array import array

from libtiepie import const
from libtiepie.oscilloscope import Oscilloscope as LtpOscilloscope

from .const import MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2
from .oscilloscopechannel import OscilloscopeChannel
from .oscilloscopetrigger import OscilloscopeTrigger


class Oscilloscope(LtpOscilloscope):
    """"""

    def __init__(self, serial_number) -> None:
        self._serial_number = serial_number

        self._is_running = False
        self._sample_rate = None
        self._record_length = None
        self._pre_sample_ratio = None
        self._valid_pre_sample_count = None
        self._resolution = None
        self._trigger = OscilloscopeTrigger()
        self._is_data_ready = True
        self._mock_reduce_data = 0
        self._is_triggered = False
        self._auto_resolution_mode = const.ARM_UNKNOWN

        self._channels = []

        # add 3 test channels
        self.add_channel()
        self.add_channel()
        self.add_channel()

        # add physical device parameters
        self._record_length_max = 1e9
        self._sample_rate_max = 1e9
        self._trigger_delay_max = 1
        if serial_number == MOCK_OSCILLOSCOPE_SERIAL_NUMBER_2:
            self._block_measurement_support = False
        else:
            self._block_measurement_support = True

    def add_channel(self) -> None:
        channel = OscilloscopeChannel()
        self._channels.append(channel)

    def _get_channels(self):
        return self._channels

    def _get_trigger(self):
        return self._trigger

    def _get_block_measurement_support(self):
        return self._block_measurement_support

    def _get_measure_modes(self):
        return const.MM_BLOCK if self._block_measurement_support else 0

    def _get_pre_sample_ratio(self):
        return self._pre_sample_ratio

    def _set_pre_sample_ratio(self, value):
        self._pre_sample_ratio = value

    def _get_record_length(self):
        return self._record_length

    def _get_record_length_max(self):
        return self._record_length_max

    def _set_record_length(self, value):
        self._record_length = value

    def _get_valid_pre_sample_count(self):
        return self._valid_pre_sample_count

    def _set_valid_presample_count(self, value):
        self._valid_pre_sample_count = value

    def verify_record_length(self, record_length):
        return record_length

    def _get_resolution(self):
        return self._resolution

    def _set_resolution(self, value):
        self._resolution = value

    def _get_auto_resolution_mode(self):
        return self._auto_resolution_mode

    def _set_auto_resolution_mode(self, value):
        self._auto_resolution_mode = value

    def _get_trigger_delay_max(self):
        return self._trigger_delay_max

    def _get_sample_rate(self):
        return self._sample_rate

    def _set_sample_rate(self, value):
        self._sample_rate = value

    def verify_sample_rate(self, sample_rate):
        return sample_rate

    def _get_sample_rate_max(self):
        return self._sample_rate_max

    def verify_trigger_time_out(self, timeout):
        return timeout

    def _get_is_data_ready(self):
        return self._is_data_ready

    def _set_is_data_ready(self, is_data_ready):
        self._is_data_ready = is_data_ready

    def _get_mock_reduce_data(self):
        return self._mock_reduce_data

    def _set_mock_reduce_data(self, mock_reduce_data):
        self._mock_reduce_data = mock_reduce_data

    def _get_is_triggered(self):
        return self._is_triggered

    def _set_is_triggered(self, is_triggered):
        self._is_triggered = is_triggered

    def _get_is_running(self):
        return self._is_running

    def _set_is_running(self, is_running):
        self._is_running = is_running

    def force_trigger(self) -> None:
        pass

    def start(self) -> bool:
        return True

    def stop(self) -> None:
        pass

    def get_data(self):
        data = [
            (
                array("d", range(self.record_length - 1 - self.mock_reduce_data))
                if ch.enabled
                else None
            )
            # Generate measured data; length is reduced by 1 to mock a non-completely
            # filled buffer
            for _, ch in enumerate(self.channels)
        ]
        self.mock_reduce_data = 0
        return data

    def __del__(self) -> None:
        pass

    measure_modes = property(_get_measure_modes)
    pre_sample_ratio = property(_get_pre_sample_ratio, _set_pre_sample_ratio)
    record_length = property(_get_record_length, _set_record_length)
    valid_pre_sample_count = property(
        _get_valid_pre_sample_count, _set_valid_presample_count
    )
    resolution = property(_get_resolution, _set_resolution)
    auto_resolution_mode = property(
        _get_auto_resolution_mode,
        _set_auto_resolution_mode,
    )
    sample_rate = property(_get_sample_rate, _set_sample_rate)
    channels = property(_get_channels)
    record_length_max = property(_get_record_length_max)
    sample_rate_max = property(_get_sample_rate_max)
    trigger_delay_max = property(_get_trigger_delay_max)

    is_running = property(_get_is_running, _set_is_running)
    is_data_ready = property(_get_is_data_ready, _set_is_data_ready)
    is_triggered = property(_get_is_triggered, _set_is_triggered)
    mock_reduce_data = property(_get_mock_reduce_data, _set_mock_reduce_data)
