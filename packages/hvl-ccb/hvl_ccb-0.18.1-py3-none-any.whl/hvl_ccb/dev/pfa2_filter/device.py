#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
The main device class for the PFA-2 filter from Precision Filter Inc..

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

import logging

from hvl_ccb import configdataclass
from hvl_ccb.dev.base import SingleCommDevice
from hvl_ccb.utils.validation import validate_number

from .base import (
    HPF_FREQUENCY_MAX,
    HPF_FREQUENCY_MIN,
    LPF_FREQUENCY_MAX,
    LPF_FREQUENCY_MIN,
    N_CHANNELS,
    Pfa2FilterChannelCoupling,
    Pfa2FilterChannelMode,
    Pfa2FilterCommunicationError,
    Pfa2FilterError,
    Pfa2FilterHPFState,
    Pfa2FilterLPFMode,
    Pfa2FilterOverloadMode,
    Pfa2FilterPostGain,
    Pfa2FilterPreGain,
    Pfa2FilterSerialCommunication,
    _Pfa2FilterCommands,
)

logger = logging.getLogger(__name__)


@configdataclass
class Pfa2FilterConfig:
    """Init configuration of a filter channel."""

    # Define whether the filter has the high pass filter option, default is True
    device_option_hpf: bool = True

    # Default values for both filter channels
    # Coupling mode, default is DC
    coupling_init: Pfa2FilterChannelCoupling | str = Pfa2FilterChannelCoupling.DC
    # Input mode, default is OPERATE
    mode_init: Pfa2FilterChannelMode | str = Pfa2FilterChannelMode.OPERATE
    # Pre filter gain, default is 1
    pregain_init: Pfa2FilterPreGain | float = Pfa2FilterPreGain.ONE
    # Post filter gain, default is 1
    postgain_init: Pfa2FilterPostGain | float = Pfa2FilterPostGain.ONE
    # Low pass filter frequency, default is 127750 Hz
    lpf_freq_init: int = LPF_FREQUENCY_MAX
    # Low pass filter mode, default is FLAT
    lpf_mode_init: Pfa2FilterLPFMode | str = Pfa2FilterLPFMode.FLAT
    # High pass filter state, default is ON
    hpf_state_init: bool = True
    # High pass filter frequency, default is 1 Hz
    hpf_freq_init: int = HPF_FREQUENCY_MIN
    # Overload limit, default is 10 V
    overload_limit_init: float = 10
    # Overload handling mode, default is CONTINUOUS
    overload_mode_init: Pfa2FilterOverloadMode | str = Pfa2FilterOverloadMode.CONTINUOUS


class Pfa2Filter(SingleCommDevice):
    """Device class to control the PFA-2 filter"""

    def __init__(self, com, dev_config=None) -> None:
        super().__init__(com, dev_config)

        self.channel_dict: dict[int, Channel] = {
            index: Channel(index, self.com, self.config.device_option_hpf)
            for index in range(N_CHANNELS)
        }

    def __str__(self) -> str:
        return "PFA-2 Filter"

    @staticmethod
    def config_cls() -> type[Pfa2FilterConfig]:
        return Pfa2FilterConfig

    @staticmethod
    def default_com_cls() -> type[Pfa2FilterSerialCommunication]:
        return Pfa2FilterSerialCommunication

    def start(self) -> None:
        """Starting the PFA-2 Filter"""

        logger.info(f"Starting device {self}")
        super().start()

        for channel in self.channel_dict.values():
            channel.coupling = self.config.coupling_init
            channel.input_mode = self.config.mode_init
            channel.pregain = self.config.pregain_init
            channel.postgain = self.config.postgain_init
            channel.lpf_freq = self.config.lpf_freq_init
            channel.lpf_mode = self.config.lpf_mode_init
            channel.overload_limit = self.config.overload_limit_init
            channel.overload_mode = self.config.overload_mode_init
            if self.config.device_option_hpf:
                channel.hpf_state = self.config.hpf_state_init
                channel.hpf_freq = self.config.hpf_freq_init

        logger.info("Initial settings applied")

    def stop(self) -> None:
        """
        Stop this device and close the communication protocol.
        """
        if not self.com.is_open:
            logger.warning(f"Device {self} already stopped")
            return

        logger.info(f"Stopping device {self}")
        super().stop()


