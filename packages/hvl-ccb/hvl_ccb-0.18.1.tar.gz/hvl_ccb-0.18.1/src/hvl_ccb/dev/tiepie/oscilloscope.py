#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
""" """

import logging
import time
from collections.abc import Generator
from typing import cast

import libtiepie as ltp
import numpy as np
import numpy.typing as npt
from aenum import IntEnum
from libtiepie import oscilloscope as ltp_osc

from hvl_ccb.comm import NullCommunicationProtocol
from hvl_ccb.dev import SingleCommDevice
from hvl_ccb.utils.enum import NameEnum
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

from .base import (
    TiePieDeviceConfig,
    TiePieDeviceType,
    TiePieError,
    _LtpDeviceReturnType,
    _require_dev_handle,
    _verify_via_libtiepie,
    get_device_by_serial_number,
    wrap_libtiepie_exception,
)
from .channel import TiePieOscilloscopeChannelConfig
from .utils import PublicPropertiesReprMixin

logger = logging.getLogger(__name__)


class TiePieOscilloscopeResolution(IntEnum):
    EIGHT_BIT = 8
    TWELVE_BIT = 12
    FOURTEEN_BIT = 14
    SIXTEEN_BIT = 16


class TiePieOscilloscopeAutoResolutionModes(NameEnum, init="value description"):  # type: ignore[call-arg]
    UNKNOWN = ltp.ARM_UNKNOWN, "Unknown"
    DISABLED = ltp.ARM_DISABLED, "Disabled"
    NATIVEONLY = ltp.ARM_NATIVEONLY, "Native only"
    ALL = ltp.ARM_ALL, "All"


class TiePieOscilloscopeConfigLimits:
    """
    Default limits for oscilloscope parameters.
    """

    def __init__(self, dev_osc: ltp_osc.Oscilloscope) -> None:
        self.record_length = (0, dev_osc.record_length_max)
        self.sample_rate = (0, dev_osc.sample_rate_max)  # [samples/s]
        self.pre_sample_ratio = (0, 1)
        # self.trigger_delay = (0, dev_osc.trigger_delay_max)  # trigger_delay is not
        # available for all instruments, cf. API from TiePie:
        # Functions » Oscilloscope » Trigger » Delay


