#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
""" """

import logging
from typing import Literal

import libtiepie as ltp
from aenum import Enum, MultiValue
from libtiepie import oscilloscopechannel as ltp_osc_ch

from hvl_ccb.utils.enum import NameEnum, RangeEnum
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_bool, validate_number

from .base import TiePieError, wrap_libtiepie_exception
from .utils import PublicPropertiesReprMixin

logger = logging.getLogger(__name__)


class TiePieOscilloscopeChannelCoupling(NameEnum, init="value description"):  # type: ignore[call-arg]
    DCV = ltp.CK_DCV, "DC volt"
    ACV = ltp.CK_ACV, "AC volt"
    DCA = ltp.CK_DCA, "DC current"
    ACA = ltp.CK_ACA, "AC current"


class TiePieOscilloscopeRange(RangeEnum):
    TWO_HUNDRED_MILLI_VOLT = 0.2
    FOUR_HUNDRED_MILLI_VOLT = 0.4
    EIGHT_HUNDRED_MILLI_VOLT = 0.8
    TWO_VOLT = 2
    FOUR_VOLT = 4
    EIGHT_VOLT = 8
    TWENTY_VOLT = 20
    FORTY_VOLT = 40
    EIGHTY_VOLT = 80

    @classmethod
    def unit(cls) -> Literal["V"]:
        return "V"


class TiePieOscilloscopeTriggerKind(Enum, settings=MultiValue):  # type: ignore[call-arg]
    RISING = ltp.TK_RISINGEDGE, "Rising", "RISING"
    FALLING = ltp.TK_FALLINGEDGE, "Falling", "FALLING"
    ANY = ltp.TK_ANYEDGE, "Any", "ANY"


class TiePieOscilloscopeTriggerLevelMode(NameEnum, init="value description"):  # type: ignore[call-arg]
    UNKNOWN = ltp.TLM_UNKNOWN, "Unknown"
    RELATIVE = ltp.TLM_RELATIVE, "Relative"
    ABSOLUTE = ltp.TLM_ABSOLUTE, "Absolute"