class Channel:
    """
    Class to control a single channel of the PFA-2 filter.
    Will be used for each channel.
    """

    def __init__(
        self, channel: int, com: Pfa2FilterSerialCommunication, option_hpf: bool
    ) -> None:
        self._com: Pfa2FilterSerialCommunication = com
        self._channel: int = channel
        self._option_hpf: bool = option_hpf

    @property
    def coupling(self) -> Pfa2FilterChannelCoupling:
        """
        Get the coupling of the channel

        AC: AC coupling
        DC: DC coupling

        :raises Pfa2FilterCommunicationError: When the device does not respond
        :return: Channel coupling as Pfa2FilterChannelCoupling
        """
        value = self._com.query(_Pfa2FilterCommands.COUPLING.build_str(self._channel))  # type: ignore[attr-defined]
        if value is None:
            err_msg = "The device did not respond with a valid coupling value"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        value = Pfa2FilterChannelCoupling(value)
        logger.info(f"Coupling for channel {self._channel} is '{value.name}'")
        return value

    @coupling.setter
    def coupling(self, value: Pfa2FilterChannelCoupling | str) -> None:
        """
        Set the AC/DC coupling for the channel

        :param value: Value from Pfa2FilterChannelCoupling
        :raises TypeError: When value is not a string
        :raises ValueError: When value is not in Pfa2FilterChannelCoupling
        :raises Pfa2FilterCommunicationError: When the device does not respond
        """
        if not isinstance(value, str):
            raise TypeError
        if value not in Pfa2FilterChannelCoupling:  # type: ignore[attr-defined]
            raise ValueError

        response = self._com.query(
            _Pfa2FilterCommands.COUPLING.build_str(self._channel, value)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = "The device did not respond with a valid coupling value"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterChannelCoupling(response)
        logger.info(
            f"Setting coupling to '{response.name}' for channel {self._channel}"
        )

    @property
    def input_mode(self) -> Pfa2FilterChannelMode:
        """
        Get the input mode

        OPERATE: Channel is operational
        CALIBRATION: Channel routed to calibration input
        SHORT: Channel is shorted to ground

        :raises Pfa2FilterCommunicationError: When input mode is not set or unknown
        :return: Input mode as Pfa2FilterChannelMode
        """
        value = self._com.query(_Pfa2FilterCommands.MODE.build_str(self._channel))  # type: ignore[attr-defined]
        if value is None:
            err_msg = f"Input mode for channel {self._channel} is not set or unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        value = Pfa2FilterChannelMode(value)
        logger.debug(f"Input mode for channel {self._channel} is '{value}'")
        return value

    @input_mode.setter
    def input_mode(self, value: Pfa2FilterChannelMode | str) -> None:
        """
        Sets the input mode

        :param value: Value from Pfa2FilterChannelMode
        :raises TypeError: When value is not a string
        :raises ValueError: When value is not in Pfa2FilterChannelMode
        :raises Pfa2FilterCommunicationError: When the device does not respond
        """
        if not isinstance(value, str):
            raise TypeError
        if value not in Pfa2FilterChannelMode:  # type: ignore[attr-defined]
            raise ValueError

        response = self._com.query(
            _Pfa2FilterCommands.MODE.build_str(self._channel, value)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Input mode for channel {self._channel} is not set or unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterChannelMode(response)
        logger.info(f"Setting input mode to '{response}' for channel {self._channel}")

    @property
    def lpf_mode(self) -> Pfa2FilterLPFMode:
        """
        Get the operation mode of the low pass filter

        OFF: Filter is disabled
        PULSE: For measurements if time domain
        FLAT: For measurements in frequency domain

        :raise Pfa2FilterCommunicationError: When LPF mode is not set or unknown
        :return: LPF filter mode as Pfa2FilterLPFMode
        """
        response = self._com.query(
            _Pfa2FilterCommands.LPF_TYPE.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"LPF mode for channel {self._channel} is not set or unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterLPFMode(response)  # type: ignore[attr-defined]
        logger.debug(f"LPF mode for channel {self._channel} is '{response}'")
        return response

    @lpf_mode.setter
    def lpf_mode(self, value: Pfa2FilterLPFMode | str) -> None:
        """
        Set the operation mode of the low pass filter

        :param value: Value from Pfa2FilterLPFMode
        :raises TypeError: When value is not a string
        :raises ValueError: When value is not in Pfa2FilterLPFMode
        :raises Pfa2FilterCommunicationError: When LPF mode could not be set
        """
        if not isinstance(value, str):
            raise TypeError
        if value not in Pfa2FilterLPFMode:  # type: ignore[attr-defined]
            raise ValueError

        response = self._com.query(
            _Pfa2FilterCommands.LPF_TYPE.build_str(self._channel, value)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"LPF mode for channel {self._channel} is not set or unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterLPFMode(response)  # type: ignore[attr-defined]
        logger.info(f"Setting LPF mode to '{response}' for channel {self._channel}")

    @property
    def lpf_freq(self) -> int:
        """
        Get the set 3 dB cut off frequency of the low pass filter

        :raises Pfa2FilterCommunicationError: When the device does not respond
        :return: Frequency in Hz
        """
        response_str = self._com.query(
            _Pfa2FilterCommands.LPF_FREQUENCY.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response_str is None:
            err_msg = f"LPF frequency for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = int(response_str)
        logger.debug(f"LPF frequency for channel {self._channel} is {response} Hz")
        return response

    @lpf_freq.setter
    def lpf_freq(self, value: int) -> None:
        """
        Set the 3 dB cut of frequency for the low pass filter

        :param value: Frequency in Hz
        :raises Pfa2FilterCommunicationError: When the device does not respond
        """
        value = self._clean_lpf_value(value)

        response_str = self._com.query(
            _Pfa2FilterCommands.LPF_FREQUENCY.build_str(self._channel, str(value))  # type: ignore[attr-defined]
        )
        if response_str is None:
            err_msg = f"LPF frequency for channel {self._channel} could not be set"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = int(response_str)
        logger.info(
            f"The LPF frequency for channel {self._channel} is set to {response} Hz"
        )

    @property
    def hpf_freq(self) -> int:
        """
        Get the set 3 dB cut of frequency of the high pass filter

        :raises Pfa2FilterCommunicationError: When the device does not respond
        :raises Pfa2FilterError: When the filter does not have a HPF
        :return: Frequency in Hz
        """
        if self._option_hpf:
            response_str = self._com.query(
                _Pfa2FilterCommands.HPF_FREQUENCY.build_str(self._channel)  # type: ignore[attr-defined]
            )
            if response_str is None:
                err_msg = f"HPF frequency for channel {self._channel} is unknown"
                logger.error(err_msg)
                raise Pfa2FilterCommunicationError(err_msg)

            response = int(response_str)
            logger.debug(f"HPF frequency for channel {self._channel} is {response} Hz")
            return response

        msg = "This filter does not have the high pass filter option"
        logger.error(msg)
        raise Pfa2FilterError(msg)

    @hpf_freq.setter
    def hpf_freq(self, value: int) -> None:
        """
        Set the 3 dB cut of frequency of the high pass filter

        :param value: Frequency in Hz
        :raises Pfa2FilterCommunicationError: When the device does not respond
        :raises Pfa2FilterError: When the filter does not have a HPF
        """
        if self._option_hpf:
            value = self._clean_hpf_value(value)

            response_str = self._com.query(
                _Pfa2FilterCommands.HPF_FREQUENCY.build_str(self._channel, str(value))  # type: ignore[attr-defined]
            )
            if response_str is None:
                err_msg = f"HPF frequency for channel {self._channel} could not be set"
                logger.error(err_msg)
                raise Pfa2FilterCommunicationError(err_msg)

            response = int(response_str)
            logger.info(
                f"The HPF frequency for channel {self._channel} is set to {response} Hz"
            )
            return

        msg = "This filter does not have the high pass filter option"
        logger.error(msg)
        raise Pfa2FilterError(msg)

    @property
    def hpf_state(self) -> bool:
        """
        Get the ON/OFF state of the high pass filter

        :raises Pfa2FilterCommunicationError: When the device does not respond
        :raises Pfa2FilterError: When the filter does not have a HPF
        :return: ON/OFF state of the high pass filter as bool
        """
        if self._option_hpf:
            response = (
                self._com.query(_Pfa2FilterCommands.HPF_STATE.build_str(self._channel))  # type: ignore[attr-defined]
            )
            if response is None:
                err_msg = f"HPF state for channel {self._channel} is unknown"
                logger.error(err_msg)
                raise Pfa2FilterCommunicationError(err_msg)

            response = Pfa2FilterHPFState(response)
            logger.info(f"HPF state for channel {self._channel} is {response.name}")
            return response == Pfa2FilterHPFState.ON

        msg = "This filter does not have the high pass filter option"
        logger.error(msg)
        raise Pfa2FilterError(msg)

    @hpf_state.setter
    def hpf_state(self, value: bool) -> None:
        """
        Set the ON/OFF state of the high pass filter

        :param value: Bool indicating the state
        :raises TypeError: When value is not a boolean
        :raises Pfa2FilterCommunicationError: When the device does not respond
        :raises Pfa2FilterError: When the filter does not have a HPF
        """
        if self._option_hpf:
            if not isinstance(value, bool):
                msg = "Value must be a boolean"
                raise TypeError(msg)
            msg = Pfa2FilterHPFState.ON if value else Pfa2FilterHPFState.OFF

            response = self._com.query(
                _Pfa2FilterCommands.HPF_STATE.build_str(self._channel, msg)  # type: ignore[attr-defined]
            )
            if response is None:
                err_msg = f"HPF state for channel {self._channel} could not be set"
                logger.error(err_msg)
                raise Pfa2FilterCommunicationError(err_msg)

            response = Pfa2FilterHPFState(response)
            logger.info(
                f"Setting HPF state to '{response.name}' for channel {self._channel}"
            )
            return

        err_msg = "This filter does not have the high pass filter option"
        logger.error(err_msg)
        raise Pfa2FilterError(err_msg)

    @property
    def pregain(self) -> Pfa2FilterPreGain:
        """
        Get the gain value of the pre-filter amplifier

        :raises Pfa2FilterCommunicationError: When pre filter gain is unknown
        :return: Gain value from Pfa2FilterPreGain
        """
        response = self._com.query(_Pfa2FilterCommands.PREGAIN.build_str(self._channel))  # type: ignore[attr-defined]
        if response is None:
            err_msg = f"Pre filter gain for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterPreGain(float(response))
        logger.info(f"Pre filter gain for channel {self._channel} is '{response.name}'")
        return response

    @pregain.setter
    def pregain(self, value: Pfa2FilterPreGain | float) -> None:
        """
        Set the gain of the pre-filter amplifier

        :param value: Amplification value from Pfa2FilterPreGain
        :raises Pfa2FilterCommunicationError: When pre filter gain could not be set
        """
        value = Pfa2FilterPreGain(value)

        response = self._com.query(
            _Pfa2FilterCommands.PREGAIN.build_str(self._channel, str(value))  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Pre filter gain for channel {self._channel} could not be set"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterPreGain(float(response))
        logger.info(
            f"Setting pre filter gain to {value.name} for channel {self._channel}"
        )

    @property
    def postgain(self) -> Pfa2FilterPostGain:
        """
        Get the set gain of the post filter amplifier

        :raises Pfa2FilterCommunicationError: When post filter gain is unknown
        :return: Gain value from Pfa2FilterPostGain
        """
        response = self._com.query(
            _Pfa2FilterCommands.POSTGAIN.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Post filter gain for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterPostGain(float(response))
        logger.info(
            f"Post filter gain for channel {self._channel} is '{response.name}'"
        )
        return response

    @postgain.setter
    def postgain(self, value: Pfa2FilterPostGain | float) -> None:
        """
        Set the gain of the post filter amplifier

        :param value: Amplification value from Pfa2FilterPostGain
        :raises Pfa2FilterCommunicationError: When post filter gain could not be set
        """
        value = Pfa2FilterPostGain(value)

        response = self._com.query(
            _Pfa2FilterCommands.POSTGAIN.build_str(self._channel, str(value))  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Post filter gain for channel {self._channel} could not be set"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterPostGain(float(response))
        logger.info(
            f"Setting post filter gain to {response.name} for channel {self._channel}"
        )

    @property
    def input_overload(self) -> bool:
        """
        Check if the input is overloaded

        :raises Pfa2FilterCommunicationError: When input overload status is unknown
        :return: Bool indicating overload
        """
        response_str = self._com.query(
            _Pfa2FilterCommands.IN_OVERLOAD.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response_str is None:
            err_msg = f"Input overload for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = response_str == "1"
        logger.info(
            f"Input for channel {self._channel} is"
            f"{' ' if response else ' not '}overloaded"
        )
        return response

    @property
    def output_overload(self) -> bool:
        """
        Check if the output is overloaded

        :raises Pfa2FilterCommunicationError: When output overload is unknown
        :return: Bool indicating overload
        """
        response_str = self._com.query(
            _Pfa2FilterCommands.OUT_OVERLOAD.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response_str is None:
            err_msg = f"Output overload for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = response_str == "1"
        logger.info(
            f"Output for channel {self._channel} "
            f"is{' ' if response else ' not '}overloaded"
        )
        return response

    @property
    def overload_limit(self) -> float:
        """
        Get the overload limit

        :raises Pfa2FilterCommunicationError: When overload limit is unknown
        :return: Overload limit in V
        """
        response = self._com.query(
            _Pfa2FilterCommands.OVERLOAD_LIMIT.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Overload limit for channel {self._channel} is unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        value = float(response)
        logger.info(f"Overload limit for channel {self._channel} is '{value} V'")
        return value

    @overload_limit.setter
    def overload_limit(self, value: float) -> None:
        """
        Set the overload limit

        :param value: Overload limit in V in 0.1 V steps
        :raises ValueError: When value is not in [0.1 V; 10 V]
        :raises Pfa2FilterCommunicationError: When overload limit could not be set
        """
        validate_number("overload limit", value, (0.1, 10), logger=logger)

        response_str = self._com.query(
            _Pfa2FilterCommands.OVERLOAD_LIMIT.build_str(self._channel, str(value))  # type: ignore[attr-defined]
        )
        if response_str is None:
            err_msg = f"Overload limit for channel {self._channel} could not be set"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = float(response_str)
        logger.info(
            f"Setting overload limit to {response} V for channel {self._channel}"
        )

    @property
    def overload_mode(self) -> Pfa2FilterOverloadMode:
        """
        Get the set overload handling mode

        CONTINUOUS: Overload will reset itself
        LATCHING: Overload must be reset my command or manually at device

        :raises Pfa2FilterCommunicationError: When overload mode is unknown
        :return: Overload handling mode
        """
        response = self._com.query(
            _Pfa2FilterCommands.OVERLOAD_MODE.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Overload mode for channel {self._channel} is not set or unknown"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterOverloadMode(response)
        logger.info(f"Overload mode for channel {self._channel} is '{response.name}'")
        return response

    @overload_mode.setter
    def overload_mode(self, value: Pfa2FilterOverloadMode | str) -> None:
        """
        Set the overload handling mode

        :param value: Value from Pfa2FilterOverloadMode
        :raises TypeError: When value is not a string
        :raises ValueError: When value is not in Pfa2FilterOverloadMode
        :raises Pfa2FilterCommunicationError: When overload mode could not be set
        """
        if not isinstance(value, str):
            raise TypeError
        if value not in Pfa2FilterOverloadMode:  # type: ignore[attr-defined]
            raise ValueError

        response = self._com.query(
            _Pfa2FilterCommands.OVERLOAD_MODE.build_str(self._channel, value)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Overload mode for channel {self._channel} could not be set"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        response = Pfa2FilterOverloadMode(response)
        logger.info(
            f"Setting overload mode to '{response.name}' for channel {self._channel}"
        )

    def overload_clear(self) -> bool:
        """
        Clear a overload

        :raises Pfa2FilterCommunicationError: When filter could not be reached
        :return: True if overload was cleared, False if not, None if in continuous mode
        """
        if self.overload_mode != Pfa2FilterOverloadMode.LATCHING:
            logger.info(
                f"Overload mode for channel {self._channel} is not "
                f"{Pfa2FilterOverloadMode.LATCHING.name}, no need to clear"  # type: ignore[attr-defined]
            )
            return not (self.input_overload or self.output_overload)

        response = self._com.query(
            _Pfa2FilterCommands.OVERLOAD_CLEAR.build_str(self._channel)  # type: ignore[attr-defined]
        )
        if response is None:
            err_msg = f"Overload for channel {self._channel} was not cleared"
            logger.error(err_msg)
            raise Pfa2FilterCommunicationError(err_msg)

        clear = not (self.input_overload or self.output_overload)
        logger.info(
            f"Overload for channel {self._channel} was {'' if clear else 'not '}"
            f"cleared successfully"
        )
        return clear

    @staticmethod
    def _clean_lpf_value(value: int) -> int:
        """
        Checks the value and rounds up to the next available value:
        - If value ≤ 2555, round up to the nearest multiple of 5 Hz
        - If 2555 < value ≤ 2750, use 2750
        - If value > 2750, round up to the nearest multiple of 250 Hz

        :param value: value to check
        :return: checked and rounded value
        """
        validate_number(
            "lpf_value",
            value,
            (LPF_FREQUENCY_MIN, LPF_FREQUENCY_MAX),
            int,
            logger=logger,
        )

        value_out = value

        if value <= 2555:
            value_out = ((value + 4) // 5) * 5  # Round up to nearest multiple of 5
        elif value <= 2750:
            value_out = 2750
        elif value <= 127750:
            value_out = (
                (value + 249) // 250
            ) * 250  # Round up to nearest multiple of 250

        if value_out != value:
            logger.info(f"The LPF frequency was changed to {value} Hz")
        return value_out

    @staticmethod
    def _clean_hpf_value(value: int) -> int:
        """
        Checks the value and rounds down to the next available hpf setting.
        - If value < 255 Hz round down to the nearest multiple of 1 Hz
        - If 255 Hz ≤ value < 300 Hz, use 255 Hz
        - If 300 Hz ≤ value < 12750 Hz, round down to the nearest multiple 50 Hz
        - If 12750 Hz ≤ value < 13000 Hz, use 12750 Hz
        - If 13000 Hz ≤ value, round down to the nearest multiple 500 Hz

        :param value: value to check
        :return: checked and rounded value
        """
        validate_number(
            "hpf_value",
            value,
            (HPF_FREQUENCY_MIN, HPF_FREQUENCY_MAX),
            int,
            logger=logger,
        )

        value_out = value

        if value < 255:
            pass
        elif value < 300:
            value_out = 255
        elif value < 12750:
            value_out = (value // 50) * 50  # Round down to nearest multiple of 50
        elif value < 13000:
            value_out = 12750
        elif value <= 127500:
            value_out = (value // 500) * 500  # Round down to nearest multiple of 500

        if value_out != value:
            logger.info(f"The HPF frequency was changed to {value} Hz")
        return value_out