class TiePieOscilloscopeConfig(PublicPropertiesReprMixin):
    """
    Oscilloscope's configuration with cleaning of values in properties setters.
    """

    def __init__(self, dev_osc: ltp_osc.Oscilloscope) -> None:
        self.dev_osc: ltp_osc.Oscilloscope = dev_osc
        self.param_lim: TiePieOscilloscopeConfigLimits = TiePieOscilloscopeConfigLimits(
            dev_osc=dev_osc
        )

    def clean_pre_sample_ratio(self, pre_sample_ratio: float) -> float:
        validate_number(
            "pre sample ratio",
            pre_sample_ratio,
            self.param_lim.pre_sample_ratio,
            logger=logger,
        )
        return float(pre_sample_ratio)

    @property
    def pre_sample_ratio(self) -> float:
        return self.dev_osc.pre_sample_ratio

    @pre_sample_ratio.setter
    def pre_sample_ratio(self, pre_sample_ratio: float) -> None:
        """
        Set pre sample ratio

        :param pre_sample_ratio: pre sample ratio numeric value.
        :raise ValueError: If `pre_sample_ratio` is not a number between 0 and 1
            (inclusive).
        """
        self.dev_osc.pre_sample_ratio = self.clean_pre_sample_ratio(pre_sample_ratio)
        logger.info(f"Pre-sample ratio is set to {pre_sample_ratio}.")

    def clean_record_length(self, record_length: Number) -> int:
        validate_number(
            "record length",
            record_length,
            limits=self.param_lim.record_length,
            logger=logger,
        )

        if not (float(record_length).is_integer()):
            msg = (
                "The record_length has to be a value, that can be cast "
                "into an integer without significant precision loss; "
                f"but {record_length:_d} was assigned."
            )
            raise ValueError(msg)

        return cast(
            "int",
            _verify_via_libtiepie(self.dev_osc, "record_length", int(record_length)),
        )

    @property
    def record_length(self) -> int:
        return self.dev_osc.record_length

    @record_length.setter
    def record_length(self, record_length: int) -> None:
        record_length = self.clean_record_length(record_length)
        self.dev_osc.record_length = record_length
        logger.info(f"Record length is set to {record_length:_d} Sa.")

    @staticmethod
    def clean_resolution(
        resolution: int | TiePieOscilloscopeResolution,
    ) -> TiePieOscilloscopeResolution:
        if not isinstance(resolution, TiePieOscilloscopeResolution):
            validate_number("resolution", resolution, number_type=int, logger=logger)
        return TiePieOscilloscopeResolution(resolution)

    @property
    def resolution(self) -> TiePieOscilloscopeResolution:
        return self.dev_osc.resolution

    @resolution.setter
    def resolution(self, resolution: int | TiePieOscilloscopeResolution) -> None:
        """
        Setter for resolution of the Oscilloscope.

        :param resolution: resolution integer.
        :raises ValueError: if resolution is not one of
            `TiePieOscilloscopeResolution` instance or integer values
        """
        self.dev_osc.resolution = self.clean_resolution(resolution)
        logger.info(f"Resolution is set to {self.dev_osc.resolution} bit.")

    @staticmethod
    def clean_auto_resolution_mode(
        auto_resolution_mode: int | TiePieOscilloscopeAutoResolutionModes,
    ) -> TiePieOscilloscopeAutoResolutionModes:
        if not isinstance(auto_resolution_mode, TiePieOscilloscopeAutoResolutionModes):
            validate_number(
                "auto resolution mode",
                auto_resolution_mode,
                number_type=int,
                logger=logger,
            )
        if isinstance(auto_resolution_mode, bool):
            msg = "Auto resolution mode cannot be of boolean type"
            logger.error(msg)
            raise TypeError
        return TiePieOscilloscopeAutoResolutionModes(auto_resolution_mode)

    @property
    def auto_resolution_mode(self) -> TiePieOscilloscopeAutoResolutionModes:
        return TiePieOscilloscopeAutoResolutionModes(self.dev_osc.auto_resolution_mode)

    @auto_resolution_mode.setter
    def auto_resolution_mode(self, auto_resolution_mode):
        self.dev_osc.auto_resolution_mode = self.clean_auto_resolution_mode(
            auto_resolution_mode
        ).value
        logger.info(f"Auto resolution mode is set to {auto_resolution_mode}.")

    def clean_sample_rate(self, sample_rate: float) -> float:
        validate_number(
            "sample rate",
            sample_rate,
            self.param_lim.sample_rate,
            logger=logger,
        )
        sample_rate = _verify_via_libtiepie(self.dev_osc, "sample_rate", sample_rate)
        return float(sample_rate)

    @property
    def sample_rate(self) -> float:
        return self.dev_osc.sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate: float):
        """
        Set sample rate of the oscilloscope.

        :param sample_rate: rate to set
        :raises ValueError: when rate is not in device range
        """
        sample_rate = self.clean_sample_rate(sample_rate)
        self.dev_osc.sample_rate = sample_rate
        logger.info(f"Sample rate is set to {sample_rate:_.3f} Sa/s.")

    @property
    def sample_frequency(self) -> float:
        """For backwards compatibility. Use `sample_rate` instead"""
        logger.warning(
            "The usage of `sample_frequency` is deprecated, use "
            "`sample_rate` instead. In future versions this will raise an "
            "`AttributeError`."
        )
        return self.sample_rate

    @sample_frequency.setter
    def sample_frequency(self, sample_frequency: float):
        """For backwards compatibility. Use `sample_rate` instead"""
        logger.warning(
            "The usage of `sample_frequency` is deprecated, use "
            "`sample_rate` instead. In future versions this will raise an "
            "`AttributeError`."
        )
        self.sample_rate = sample_frequency

    def clean_trigger_timeout(self, trigger_timeout: Number | None) -> float:
        if trigger_timeout in (None, ltp.const.TO_INFINITY):
            # infinite timeout: `TO_INFINITY = -1` in `libtiepie.const`
            trigger_timeout = ltp.const.TO_INFINITY
        else:
            validate_number(
                "trigger timeout",
                trigger_timeout,
                limits=(0, None),
                logger=logger,
            )
        trigger_timeout = _verify_via_libtiepie(
            self.dev_osc.trigger, "timeout", cast("Number", trigger_timeout)
        )
        return float(trigger_timeout)

    @property
    def trigger_timeout(self) -> float | None:
        if self.dev_osc.trigger.timeout == ltp.const.TO_INFINITY:
            return None
        return self.dev_osc.trigger.timeout

    @trigger_timeout.setter
    def trigger_timeout(self, trigger_timeout: Number | None) -> None:
        """
        Set trigger time-out.

        :param trigger_timeout: Trigger timeout value, in seconds; `0`  forces
            trigger to start immediately after starting a measurement;
            None leads to no timeout
        :raise ValueError: If trigger timeout is not a non-negative real number.
        """
        trigger_timeout = self.clean_trigger_timeout(trigger_timeout)
        self.dev_osc.trigger.timeout = trigger_timeout
        if trigger_timeout == ltp.const.TO_INFINITY:
            logger.info("Trigger timeout is set to \u221e (INFINITY) s.")
        else:
            logger.info(f"Trigger timeout is set to {trigger_timeout} s.")


