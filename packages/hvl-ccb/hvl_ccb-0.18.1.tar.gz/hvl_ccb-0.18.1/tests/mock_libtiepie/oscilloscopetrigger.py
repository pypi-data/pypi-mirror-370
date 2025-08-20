#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock OscilloscopeTrigger

"""

from libtiepie.oscilloscope import Oscilloscope as LtpOscilloscopeTrigger


class OscilloscopeTrigger(LtpOscilloscopeTrigger):
    """"""

    def __init__(self) -> None:
        self._timeout = None

    def __del__(self) -> None:
        pass

    def _get_timeout(self):
        """ """
        return self._timeout

    def _set_timeout(self, value):
        self._timeout = value

    def verify_timeout(self, value):
        """Verify if a required trigger time out can be set, without actually setting
        the hardware itself.

        :param value: The required trigger time out in seconds,
            or #TIEPIE_HW_TO_INFINITY.
        :returns: The trigger time out that would have been set,
            if tiepie_hw_oscilloscope_trigger_set_timeout() was used.
        .. version added:: 1.0
        """
        return value

    def verify_timeout_ex(self, value, measure_mode, sample_rate) -> None:
        """Verify if a required trigger time out can be set, without actually setting
        the hardware itself.

        :param value: The required trigger time out in seconds, or
            #TIEPIE_HW_TO_INFINITY.
        :param measure_mode: Measure mode, a TIEPIE_HW_MM_* value.
        :param sample_rate: Sample rate in Hz.
        :returns: The trigger time out that would have been set,
            if tiepie_hw_oscilloscope_trigger_set_timeout() was used.
        .. version added:: 1.0
        """

    def _get_has_delay(self):
        """ """
        return

    def has_delay_ex(self, measure_mode) -> None:
        """Check whether the oscilloscope has trigger delay support for a specified
        measure mode.

        :param measure_mode: Measure mode, a TIEPIE_HW_MM_* value.
        :returns: ``True`` if the oscilloscope has trigger delay support,
            ``False`` otherwise.
        .. version added:: 1.0
        """

    def _get_delay_max(self):
        """Maximum trigger delay in seconds, for the currently selected measure mode and
        sample rate."""
        return

    def get_delay_max_ex(self, measure_mode, sample_rate) -> None:
        """Get the maximum trigger delay in seconds, for a specified measure mode and
        sample rate.

        :param measure_mode: Measure mode, a TIEPIE_HW_MM_* value.
        :param sample_rate: Sample rate in Hz.
        :returns: The maximum trigger delay in seconds.
        .. version added:: 1.0
        """

    def _get_delay(self):
        """Currently selected trigger delay in seconds."""
        return

    def _set_delay(self, value): ...

    def verify_delay(self, value) -> None:
        """Verify if a required trigger delay can be set, without actually setting the
        hardware itself.

        :param value: The required trigger delay in seconds.
        :returns: The trigger delay that would have been set,
            if tiepie_hw_oscilloscope_trigger_set_delay() was used.
        .. version added:: 1.0
        """

    def verify_delay_ex(self, value, measure_mode, sample_rate) -> None:
        """Verify if a required trigger delay can be set, without actually setting the
        hardware itself.

        :param value: The required trigger delay in seconds.
        :param measure_mode: Measure mode, a TIEPIE_HW_MM_* value.
        :param sample_rate: Sample rate in Hz.
        :returns: The trigger delay that would have been set,
            if tiepie_hw_oscilloscope_trigger_set_delay() was used.
        .. version added:: 1.0
        """

    timeout = property(_get_timeout, _set_timeout)
    has_delay = property(_get_has_delay)
    delay_max = property(_get_delay_max)
    delay = property(_get_delay, _set_delay)