class TiePieOscilloscopeChannelConfig(PublicPropertiesReprMixin):
    """
    Oscilloscope's channel configuration, with cleaning of
    values in properties setters as well as setting and reading them on and
    from the device's channel.
    """

    def __init__(self, ch_number: int, channel: ltp_osc_ch.OscilloscopeChannel) -> None:
        self.ch_number: int = ch_number
        self._channel: ltp_osc_ch.OscilloscopeChannel = channel
        self.param_lim: TiePieOscilloscopeChannelConfigLimits = (
            TiePieOscilloscopeChannelConfigLimits(osc_channel=channel)
        )

    @staticmethod
    def clean_coupling(
        coupling: str | TiePieOscilloscopeChannelCoupling,
    ) -> TiePieOscilloscopeChannelCoupling:
        return TiePieOscilloscopeChannelCoupling(coupling)

    @property
    @wrap_libtiepie_exception
    def coupling(self) -> TiePieOscilloscopeChannelCoupling:
        return TiePieOscilloscopeChannelCoupling(self._channel.coupling)

    @coupling.setter
    def coupling(self, coupling: str | TiePieOscilloscopeChannelCoupling) -> None:
        self._channel.coupling = self.clean_coupling(coupling).value
        logger.info(f"Coupling is set to {coupling}.")

    @staticmethod
    def clean_enabled(enabled: bool) -> bool:
        validate_bool("channel enabled", enabled, logger=logger)
        return enabled

    @property
    def enabled(self) -> bool:
        return self._channel.enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self._channel.enabled = self.clean_enabled(enabled)
        msg = "enabled" if enabled else "disabled"
        logger.info(f"Channel {self.ch_number} is set to {msg}.")

    def clean_input_range(
        self, input_range: float | TiePieOscilloscopeRange
    ) -> TiePieOscilloscopeRange:
        if not isinstance(input_range, TiePieOscilloscopeRange):
            validate_number(
                "input range",
                input_range,
                self.param_lim.input_range,
                logger=logger,
            )
        return TiePieOscilloscopeRange(input_range)

    @property
    def input_range(self) -> TiePieOscilloscopeRange:
        return TiePieOscilloscopeRange(self._channel.range)

    @input_range.setter
    def input_range(self, input_range: float | TiePieOscilloscopeRange) -> None:
        input_range = self.clean_input_range(input_range).value
        self._channel.range = input_range
        self.param_lim.trigger_level_abs = (-input_range, input_range)
        logger.info(f"input range is set to {self._channel.range} V.")

    @property
    def probe_offset(self) -> float:
        """The measured value of the channel will be shifted by an offset.
        *This feature is currently not implemented*
        """
        msg = (
            "The 'probe_offset' is deprecated and cannot be used anymore. Please,"
            " support the 'hvl_ccb' with an own implementation."
        )
        logger.error(msg)
        raise NotImplementedError(msg)

    @probe_offset.setter
    def probe_offset(self, _probe_offset: float) -> None:
        """The measured value of the channel will be shifted by an offset.
        *This feature is currently not implemented*
        """
        msg = (
            "The 'probe_offset' is deprecated and cannot be used anymore. Please,"
            " support the 'hvl_ccb' with an own implementation."
        )
        logger.error(msg)
        raise NotImplementedError(msg)

    @property
    def probe_gain(self) -> float:
        """The measured value of the channel will be scaled by a gain.
        *This feature is currently not implemented*
        """
        msg = (
            "The 'probe_gain' is deprecated and cannot be used anymore. Please,"
            " support the 'hvl_ccb' with an own implementation."
        )
        logger.error(msg)
        raise NotImplementedError(msg)

    @probe_gain.setter
    def probe_gain(self, _probe_gain: float) -> None:
        """The measured value of the channel will be scaled by a gain.
        *This feature is currently not implemented*
        """
        msg = (
            "The 'probe_gain' is deprecated and cannot be used anymore. Please,"
            " support the 'hvl_ccb' with an own implementation."
        )
        logger.error(msg)
        raise NotImplementedError(msg)

    @property
    @wrap_libtiepie_exception
    def has_safeground(self) -> bool:
        """
        Check whether bound oscilloscope device has "safeground" option

        :return: bool: 1=safeground available
        """
        return self._channel.has_safeground

    @property
    @wrap_libtiepie_exception
    def safeground_enabled(self) -> bool:
        """safeground

        :return: _description_
        """
        if not self.has_safeground:
            msg = "The oscilloscope has no safe ground option."
            logger.error(msg)
            raise TiePieError(msg)

        return self._channel.safeground_enabled

    @safeground_enabled.setter
    @wrap_libtiepie_exception
    def safeground_enabled(self, value: bool) -> None:
        if not self.has_safeground:
            msg = "The oscilloscope has no safeground option."
            raise TiePieError(msg)

        validate_bool("safeground enabled", value, logger=logger)
        self._channel.safeground_enabled = value
        msg = "enabled" if value else "disabled"
        logger.info(f"Safeground is {msg}.")

    def clean_trigger_hysteresis(self, trigger_hysteresis: float) -> float:
        validate_number(
            "trigger hysteresis",
            trigger_hysteresis,
            self.param_lim.trigger_hysteresis,
            logger=logger,
        )
        return float(trigger_hysteresis)

    @property
    def trigger_hysteresis(self) -> float:
        return self._channel.trigger.hystereses[0]

    @trigger_hysteresis.setter
    def trigger_hysteresis(self, trigger_hysteresis: float) -> None:
        self._channel.trigger.hystereses[0] = self.clean_trigger_hysteresis(
            trigger_hysteresis
        )
        logger.info(f"Trigger hysteresis is set to {trigger_hysteresis}.")

    @staticmethod
    def clean_trigger_kind(
        trigger_kind: str | TiePieOscilloscopeTriggerKind,
    ) -> TiePieOscilloscopeTriggerKind:
        return TiePieOscilloscopeTriggerKind(trigger_kind)

    @property
    def trigger_kind(self) -> TiePieOscilloscopeTriggerKind:
        return TiePieOscilloscopeTriggerKind(self._channel.trigger.kind)

    @trigger_kind.setter
    def trigger_kind(self, trigger_kind: str | TiePieOscilloscopeTriggerKind) -> None:
        self._channel.trigger.kind = self.clean_trigger_kind(trigger_kind).value
        logger.info(f"Trigger kind is set to {trigger_kind}.")

    @staticmethod
    def clean_trigger_level_mode(
        level_mode: str | TiePieOscilloscopeTriggerLevelMode,
    ) -> TiePieOscilloscopeTriggerLevelMode:
        return TiePieOscilloscopeTriggerLevelMode(level_mode)

    @property
    def trigger_level_mode(self) -> TiePieOscilloscopeTriggerLevelMode:
        return TiePieOscilloscopeTriggerLevelMode(self._channel.trigger.level_mode)

    @trigger_level_mode.setter
    def trigger_level_mode(
        self, level_mode: str | TiePieOscilloscopeTriggerLevelMode
    ) -> None:
        level_mode_ = self.clean_trigger_level_mode(level_mode)
        self._channel.trigger.level_mode = level_mode_.value
        logger.info(f"Trigger level mode is set to {level_mode_.name}.")

    def clean_trigger_level(self, trigger_level: Number) -> float:
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.RELATIVE:
            validate_number(
                "trigger level",
                trigger_level,
                self.param_lim.trigger_level_rel,
                float,
                logger=logger,
            )
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.ABSOLUTE:
            validate_number(
                "trigger level",
                trigger_level,
                self.param_lim.trigger_level_abs,
                (int, float),
                logger=logger,
            )
        return float(trigger_level)

    @property
    def trigger_level(self) -> float:
        return self._channel.trigger.levels[0]

    @trigger_level.setter
    def trigger_level(self, trigger_level: Number) -> None:
        self._channel.trigger.levels[0] = self.clean_trigger_level(trigger_level)
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.RELATIVE:
            logger.info(f"Trigger level is set to {trigger_level}.")
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.ABSOLUTE:
            logger.info(f"Trigger level is set to {trigger_level} V.")

    @staticmethod
    def clean_trigger_enabled(trigger_enabled: bool) -> bool:
        validate_bool("Trigger enabled", trigger_enabled, logger=logger)
        return trigger_enabled

    @property
    def trigger_enabled(self) -> bool:
        return self._channel.trigger.enabled

    @trigger_enabled.setter
    def trigger_enabled(self, trigger_enabled: bool) -> None:
        self._channel.trigger.enabled = self.clean_trigger_enabled(trigger_enabled)
        msg = "enabled" if trigger_enabled else "disabled"
        logger.info(f"Trigger is set to {msg}.")


class TiePieOscilloscopeChannelConfigLimits:
    """
    Default limits for oscilloscope channel parameters.
    """

    def __init__(self, osc_channel: ltp_osc_ch.OscilloscopeChannel) -> None:
        self.input_range = (osc_channel.ranges[0], osc_channel.ranges[-1])  # [V]
        self.trigger_hysteresis = (0, 1)
        self.trigger_level_rel = (0, 1)
        self.trigger_level_abs = (-osc_channel.ranges[-1], osc_channel.ranges[-1])