class TiePieOscilloscope(SingleCommDevice):
    """
    TiePie oscilloscope.

    A wrapper for TiePie oscilloscopes, based on the class
    `libtiepie.oscilloscope.Oscilloscope` with simplifications for starting of the
    device (using serial number) and managing mutable configuration of both the
    device and its channels, including extra validation and typing hints support for
    configurations.

    Note that, in contrast to `libtiepie` library, since all physical TiePie devices
    include an oscilloscope, this is the base class for all physical TiePie devices.
    The additional TiePie sub-devices: "Generator" is mixed-in to this base class in
    subclasses.

    The channels use `1..N` numbering (not `0..N-1`), as in, e.g., the Multi Channel
    software.
    """

    @staticmethod
    def config_cls() -> type[TiePieDeviceConfig]:
        return TiePieDeviceConfig

    @staticmethod
    def default_com_cls() -> type[NullCommunicationProtocol]:
        return NullCommunicationProtocol

    def __init__(self, com, dev_config) -> None:
        """
        Constructor for a TiePie device.
        """
        super().__init__(com, dev_config)

        self._osc: ltp_osc.Oscilloscope | None = None

        self.config_osc: TiePieOscilloscopeConfig | None = None
        """
        Oscilloscope's dynamical configuration.
        """

        self.config_osc_channel_dict: dict[int, TiePieOscilloscopeChannelConfig] = {}
        """
        Channel configuration.
        A `dict` mapping actual channel number, numbered `1..N`, to channel
        configuration. The channel info is dynamically read from the device only on
        the first `start()`; beforehand the `dict` is empty.
        """

    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def _osc_config_setup(self) -> None:
        """
        Setup dynamical configuration for the connected oscilloscope.
        """
        self.config_osc = TiePieOscilloscopeConfig(
            cast("ltp_osc.Oscilloscope", self._osc)
        )
        for n in range(1, self.n_channels + 1):
            self.config_osc_channel_dict[n] = TiePieOscilloscopeChannelConfig(
                ch_number=n,
                channel=cast("ltp_osc.Oscilloscope", self._osc).channels[n - 1],
            )

    def _osc_config_teardown(self) -> None:
        """
        Teardown dynamical configuration for the oscilloscope.
        """
        self.config_osc = None
        self.config_osc_channel_dict = {}

    def _osc_close(self) -> None:
        """
        Close the wrapped `libtiepie` oscilloscope.
        """
        if self._osc is not None:
            del self._osc
            self._osc = None

    def _get_device_by_serial_number(
        self,
        # Note: TiePieDeviceType aenum as a tuple to define a return value type
        ltp_device_type: tuple[int, _LtpDeviceReturnType],
    ) -> _LtpDeviceReturnType:
        """
        Wrapper around `get_device_by_serial_number` using this device's config options.

        :return: A `libtiepie` device object specific to a class it is called on.
        """
        return get_device_by_serial_number(
            self.config.serial_number,
            ltp_device_type,
            n_max_try_get_device=self.config.n_max_try_get_device,
            wait_sec_retry_get_device=self.config.wait_sec_retry_get_device,
        )

    @wrap_libtiepie_exception
    def start(self) -> None:
        """
        Start the oscilloscope.
        """
        logger.info(f"Starting {self}")
        super().start()
        logger.info(
            f"Starting oscilloscope with serial number {self.config.serial_number}"
        )

        self._osc = self._get_device_by_serial_number(TiePieDeviceType.OSCILLOSCOPE)

        # Check for block measurement support if required
        if self.config.require_block_measurement_support and not (
            self._osc.measure_modes & ltp.MM_BLOCK
        ):
            self._osc_close()
            msg = (
                f"Oscilloscope with serial number {self.config.serial_number} does not "
                "have required block measurement support."
            )
            logger.error(msg)
            raise TiePieError(msg)

        self._osc_config_setup()

    @wrap_libtiepie_exception
    def stop(self) -> None:
        """
        Stop the oscilloscope.
        """
        logger.info(f"Stopping {self}")
        logger.info("Stopping oscilloscope")

        self._osc_config_teardown()
        self._osc_close()

        super().stop()

    @staticmethod
    @wrap_libtiepie_exception
    def list_devices() -> ltp.devicelist.DeviceList:
        """
        List available TiePie devices.

        :return: libtiepie up to date list of devices
        """
        ltp.network.auto_detect_enabled = True
        device_list = ltp.device_list
        device_list.update()

        # log devices list
        if device_list:
            logger.info("Available devices:\n")

            for item in ltp.device_list:
                logger.info(f"  Name:              {item.name}")
                logger.info(f"  Serial number:     {item.serial_number}")
                logger.info(f"  Available types:   {ltp.device_type_str(item.types)}")
                if item.has_server:
                    logger.info(
                        f"  Server:            {item.server.url}({item.server.name})"
                    )
                logger.info(
                    "  Can be opened as "
                    f"Oscilloscope: {item.can_open(ltp.DEVICETYPE_OSCILLOSCOPE)}\n"
                )

        else:
            logger.info("No devices found!")

        return device_list

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def start_measurement(self) -> None:
        """
        Start a measurement using set configuration.

        :raises TiePieError: when device is not started, when measurement is already
        running, or when status of underlying device gives an error.
        """
        if self.is_measurement_running():
            msg = "TiePie measurement is already running"
            raise TiePieError(msg)
        cast("ltp_osc.Oscilloscope", self._osc).start()

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def stop_measurement(self) -> None:
        """
        Stop a measurement that is already running.

        :raises TiePieError: when device is not started, when measurement is not
        running, or when status of underlying device gives an error
        """
        if not self.is_measurement_running():
            msg = "TiePie measurement is not running"
            raise TiePieError(msg)
        cast("ltp_osc.Oscilloscope", self._osc).stop()

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def is_measurement_running(self) -> bool:
        """
        Reports if TiePie measurement is running (ready for trigger)

        :return: if a TiePie measurement is running (ready for trigger)
        """
        _is_running = cast("ltp_osc.Oscilloscope", self._osc).is_running
        logger.debug(f"TiePie measurement is running: {_is_running}")
        return _is_running

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def is_triggered(self) -> bool:
        """
        Reports if TiePie has triggered. Maybe data is not yet available. One can
        check with the function `is_measurement_data_ready()`.

        :return: if a trigger event occurred
        """
        _is_triggered = cast("ltp_osc.Oscilloscope", self._osc).is_triggered
        logger.debug(f"TiePie has triggered: {_is_triggered}")
        return _is_triggered

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def is_measurement_data_ready(self) -> bool:
        """
        Reports if TiePie has data which is ready to collect

        :return: if the data is ready to collect.
        :raises TiePieError: when device is not started or status of underlying device
            gives an error
        """
        _is_measurement_data_ready = cast(
            "ltp_osc.Oscilloscope", self._osc
        ).is_data_ready
        logger.debug(f"TiePie has measurement data ready: {_is_measurement_data_ready}")
        return _is_measurement_data_ready

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def force_trigger(self) -> None:
        """
        Forces the TiePie to trigger with a software sided trigger event.

        :return None:
        :raises TiePieError: when device is not started or status of underlying device
            gives an error
        """
        cast("ltp_osc.Oscilloscope", self._osc).force_trigger()
        logger.info("A force trigger was sent to TiePie")

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def _check_record_length(self, data_array: npt.NDArray) -> None:
        """
        Check record length

        :param data_array: raw data from TiePie as np.ndarray, which is already
            filtered
        :return None:
        """
        if self.config_osc is None:
            logger.warning("Oscilloscope is not configured")
            return

        record_length_actual = len(data_array[:, 0])
        if record_length_actual < self.config_osc.record_length:
            logger.warning(
                "Less Data than expected: Most likely the trigger occurred "
                "before all pre trigger samples could be recorded. "
                "(pre_sample_ratio was too high)"
            )
            pre_sample_count = cast(
                "ltp_osc.Oscilloscope", self._osc
            ).valid_pre_sample_count
        record_length_predicted = (
            int(self.config_osc.record_length * (1 - self.config_osc.pre_sample_ratio))
            + pre_sample_count
        )
        if record_length_actual != record_length_predicted:
            logger.warning(
                f"The actual record length ({record_length_actual} Sa) "
                "is shorter than the "
                f"predicted record length ({record_length_predicted} Sa)"
            )

    @wrap_libtiepie_exception
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    def collect_measurement_data(
        self, timeout: Number | None = 0
    ) -> npt.NDArray | None:
        """
        Try to collect the data from TiePie; return `None` if data is not ready.

        :param timeout: The timeout to wait until data is available. This
            option makes this function blocking the code. `timeout = None` blocks the
            code infinitely till data will be available. Per default, the `timeout`
            is set to `0`: The function will not block.
        :return: Measurement data of only enabled channels and time vector in a
            2D-`numpy.ndarray` with float sample data; or None if there is no data
            available.
        """
        # make mypy happy: config_osc could be None, which has no attributes
        if self.config_osc is None:
            logger.warning("Oscilloscope is not configured")
            return None

        if timeout is not None and not isinstance(timeout, float | int):
            msg = (
                "timeout must be non-negative number, "
                f"but '{timeout}' of type {type(timeout)} was given"
            )
            logger.error(msg)
            raise ValueError(msg)

        # Wait till timeout or till data is ready
        start_time = time.time()
        while not self.is_measurement_data_ready() and (
            timeout is None or (time.time() - start_time < timeout)
        ):
            time.sleep(self.config.is_data_ready_polling_interval_sec)

        if not self.is_measurement_data_ready():
            logger.warning(
                "Data from TiePie was not ready to collect "
                f"during a timeout of {timeout} s."
            )
            return None

        # Collect raw data from tiepie
        data = cast("ltp_osc.Oscilloscope", self._osc).get_data()
        # filter-out disabled channels entries
        data_array: npt.NDArray = np.array(list(filter(None, data))).T

        self._check_record_length(data_array)

        pre_sample_count = cast(
            "ltp_osc.Oscilloscope", self._osc
        ).valid_pre_sample_count
        record_length_actual = len(data_array[:, 0])
        time_vector = np.arange(
            -pre_sample_count, record_length_actual - pre_sample_count
        )
        time_vector = time_vector / self.config_osc.sample_rate

        return np.column_stack([time_vector, data_array])

    @property
    @_require_dev_handle(TiePieDeviceType.OSCILLOSCOPE)
    @wrap_libtiepie_exception
    def n_channels(self) -> int:
        """
        Number of channels in the oscilloscope.

        :return: Number of channels.
        """
        return len(self._osc.channels)  # type: ignore[union-attr]

    @property
    def channels_enabled(self) -> Generator[int, None, None]:
        """
        Yield numbers of enabled channels.

        :return: Numbers of enabled channels
        """
        for ch_nr, ch_config in self.config_osc_channel_dict.items():
            if ch_config.enabled:
                yield ch_nr
